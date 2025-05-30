from dataclasses import asdict
from typing import Any

from dependency_injector.wiring import Provide, inject
from ipinfo import AsyncHandler
from redis.asyncio import Redis

from src import config
from src.di import Container
from src.interfaces import IRingBuffer
from src.types import IPEvent, Location


@inject
async def handle(  # type:ignore[no-any-unimported]
    event: IPEvent,
    redis: Redis = Provide[Container.redis],
    ring_buffer: IRingBuffer[dict[str, Any]] = Provide[Container.ring_buffer],
    ipinfo_handler: AsyncHandler = Provide[Container.ipinfo_handler],
) -> None:
    _location: str | bytes | None = await redis.hget(  # type:ignore[misc]
        config.LOCATIONS_HASHSET_NAME,
        event.ip,
    )
    if _location is None:
        details = await ipinfo_handler.getDetails(
            event.ip,
            timeout=config.IPINFO_TIMEOUT,
        )
        location = str(getattr(details, "city", config.IPINFO_DEFAULT_CITY))
        await redis.hset(
            config.LOCATIONS_HASHSET_NAME, event.ip, location
        )  # type:ignore[misc]
    else:
        location = _location.decode() if isinstance(_location, bytes) else _location

    await ring_buffer.put(
        asdict(
            Location(
                location=location,
                timestamp=event.timestamp,
            )
        )
    )
