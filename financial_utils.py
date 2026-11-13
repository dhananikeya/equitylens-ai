from formatting import (
    format_market_price,
    format_market_volume,
    format_money,
    format_multiple,
    pct,
    safe_float,
)


def calc_growth(current, prior):
    if current is None or prior in (None, 0):
        return None
    return ((current - prior) / prior) * 100


def calc_margin(profit, revenue):
    if profit is None or revenue in (None, 0):
        return None
    return (profit / revenue) * 100


def financial_period_label(record, default="Period unavailable"):
    for field in ("period", "quarter_label", "period_end", "fiscal_year", "year", "quarter", "label"):
        value = record.get(field)
        if value not in (None, ""):
            return str(value)
    return default


def choose_income_period(company, quarterly, fallback):
    """Choose one income-statement record; never fill it from another period."""
    latest_quarter = quarterly.get("latest_quarter", {})
    structured_history = sorted(
        [row for row in company.get("history", []) if row.get("fiscal_year") is not None],
        key=lambda row: str(row["fiscal_year"]),
    )
    fallback_history = sorted(
        [row for row in fallback.get("history", []) if row.get("fiscal_year") is not None],
        key=lambda row: str(row["fiscal_year"]),
    )
    annual_history = structured_history or fallback_history
    annual_source = "Structured annual company dataset" if structured_history else "Yahoo Finance annual statements"
    if latest_quarter.get("revenue") is not None:
        return {
            "record": latest_quarter,
            "currency": (
                quarterly.get("currency")
                or company.get("currency")
                or fallback.get("currency")
                or "USD"
            ),
            "period": quarterly.get("quarter_label") or quarterly.get("period_end") or financial_period_label(latest_quarter),
            "source": "Structured quarterly company dataset",
            "source_url": quarterly.get("source_filing"),
            "growth": calc_growth(latest_quarter.get("revenue"), quarterly.get("prior_year_quarter", {}).get("revenue")),
            "growth_basis": "Same quarter one year earlier",
            "annual_history": annual_history,
            "annual_source": annual_source,
        }
    if annual_history:
        current = annual_history[-1]
        prior = annual_history[-2] if len(annual_history) > 1 else {}
        try:
            consecutive = int(current["fiscal_year"]) - int(prior.get("fiscal_year")) == 1
        except (TypeError, ValueError):
            consecutive = False
        return {
            "record": current,
            "currency": (
                company.get("currency")
                or fallback.get("currency")
                or "USD"
            ),
            "period": financial_period_label(current),
            "source": annual_source,
            "source_url": company.get("filing_url") if structured_history else None,
            "growth": calc_growth(current.get("revenue"), prior.get("revenue")) if consecutive else None,
            "growth_basis": "Previous fiscal year" if consecutive else "Comparable prior year unavailable",
            "annual_history": annual_history,
            "annual_source": annual_source,
        }
    record = fallback.get("latest") or company
    return {
        "record": record,
        "currency": (
            fallback.get("currency")
            or company.get("currency")
            or "USD"
        ),
        "period": financial_period_label(record),
        "source": "Yahoo Finance annual statements" if fallback.get("latest") else "Structured company dataset",
        "source_url": None,
        "growth": None,
        "growth_basis": "Comparable prior period unavailable",
        "annual_history": [],
        "annual_source": annual_source,
    }


def quarterly_metrics(qdata):
    latest = qdata.get("latest_quarter", {})
    prior_q = qdata.get("prior_quarter", {})
    prior_y = qdata.get("prior_year_quarter", {})

    revenue = latest.get("revenue")
    prior_q_revenue = prior_q.get("revenue")
    prior_y_revenue = prior_y.get("revenue")

    return {
        "revenue": revenue,
        "yoy_growth": calc_growth(revenue, prior_y_revenue),
        "qoq_growth": calc_growth(revenue, prior_q_revenue),
        "gross_margin": calc_margin(latest.get("gross_profit"), revenue),
        "operating_margin": calc_margin(latest.get("operating_income"), revenue),
        "net_margin": calc_margin(latest.get("net_income"), revenue),
        "prior_q_operating_margin": calc_margin(
            prior_q.get("operating_income"), prior_q_revenue
        ),
        "prior_y_operating_margin": calc_margin(
            prior_y.get("operating_income"), prior_y_revenue
        )
    }


def build_change_notes(qdata):
    currency = (
        qdata.get("currency")
        or "USD"
    )
    latest = qdata.get("latest_quarter", {})
    prior_q = qdata.get("prior_quarter", {})
    prior_y = qdata.get("prior_year_quarter", {})
    m = quarterly_metrics(qdata)

    notes = []

    if m["qoq_growth"] is not None:
        notes.append((
            "Sequential revenue",
            f"Revenue changed {m['qoq_growth']:+.1f}% from the prior quarter, "
            f"from {format_money(
                prior_q.get('revenue'),
                currency,
            )} to {format_money(
                latest.get('revenue'),
                currency,
            )}."
        ))

    if m["yoy_growth"] is not None:
        notes.append((
            "Year-over-year revenue",
            f"Revenue changed {m['yoy_growth']:+.1f}% from the same quarter a year earlier, "
            f"from {format_money(
                prior_y.get('revenue'),
                currency,
            )} to {format_money(
                latest.get('revenue'),
                currency,
            )}."
        ))

    if m["operating_margin"] is not None and m["prior_q_operating_margin"] is not None:
        delta = m["operating_margin"] - m["prior_q_operating_margin"]
        notes.append((
            "Operating margin",
            f"Operating margin changed {delta:+.1f} percentage points sequentially, "
            f"from {m['prior_q_operating_margin']:.1f}% to {m['operating_margin']:.1f}%."
        ))

    current_net = latest.get("net_income")
    prior_net = prior_q.get("net_income")
    if current_net is not None and prior_net is not None:
        if prior_net < 0 <= current_net:
            copy = (
                f"Net income moved from a loss of {format_money(
                    prior_net,
                    currency,
                )} "
                f"to profit of {format_money(
                    current_net,
                    currency,
                )}."
            )
        elif prior_net >= 0 > current_net:
            copy = (
                f"Net income moved from profit of {format_money(
                    prior_net,
                    currency,
                )} "
                f"to a loss of {format_money(
                    current_net,
                    currency,
                )}."
            )
        else:
            copy = (
                f"Net income changed from {format_money(
                    prior_net,
                    currency,
                )} "
                f"to {format_money(
                    current_net,
                    currency,
                )}."
            )
        notes.append(("Net income", copy))

    return notes


