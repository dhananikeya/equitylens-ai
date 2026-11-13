from config import PROVIDERS


def source_label(provider_key, fallback="Source unavailable"):
    provider = PROVIDERS.get(provider_key, {})
    return provider.get("label", fallback)


def source_authority(provider_key):
    provider = PROVIDERS.get(provider_key, {})
    return provider.get("authority", "supplemental")
