import asyncio
import json
import re
from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request, Response
from sse_starlette.sse import EventSourceResponse

from config.di import Container
from schemas.changelog import Changelog, ChangelogItem
from schemas.webhooks import GitHubCreateHook
from services.interfaces import IHashAndCompare, IRingBuffer

router = APIRouter(prefix="/changelog", tags=["changelog"])

MESSAGE_STREAM_DELAY = 1  # second
CHANGELOG_KEY = "CHANGELOG"
GITHUB_TAG_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


@router.get("", response_model=Changelog)
@inject
async def changelog(
    ring_buffer: IRingBuffer[dict] = Depends(Provide[Container.changelog_ring_buffer]),
):
    return {"updates": await ring_buffer.all()}


@router.get("/stream")
@inject
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


@router.post("/webhook")
@inject
async def webhook(
    request: Request,
    hook: GitHubCreateHook,
    ring_buffer: IRingBuffer[dict] = Depends(Provide[Container.changelog_ring_buffer]),
    hash_n_compare: IHashAndCompare = Depends(
        Provide[Container.hash_n_compare_github_payload_on_create.provider]
    ),
):
    if "X-Hub-Signature-256" not in request.headers or not hash_n_compare(
        value=await request.body(),
        expected=request.headers["X-Hub-Signature-256"],
    ):
        return Response("Unauthorized", status_code=401)

    if hook.ref_type != "tag" or not re.match(GITHUB_TAG_PATTERN, hook.ref):
        return "OK"

    latest_item = await ring_buffer.latest(n=1)
    last_major, last_feature, last_bugfix = "0", "0", "0"
    major, feature, bugfix = hook.ref.split(".")
    if latest_item:
        last_major, last_feature, last_bugfix = (
            latest_item[0].get("version", "0.0.0").split(".")
        )
    if major == last_major and feature == last_feature and bugfix == last_bugfix:
        return "OK"

    await ring_buffer.put(
        ChangelogItem(
            id=hook.ref,
            title=hook.ref,
            type="feature" if bugfix == "0" else "bugfix",
            description=hook.description or "No description provided :(",
            version=hook.ref,
            date=str(datetime.now().timestamp()),
        ).model_dump()
    )
    return "OK"
