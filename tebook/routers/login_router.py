from fastapi.security import APIKeyCookie, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Request, Security, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from typing import Annotated
import bcrypt
import jwt
from ..models import User

SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()
templates = Jinja2Templates(directory="tebook/templates")
cookie_scheme = APIKeyCookie(name="access_token")


def get_authenticated_user(username: str, password: str) -> User | None:
    """
    Повертає перевіреного юзера або None
    """
    # Тимчасово: задані користувачі для тестування
    # Пізніше тут буде перевірка з БД
    users = {
        "admin": ("123456", "admin"),
        "teacher": ("123456", "teacher"),
        "student": ("123456", "student")
    }
    
    if username in users:
        stored_password, role = users[username]
        if password == stored_password:
            return User(
                username=username,
                hashed_password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()),
                role=role
            )
    return None


def get_current_user_optional(request: Request) -> User | None:
    """Отримує поточного користувача з токена (необов'язково)"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return User(username=payload.get("sub"), role=payload.get("role"))
    except Exception:
        return None


def get_current_user(token: Annotated[str, Security(cookie_scheme)] = None) -> User:
    """Отримує поточного користувача з токена (обов'язково)"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return User(username=payload.get("sub"), role=payload.get("role"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_teacher(user: Annotated[User, Depends(get_current_user)]) -> User:
    """Перевіряє, чи користувач є викладачем (teacher або admin)"""
    if user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Доступ заборонено. Тільки викладачі можуть створювати чернетки.")
    return user


@router.get("", response_class=HTMLResponse)
async def get_login(request: Request):
    """Форма входу"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("")
async def post_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Обробка входу та видача токена"""
    user = get_authenticated_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Створення токену
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    claims = {
        "sub": user.username,
        "role": user.role,
        "exp": datetime.utcnow() + expires_delta
    }
    access_token = jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)
    
    # Встановлення кукі
    response = RedirectResponse("/drafts/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@router.post("/logout")
async def logout():
    """Вихід з системи"""
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response