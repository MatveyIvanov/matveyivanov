import asyncio
import json
import re
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import cast

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request, Response
from sse_starlette.sse import EventSourceResponse

from config import settings
from config.di import Container
from schemas.changelog import Changelog, ChangelogItem, ChangelogItemDict
from schemas.webhooks import GitHubCreateHook
from services.interfaces import IHashAndCompare, IRingBuffer

router = APIRouter(prefix="/changelog", tags=["changelog"])


@router.get("", response_model=Changelog)
@inject
async def changelog(
    ring_buffer: IRingBuffer[ChangelogItemDict] = Depends(
        Provide[Container.changelog_ring_buffer]
    ),
) -> Changelog:
    items = await ring_buffer.all()
    return Changelog(
        updates=[
            ChangelogItem(
                id=item["id"],
                title=item["title"],
                type=item["type"],
                description=item["description"],
                version=item["version"],
                date=item["date"],
            )
            for item in items
        ]
    )


@router.get("/stream")
@inject
async def stream(
    request: Request,
    ring_buffer: IRingBuffer[ChangelogItemDict] = Depends(
        Provide[Container.changelog_ring_buffer]
    ),
) -> EventSourceResponse:
    async def generator() -> AsyncGenerator[dict[str, str]]:
        while True:
            if await request.is_disconnected():
                break

            yield {
                "event": "message",
                "data": json.dumps({"updates": await ring_buffer.all()}),
            }

            await asyncio.sleep(settings.CHANGELOG_SSE_INTERVAL_SECONDS)

    return EventSourceResponse(generator())


@router.post("/webhook")
@inject
async def webhook(
    request: Request,
    hook: GitHubCreateHook,
    ring_buffer: IRingBuffer[ChangelogItemDict] = Depends(
        Provide[Container.changelog_ring_buffer]
    ),
    hash_n_compare: IHashAndCompare = Depends(
        Provide[Container.hash_n_compare_github_payload_on_create.provider]
    ),
) -> str:
    if "X-Hub-Signature-256" not in request.headers or not hash_n_compare(
        value=await request.body(),
        expected=request.headers["X-Hub-Signature-256"],
    ):
        return Response(  # type:ignore[return-value]
            "Unauthorized",
            status_code=401,
        )

    if hook.ref_type != "tag" or not re.match(settings.GITHUB_TAG_PATTERN, hook.ref):
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

    _ = await ring_buffer.put(
        cast(
            ChangelogItemDict,
            ChangelogItem(
                id=hook.ref,
                title=hook.ref,
                type="feature" if bugfix == "0" else "bugfix",
                description="",
                version=hook.ref,
                date=str(datetime.now().timestamp()),
            ).model_dump(),
        )
    )
    return "OK"
