from dataclasses import asdict

from dependency_injector.wiring import Provide, inject
from ipinfo import AsyncHandler
from redis.asyncio import Redis

from src.di import Container
from src.interfaces import IRingBuffer
from src.types import IPEvent, Location

HASHSET_NAME = "hashset:locations"


@inject
async def handle(
    event: IPEvent,
    redis: Redis = Provide[Container.redis],
    ring_buffer: IRingBuffer[dict] = Provide[Container.ring_buffer],
    ipinfo_handler: AsyncHandler = Provide[Container.ipinfo_handler],
) -> None:
    location = await redis.hget(HASHSET_NAME, event.ip)
    if location is None:
        details = await ipinfo_handler.getDetails(event.ip, timeout=5)
        location = details.city or "unknown"
        await redis.hset(HASHSET_NAME, event.ip, location)

    await ring_buffer.put(asdict(Location(locaton=location, timestamp=event.timestamp)))
