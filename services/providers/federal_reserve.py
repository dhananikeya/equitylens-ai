from services.http import get


FOMC_CALENDAR_URL = (
    "https://www.federalreserve.gov/"
    "monetarypolicy/fomccalendars.htm"
)
MONETARY_FEED_URL = (
    "https://www.federalreserve.gov/"
    "feeds/press_monetary.xml"
)


def fetch_fomc_calendar(headers):
    return get(
        FOMC_CALENDAR_URL,
        headers=headers,
        timeout=(5, 25),
        provider="FederalReserve",
    )


def fetch_monetary_feed(headers):
    return get(
        MONETARY_FEED_URL,
        headers=headers,
        timeout=(5, 25),
        provider="FederalReserve",
    )
