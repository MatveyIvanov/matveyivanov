import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

import endpoints
from config import di, settings
from utils.exceptions import (
    CustomException,
    http_exception_handler,
    internal_exception_handler,
    request_validation_exception_handler,
)
from utils.logging import get_config
from utils.middleware import TranslationMiddleware

logging.config.dictConfig(get_config())  # type: ignore[attr-defined]

container = di.Container()

__app = FastAPI(
    debug=settings.DEBUG,
    exception_handlers={
        CustomException: http_exception_handler,
        HTTPException: http_exception_handler,
        RequestValidationError: request_validation_exception_handler,
        HTTP_500_INTERNAL_SERVER_ERROR: internal_exception_handler,
    },
)
__app.container = container
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


def get_fastapi_app() -> FastAPI:
    return __app
