import asyncio
import json
from collections.abc import AsyncGenerator

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from redis.asyncio import Redis
from sse_starlette.sse import EventSourceResponse

from config import settings
from config.di import Container
from schemas.visitors import Visitors
from utils.contexts import no_exc

router = APIRouter(prefix="/visitors", tags=["visitors"])


@router.get("", response_model=Visitors)
@inject
async def count(
    redis: Redis = Depends(Provide[Container.redis]),
) -> Visitors:
    count = await redis.get(settings.REDIS_VISITORS_COUNTER_KEY)
    count = int(count) if count else 0
    return Visitors(count=count)


@router.get("/stream")
@inject
async def stream(
    request: Request,
    background_tasks: BackgroundTasks,
    redis: Redis = Depends(Provide[Container.redis]),
) -> EventSourceResponse:
    async def update(increment: int = 0) -> int:
        pipe = redis.pipeline(transaction=True)
        await pipe.incr(settings.REDIS_VISITORS_COUNTER_KEY, increment)
        await pipe.get(settings.REDIS_VISITORS_COUNTER_KEY)
        results = await pipe.execute()

        count = int(results[1] or 0)

        if count < 0:
            await redis.set(settings.REDIS_VISITORS_COUNTER_KEY, 0)
            return 0

        return count

    async def generator() -> AsyncGenerator[dict[str, str]]:
        with no_exc():
            count = await update(+1)

            yield {"event": "message", "data": json.dumps({"count": count})}
            while True:
                if await request.is_disconnected():
                    break

                count = await update()

                yield {"event": "message", "data": json.dumps({"count": count})}

                await asyncio.sleep(settings.VISITORS_SSE_INTERVAL_SECONDS)

    async def cleanup() -> None:
        _ = await update(-1)

    background_tasks.add_task(cleanup)

    return EventSourceResponse(generator(), background=background_tasks)
