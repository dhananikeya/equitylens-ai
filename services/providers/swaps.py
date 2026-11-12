from services.http import get


DEFAULT_SWAP_URL = (
    "https://checkmyswap.com/api/curves/USD"
)


def fetch_swap_curve(
    configured_endpoint,
    headers,
):
    endpoint = (
        str(configured_endpoint or "").strip()
        or DEFAULT_SWAP_URL
    )
    return get(
        endpoint,
        headers=headers,
        timeout=(5, 12),
        provider="SwapCurve",
    )
