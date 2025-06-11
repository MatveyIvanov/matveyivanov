import logging
from typing import Any

from starlette.types import Scope

requests_logger = logging.getLogger("requests")


def headers_from_scope(scope: Scope) -> dict[str, Any]:
    return dict((k.decode().lower(), v.decode()) for k, v in scope.get("headers", {}))
