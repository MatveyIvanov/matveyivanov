import os


def load[
    T: str | int | float
](
    key: str,
    default: T,
    *,
    cast_to: type[T] | None = None,
    ensure_not_empty: bool = False,
) -> T:
    value = os.environ.get(key, default)
    if not value and ensure_not_empty:
        return default
    return value if cast_to is None else cast_to(value)  # type:ignore[return-value]


REDIS_HOST: str = load("REDIS_HOST", "redis", ensure_not_empty=True)
REDIS_PORT: int = load("REDIS_PORT", 6379, cast_to=int, ensure_not_empty=True)
REDIS_PASSWORD: str = load("REDIS_PASSWORD", "password", ensure_not_empty=True)
REDIS_SOCKET_TIMEOUT: int = load(
    "REDIS_SOCKET_TIMEOUT",
    5,
    cast_to=int,
    ensure_not_empty=True,
)
REDIS_SOCKET_CONNECTION_TIMEOUT: int = load(
    "REDIS_SOCKET_CONNECTION_TIMEOUT",
    5,
    cast_to=int,
    ensure_not_empty=True,
)

IPINFO_ACCESS_TOKEN: str = load("IPINFO_ACCESS_TOKEN", "")
IPINFO_TIMEOUT: int = load("IPINFO_TIMEOUT", 5, cast_to=int, ensure_not_empty=True)
IPINFO_DEFAULT_CITY: str = load("IPINFO_DEFAULT_CITY", "Unknown", ensure_not_empty=True)

LOCATIONS_BUFFER_NAME: str = load(
    "LOCATIONS_BUFFER_NAME",
    "locations",
    ensure_not_empty=True,
)
LOCATIONS_BUFFER_MAX_SIZE: int = load(
    "LOCATIONS_BUFFER_MAX_SIZE",
    5,
    cast_to=int,
    ensure_not_empty=True,
)
LOCATIONS_HASHSET_NAME: str = load(
    "LOCATIONS_HASHSET_NAME",
    "hashset:locations",
    ensure_not_empty=True,
)
