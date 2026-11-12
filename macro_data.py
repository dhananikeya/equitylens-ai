import html
import io
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urljoin

import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

from services.http import get as service_get
from services.providers.bls import (
    fetch_calendar as fetch_bls_calendar,
    fetch_series as fetch_bls_series,
)
from services.providers.bloomberg import (
    fetch_feed as fetch_bloomberg_feed,
    fetch_markets as fetch_bloomberg_markets,
)
from services.providers.federal_reserve import (
    fetch_fomc_calendar,
    fetch_monetary_feed,
)
from services.providers.nyfed import (
    fetch_sofr,
    fetch_sofr_averages,
)
from services.providers.swaps import fetch_swap_curve
from services.providers.treasury import (
    fetch_fred_csv,
    fetch_treasury_csv,
    fetch_treasury_html,
    fetch_treasury_xml,
)


def _safe_float(value):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def market_provider_error(provider, exc):
    """Return a safe, user-facing provider error without exposing credentials."""
    status_code = getattr(getattr(exc, "response", None), "status_code", None)

    if status_code == 429:
        return (
            f"{provider} rate limit reached. EquityLens will keep the last cached data "
            "and try again after the provider quota resets."
        )

    return (
        f"{provider} is temporarily unavailable. Check the provider configuration "
        "or try again shortly."
    )



PUBLIC_DATA_HEADERS = {
    "User-Agent": "EquityLensAI/1.0 (+https://github.com/dhananikeya/equitylens-ai)"
}


def _numeric_text(value):
    if value is None:
        return None
    text = str(value).strip().replace(",", "").replace("%", "")
    text = text.replace("−", "-").replace("–", "-")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _treasury_header_key(value):
    """Normalize Treasury table headers to the tenors EquityLens displays."""
    text = re.sub(
        r"[^a-z0-9.]",
        "",
        str(value or "").lower()
    )
    aliases = {
        "1mo": "1M",
        "1month": "1M",
        "3mo": "3M",
        "3month": "3M",
        "6mo": "6M",
        "6month": "6M",
        "1yr": "1Y",
        "1year": "1Y",
        "2yr": "2Y",
        "2year": "2Y",
        "3yr": "3Y",
        "3year": "3Y",
        "5yr": "5Y",
        "5year": "5Y",
        "7yr": "7Y",
        "7year": "7Y",
        "10yr": "10Y",
        "10year": "10Y",
        "20yr": "20Y",
        "20year": "20Y",
        "30yr": "30Y",
        "30year": "30Y",
    }
    return aliases.get(text)


def _fetch_treasury_yield_curve_csv():
    """Read Treasury's official downloadable daily par-yield CSV."""
    year = datetime.now(timezone.utc).year
    source_url = (
        "https://home.treasury.gov/resource-center/data-chart-center/"
        f"interest-rates/daily-treasury-rates.csv/{year}/all"
        f"?_format=csv&field_tdr_date_value={year}"
        "&page=&type=daily_treasury_yield_curve"
    )

    response = fetch_treasury_csv(
        source_url,
        {
            **PUBLIC_DATA_HEADERS,
            "Accept": "text/csv,text/plain;q=0.9,*/*;q=0.8",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0 Safari/537.36 EquityLensAI/1.0"
            ),
        },
    )

    frame = pd.read_csv(io.StringIO(response.text))
    if frame.empty:
        raise ValueError("Treasury CSV returned no observations.")

    date_column = next(
        (
            column for column in frame.columns
            if re.sub(r"[^a-z0-9]", "", str(column).lower()) == "date"
        ),
        None,
    )
    if date_column is None:
        raise ValueError("Treasury CSV did not include a Date column.")

    frame["_parsed_date"] = pd.to_datetime(
        frame[date_column],
        errors="coerce",
    )
    frame = frame[frame["_parsed_date"].notna()].copy()
    if frame.empty:
        raise ValueError("Treasury CSV contained no parseable dates.")

    latest = frame.sort_values("_parsed_date").iloc[-1]

    rates = {}
    for column in frame.columns:
        tenor = _treasury_header_key(column)
        if tenor:
            rates[tenor] = _numeric_text(latest.get(column))

    if not any(
        rates.get(tenor) is not None
        for tenor in ("2Y", "5Y", "10Y", "30Y")
    ):
        raise ValueError("Treasury CSV contained no usable core yields.")

    return {
        "date": latest["_parsed_date"].strftime("%Y-%m-%d"),
        "rates": rates,
        "source_url": source_url,
        "source_format": "Treasury official CSV",
    }


