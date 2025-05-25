import asyncio
import json

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from redis.asyncio import Redis
from sse_starlette.sse import EventSourceResponse

from config.di import Container
from utils.contexts import no_exc

router = APIRouter(prefix="/visitors", tags=["visitors"])

MESSAGE_STREAM_DELAY = 1  # second
VISITORS_COUNTER_KEY = "VISITORS_COUNTER"


@router.get("")
@inject
async def count(redis: Redis = Depends(Provide[Container.redis])):
    count = await redis.get(VISITORS_COUNTER_KEY)
    count = int(count) if count else 0
    return {"count": count}


@router.get("/stream")
@inject
async def stream(
    request: Request,
    background_tasks: BackgroundTasks,
    redis: Redis = Depends(Provide[Container.redis]),
):
    async def update(increment: int = 0) -> int:
        pipe = redis.pipeline(transaction=True)
        await pipe.incr(VISITORS_COUNTER_KEY, increment)
        await pipe.get(VISITORS_COUNTER_KEY)
        results = await pipe.execute()

        count = int(results[1] or 0)

        if count < 0:
            await redis.set(VISITORS_COUNTER_KEY, 0)
            return 0

        return count

    async def generator():
        with no_exc():
            count = await update(+1)

            yield {"event": "message", "data": json.dumps({"count": count})}
            while True:
                if await request.is_disconnected():
                    break

                count = await update()

                yield {"event": "message", "data": json.dumps({"count": count})}

                await asyncio.sleep(MESSAGE_STREAM_DELAY)

    async def cleanup():
        await update(-1)

    background_tasks.add_task(cleanup)

    return EventSourceResponse(generator(), background=background_tasks)
