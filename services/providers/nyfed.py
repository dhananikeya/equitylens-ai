from services.http import get


SOFR_URL = (
    "https://markets.newyorkfed.org/api/rates/"
    "secured/sofr/last/1.json"
)
SOFR_AVERAGES_URL = (
    "https://markets.newyorkfed.org/api/rates/"
    "secured/sofr-avg-ind/last/1.json"
)


def fetch_sofr(headers):
    return get(
        SOFR_URL,
        headers=headers,
        timeout=(4, 8),
    )


def fetch_sofr_averages(headers):
    return get(
        SOFR_AVERAGES_URL,
        headers=headers,
        timeout=(4, 8),
    )