def _fetch_fred_treasury_yield_curve():
    """Fallback to public FRED constant-maturity Treasury series."""
    source_url = (
        "https://fred.stlouisfed.org/graph/fredgraph.csv"
        "?id=DGS1MO,DGS3MO,DGS6MO,DGS1,DGS2,DGS3,DGS5,DGS7,DGS10,DGS20,DGS30"
    )
    response = fetch_fred_csv(
        source_url,
        {
            **PUBLIC_DATA_HEADERS,
            "Accept": "text/csv,text/plain;q=0.9,*/*;q=0.8",
        },
    )

    frame = pd.read_csv(io.StringIO(response.text))
    if frame.empty or "DATE" not in frame.columns:
        raise ValueError("FRED Treasury series returned no usable observations.")

    frame["_parsed_date"] = pd.to_datetime(
        frame["DATE"],
        errors="coerce",
    )

    series_map = {
        "1M": "DGS1MO",
        "3M": "DGS3MO",
        "6M": "DGS6MO",
        "1Y": "DGS1",
        "2Y": "DGS2",
        "3Y": "DGS3",
        "5Y": "DGS5",
        "7Y": "DGS7",
        "10Y": "DGS10",
        "20Y": "DGS20",
        "30Y": "DGS30",
    }

    # FRED may publish different maturities on slightly different timestamps.
    # Use the most recent available observation for each tenor.
    rates = {}
    latest_dates = []

    for tenor, series in series_map.items():
        if series not in frame.columns:
            rates[tenor] = None
            continue

        numeric_series = pd.to_numeric(
            frame[series],
            errors="coerce",
        )
        valid = frame[
            frame["_parsed_date"].notna()
            & numeric_series.notna()
        ].copy()

        if valid.empty:
            rates[tenor] = None
            continue

        latest_row = valid.sort_values("_parsed_date").iloc[-1]
        rates[tenor] = float(
            pd.to_numeric(latest_row[series], errors="coerce")
        )
        latest_dates.append(latest_row["_parsed_date"])

    if not any(
        rates.get(tenor) is not None
        for tenor in ("2Y", "5Y", "10Y", "30Y")
    ):
        raise ValueError("FRED returned no usable Treasury yields.")

    latest_date = max(latest_dates) if latest_dates else pd.NaT

    return {
        "date": (
            latest_date.strftime("%Y-%m-%d")
            if pd.notna(latest_date)
            else ""
        ),
        "rates": rates,
        "source_url": source_url,
        "source_format": "FRED Treasury constant-maturity series",
    }


def _fetch_treasury_yield_curve_html():
    """Read the latest official Treasury par-yield row from the current HTML table."""
    year = datetime.now(timezone.utc).year
    source_url = (
        "https://home.treasury.gov/resource-center/data-chart-center/"
        "interest-rates/TextView"
        f"?field_tdr_date_value={year}&type=daily_treasury_yield_curve"
    )
    response = fetch_treasury_html(
        source_url,
        {
            **PUBLIC_DATA_HEADERS,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0 Safari/537.36 EquityLensAI/1.0"
            ),
        },
    )

    soup = BeautifulSoup(response.text, "html.parser")
    observations = []

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        header_index = None
        headers = []

        for index, row in enumerate(rows):
            cells = row.find_all(["th", "td"])
            candidate_headers = [
                cell.get_text(" ", strip=True)
                for cell in cells
            ]
            normalized = [
                re.sub(r"[^a-z0-9.]", "", header.lower())
                for header in candidate_headers
            ]

            has_date = any(header == "date" for header in normalized)
            tenor_count = sum(
                1
                for header in candidate_headers
                if _treasury_header_key(header)
            )

            if has_date and tenor_count >= 5:
                header_index = index
                headers = candidate_headers
                break

        if header_index is None:
            continue

        date_column = next(
            (
                index
                for index, header in enumerate(headers)
                if re.sub(r"[^a-z0-9.]", "", header.lower()) == "date"
            ),
            None,
        )
        if date_column is None:
            continue

        tenor_columns = {}
        for index, header in enumerate(headers):
            tenor = _treasury_header_key(header)
            if tenor:
                # Treasury's combined table can repeat 20Y/30Y columns.
                # Prefer the later par-yield-curve columns.
                tenor_columns[tenor] = index

        for row in rows[header_index + 1:]:
            cells = [
                cell.get_text(" ", strip=True)
                for cell in row.find_all("td")
            ]
            if not cells or date_column >= len(cells):
                continue

            raw_date = cells[date_column]
            parsed_date = pd.to_datetime(raw_date, errors="coerce")
            if pd.isna(parsed_date):
                continue

            rates = {}
            for tenor, column_index in tenor_columns.items():
                rates[tenor] = (
                    _numeric_text(cells[column_index])
                    if column_index < len(cells)
                    else None
                )

            if any(value is not None for value in rates.values()):
                observations.append({
                    "date": parsed_date,
                    "rates": rates,
                })

    if not observations:
        raise ValueError(
            "Treasury HTML table returned no usable yield-curve observations."
        )

    latest = max(observations, key=lambda item: item["date"])
    return {
        "date": latest["date"].strftime("%Y-%m-%d"),
        "rates": latest["rates"],
        "source_url": source_url,
        "source_format": "Treasury daily rates table",
    }


