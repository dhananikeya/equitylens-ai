from services.http import get


SEC_HEADERS = {
    "User-Agent": (
        "EquityLens AI research app "
        "dhananikeya@gmail.com"
    )
}


def fetch_company_facts(cik):
    normalized = str(cik).zfill(10)
    return get(
        (
            "https://data.sec.gov/api/xbrl/"
            f"companyfacts/CIK{normalized}.json"
        ),
        headers=SEC_HEADERS,
        timeout=(5, 20),
        provider="SEC",
    )


def fetch_ticker_directory():
    return get(
        "https://www.sec.gov/files/company_tickers.json",
        headers=SEC_HEADERS,
        timeout=(5, 30),
        provider="SEC",
    )


def fetch_submissions(cik):
    normalized = str(cik).zfill(10)
    return get(
        (
            "https://data.sec.gov/submissions/"
            f"CIK{normalized}.json"
        ),
        headers=SEC_HEADERS,
        timeout=(5, 30),
        provider="SEC",
    )


def fetch_submission_history(name):
    return get(
        (
            "https://data.sec.gov/submissions/"
            + str(name)
        ),
        headers=SEC_HEADERS,
        timeout=(5, 30),
        provider="SEC",
    )
