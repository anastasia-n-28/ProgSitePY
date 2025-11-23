from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from fastapi import Depends
from ..models import User
from ..routers.login_router import get_current_user_optional

router = APIRouter()
templates = Jinja2Templates(directory="tebook/templates")


@router.get("/", response_class=HTMLResponse)
async def instructions(request: Request,
                      user: Annotated[User | None, Depends(get_current_user_optional)]):
    """Сторінка з інструкціями для користувачів"""
    return templates.TemplateResponse("instructions.html", {
        "request": request,
        "user": user
    })

