import logging
import os

from validators import validator_int
from validators.interfaces import IValidator


def load[
    T: str | int | float
](
    key: str,
    default: T,
    *,
    cast_to: type[T] | None = None,
    ensure_not_empty: bool = False,
    validator: IValidator | None = None,
) -> T:
    value = os.environ.get(key, default)
    if not value and ensure_not_empty:
        return default
    try:
        casted = value if cast_to is None else cast_to(value)
    except ValueError:
        casted = value
    if validator and not validator(casted):
        logging.warning(f"Value {casted} is not valid for {key}... using default.")
        return default
    return casted  # type:ignore[return-value]


REDIS_HOST: str = load("REDIS_HOST", "redis", ensure_not_empty=True)
REDIS_PORT: int = load(
    "REDIS_PORT",
    6379,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)
REDIS_PASSWORD: str = load("REDIS_PASSWORD", "password", ensure_not_empty=True)
REDIS_SOCKET_TIMEOUT: int = load(
    "REDIS_SOCKET_TIMEOUT",
    5,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)
REDIS_SOCKET_CONNECTION_TIMEOUT: int = load(
    "REDIS_SOCKET_CONNECTION_TIMEOUT",
    5,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)

IPINFO_ACCESS_TOKEN: str = load("IPINFO_ACCESS_TOKEN", "")
IPINFO_TIMEOUT: int = load(
    "IPINFO_TIMEOUT",
    5,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)
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
    validator=validator_int,
)
LOCATIONS_HASHSET_NAME: str = load(
    "LOCATIONS_HASHSET_NAME",
    "hashset:locations",
    ensure_not_empty=True,
)
LOCATIONS_SECONDS_CONSIDER_AS_NEW: int = load(
    "LOCATIONS_SECONDS_CONSIDER_AS_NEW",
    60 * 60 * 24,
    ensure_not_empty=True,
    cast_to=int,
    validator=validator_int,
)
