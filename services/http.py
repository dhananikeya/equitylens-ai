import requests

from services.errors import ProviderError


DEFAULT_HEADERS = {
    "User-Agent": "EquityLens/1.0",
}


def get(
    url,
    *,
    headers=None,
    params=None,
    timeout=(5, 15),
    provider="HTTP",
):
    merged_headers = {
        **DEFAULT_HEADERS,
        **(headers or {}),
    }
    try:
        response = requests.get(
            url,
            headers=merged_headers,
            params=params,
            timeout=timeout,
        )
        response.raise_for_status()
        return response
    except requests.RequestException as exc:
        raise ProviderError(
            provider,
            str(exc),
        ) from exc


def post(
    url,
    *,
    headers=None,
    json=None,
    timeout=(5, 20),
    provider="HTTP",
):
    merged_headers = {
        **DEFAULT_HEADERS,
        **(headers or {}),
    }
    try:
        response = requests.post(
            url,
            headers=merged_headers,
            json=json,
            timeout=timeout,
        )
        response.raise_for_status()
        return response
    except requests.RequestException as exc:
        raise ProviderError(
            provider,
            str(exc),
        ) from exc
