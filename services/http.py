import time
from urllib.parse import urlparse

import requests

from services.errors import ProviderError


DEFAULT_HEADERS = {
    "User-Agent": "EquityLens/1.0",
}

RETRYABLE_STATUS_CODES = {
    408,
    425,
    429,
    500,
    502,
    503,
    504,
}

DEFAULT_ATTEMPTS = 3
MAX_RETRY_DELAY_SECONDS = 8.0

_SESSION = requests.Session()


def _validate_url(url):
    parsed = urlparse(
        str(url)
    )
    if parsed.scheme not in {
        "http",
        "https",
    } or not parsed.netloc:
        raise ProviderError(
            "HTTP",
            "Provider URL is invalid.",
            retryable=False,
        )


def _retry_delay(
    response,
    attempt,
):
    retry_after = None
    if response is not None:
        raw = response.headers.get(
            "Retry-After"
        )
        try:
            retry_after = float(
                raw
            )
        except (
            TypeError,
            ValueError,
        ):
            retry_after = None

    if retry_after is None:
        retry_after = (
            0.75
            * (2 ** attempt)
        )

    return min(
        max(
            retry_after,
            0.0,
        ),
        MAX_RETRY_DELAY_SECONDS,
    )


def _provider_error(
    provider,
    *,
    status_code=None,
    retryable=True,
):
    if status_code is None:
        message = (
            f"{provider} request failed."
        )
    else:
        message = (
            f"{provider} returned HTTP "
            f"{status_code}."
        )
    return ProviderError(
        provider,
        message,
        retryable=retryable,
        status_code=status_code,
    )


def _request(
    method,
    url,
    *,
    headers=None,
    params=None,
    json=None,
    timeout,
    provider,
    attempts=DEFAULT_ATTEMPTS,
):
    _validate_url(url)

    merged_headers = {
        **DEFAULT_HEADERS,
        **(headers or {}),
    }
    attempts = max(
        1,
        int(attempts),
    )

    for attempt in range(
        attempts
    ):
        response = None
        try:
            response = _SESSION.request(
                method,
                url,
                headers=merged_headers,
                params=params,
                json=json,
                timeout=timeout,
            )
        except (
            requests.Timeout,
            requests.ConnectionError,
        ) as exc:
            if attempt < attempts - 1:
                time.sleep(
                    _retry_delay(
                        None,
                        attempt,
                    )
                )
                continue
            raise _provider_error(
                provider,
                retryable=True,
            ) from exc
        except requests.RequestException as exc:
            raise _provider_error(
                provider,
                retryable=False,
            ) from exc

        status_code = (
            response.status_code
        )
        if 200 <= status_code < 400:
            return response

        retryable = (
            status_code
            in RETRYABLE_STATUS_CODES
        )
        if (
            retryable
            and attempt
            < attempts - 1
        ):
            time.sleep(
                _retry_delay(
                    response,
                    attempt,
                )
            )
            continue

        raise _provider_error(
            provider,
            status_code=status_code,
            retryable=retryable,
        )

    raise _provider_error(
        provider,
        retryable=True,
    )


def get(
    url,
    *,
    headers=None,
    params=None,
    timeout=(5, 15),
    provider="HTTP",
    attempts=DEFAULT_ATTEMPTS,
):
    return _request(
        "GET",
        url,
        headers=headers,
        params=params,
        timeout=timeout,
        provider=provider,
        attempts=attempts,
    )


def post(
    url,
    *,
    headers=None,
    json=None,
    timeout=(5, 20),
    provider="HTTP",
    attempts=DEFAULT_ATTEMPTS,
):
    return _request(
        "POST",
        url,
        headers=headers,
        json=json,
        timeout=timeout,
        provider=provider,
        attempts=attempts,
    )
