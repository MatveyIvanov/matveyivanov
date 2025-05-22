import asyncio
import json
from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from config.di import Container
from schemas.locations import IPEvent, Locations
from services.interfaces import IRingBuffer

router = APIRouter(prefix="/locations", tags=["locations"])

MESSAGE_STREAM_DELAY = 1  # second
LOCATIONS_KEY = "LOCATIONS"


@router.get("", response_model=Locations)
@inject
async def locations(
    request: Request,
    ring_buffer: IRingBuffer[dict] = Depends(Provide[Container.locations_ring_buffer]),
    queue=Depends(Provide[Container.ymq_locations_queue]),
):
    if request.client:
        queue.send_message(
            MessageBody=json.dumps(
                IPEvent(
                    ip=request.client.host,
                    timestamp=str(datetime.now().timestamp()),
                ).model_dump()
            ),
            MessageGroupId="default",
        )
    return {"locations": await ring_buffer.all()}


@router.get("/stream")
@inject
async def stream(
    request: Request,
    ring_buffer: IRingBuffer[dict] = Depends(Provide[Container.locations_ring_buffer]),
):
    async def generator():
        while True:
            if await request.is_disconnected():
                break

            yield {
                "event": "message",
                "data": json.dumps({"locations": await ring_buffer.all()}),
            }

            await asyncio.sleep(MESSAGE_STREAM_DELAY)

    return EventSourceResponse(generator())
