from fastapi import Request
from fastapi.responses import HTMLResponse

from utils.templates import templates
from utils.routing import APIRouter


router = APIRouter()


@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
    )
