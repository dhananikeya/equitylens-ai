def retry_company_data(st, ticker):
    """Clear cached company data only when the user explicitly refreshes."""
    from sec_data import (
        get_sec_company_research,
    )
    from market_data import (
        get_company_analyst_data,
        get_company_financial_snapshot,
        get_company_ownership_data,
        get_live_market_data,
        get_major_etf_exposure,
        get_market_history,
    )

    normalized_ticker = (
        str(ticker).upper().strip()
    )

    get_sec_company_research.clear(
        ticker
    )
    get_live_market_data.clear(
        [ticker]
    )
    get_company_financial_snapshot.clear(
        ticker
    )
    get_company_ownership_data.clear(
        ticker
    )
    get_company_analyst_data.clear(
        ticker
    )
    get_major_etf_exposure.clear(
        ticker
    )
    get_market_history.clear()

    prefixes = (
        f"company_core_snapshot::{normalized_ticker}",
        f"company_ownership::{normalized_ticker}",
        f"company_analyst::{normalized_ticker}",
        f"company_etf_exposure::{normalized_ticker}",
        f"company_history::{normalized_ticker}::",
    )

    for key in list(st.session_state):
        if any(
            key == prefix
            or key.startswith(prefix)
            for prefix in prefixes
        ):
            st.session_state.pop(
                key,
                None,
            )
