import requests
from requests import RequestException

from app.core.config import settings
from app.core.errors import service_unavailable_error
from app.services.cache_service import get_cached_value, set_cached_value

AWESOME_API_URL = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
FRANKFURTER_API_URL = "https://api.frankfurter.app/latest?from=USD&to=BRL"


def get_usd_to_brl() -> float:
    cached_rate = get_cached_value(settings.usd_cache_key)
    if cached_rate is not None:
        return float(cached_rate)

    try:
        rate = _get_from_awesome_api()
        _cache_rate(rate)
        return rate
    except (KeyError, RequestException, TypeError, ValueError):
        pass

    try:
        rate = _get_from_frankfurter()
        _cache_rate(rate)
        return rate
    except (KeyError, RequestException, TypeError, ValueError) as exc:
        raise service_unavailable_error(
            "Unable to fetch USD to BRL exchange rate."
        ) from exc


def _get_from_awesome_api() -> float:
    data = _fetch_json(AWESOME_API_URL)
    return float(data["USDBRL"]["bid"])


def _get_from_frankfurter() -> float:
    data = _fetch_json(FRANKFURTER_API_URL)
    return float(data["rates"]["BRL"])


def _fetch_json(url: str) -> dict:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()


def _cache_rate(rate: float) -> None:
    set_cached_value(
        key=settings.usd_cache_key,
        value=str(rate),
        ttl_seconds=settings.usd_cache_ttl_seconds,
    )
