import logging
from typing import Dict

from starlette.types import Receive, Scope, Send

requests_logger = logging.getLogger("requests")


def headers_from_scope(scope: Scope) -> Dict:
    return dict((k.decode().lower(), v.decode()) for k, v in scope.get("headers", {}))


class TranslationMiddleware:
    def __init__(self, app):
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if not scope["type"] == "http":
            await self._app(scope, receive, send)

        headers = self._get_headers(scope)
        self._activate_translation(headers)

        await self._app(scope, receive, send)

    def _get_headers(self, scope: Scope) -> Dict:
        return headers_from_scope(scope)

    def _activate_translation(self, headers: Dict) -> None:
        from config.i18n import activate_translation

        activate_translation(headers.get("accept-language", None))
