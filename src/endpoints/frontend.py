from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config import settings
from utils.routing import APIRouter
from utils.uri import build_absolute_uri


def url_for(static_url: str, path: str, *args: Any, **kwargs: Any):
    return build_absolute_uri(f"{static_url.strip('/')}/{path.strip('/')}")


router = APIRouter()
templates = Jinja2Templates(directory="templates")
templates.env.globals["url_for"] = url_for


@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
    )
