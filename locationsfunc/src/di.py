import ipinfo
from dependency_injector import containers, providers
from redis.asyncio import Redis, StrictRedis

from locationsfunc.src import config
from locationsfunc.src.redis import RedisRingBuffer


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["locationsfunc.src"])

    redis: providers.Singleton[Redis] = providers.Singleton(
        StrictRedis,
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
        socket_timeout=5,
        socket_connect_timeout=5,
    )

    ring_buffer: providers.Singleton[RedisRingBuffer] = providers.Singleton(
        RedisRingBuffer,
        redis=redis,
        name="locations",
        max_size=5,
    )

    ipinfo_handler: providers.Singleton[ipinfo.AsyncHandler] = providers.Singleton(
        ipinfo.getHandlerAsync,
        config.IPINFO_ACCESS_TOKEN,
    )
