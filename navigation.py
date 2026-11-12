from urllib.parse import urlencode

from config import PUBLIC_APP_URL


NAVIGATION_LABELS = {
    "Home": "Home",
    "Company Research": "Company Research — companies, tickers & SEC analysis",
    "Industry Comparison": "Industry Comparison — industries & peers",
    "Market Monitor": "Market Monitor — company monitor, markets, ticker & heat map",
    "Filings": "Filings — SEC tracker, S-1, 10-K & 10-Q",
    "Learn": "Learn — learn the basics, lessons & financial terms",
}

CHOICE_KEYS = {
    "workspace_company_search",
    "workspace_sector",
    "workspace_industry",
    "peer_industry",
    "peer_subgroup",
    "peer_companies",
    "nyse_heatmap_sector",
    "nyse_heatmap_limit",
    "nyse_heatmap_search",
    "market_monitor_industry",
    "market_movement_threshold",
    "market_monitor_section",
    "finviz_min_relative_volume",
    "finviz_min_abs_change",
    "peer_comparison_focus",
    "learning_path",
    "sec_tracker_company",
    "sec_tracker_forms",
    "sec_registration_company",
    "sec_tracker_search",
    "sec_tracker_category",
    "sec_tracker_display_limit",
    "sec_tracker_start_date",
    "sec_tracker_end_date",
}


def initialize_saved_choices(st):
    saved = st.session_state.setdefault(
        "saved_choices",
        {},
    )
    for key, value in saved.items():
        st.session_state.setdefault(
            key,
            value,
        )


def remember_choice(st, key, value):
    st.session_state[key] = value
    st.session_state.setdefault(
        "saved_choices",
        {},
    )[key] = value


def save_rendered_choices(st):
    saved = st.session_state.setdefault(
        "saved_choices",
        {},
    )
    for key, value in list(
        st.session_state.items()
    ):
        if (
            key in CHOICE_KEYS
            or key.startswith(
                (
                    "workspace_chart_range_",
                    "workspace_section_",
                )
            )
        ):
            saved[key] = value


def reset_coverage_selection(st):
    st.session_state.pop(
        "workspace_coverage_table",
        None,
    )


def clear_company_filters(st):
    remember_choice(
        st,
        "workspace_sector",
        "All sectors",
    )
    remember_choice(
        st,
        "workspace_industry",
        "All industries",
    )
    reset_coverage_selection(st)


def navigate_to(st, destination):
    st.session_state[
        "main_navigation"
    ] = destination


def research_link(
    ticker=None,
    destination="Company Research",
):
    params = {"section": destination}
    if ticker:
        params["ticker"] = ticker
    return (
        PUBLIC_APP_URL
        + "?"
        + urlencode(params)
    )


def build_global_company_lookup(
    company_universe,
):
    lookup = {}
    for _, row in company_universe.iterrows():
        ticker = str(
            row.get("Ticker", "")
        ).upper().strip()
        if not ticker:
            continue
        lookup[
            f"ticker::{ticker}"
        ] = {
            "ticker": ticker,
            "company": str(
                row.get("Company", "")
            ).strip(),
            "industry": str(
                row.get("Industry", "")
            ).strip(),
        }
    return lookup


def global_search_options(
    lookup,
):
    return (
        list(NAVIGATION_LABELS)
        + sorted(
            lookup,
            key=lambda option: (
                lookup[option]["company"].lower(),
                lookup[option]["ticker"].lower(),
            ),
        )
    )


def format_global_search_option(
    option,
    lookup,
):
    if option in NAVIGATION_LABELS:
        return NAVIGATION_LABELS[option]

    company = lookup.get(option, {})
    ticker = company.get("ticker", "")
    name = company.get(
        "company",
        ticker,
    )
    industry = company.get(
        "industry",
        "",
    )
    suffix = (
        f" · {industry}"
        if industry
        else ""
    )
    return f"{ticker} · {name}{suffix}"
