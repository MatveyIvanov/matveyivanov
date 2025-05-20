from typing import Tuple

from fastapi import APIRouter

from endpoints.changelog import router as changelog_router
from endpoints.frontend import router as frontend_router
from endpoints.locations import router as locations_router
from endpoints.visitors import router as visitors_router


def get_routers() -> Tuple[APIRouter, ...]:
    return (
        frontend_router,
        changelog_router,
        locations_router,
        visitors_router,
    )
