import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import TYPE_CHECKING, Any, TypeAlias

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

if TYPE_CHECKING:
    from types_boto3_sqs.service_resource import Queue
else:
    Queue: TypeAlias = Any

from config import settings
from config.di import Container
from schemas.locations import IPEvent, Location, LocationDict, Locations
from services.interfaces import IRingBuffer

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=Locations)
@inject
async def locations(
    request: Request,
    ring_buffer: IRingBuffer[LocationDict] = Depends(
        Provide[Container.locations_ring_buffer]
    ),
    queue: Queue = Depends(Provide[Container.sqs_locations_queue]),
) -> Locations:
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

    _locations = await ring_buffer.all()
    return Locations(
        locations=[
            Location(
                location=location["location"],
                timestamp=location["timestamp"],
            )
            for location in _locations
        ]
    )


@router.get("/stream")
@inject
async def stream(
    request: Request,
    ring_buffer: IRingBuffer[LocationDict] = Depends(
        Provide[Container.locations_ring_buffer]
    ),
) -> EventSourceResponse:
    async def generator() -> AsyncGenerator[dict[str, str]]:
        while True:
            if await request.is_disconnected():
                break

            yield {
                "event": "message",
                "data": json.dumps({"locations": await ring_buffer.all()}),
            }

            await asyncio.sleep(settings.LOCATIONS_SSE_INTERVAL_SECONDS)

    return EventSourceResponse(generator())
