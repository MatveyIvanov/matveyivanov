# fmt: off
from typing import Any

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
        socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
        socket_connect_timeout=settings.REDIS_SOCKET_CONNECTION_TIMEOUT,
    )

    changelog_ring_buffer: providers.Singleton[RedisRingBuffer[dict[str, Any]]] = (
        providers.Singleton(
            RedisRingBuffer,
            redis=redis,
            name=settings.CHANGELOG_BUFFER_NAME,
            max_size=settings.CHANGELOG_BUFFER_MAX_SIZE,
        )
    )
    locations_ring_buffer: providers.Singleton[RedisRingBuffer[dict[str, Any]]] = (
        providers.Singleton(
            RedisRingBuffer,
            redis=redis,
            name=settings.LOCATIONS_BUFFER_NAME,
            max_size=settings.LOCATIONS_BUFFER_MAX_SIZE,
        )
    )

    hash_n_compare_github_payload_on_create = providers.Callable(
        hash_github_payload_and_compare,
        key=settings.GITHUB_CREATE_WEBHOOK_TOKEN,
    )

    _sqs_locations_session = providers.Resource(
        boto3.session.Session,
        aws_access_key_id=settings.SQS_LOCATIONS_ACCESS_KEY,
        aws_secret_access_key=settings.SQS_LOCATIONS_SECRET_KEY,
    )
    _sqs_locations_resource = providers.Resource(
        _sqs_locations_session.provided.resource.call(),
        service_name="sqs",
        endpoint_url=settings.SQS_LOCATIONS_ENDPOINT_URL,
        region_name=settings.SQS_LOCATIONS_REGION_NAME,
    )
    sqs_locations_queue = providers.Resource(
        _sqs_locations_resource.provided.Queue.call(),
        settings.SQS_LOCATIONS_QUEUE_URL,
    )
