import asyncio
import json
from collections.abc import AsyncGenerator, Iterable
from datetime import datetime
from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from config import settings
from config.di import Container
from schemas.locations import IPEvent, Locations
from services.interfaces import IRingBuffer

router = APIRouter(prefix="/locations", tags=["locations"])


def unique_dict[T: dict[str, Any]](objs: Iterable[T], *, key: str) -> list[T]:
    seen = set[Any]()
    result = list[T]()
    for obj in objs:
        if obj[key] not in seen:
            seen.add(obj[key])
            result.append(obj)
    return result


@router.get("", response_model=Locations)
@inject
async def locations(  # type:ignore[no-untyped-def]
    request: Request,
    ring_buffer: IRingBuffer[dict[str, Any]] = Depends(
        Provide[Container.locations_ring_buffer]
    ),
    queue=Depends(Provide[Container.sqs_locations_queue]),
) -> dict[str, Any]:
    if request.client and settings.PROD:
        queue.send_message(
            MessageBody=json.dumps(
                IPEvent(
                    ip=request.client.host,
                    timestamp=str(datetime.now().timestamp()),
                ).model_dump()
            ),
            MessageGroupId="default",
        )
    return {"locations": unique_dict(await ring_buffer.all(), key="location")}


@router.get("/stream")
@inject
async def stream(
    request: Request,
    ring_buffer: IRingBuffer[dict[str, Any]] = Depends(
        Provide[Container.locations_ring_buffer]
    ),
) -> EventSourceResponse:
    async def generator() -> AsyncGenerator[dict[str, str]]:
        while True:
            if await request.is_disconnected():
                break

            yield {
                "event": "message",
                "data": json.dumps(
                    {"locations": unique_dict(await ring_buffer.all(), key="location")}
                ),
            }

            await asyncio.sleep(settings.LOCATIONS_SSE_INTERVAL_SECONDS)

    return EventSourceResponse(generator())
