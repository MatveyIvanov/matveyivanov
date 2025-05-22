from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from config import settings
from utils.templates import templates

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"lines": settings.HOME},
    )


@router.get("/experience", response_class=HTMLResponse)
async def experience(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="experience.html",
        context={
            "timeline": [
                {
                    "direction": "right" if i % 2 == 0 else "left",
                    "place": item.place,
                    "from": item.from_,
                    "to": item.to_,
                    "description": item.description,
                }
                for i, item in enumerate(settings.EXPERIENCE, 0)
            ],
        },
    )


@router.get("/stack", response_class=HTMLResponse)
async def stack(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="stack.html",
        context={"stack": settings.STACK},
    )


@router.get("/python", response_class=HTMLResponse)
async def python(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="python.html",
        context={"libraries": settings.PYTHON},
    )


@router.get("/books", response_class=HTMLResponse)
async def books(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="books.html",
        context={
            "work_books": settings.WORK_BOOKS,
            "off_work_books": settings.OFF_WORK_BOOKS,
        },
    )


@router.get("/projects", response_class=HTMLResponse)
async def projects(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={"projects": settings.PROJECTS},
    )
