import boto3
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
        socket_timeout=5,
        socket_connect_timeout=5,
    )

    changelog_ring_buffer: providers.Singleton[RedisRingBuffer] = providers.Singleton(
        RedisRingBuffer,
        redis=redis,
        name="changelog",
        max_size=5,
    )
    locations_ring_buffer: providers.Singleton[RedisRingBuffer] = providers.Singleton(
        RedisRingBuffer,
        redis=redis,
        name="locations",
        max_size=5,
    )

    hash_n_compare_github_payload_on_create: providers.Callable[
        hash_github_payload_and_compare
    ] = providers.Callable(
        hash_github_payload_and_compare,
        key=settings.GITHUB_CREATE_WEBHOOK_TOKEN,
    )

    _ymq_locations_session = providers.Resource(  # type:ignore
        boto3.session.Session,
        aws_access_key_id=settings.YMQ_LOCATIONS_ACCESS_KEY,
        aws_secret_access_key=settings.YMQ_LOCATIONS_SECRET_KEY,
    )
    _ymq_locations_resource = providers.Resource(
        _ymq_locations_session.provided.resource.call(),
        service_name="sqs",
        endpoint_url=settings.YMQ_LOCATIONS_ENDPOINT_URL,
        region_name=settings.YMQ_LOCATIONS_REGION_NAME,
    )
    ymq_locations_queue = providers.Resource(
        _ymq_locations_resource.provided.Queue.call(),
        settings.YMQ_LOCATIONS_QUEUE_URL,
    )
