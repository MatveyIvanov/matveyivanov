from typing import Tuple

from fastapi import APIRouter

from endpoints.changelog import router as changelog_router
from endpoints.frontend import router as frontend_router
from endpoints.locations import router as locations_router
from endpoints.visitors import router as visitors_router

api_router = APIRouter(prefix="/api/v1", tags=["API"])
api_router.include_router(changelog_router)
api_router.include_router(locations_router)
api_router.include_router(visitors_router)


def get_routers() -> Tuple[APIRouter, ...]:
    return (
        frontend_router,
        api_router,
    )
