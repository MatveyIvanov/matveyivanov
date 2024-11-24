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


@router.get("/experience", response_class=HTMLResponse)
async def experience(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="experience.html",
        context={
            "timeline": [
                {
                    "direction": "right",
                    "place": "SIXHANDS",
                    "from": "2024",
                    "to": "present",
                    "description": "Middle Python Backend Developer",
                },
                {
                    "direction": "left",
                    "place": "SIXHANDS",
                    "from": "2022",
                    "to": "2024",
                    "description": "Junior Python Backend Developer",
                },
                {
                    "direction": "right",
                    "place": "LETI",
                    "from": "2019",
                    "to": "2023",
                    "description": "University degree",
                },
            ]
        },
    )


@router.get("/stack", response_class=HTMLResponse)
async def stack(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="stack.html",
        context={
            "stack": [
                {"name": "Python", "progress": "60"},
                {"name": "Python", "progress": "60"},
                {"name": "Python", "progress": "60"},
                {"name": "Python", "progress": "60"},
                {"name": "Python", "progress": "60"},
                {"name": "Python", "progress": "60"},
                {"name": "Python", "progress": "60"},
            ]
        },
    )


@router.get("/python", response_class=HTMLResponse)
async def python(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="python.html",
    )