def _fetch_treasury_yield_curve_xml():
    """Fallback parser for Treasury's official XML yield-curve feed."""
    year = datetime.now(timezone.utc).year
    source_url = (
        "https://home.treasury.gov/resource-center/data-chart-center/"
        "interest-rates/pages/xml"
        f"?data=daily_treasury_yield_curve&field_tdr_date_value={year}"
    )
    response = fetch_treasury_xml(
        source_url,
        {
            **PUBLIC_DATA_HEADERS,
            "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.8",
        },
    )

    root = ET.fromstring(response.content)
    records = []
    for element in root.iter():
        if element.tag.split("}")[-1].lower() != "properties":
            continue
        record = {}
        for child in list(element):
            key = child.tag.split("}")[-1]
            record[key] = (child.text or "").strip()
        if record:
            records.append(record)

    if not records:
        raise ValueError(
            "Treasury XML feed returned no yield-curve observations."
        )

    def record_date(record):
        raw = record.get("NEW_DATE") or record.get("Date") or ""
        parsed = pd.to_datetime(raw, errors="coerce")
        return parsed if pd.notna(parsed) else pd.Timestamp.min

    latest = max(records, key=record_date)
    latest_date = record_date(latest)

    field_map = {
        "1M": "BC_1MONTH",
        "3M": "BC_3MONTH",
        "6M": "BC_6MONTH",
        "1Y": "BC_1YEAR",
        "2Y": "BC_2YEAR",
        "3Y": "BC_3YEAR",
        "5Y": "BC_5YEAR",
        "7Y": "BC_7YEAR",
        "10Y": "BC_10YEAR",
        "20Y": "BC_20YEAR",
        "30Y": "BC_30YEAR",
    }
    rates = {
        tenor: _numeric_text(latest.get(field))
        for tenor, field in field_map.items()
    }

    if not any(value is not None for value in rates.values()):
        raise ValueError(
            "Treasury XML feed returned a row without usable yields."
        )

    return {
        "date": (
            latest_date.strftime("%Y-%m-%d")
            if latest_date != pd.Timestamp.min
            else ""
        ),
        "rates": rates,
        "source_url": source_url,
        "source_format": "Treasury XML feed",
    }


def _fetch_treasury_yield_curve():
    """Load the latest official U.S. Treasury par yield curve with format fallback."""
    errors = []

    for fetcher in (
        _fetch_treasury_yield_curve_csv,
        _fetch_treasury_yield_curve_html,
        _fetch_treasury_yield_curve_xml,
        _fetch_fred_treasury_yield_curve,
    ):
        try:
            result = fetcher()
            rates = result.get("rates", {})
            required_tenors = ("2Y", "5Y", "10Y", "30Y")
            if not any(rates.get(tenor) is not None for tenor in required_tenors):
                raise ValueError(
                    "Treasury response did not include core curve tenors."
                )
            return result
        except Exception as exc:
            errors.append(str(exc))

    raise RuntimeError(
        "Treasury yield-curve sources failed: "
        + " | ".join(errors)
    )



def _find_html_data_row(url, required_header_terms):
    response = service_get(
        url,
        headers={
            **PUBLIC_DATA_HEADERS,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 Safari/537.36 EquityLensAI/1.0"
            ),
        },
        timeout=(4, 7),
        provider="MacroHTML",
    )
    soup = BeautifulSoup(response.text, "html.parser")

    for table in soup.find_all("table"):
        header_text = " ".join(
            cell.get_text(" ", strip=True)
            for cell in table.find_all("th")
        ).upper()
        if not all(term.upper() in header_text for term in required_header_terms):
            continue

        for row in table.find_all("tr"):
            cells = [
                cell.get_text(" ", strip=True)
                for cell in row.find_all("td")
            ]
            if cells:
                return cells
    return []


