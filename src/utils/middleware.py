import logging
from typing import Any

from fastapi import FastAPI
from starlette.types import Receive, Scope, Send

requests_logger = logging.getLogger("requests")


def headers_from_scope(scope: Scope) -> dict[str, Any]:
    return dict((k.decode().lower(), v.decode()) for k, v in scope.get("headers", {}))


class TranslationMiddleware:
    def __init__(self, app: FastAPI) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not scope["type"] == "http":
            await self._app(scope, receive, send)

        headers = self._get_headers(scope)
        self._activate_translation(headers)

        await self._app(scope, receive, send)

    def _get_headers(self, scope: Scope) -> dict[str, Any]:
        return headers_from_scope(scope)

    def _activate_translation(self, headers: dict[str, Any]) -> None:
        from config.i18n import activate_translation

        activate_translation(headers.get("accept-language", "unknown"))
