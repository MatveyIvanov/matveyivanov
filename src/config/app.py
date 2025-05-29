import logging

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

import endpoints
from config import di, settings
from utils.logging import get_config
from utils.middleware import TranslationMiddleware

logging.config.dictConfig(get_config())  # type: ignore[attr-defined]

container = di.Container()

__app = FastAPI(debug=settings.DEBUG)
__app.container = container
for router in endpoints.get_routers():
    __app.include_router(router, tags=router.tags)

__app.mount(
    settings.STATIC_URL,
    StaticFiles(directory=settings.STATIC_PATH),
    name="static",
)
__app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)
__app.add_middleware(TranslationMiddleware)
__app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=settings.PROXY_TRUSTED_HOSTS)


def get_fastapi_app() -> FastAPI:
    return __app