def _walk_dicts(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_dicts(child)


def _normalized_dict(record):
    return {
        re.sub(r"[^a-z0-9]", "", str(key).lower()): value
        for key, value in record.items()
    }


def _fetch_sofr_reference_rates():
    """Load SOFR and published SOFR averages from the New York Fed."""
    sofr_url = "https://www.newyorkfed.org/markets/reference-rates/sofr"
    averages_url = (
        "https://www.newyorkfed.org/markets/reference-rates/"
        "sofr-averages-and-index"
    )

    result = {
        "date": "",
        "SOFR": None,
        "30D": None,
        "90D": None,
        "180D": None,
        "source_url": averages_url,
    }

    # Prefer the New York Fed's Markets Data API when available.
    try:
        response = fetch_sofr(PUBLIC_DATA_HEADERS)
        if response.ok:
            for record in _walk_dicts(response.json()):
                normalized = _normalized_dict(record)
                rate = (
                    normalized.get("percentrate")
                    or normalized.get("rate")
                    or normalized.get("percent")
                )
                rate_type = str(
                    normalized.get("type")
                    or normalized.get("ratetype")
                    or ""
                ).upper()
                if rate is not None and ("SOFR" in rate_type or not rate_type):
                    result["SOFR"] = _numeric_text(rate)
                    result["date"] = str(
                        normalized.get("effectivedate")
                        or normalized.get("date")
                        or result["date"]
                    )
                    break
    except Exception:
        pass

    try:
        response = fetch_sofr_averages(
            PUBLIC_DATA_HEADERS
        )
        if response.ok:
            for record in _walk_dicts(response.json()):
                normalized = _normalized_dict(record)
                aliases = {
                    "30D": [
                        "average30day", "avg30day", "sofr30dayavg",
                        "thirtydayaverage", "30dayaverage"
                    ],
                    "90D": [
                        "average90day", "avg90day", "sofr90dayavg",
                        "ninetydayaverage", "90dayaverage"
                    ],
                    "180D": [
                        "average180day", "avg180day", "sofr180dayavg",
                        "onehundredeightydayaverage", "180dayaverage"
                    ],
                }
                found_any = False
                for label, keys in aliases.items():
                    for key in keys:
                        if key in normalized:
                            result[label] = _numeric_text(normalized[key])
                            found_any = True
                            break
                if found_any:
                    result["date"] = str(
                        normalized.get("effectivedate")
                        or normalized.get("date")
                        or result["date"]
                    )
                    break
    except Exception:
        pass

    # Fallback to the official public HTML tables.
    if result["SOFR"] is None:
        try:
            cells = _find_html_data_row(
                sofr_url,
                ["DATE", "RATE", "VOLUME"]
            )
            if len(cells) >= 2:
                result["date"] = cells[0]
                result["SOFR"] = _numeric_text(cells[1])
        except Exception:
            pass

    if any(result[key] is None for key in ["30D", "90D", "180D"]):
        try:
            cells = _find_html_data_row(
                averages_url,
                ["DATE", "30-DAY", "90-DAY", "180-DAY"]
            )
            if len(cells) >= 4:
                if not result["date"]:
                    result["date"] = cells[0]
                result["30D"] = (
                    result["30D"]
                    if result["30D"] is not None
                    else _numeric_text(cells[1])
                )
                result["90D"] = (
                    result["90D"]
                    if result["90D"] is not None
                    else _numeric_text(cells[2])
                )
                result["180D"] = (
                    result["180D"]
                    if result["180D"] is not None
                    else _numeric_text(cells[3])
                )
        except Exception:
            pass

    return result


def render_rates_ticker(treasury_curve, sofr_rates):
    """Render official Treasury and New York Fed reference rates as a tape."""
    treasury_rates = treasury_curve.get("rates", {}) if treasury_curve else {}
    tape_data = [
        ("U.S. Treasury", "2Y", treasury_rates.get("2Y"), "%"),
        ("U.S. Treasury", "5Y", treasury_rates.get("5Y"), "%"),
        ("U.S. Treasury", "10Y", treasury_rates.get("10Y"), "%"),
        ("U.S. Treasury", "30Y", treasury_rates.get("30Y"), "%"),
    ]

    two_year = treasury_rates.get("2Y")
    ten_year = treasury_rates.get("10Y")
    spread = None
    if two_year is not None and ten_year is not None:
        spread = (ten_year - two_year) * 100
    tape_data.append(("Yield Curve", "2s10s", spread, " bp"))

    if sofr_rates:
        tape_data.extend([
            ("New York Fed", "SOFR", sofr_rates.get("SOFR"), "%"),
            ("New York Fed", "30D SOFR", sofr_rates.get("30D"), "%"),
            ("New York Fed", "90D SOFR", sofr_rates.get("90D"), "%"),
            ("New York Fed", "180D SOFR", sofr_rates.get("180D"), "%"),
        ])

    items = []
    for provider, label, value, suffix in tape_data:
        if value is None:
            value_text = "N/A"
        elif suffix == " bp":
            value_text = f"{value:+.1f} bp"
        else:
            value_text = f"{value:.3f}%"

        items.append(
            '<div class="el-ticker-item">'
            f'<span class="el-ticker-company">{html.escape(provider)}</span>'
            f'<span class="el-ticker-symbol">{html.escape(label)}</span>'
            f'<span class="el-ticker-price">{html.escape(value_text)}</span>'
            '<span class="el-ticker-change flat">Official</span>'
            '</div>'
        )

    if not items:
        st.caption("Official rates are temporarily unavailable.")
        return

    st.markdown(
        f"""
        <div class="el-exchange-tape">
            <div class="el-exchange-pill">
                <span>RATES</span>
                <span class="el-exchange-chevron">⌄</span>
            </div>
            <div class="el-ticker-shell">
                <div class="el-ticker-track">{"".join(items + items)}</div>
            </div>
        </div>
        <div class="el-market-delay">
            U.S. Treasury + Federal Reserve Bank of New York · official public data
        </div>
        """,
        unsafe_allow_html=True,
    )


BLS_SERIES_META = {
    "CPI": {
        "series_id": "CUUR0000SA0",
        "label": "CPI YoY",
        "mode": "yoy",
        "lag": 12,
        "source": "Consumer Price Index",
    },
    "Core CPI": {
        "series_id": "CUUR0000SA0L1E",
        "label": "Core CPI YoY",
        "mode": "yoy",
        "lag": 12,
        "source": "Consumer Price Index",
    },
    "PPI": {
        "series_id": "WPUFD4",
        "label": "PPI Final Demand YoY",
        "mode": "yoy",
        "lag": 12,
        "source": "Producer Price Index",
    },
    "Unemployment": {
        "series_id": "LNS14000000",
        "label": "Unemployment Rate",
        "mode": "percent",
        "lag": 1,
        "source": "Employment Situation",
    },
    "Payrolls": {
        "series_id": "CES0000000001",
        "label": "Nonfarm Payrolls MoM",
        "mode": "delta",
        "lag": 1,
        "source": "Employment Situation",
    },
    "Hourly Earnings": {
        "series_id": "CES0500000003",
        "label": "Avg. Hourly Earnings YoY",
        "mode": "yoy",
        "lag": 12,
        "source": "Employment Situation",
    },
    "ECI": {
        "series_id": "CIU1010000000000A",
        "label": "Employment Cost Index YoY",
        "mode": "yoy",
        "lag": 4,
        "source": "Employment Cost Index",
    },
}


@st.cache_data(ttl=3600)
def get_bls_macro_snapshot():
    """Retrieve selected material U.S. labor/inflation series from BLS."""
    now = datetime.now(timezone.utc)
    payload = {
        "seriesid": [
            metadata["series_id"]
            for metadata in BLS_SERIES_META.values()
        ],
        "startyear": str(now.year - 2),
        "endyear": str(now.year),
    }
    response = fetch_bls_series(
        payload,
        PUBLIC_DATA_HEADERS,
    )
    data = response.json()

    if data.get("status") != "REQUEST_SUCCEEDED":
        raise ValueError("BLS API request did not succeed.")

    meta_by_id = {
        metadata["series_id"]: (name, metadata)
        for name, metadata in BLS_SERIES_META.items()
    }
    results = {}

    for series in data.get("Results", {}).get("series", []):
        series_id = series.get("seriesID")
        if series_id not in meta_by_id:
            continue

        name, metadata = meta_by_id[series_id]
        observations = []
        for row in series.get("data", []):
            period = str(row.get("period", ""))
            if not (
                period.startswith("M")
                or period.startswith("Q")
            ):
                continue
            if period == "M13":
                continue
            value = _numeric_text(row.get("value"))
            if value is None:
                continue
            try:
                period_number = int(re.sub(r"\D", "", period))
                year = int(row.get("year"))
            except (TypeError, ValueError):
                continue
            observations.append({
                "year": year,
                "period": period,
                "period_number": period_number,
                "period_name": row.get("periodName", period),
                "value": value,
            })

        observations.sort(
            key=lambda row: (row["year"], row["period_number"])
        )
        if not observations:
            continue

        latest = observations[-1]
        previous = observations[-2] if len(observations) >= 2 else None
        lag = int(metadata.get("lag", 1))
        lagged = observations[-(lag + 1)] if len(observations) > lag else None

        metric_value = latest["value"]
        if metadata["mode"] == "yoy":
            if lagged and lagged["value"] not in (None, 0):
                metric_value = (
                    (latest["value"] - lagged["value"])
                    / lagged["value"]
                ) * 100
            else:
                metric_value = None
        elif metadata["mode"] == "delta":
            metric_value = (
                latest["value"] - previous["value"]
                if previous else None
            )

        results[name] = {
            **metadata,
            "latest_level": latest["value"],
            "previous_level": previous["value"] if previous else None,
            "display_value": metric_value,
            "period": f"{latest['period_name']} {latest['year']}",
        }

    return results


def format_bls_display(item):
    value = item.get("display_value")
    if value is None:
        return "N/A"
    mode = item.get("mode")
    if mode in {"yoy", "percent"}:
        return f"{value:.1f}%"
    if mode == "delta":
        return f"{value:+,.0f}K"
    return f"{value:,.2f}"


@st.cache_data(ttl=3600)
def get_bls_release_calendar(limit=16):
    """Read the automatically updated BLS release calendar."""
    calendar_url = "https://www.bls.gov/schedule/news_release/bls.ics"
    response = fetch_bls_calendar(
        PUBLIC_DATA_HEADERS
    )

    ics = (
        response.text
        .replace("\r\n ", "")
        .replace("\n ", "")
    )
    blocks = re.findall(
        r"BEGIN:VEVENT(.*?)END:VEVENT",
        ics,
        flags=re.DOTALL,
    )

    material_terms = [
        "consumer price index",
        "producer price index",
        "employment situation",
        "job openings",
        "employment cost index",
        "productivity and costs",
    ]
    source_links = {
        "consumer price index": "https://www.bls.gov/news.release/cpi.htm",
        "producer price index": "https://www.bls.gov/news.release/ppi.htm",
        "employment situation": "https://www.bls.gov/news.release/empsit.htm",
        "job openings": "https://www.bls.gov/news.release/jolts.htm",
        "employment cost index": "https://www.bls.gov/news.release/eci.htm",
        "productivity and costs": "https://www.bls.gov/news.release/prod2.htm",
    }

    events = []
    today = datetime.now(timezone.utc).date()

    for block in blocks:
        summary_match = re.search(
            r"SUMMARY(?:;[^:]*)?:(.*)",
            block,
        )
        date_match = re.search(
            r"DTSTART(?:;[^:]*)?:(\d{8})(?:T(\d{6}))?",
            block,
        )
        if not summary_match or not date_match:
            continue

        summary = (
            summary_match.group(1)
            .strip()
            .replace("\\,", ",")
            .replace("\\;", ";")
        )
        lowered = summary.lower()
        matched_term = next(
            (term for term in material_terms if term in lowered),
            None,
        )
        if not matched_term:
            continue

        date_value = datetime.strptime(
            date_match.group(1),
            "%Y%m%d",
        ).date()
        if date_value < today:
            continue

        time_value = ""
        if date_match.group(2):
            raw_time = date_match.group(2)
            time_value = (
                f"{raw_time[:2]}:{raw_time[2:4]}"
            )

        events.append({
            "Date": date_value.isoformat(),
            "Time": time_value,
            "Event": summary,
            "Agency": "BLS",
            "Source": source_links[matched_term],
        })

    events.sort(key=lambda row: (row["Date"], row["Time"]))
    return events[:limit]


@st.cache_data(ttl=21600)
def get_fomc_calendar(limit=12):
    """Parse the official Federal Reserve FOMC meeting calendar."""
    source_url = (
        "https://www.federalreserve.gov/monetarypolicy/"
        "fomccalendars.htm"
    )
    response = fetch_fomc_calendar(
        PUBLIC_DATA_HEADERS
    )
    soup = BeautifulSoup(response.text, "html.parser")
    text_lines = [
        line.strip()
        for line in soup.stripped_strings
        if line.strip()
    ]

    months = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }
    today = datetime.now(timezone.utc).date()
    current_year = today.year
    events = []

    for year in [current_year, current_year + 1]:
        heading = f"{year} FOMC Meetings"
        try:
            start = text_lines.index(heading) + 1
        except ValueError:
            continue

        end = len(text_lines)
        for idx in range(start, len(text_lines)):
            if re.fullmatch(r"\d{4} FOMC Meetings", text_lines[idx]):
                end = idx
                break

        block = text_lines[start:end]
        for idx, line in enumerate(block):
            if line not in months:
                continue

            date_text = None
            for candidate in block[idx + 1: idx + 7]:
                if re.fullmatch(r"\d{1,2}(?:-\d{1,2})?\*?", candidate):
                    date_text = candidate
                    break
            if not date_text:
                continue

            clean_date = date_text.rstrip("*")
            parts = clean_date.split("-")
            start_day = int(parts[0])
            end_day = int(parts[-1])
            meeting_end = datetime(
                year,
                months[line],
                end_day,
            ).date()
            if meeting_end < today:
                continue

            events.append({
                "Date": (
                    f"{year}-{months[line]:02d}-{start_day:02d}"
                    + (
                        f" to {year}-{months[line]:02d}-{end_day:02d}"
                        if end_day != start_day else ""
                    )
                ),
                "Time": "",
                "Event": (
                    f"FOMC Meeting{' · SEP' if date_text.endswith('*') else ''}"
                ),
                "Agency": "Federal Reserve",
                "Source": source_url,
            })

    if not events:
        joined = " ".join(text_lines)
        for year in [current_year, current_year + 1]:
            year_match = re.search(
                rf"{year} FOMC Meetings(.*?)(?=\\d{{4}} FOMC Meetings|$)",
                joined,
                flags=re.DOTALL,
            )
            if not year_match:
                continue
            for month_name, date_text in re.findall(
                r"(January|February|March|April|May|June|July|August|"
                r"September|October|November|December)\\s+"
                r"(\\d{1,2}(?:-\\d{1,2})?\\*?)",
                year_match.group(1),
            ):
                clean_date = date_text.rstrip("*")
                parts = clean_date.split("-")
                start_day = int(parts[0])
                end_day = int(parts[-1])
                meeting_end = datetime(
                    year,
                    months[month_name],
                    end_day,
                ).date()
                if meeting_end < today:
                    continue
                events.append({
                    "Date": (
                        f"{year}-{months[month_name]:02d}-{start_day:02d}"
                        + (
                            f" to {year}-{months[month_name]:02d}-{end_day:02d}"
                            if end_day != start_day else ""
                        )
                    ),
                    "Time": "",
                    "Event": (
                        f"FOMC Meeting{' · SEP' if date_text.endswith('*') else ''}"
                    ),
                    "Agency": "Federal Reserve",
                    "Source": source_url,
                })

    events.sort(key=lambda row: row["Date"])
    return events[:limit]


