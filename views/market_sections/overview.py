import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from charts import apply_equitylens_layout

from market_data import finviz_numeric
from ui_components import section


def render_market_tape(nyse_finviz):
    section("NYSE", "NYSE Market Ticker")

    if nyse_finviz is None or nyse_finviz.empty:
        st.info(
            "NYSE market data is not available right now. "
            "Check the market-data connection and refresh the page."
        )
        return False

    ticker_source = nyse_finviz.copy()
    if "Volume" in ticker_source.columns:
        ticker_source["_volume_num"] = ticker_source[
            "Volume"
        ].apply(finviz_numeric)
        ticker_source = ticker_source.sort_values(
            "_volume_num",
            ascending=False,
            na_position="last",
        )

    tape_items = []
    for _, row in ticker_source.head(20).iterrows():
        symbol = str(row.get("Ticker", "")).strip()
        company = str(row.get("Company", "")).strip()
        price = finviz_numeric(row.get("Price"))
        change = finviz_numeric(row.get("Change"))
        if not symbol:
            continue
        if not company or company.lower() == "nan":
            company = symbol

        if change is None:
            change_class, change_text, arrow = (
                "flat",
                "N/A",
                "•",
            )
        elif change > 0:
            change_class, change_text, arrow = (
                "positive",
                f"{change:.2f}%",
                "▲",
            )
        elif change < 0:
            change_class, change_text, arrow = (
                "negative",
                f"{abs(change):.2f}%",
                "▼",
            )
        else:
            change_class, change_text, arrow = (
                "flat",
                "0.00%",
                "•",
            )

        price_text = (
            "$" + f"{price:,.2f}"
            if price is not None
            else "N/A"
        )
        tape_items.append(
            '<div class="el-ticker-item">'
            f'<span class="el-ticker-company">{html.escape(company)}</span>'
            f'<span class="el-ticker-symbol">{html.escape(symbol)}</span>'
            f'<span class="el-ticker-price">{price_text}</span>'
            f'<span class="el-ticker-change {change_class}">'
            f'<span class="el-ticker-arrow">{arrow}</span>{change_text}'
            '</span></div>'
        )

    if tape_items:
        tape_html = "".join(tape_items + tape_items)
        st.markdown(
            f"""
            <div class="el-exchange-tape">
                <div class="el-exchange-pill">
                    <span>NYSE</span>
                    <span class="el-exchange-chevron">⌄</span>
                </div>
                <div class="el-ticker-shell">
                    <div class="el-ticker-track">{tape_html}</div>
                </div>
            </div>
            <div class="el-market-delay">
                Market-data snapshot · quotes may be delayed · hover to pause
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.caption(
            "NYSE ticker data is not available in the current market feed."
        )
    return True


def render_market_heatmap(
    nyse_finviz,
    workspace_known_tickers,
    research_link,
):
    section("Market Map", "NYSE Heat Map")
    st.markdown(
        """
        <div class="el-heatmap-head">
            <div class="el-heatmap-copy">
                Larger tiles represent larger market capitalization. Color represents today's price move.
            </div>
            <div class="el-heatmap-legend">
                <span class="el-legend-item"><span class="el-legend-swatch" style="background:#7F1D1D;"></span>Lower</span>
                <span class="el-legend-item"><span class="el-legend-swatch" style="background:#B94A50;"></span>Down</span>
                <span class="el-legend-item"><span class="el-legend-swatch" style="background:#24333A;"></span>Flat</span>
                <span class="el-legend-item"><span class="el-legend-swatch" style="background:#137F72;"></span>Up</span>
                <span class="el-legend-item"><span class="el-legend-swatch" style="background:#16C7B2;"></span>Higher</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    required = {
        "Ticker",
        "Sector",
        "Market Cap",
        "Change",
    }
    if not required.issubset(set(nyse_finviz.columns)):
        st.caption(
            "The current market feed is missing fields needed for the NYSE heat map."
        )
        return

    heatmap_df = nyse_finviz.copy()
    heatmap_df["_market_cap_num"] = heatmap_df[
        "Market Cap"
    ].apply(finviz_numeric)
    heatmap_df["_change_num"] = heatmap_df[
        "Change"
    ].apply(finviz_numeric)
    heatmap_df = heatmap_df.dropna(
        subset=[
            "_market_cap_num",
            "_change_num",
            "Sector",
        ]
    )
    heatmap_df = heatmap_df[
        heatmap_df["_market_cap_num"] > 0
    ]

    sectors = sorted(
        [
            str(sector)
            for sector in heatmap_df["Sector"]
            .dropna()
            .unique()
            .tolist()
            if str(sector).strip()
        ]
    )

    controls = st.columns([1.35, 1, 1.15])
    with controls[0]:
        selected_sector = st.selectbox(
            "Heat map sector",
            ["All sectors"] + sectors,
            key="nyse_heatmap_sector",
        )
    with controls[1]:
        limit = st.select_slider(
            "Companies shown",
            options=[40, 60, 80, 100, 120],
            value=120,
            key="nyse_heatmap_limit",
        )
    with controls[2]:
        search = st.text_input(
            "Find ticker",
            placeholder="e.g. JPM",
            key="nyse_heatmap_search",
        ).strip().upper()

    if selected_sector != "All sectors":
        heatmap_df = heatmap_df[
            heatmap_df["Sector"].astype(str)
            == selected_sector
        ]

    heatmap_df = heatmap_df.sort_values(
        "_market_cap_num",
        ascending=False,
    ).head(limit)

    if heatmap_df.empty:
        st.caption(
            "No NYSE companies match the current heat-map filters."
        )
        return

    matching_tickers = set()
    if search:
        matching_tickers = set(
            heatmap_df.loc[
                heatmap_df["Ticker"]
                .astype(str)
                .str.upper()
                .str.contains(
                    search,
                    regex=False,
                    na=False,
                ),
                "Ticker",
            ].astype(str)
        )

    if search and matching_tickers:
        matched_rows = heatmap_df[
            heatmap_df["Ticker"]
            .astype(str)
            .isin(matching_tickers)
        ].copy()
        matched_display = pd.DataFrame([
            {
                "Ticker": str(row.get("Ticker", "")),
                "Company": str(row.get("Company", "")),
                "Sector": str(row.get("Sector", "")),
                "Price": (
                    "$"
                    + f"{finviz_numeric(row.get('Price')):,.2f}"
                    if finviz_numeric(
                        row.get("Price")
                    ) is not None
                    else "N/A"
                ),
                "Daily Move": (
                    f"{float(row['_change_num']):+.2f}%"
                ),
                "Market Cap": (
                    "$"
                    + f"{float(row['_market_cap_num']):,.0f}"
                ),
                "Research": (
                    research_link(
                        str(row.get("Ticker", ""))
                    )
                    if str(
                        row.get("Ticker", "")
                    ).upper()
                    in workspace_known_tickers
                    else ""
                ),
            }
            for _, row in matched_rows.iterrows()
        ])
        st.markdown("**Ticker search result**")
        st.dataframe(
            matched_display,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Research": (
                    st.column_config.LinkColumn(
                        "Research",
                        display_text="Open research",
                    )
                )
            },
        )

    sector_rows = (
        heatmap_df.groupby(
            "Sector",
            dropna=False,
        )
        .apply(
            lambda group: pd.Series({
                "_sector_cap": group[
                    "_market_cap_num"
                ].sum(),
                "_sector_change": (
                    (
                        group["_change_num"]
                        * group["_market_cap_num"]
                    ).sum()
                    / group[
                        "_market_cap_num"
                    ].sum()
                ),
            })
        )
        .reset_index()
    )

    heat_ids = []
    heat_labels = []
    heat_parents = []
    heat_values = []
    heat_colors = []
    heat_custom = []

    for _, sector_row in sector_rows.iterrows():
        sector_name = str(sector_row["Sector"])
        heat_ids.append(f"sector::{sector_name}")
        heat_labels.append(sector_name)
        heat_parents.append("")
        heat_values.append(
            float(sector_row["_sector_cap"])
        )
        heat_colors.append(
            float(sector_row["_sector_change"])
        )
        heat_custom.append([
            sector_name,
            "",
            "",
            float(sector_row["_sector_change"]),
            float(sector_row["_sector_cap"]),
            "",
        ])

    for _, stock_row in heatmap_df.iterrows():
        symbol = str(stock_row.get("Ticker", ""))
        company = str(stock_row.get("Company", ""))
        sector = str(stock_row.get("Sector", ""))
        price = finviz_numeric(
            stock_row.get("Price")
        )
        change = float(stock_row["_change_num"])

        heat_ids.append(f"stock::{symbol}")
        heat_labels.append(symbol)
        heat_parents.append(f"sector::{sector}")
        heat_values.append(
            float(stock_row["_market_cap_num"])
        )
        heat_colors.append(change)
        heat_custom.append([
            company,
            sector,
            (
                "$" + f"{price:,.2f}"
                if price is not None
                else "N/A"
            ),
            change,
            float(stock_row["_market_cap_num"]),
            (
                "Match"
                if symbol in matching_tickers
                else ""
            ),
        ])

    fig = go.Figure(
        go.Treemap(
            ids=heat_ids,
            labels=heat_labels,
            parents=heat_parents,
            values=heat_values,
            branchvalues="total",
            maxdepth=2,
            pathbar={
                "visible": True,
                "textfont": {
                    "family": "IBM Plex Mono",
                    "size": 12,
                    "color": "#C6D0D5",
                },
                "thickness": 28,
            },
            tiling={
                "packing": "squarify",
                "pad": 2,
            },
            marker={
                "colors": heat_colors,
                "colorscale": [
                    [0.0, "#7F1D1D"],
                    [0.35, "#B94A50"],
                    [0.5, "#24333A"],
                    [0.65, "#137F72"],
                    [1.0, "#16C7B2"],
                ],
                "cmid": 0,
                "line": {
                    "color": "#050B0E",
                    "width": 1.4,
                },
            },
            customdata=heat_custom,
            hovertemplate=(
                "<b>%{label}</b><br>"
                "%{customdata[0]}<br>"
                "Sector: %{customdata[1]}<br>"
                "Price: %{customdata[2]}<br>"
                "Daily change: %{customdata[3]:+.2f}%<br>"
                "Market cap: $%{customdata[4]:,.0f}<br>"
                "%{customdata[5]}"
                "<extra></extra>"
            ),
            texttemplate=(
                "<b>%{label}</b><br>"
                "%{customdata[3]:+.1f}%"
            ),
            textfont={
                "family": "IBM Plex Mono",
                "size": 13,
            },
            hoverlabel={
                "bgcolor": "#091217",
                "bordercolor": "#263640",
                "font": {
                    "family": "IBM Plex Sans",
                    "color": "#EEF3F5",
                },
            },
            root={"color": "#071014"},
        )
    )
    apply_equitylens_layout(
        fig,
        height=560,
        margin={
            "l": 0,
            "r": 0,
            "t": 8,
            "b": 0,
        },
    )
    fig.update_layout(
        plot_bgcolor="#050B0E",
    )
    with st.container(
        key="nyse_heatmap_visual"
    ):
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )
    st.caption(
        "Click a sector to drill into it, then use the breadcrumb above the map to return. "
        "Tile size represents market capitalization. Color and the printed percentage both represent "
        "the daily price move, so the map does not rely on red/green color alone. "
        "This is market context, not a recommendation."
    )

    with st.expander(
        "Open research for a company on this map"
    ):
        rows = heatmap_df[["Ticker"]].copy()
        rows["Company"] = heatmap_df.get(
            "Company",
            heatmap_df["Ticker"],
        )
        rows = rows[
            rows["Ticker"]
            .astype(str)
            .str.upper()
            .isin(workspace_known_tickers)
        ]
        if search:
            rows = rows[
                rows["Ticker"]
                .astype(str)
                .isin(matching_tickers)
            ]
        if not rows.empty:
            rows["Research"] = rows[
                "Ticker"
            ].apply(research_link)
            st.dataframe(
                rows,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Research": (
                        st.column_config.LinkColumn(
                            "Research",
                            display_text="Open research",
                        )
                    )
                },
            )
        else:
            st.caption(
                "No companies in this map selection have a matching research profile."
            )

    if search:
        if matching_tickers:
            st.caption(
                "Ticker search match: "
                + ", ".join(
                    sorted(matching_tickers)
                )
            )
        else:
            st.caption(
                f'No displayed ticker matches "{search}". '
                "Try a broader search or show more companies."
            )


def render_nyse_market_monitor(
    nyse_finviz,
    workspace_known_tickers,
    research_link,
):
    if not render_market_tape(nyse_finviz):
        return
    render_market_heatmap(
        nyse_finviz,
        workspace_known_tickers,
        research_link,
    )
