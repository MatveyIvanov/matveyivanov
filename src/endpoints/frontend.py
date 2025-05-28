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
        name=settings.HTML_FOR_HOME,
        context=settings.TEMPLATE_CONTEXT_BASE | {"lines": settings.HOME},
    )


@router.get("/experience", response_class=HTMLResponse)
async def experience(request: Request):
    return templates.TemplateResponse(
        request=request,
        name=settings.HTML_FOR_EXPERIENCE,
        context=settings.TEMPLATE_CONTEXT_BASE
        | {
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
        name=settings.HTML_FOR_STACK,
        context=settings.TEMPLATE_CONTEXT_BASE | {"stack": settings.STACK},
    )


@router.get("/python", response_class=HTMLResponse)
async def python(request: Request):
    return templates.TemplateResponse(
        request=request,
        name=settings.HTML_FOR_PYTHON,
        context=settings.TEMPLATE_CONTEXT_BASE | {"libraries": settings.PYTHON},
    )


@router.get("/books", response_class=HTMLResponse)
async def books(request: Request):
    return templates.TemplateResponse(
        request=request,
        name=settings.HTML_FOR_BOOKS,
        context=settings.TEMPLATE_CONTEXT_BASE
        | {
            "work_books": settings.WORK_BOOKS,
            "off_work_books": settings.OFF_WORK_BOOKS,
        },
    )


@router.get("/projects", response_class=HTMLResponse)
async def projects(request: Request):
    return templates.TemplateResponse(
        request=request,
        name=settings.HTML_FOR_PROJECTS,
        context=settings.TEMPLATE_CONTEXT_BASE | {"projects": settings.PROJECTS},
    )