@st.cache_data(ttl=3600)
def get_fed_monetary_updates(limit=6):
    """Read official Federal Reserve monetary-policy press releases."""
    feed_url = "https://www.federalreserve.gov/feeds/press_monetary.xml"
    response = fetch_monetary_feed(
        PUBLIC_DATA_HEADERS
    )
    root = ET.fromstring(response.content)

    rows = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        published = (
            item.findtext("pubDate")
            or item.findtext("date")
            or ""
        ).strip()
        if not title or not link:
            continue
        rows.append({
            "Published": published,
            "Federal Reserve update": title,
            "Source": link,
        })
        if len(rows) >= limit:
            break

    if not rows:
        atom = "{http://www.w3.org/2005/Atom}"
        for entry in root.findall(f".//{atom}entry"):
            title = (
                entry.findtext(f"{atom}title")
                or ""
            ).strip()
            link_element = entry.find(f"{atom}link")
            link = (
                link_element.attrib.get("href", "")
                if link_element is not None else ""
            )
            published = (
                entry.findtext(f"{atom}updated")
                or entry.findtext(f"{atom}published")
                or ""
            ).strip()
            if not title or not link:
                continue
            rows.append({
                "Published": published,
                "Federal Reserve update": title,
                "Source": link,
            })
            if len(rows) >= limit:
                break
    return rows


