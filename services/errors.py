class EquityLensError(Exception):
    """Base application error."""


class ProviderError(EquityLensError):
    def __init__(self, provider, message, *, retryable=True):
        super().__init__(message)
        self.provider = provider
        self.retryable = retryable


def safe_provider_call(
    provider,
    callable_obj,
    *,
    fallback=None,
):
    try:
        return callable_obj()
    except Exception as exc:
        if fallback is not None:
            return fallback
        raise ProviderError(
            provider,
            str(exc),
        ) from exc
