from typing import Tuple

from endpoints.frontend import router as frontend_router
from utils.routing import APIRouter


def get_routers() -> Tuple[APIRouter]:
    return (frontend_router,)  # type: ignore[return-value]
