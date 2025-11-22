from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="tebook/templates")


@router.get("/", response_class=HTMLResponse)
async def instructions(request: Request):
    """Сторінка з інструкціями для користувачів"""
    return templates.TemplateResponse("instructions.html", {
        "request": request
    })

