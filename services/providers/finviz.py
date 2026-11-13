from services.http import get


def fetch_screener(
    url,
    *,
    headers,
    params=None,
):
    return get(
        str(url),
        headers=headers,
        params=params,
        timeout=(5, 30),
        provider="Finviz",
    )
