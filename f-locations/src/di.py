import logging
from copy import deepcopy
from typing import Any

import ipinfo
from dependency_injector import containers, providers
from redis.asyncio import Redis, StrictRedis

from src import config
from src.redis import RedisRingBuffer


def _validate_provider[
    T: providers.Provider
](  # type:ignore[type-arg]
    provider: T,
    *,
    panic: bool = False,
    fallback_to: T | None = None,
) -> T:
    ok, error = True, None
    copy = deepcopy(provider)
    try:
        copy()
    except Exception as e:
        logging.error(f"Error providing {provider} - {str(e)}")
        ok, error = False, e

    if not ok and panic and error:
        raise error
    return (fallback_to or provider) if not ok else provider


class RedisFallback:
    def __init__(self, *args, **kwargs) -> None:  # type:ignore[no-untyped-def]
        self.__pipeline = []  # type:ignore[var-annotated]

    async def get(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        self.__pipeline.append(None)
        return None

    async def set(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        return None

    async def hgetall(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        return {}

    async def hset(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        return 0

    async def exists(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        return False

    def register_script(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        return

    def pipeline(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        return RedisFallback()

    async def incrby(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        self.__pipeline.append(None)

    incr = incrby

    async def execute(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        result = self.__pipeline
        self.__pipeline.clear()
        return result


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["src"])

    redis: providers.Singleton[Redis] = providers.Singleton(
        StrictRedis,
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
        socket_timeout=config.REDIS_SOCKET_TIMEOUT,
        socket_connect_timeout=config.REDIS_SOCKET_CONNECTION_TIMEOUT,
    )
    redis = _validate_provider(
        redis,
        fallback_to=providers.Singleton(RedisFallback),  # type:ignore[arg-type]
    )

    ring_buffer: providers.Singleton[RedisRingBuffer[dict[str, Any]]] = (
        providers.Singleton(
            RedisRingBuffer,
            redis=redis,
            name=config.LOCATIONS_BUFFER_NAME,
            max_size=config.LOCATIONS_BUFFER_MAX_SIZE,
        )
    )

    ipinfo_handler: providers.Singleton = providers.Singleton(  # type:ignore[type-arg]
        ipinfo.getHandlerAsync,
        config.IPINFO_ACCESS_TOKEN,
    )
