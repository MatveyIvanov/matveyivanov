import asyncio
import json
import pickle
from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from redis.asyncio import Redis
from sse_starlette.sse import EventSourceResponse

from config.di import Container
from schemas.changelog import Changelog, ChangelogItem
from schemas.webhooks import GitHubCreateHook
from src.services.interfaces import IRingBuffer

router = APIRouter(prefix="/api/v1/changelog")  # FIXME: вынести префикс апи выше

MESSAGE_STREAM_DELAY = 1  # second
CHANGELOG_KEY = "CHANGELOG"


@inject
@router.get("", response_model=Changelog)
async def changelog(
    ring_buffer: IRingBuffer[dict] = Depends(Provide[Container.changelog_ring_buffer]),
):
    return {"updates": await ring_buffer.all()}


@inject
@router.get("/stream")
async def stream(
    request: Request,
    ring_buffer: IRingBuffer[dict] = Depends(Provide[Container.changelog_ring_buffer]),
):
    async def generator():
        while True:
            if await request.is_disconnected():
                break

            yield {
                "event": "message",
                "data": json.dumps({"updates": await ring_buffer.all()}),
            }

            await asyncio.sleep(MESSAGE_STREAM_DELAY)

    return EventSourceResponse(generator())


@inject
@router.post("/webhook")
async def webhook(
    hook: GitHubCreateHook,
    ring_buffer: IRingBuffer[dict] = Depends(Provide[Container.changelog_ring_buffer]),
):
    if hook.ref_type != "tag":
        return "OK"

    latest_item = await ring_buffer.latest(n=1)
    last_major, last_feature, last_bugfix = "0", "0", "0"
    major, feature, bugfix = hook.ref.split(".")
    if latest_item:
        last_major, last_feature, last_bugfix = (
            latest_item[0].get("version", "0.0.0").split(".")
        )

    item = ChangelogItem(
        id=hook.ref,
        title=hook.ref,
        type="release" if major != last_major or feature != last_feature else "bugfix",
        description=hook.description,
        version=hook.ref,
        date=datetime.now(),
    )
    await ring_buffer.put(item.model_dump())
    return "OK"
