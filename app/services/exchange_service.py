import json
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from fastapi import HTTPException, status

AWESOME_API_URL = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
FRANKFURTER_API_URL = "https://api.frankfurter.app/latest?from=USD&to=BRL"


def get_usd_to_brl() -> float:
    try:
        return _get_from_awesome_api()
    except (HTTPError, KeyError, TypeError, URLError, ValueError):
        pass

    try:
        return _get_from_frankfurter()
    except (HTTPError, KeyError, TypeError, URLError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": "Unable to fetch USD to BRL exchange rate.",
                "code": "EXCHANGE_RATE_UNAVAILABLE",
            },
        ) from exc


def _get_from_awesome_api() -> float:
    data = _fetch_json(AWESOME_API_URL)
    return float(data["USDBRL"]["bid"])


def _get_from_frankfurter() -> float:
    data = _fetch_json(FRANKFURTER_API_URL)
    return float(data["rates"]["BRL"])


def _fetch_json(url: str) -> dict:
    with urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))
