import asyncio
import json

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from redis.asyncio import Redis
from sse_starlette.sse import EventSourceResponse

from config.di import Container

router = APIRouter(prefix="/api/v1/visitors")  # FIXME: вынести префикс апи выше

MESSAGE_STREAM_DELAY = 1  # second
VISITORS_COUNTER_KEY = "VISITORS_COUNTER"


@inject
@router.get("")
async def count(redis: Redis = Depends(Provide[Container.redis])):
    count = await redis.get(VISITORS_COUNTER_KEY)
    count = int(count) if count else 0
    return {"count": count}


@inject
@router.get("/stream")
async def stream(request: Request, redis: Redis = Depends(Provide[Container.redis])):
    async def update(increment: int = 0) -> int:
        pipe = redis.pipeline(transaction=True)
        await pipe.incr(VISITORS_COUNTER_KEY, increment)
        await pipe.get(VISITORS_COUNTER_KEY)
        results = await pipe.execute()

        count = int(results[1]) if results[1] is not None else 0

        if count < 0:
            await redis.set(VISITORS_COUNTER_KEY, 0)
            return 0

        return count

    async def generator():
        count = await update(+1)

        try:
            yield {"event": "message", "data": json.dumps({"count": count})}
            while True:
                if await request.is_disconnected():
                    break

                count = await update()

                yield {"event": "message", "data": json.dumps({"count": count})}

                await asyncio.sleep(MESSAGE_STREAM_DELAY)
        finally:
            await update(-1)

    return EventSourceResponse(generator())
