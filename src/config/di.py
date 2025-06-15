# fmt: off
import logging
from copy import deepcopy

import boto3
from dependency_injector import containers, providers
from redis.asyncio import Redis, StrictRedis

from config import settings
from schemas.changelog import ChangelogItemDict
from schemas.locations import LocationDict
from services.github import hash_github_payload_and_compare
from services.redis import RedisRingBuffer


def _validate_provider[T: providers.Provider](  # type:ignore[type-arg]
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
        result = self.__pipeline.copy()
        self.__pipeline.clear()
        return result


class BotoQueueFallback:
    def send_message(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        return


class BotoResourceFallback:
    def Queue(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        return BotoQueueFallback()


class BotoSessionFallback:
    def resource(self, *args, **kwargs):  # type:ignore[no-untyped-def]
        return BotoResourceFallback()


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
    redis = _validate_provider(
        redis,
        fallback_to=providers.Singleton(RedisFallback),  # type:ignore[arg-type]
    )

    changelog_ring_buffer: providers.Singleton[RedisRingBuffer[ChangelogItemDict]] = (
        providers.Singleton(
            RedisRingBuffer,
            redis=redis,
            name=settings.CHANGELOG_BUFFER_NAME,
            max_size=settings.CHANGELOG_BUFFER_MAX_SIZE,
        )
    )
    locations_ring_buffer: providers.Singleton[RedisRingBuffer[LocationDict]] = (
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
    _sqs_locations_session = _validate_provider(
        _sqs_locations_session,
        fallback_to=providers.Singleton(BotoSessionFallback),  # type:ignore[arg-type]
    )

    _sqs_locations_resource = providers.Resource(
        _sqs_locations_session.provided.resource.call(),
        service_name="sqs",
        endpoint_url=settings.SQS_LOCATIONS_ENDPOINT_URL,
        region_name=settings.SQS_LOCATIONS_REGION_NAME,
    )
    _sqs_locations_resource = _validate_provider(
        _sqs_locations_resource,
        fallback_to=providers.Singleton(BotoResourceFallback),  # type:ignore[arg-type]
    )

    sqs_locations_queue = providers.Resource(
        _sqs_locations_resource.provided.Queue.call(),
        settings.SQS_LOCATIONS_QUEUE_URL,
    )
    sqs_locations_queue = _validate_provider(
        sqs_locations_queue,
        fallback_to=providers.Singleton(BotoQueueFallback),  # type:ignore[arg-type]
    )
