from dependency_injector import containers, providers
from redis.asyncio import StrictRedis

from config import settings
from services.redis import RedisRingBuffer


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["endpoints"])

    redis = providers.Singleton(
        StrictRedis,
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        socket_timeout=1,
        socket_connect_timeout=1,
    )

    changelog_ring_buffer = providers.Singleton(
        RedisRingBuffer,
        redis=redis,
        name="changelog",
        max_size=5,
    )
