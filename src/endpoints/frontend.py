from fastapi import Request
from fastapi.responses import HTMLResponse

from utils.routing import APIRouter
from utils.templates import templates

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
                {"name": "Python", "progress": "20%"},
                {"name": "Python", "progress": "45%"},
                {"name": "Python", "progress": "55%"},
                {"name": "Python", "progress": "75%"},
                {"name": "Python", "progress": "80%"},
                {"name": "Python", "progress": "60%"},
                {"name": "Python", "progress": "60%"},
            ]
        },
    )


@router.get("/python", response_class=HTMLResponse)
async def python(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="python.html",
        context={
            "libraries": [
                {"name": "Django", "progress": "80%"},
                {"name": "Django", "progress": "20%"},
                {"name": "Django", "progress": "80%"},
                {"name": "Django", "progress": "20%"},
                {"name": "Django", "progress": "80%"},
                {"name": "Django", "progress": "20%"},
                {"name": "Django", "progress": "80%"},
                {"name": "Django", "progress": "20%"},
            ]
        },
    )


@router.get("/books", response_class=HTMLResponse)
async def books(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="books.html",
        context={"books": [{"name": "Книга"}, {"name": "Kniga", "url": "url"}]},
    )


@router.get("/projects", response_class=HTMLResponse)
async def books(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={
            "projects": [
                {
                    "name": "Книга",
                    "description": "some long sentence some long sentence some long sentence some long sentence some long sentence some long sentence ",
                    "url": "",
                },
                {"name": "Книга", "description": "", "url": ""},
            ]
        },
    )
