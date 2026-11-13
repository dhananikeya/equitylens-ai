from services.http import get


def fetch_treasury_csv(url, headers):
    return get(
        url,
        headers=headers,
        timeout=(5, 15),
        provider="Treasury",
    )


def fetch_treasury_html(url, headers):
    return get(
        url,
        headers=headers,
        timeout=(5, 15),
        provider="Treasury",
    )


def fetch_treasury_xml(url, headers):
    return get(
        url,
        headers=headers,
        timeout=(5, 15),
        provider="Treasury",
    )


def fetch_fred_csv(url, headers):
    return get(
        url,
        headers=headers,
        timeout=(5, 15),
        provider="Treasury",
    )