@st.cache_data(ttl=900)
def get_bloomberg_market_news(limit=10):
    """Return Bloomberg market headlines and outbound links only."""
    feed_candidates = [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://feeds.bloomberg.com/economics/news.rss",
    ]
    stories = []
    seen = set()

    for feed_url in feed_candidates:
        try:
            response = fetch_bloomberg_feed(
                feed_url,
                PUBLIC_DATA_HEADERS,
            )
            root = ET.fromstring(response.content)
            for item in root.findall(".//item"):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                published = (item.findtext("pubDate") or "").strip()
                if not title or not link or title in seen:
                    continue
                seen.add(title)
                stories.append({
                    "Published": published,
                    "Headline": title,
                    "Bloomberg": link,
                })
                if len(stories) >= limit:
                    return stories
        except Exception:
            continue

    # Fallback: capture headline links from Bloomberg Markets without
    # reproducing article text.
    try:
        response = fetch_bloomberg_markets(
            {
                **PUBLIC_DATA_HEADERS,
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 Safari/537.36"
                ),
            }
        )
        soup = BeautifulSoup(response.text, "html.parser")
        for anchor in soup.find_all("a", href=True):
            title = " ".join(anchor.stripped_strings).strip()
            href = urljoin(
                "https://www.bloomberg.com",
                anchor.get("href", ""),
            )
            if (
                len(title) < 20
                or len(title) > 180
                or "bloomberg.com" not in href
                or "/news/" not in href
                or title in seen
            ):
                continue
            seen.add(title)
            stories.append({
                "Published": "",
                "Headline": title,
                "Bloomberg": href,
            })
            if len(stories) >= limit:
                break
    except Exception:
        pass

    return stories


