import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

import endpoints
from config import settings
from utils.app import FastAPI
from utils.exceptions import (
    CustomException,
    http_exception_handler,
    internal_exception_handler,
    request_validation_exception_handler,
)
from utils.logging import get_config
from utils.middleware import LoggingMiddleware, TranslationMiddleware

logging.config.dictConfig(  # type: ignore[attr-defined]
    get_config(settings.LOGGING_PATH)
)


__app = FastAPI(
    debug=True,
    exception_handlers={
        CustomException: http_exception_handler,
        HTTPException: http_exception_handler,
        RequestValidationError: request_validation_exception_handler,
        HTTP_500_INTERNAL_SERVER_ERROR: internal_exception_handler,
    },
)
for router in endpoints.get_routers():
    __app.include_router(router, tags=router.tags)

handlers_to_apply = {}
for exception, handler in __app.exception_handlers.items():
    handlers_to_apply[exception] = handler

__app.mount(
    settings.STATIC_URL,
    StaticFiles(directory="static"),
    name="static",
)
__app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["127.0.0.1", "localhost", "matveyivanov.tech"],
)
__app.add_middleware(TranslationMiddleware)


@__app.middleware("http")
async def logging_middleware(request: Request, call_next):
    return await LoggingMiddleware()(request, call_next)


# custom exception handlers do not work w/o this
# because of versioned fastapi
for sub_app in __app.routes:
    if hasattr(sub_app.app, "add_exception_handler"):
        for exception, handler in handlers_to_apply.items():
            sub_app.app.add_exception_handler(exception, handler)


def get_fastapi_app() -> FastAPI:
    return __app
