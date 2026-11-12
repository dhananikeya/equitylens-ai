import requests


DEFAULT_HEADERS = {
    "User-Agent": "EquityLens/1.0",
}


def get(
    url,
    *,
    headers=None,
    params=None,
    timeout=(5, 15),
):
    merged_headers = {
        **DEFAULT_HEADERS,
        **(headers or {}),
    }
    response = requests.get(
        url,
        headers=merged_headers,
        params=params,
        timeout=timeout,
    )
    response.raise_for_status()
    return response


def post(
    url,
    *,
    headers=None,
    json=None,
    timeout=(5, 20),
):
    merged_headers = {
        **DEFAULT_HEADERS,
        **(headers or {}),
    }
    response = requests.post(
        url,
        headers=merged_headers,
        json=json,
        timeout=timeout,
    )
    response.raise_for_status()
    return response
