from services.http import get


BLOOMBERG_MARKETS_URL = (
    "https://www.bloomberg.com/markets"
)


def fetch_feed(url, headers):
    return get(
        url,
        headers=headers,
        timeout=(5, 20),
    )


def fetch_markets(headers):
    return get(
        BLOOMBERG_MARKETS_URL,
        headers=headers,
        timeout=(5, 20),
    )
