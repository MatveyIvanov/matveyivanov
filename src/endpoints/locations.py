import asyncio
import json
import pickle

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from redis.asyncio import Redis
from sse_starlette.sse import EventSourceResponse

from config.di import Container
from schemas.locations import Location, Locations

router = APIRouter(prefix="/api/v1/locations")  # FIXME: вынести префикс апи выше

MESSAGE_STREAM_DELAY = 1  # second
LOCATIONS_KEY = "LOCATIONS"


@router.get("", response_model=Locations)
async def locations(redis: Redis = Depends(Provide[Container.redis])):
    locations = await redis.get(LOCATIONS_KEY)
    locations = pickle.loads(locations) if locations else []
    return {"locations": locations}


@router.get("/stream")
async def stream(request: Request, redis: Redis = Depends(Provide[Container.redis])):
    async def generator():
        while True:
            if await request.is_disconnected():
                break

            locations = await redis.get(LOCATIONS_KEY)
            locations = pickle.loads(locations) if locations else []

            yield {"event": "message", "data": json.dumps({"locations": locations})}

            await asyncio.sleep(MESSAGE_STREAM_DELAY)

    return EventSourceResponse(generator())
