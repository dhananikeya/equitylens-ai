from services.http import get, post


BLS_API_URL = (
    "https://api.bls.gov/publicAPI/v2/"
    "timeseries/data/"
)
BLS_CALENDAR_URL = (
    "https://www.bls.gov/schedule/"
    "news_release/bls.ics"
)


def fetch_series(payload, headers):
    return post(
        BLS_API_URL,
        headers=headers,
        json=payload,
        timeout=(5, 30),
    )


def fetch_calendar(headers):
    return get(
        BLS_CALENDAR_URL,
        headers=headers,
        timeout=(5, 25),
    )