def _market_news_topic(headline):
    text = str(headline or "").lower()
    if any(term in text for term in [
        "fed", "federal reserve", "rate", "yield", "treasury", "bond"
    ]):
        return "Rates"
    if any(term in text for term in [
        "inflation", "cpi", "ppi", "jobs", "payroll", "gdp", "economy"
    ]):
        return "Economy"
    if any(term in text for term in [
        "oil", "gold", "copper", "commodity", "natural gas"
    ]):
        return "Commodities"
    if any(term in text for term in [
        "stock", "shares", "earnings", "equity", "nasdaq", "s&p"
    ]):
        return "Equities"
    if any(term in text for term in [
        "dollar", "yen", "euro", "currency", "fx"
    ]):
        return "FX"
    return "Markets"


def _market_news_time(value):
    if not value:
        return "Latest"
    parsed = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(parsed):
        return str(value)[:42]
    try:
        eastern = parsed.tz_convert("America/New_York")
        return eastern.strftime("%b %d · %I:%M %p ET")
    except Exception:
        return parsed.strftime("%b %d · %H:%M UTC")


def _news_context_value(value, suffix="", signed=False):
    number = _safe_float(value)
    if number is None:
        return "N/A", "flat"
    css_class = "positive" if number > 0 else "negative" if number < 0 else "flat"
    sign = "+" if signed and number > 0 else ""
    return f"{sign}{number:.2f}{suffix}", css_class


