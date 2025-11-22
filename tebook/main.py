from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from .routers import drafts, presentations, login_router, instructions
from .dal import init_db

app = FastAPI(title="TeBook", description="Система для створення презентацій з чернеток")

app.mount("/static", StaticFiles(directory="tebook/static"), name="static")

app.include_router(drafts.router, prefix="/drafts", tags=["drafts"])
app.include_router(presentations.router, prefix="/presentations", tags=["presentations"])
app.include_router(login_router.router, prefix="/login", tags=["login"])
app.include_router(instructions.router, prefix="/instructions", tags=["instructions"])

@app.get("/")
async def root():
    """Головна сторінка - перенаправлення на список чернеток"""
    return RedirectResponse(url="/drafts/")

@app.on_event("startup")
async def startup_event():
    """Ініціалізація БД при запуску"""
    init_db()