from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings


def get_cached_value(key: str) -> str | None:
    try:
        redis_client = _get_redis_client()
        value = redis_client.get(key)
    except RedisError:
        return None

    if value is None:
        return None

    return value.decode("utf-8")


def set_cached_value(key: str, value: str, ttl_seconds: int) -> None:
    try:
        redis_client = _get_redis_client()
        redis_client.setex(key, ttl_seconds, value)
    except RedisError:
        return


def _get_redis_client() -> Redis:
    return Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=2,
        socket_timeout=2,
    )