def _news_visual_html(topic, context, featured=False):
    """Create an original market-context visual for a news card."""
    topic = str(topic or "Markets")
    context = context or {}
    stats = []
    bars = []
    line_values = []

    if topic == "Rates":
        treasury = context.get("treasury", {})
        stats = [
            ("2Y", treasury.get("2Y"), "%", False),
            ("10Y", treasury.get("10Y"), "%", False),
            ("SOFR", context.get("SOFR"), "%", False),
        ]
        line_values = [
            treasury.get(tenor)
            for tenor in ["1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]
            if _safe_float(treasury.get(tenor)) is not None
        ]
    elif topic == "Economy":
        stats = [
            ("CPI YoY", context.get("CPI"), "%", True),
            ("PPI YoY", context.get("PPI"), "%", True),
            ("Unemp.", context.get("Unemployment"), "%", False),
        ]
        bars = [
            context.get("CPI"),
            context.get("Core CPI"),
            context.get("PPI"),
            context.get("Unemployment"),
        ]
    elif topic == "Commodities":
        stats = [
            ("Gold · GLD", context.get("GLD"), "%", True),
            ("Oil · USO", context.get("USO"), "%", True),
        ]
        bars = [context.get("GLD"), context.get("USO"), 0.4, -0.25, 0.6]
    elif topic == "FX":
        stats = [
            ("USD · UUP", context.get("UUP"), "%", True),
            ("10Y", context.get("treasury", {}).get("10Y"), "%", False),
        ]
        bars = [context.get("UUP"), 0.25, -0.15, 0.4, -0.1]
    else:
        stats = [
            ("S&P · SPY", context.get("SPY"), "%", True),
            ("Nasdaq · QQQ", context.get("QQQ"), "%", True),
            ("10Y", context.get("treasury", {}).get("10Y"), "%", False),
        ]
        bars = [
            context.get("SPY"),
            context.get("QQQ"),
            context.get("GLD"),
            context.get("USO"),
        ]

    stat_html = []
    for label, value, suffix, signed in stats:
        value_text, css_class = _news_context_value(
            value,
            suffix=suffix,
            signed=signed,
        )
        stat_html.append(
            '<div class="el-news-viz-stat">'
            f'<div class="el-news-viz-label">{html.escape(label)}</div>'
            f'<div class="el-news-viz-value {css_class}">{html.escape(value_text)}</div>'
            '</div>'
        )

    visual_layer = ""
    clean_line = [
        _safe_float(value)
        for value in line_values
        if _safe_float(value) is not None
    ]
    if len(clean_line) >= 2:
        minimum = min(clean_line)
        maximum = max(clean_line)
        span = maximum - minimum or 1.0
        x_step = 100 / max(1, len(clean_line) - 1)
        points = []
        area_points = ["0,54"]
        for index, value in enumerate(clean_line):
            x = index * x_step
            y = 45 - ((value - minimum) / span) * 30
            points.append(f"{x:.1f},{y:.1f}")
            area_points.append(f"{x:.1f},{y:.1f}")
        area_points.append("100,54")
        visual_layer = (
            '<svg class="el-news-viz-line" viewBox="0 0 100 54" '
            'preserveAspectRatio="none" aria-hidden="true">'
            f'<polygon class="el-news-viz-area" points="{" ".join(area_points)}"></polygon>'
            f'<polyline points="{" ".join(points)}"></polyline>'
            '</svg>'
        )
    else:
        clean_bars = [
            _safe_float(value)
            for value in bars
            if _safe_float(value) is not None
        ]
        if not clean_bars:
            clean_bars = [0.2, 0.7, 0.45, 0.85, 0.58]
        magnitude = max(max(abs(value) for value in clean_bars), 0.01)
        bar_html = []
        for value in clean_bars:
            height = 9 + (abs(value) / magnitude) * 24
            opacity = 0.45 if value < 0 else 0.88
            bar_html.append(
                f'<span class="el-news-viz-bar" style="height:{height:.1f}px;opacity:{opacity:.2f};"></span>'
            )
        visual_layer = (
            '<div class="el-news-viz-bars">'
            + "".join(bar_html)
            + '</div>'
        )

    visual_label = "Live market context" if featured else "Market context"
    return (
        '<div class="el-news-visual">'
        f'<div class="el-news-visual-kicker">{visual_label}</div>'
        '<div class="el-news-viz-stats">'
        + "".join(stat_html)
        + '</div>'
        + visual_layer
        + '</div>'
    )


def render_market_news_cards(stories, market_context=None):
    """Render Bloomberg headlines with original EquityLens market visuals."""
    if not stories:
        return

    cards = []
    for index, story in enumerate(stories[:9]):
        raw_headline = str(story.get("Headline", "")).strip()
        headline = html.escape(raw_headline)
        link = html.escape(str(story.get("Bloomberg", "")).strip(), quote=True)
        published = html.escape(
            _market_news_time(story.get("Published", ""))
        )
        topic_raw = _market_news_topic(raw_headline)
        topic = html.escape(topic_raw)

        if not headline or not link:
            continue

        featured = index == 0
        featured_class = " featured" if featured else ""
        visual_html = _news_visual_html(
            topic_raw,
            market_context or {},
            featured=featured,
        )

        cards.append(
            f'<a class="el-news-card{featured_class}" '
            f'href="{link}" target="_blank" rel="noopener noreferrer">'
            '<div class="el-news-card-top">'
            '<span class="el-news-source">Bloomberg</span>'
            f'<span class="el-news-topic">{topic}</span>'
            '</div>'
            f'<div class="el-news-headline">{headline}</div>'
            f'{visual_html}'
            '<div class="el-news-spacer"></div>'
            '<div class="el-news-footer">'
            f'<span class="el-news-time">{published}</span>'
            '<span class="el-news-read">Read story ↗</span>'
            '</div>'
            '</a>'
        )

    if not cards:
        return

    st.markdown(
        """
        <div class="el-news-shell">
            <div class="el-news-topline">
                <span class="el-news-live">Latest market headlines</span>
                <span>Bloomberg headlines · EquityLens market context visuals</span>
            </div>
            <div class="el-news-grid">
        """
        + "".join(cards)
        + """
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _fetch_optional_swap_rates(configured_endpoint=''):
    """
    Load USD SOFR OIS curve data.

    Priority:
      1. A user-configured JSON endpoint in Streamlit Secrets.
      2. CheckMySwap's free public USD SOFR OIS curve endpoint.

    CheckMySwap publishes indicative OIS curves derived from public DTCC
    swap transaction reports. These are dated curve estimates, not executable
    dealer quotes.
    """
    configured_endpoint = str(configured_endpoint or "").strip()
    endpoint = (
        configured_endpoint
        if configured_endpoint
        else "https://checkmyswap.com/api/curves/USD"
    )

    response = fetch_swap_curve(
        endpoint,
        PUBLIC_DATA_HEADERS,
    )
    payload = response.json()

    rows = []
    curve_date = ""

    if isinstance(payload, dict) and isinstance(payload.get("curve"), list):
        curve_date = str(payload.get("date", "")).strip()
        for record in payload.get("curve", []):
            if not isinstance(record, dict):
                continue
            tenor = record.get("tenor")
            rate = _numeric_text(record.get("rate"))
            if tenor and rate is not None:
                rows.append({
                    "Tenor": str(tenor),
                    "Swap Rate": rate,
                    "Curve Date": curve_date or str(record.get("date", "")),
                    "Source": str(
                        record.get("source", "CheckMySwap / DTCC public data")
                    ),
                    "Method": str(record.get("method", "")),
                })
    elif isinstance(payload, dict):
        for tenor, rate in payload.items():
            numeric = _numeric_text(rate)
            if numeric is not None:
                rows.append({
                    "Tenor": str(tenor),
                    "Swap Rate": numeric,
                    "Curve Date": "",
                    "Source": "Configured provider",
                    "Method": "",
                })
    elif isinstance(payload, list):
        for record in payload:
            if not isinstance(record, dict):
                continue
            tenor = (
                record.get("tenor")
                or record.get("Tenor")
                or record.get("maturity")
            )
            rate = (
                record.get("rate")
                or record.get("Rate")
                or record.get("swap_rate")
            )
            numeric = _numeric_text(rate)
            if tenor and numeric is not None:
                rows.append({
                    "Tenor": str(tenor),
                    "Swap Rate": numeric,
                    "Curve Date": str(record.get("date", "")),
                    "Source": str(record.get("source", "Configured provider")),
                    "Method": str(record.get("method", "")),
                })

    return rows


@st.cache_data(ttl=3600, show_spinner=False)
def get_rates_bundle(swap_endpoint="", cache_version="rates-v3"):
    """Fetch independent official reference rates concurrently and cache for an hour."""
    tasks = {
        "treasury": _fetch_treasury_yield_curve,
        "sofr": _fetch_sofr_reference_rates,
        "swap": lambda: _fetch_optional_swap_rates(swap_endpoint),
    }
    result = {"treasury": {}, "sofr": {}, "swap": [], "errors": []}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {name: executor.submit(task) for name, task in tasks.items()}
        for name, future in futures.items():
            try:
                result[name] = future.result()
            except Exception:
                result["errors"].append(name)
    return result


