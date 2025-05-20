from dependency_injector import containers, providers
from redis.asyncio import Redis, StrictRedis

from config import settings
from services.github import hash_github_payload_and_compare
from services.redis import RedisRingBuffer


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["endpoints"])

    redis: providers.Singleton[Redis] = providers.Singleton(
        StrictRedis,
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        socket_timeout=1,
        socket_connect_timeout=1,
    )

    changelog_ring_buffer: providers.Singleton[RedisRingBuffer] = providers.Singleton(
        RedisRingBuffer,
        redis=redis,
        name="changelog",
        max_size=5,
    )

    hash_n_compare_github_payload_on_create: providers.Callable[
        hash_github_payload_and_compare
    ] = providers.Callable(
        hash_github_payload_and_compare,
        key=settings.GITHUB_CREATE_WEBHOOK_TOKEN,
    )
