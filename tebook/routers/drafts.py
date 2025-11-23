from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Annotated
from ..dal import create_draft, get_draft, get_all_drafts, update_draft, delete_draft, duplicate_draft
from ..models import DraftCreate, DraftUpdate, User
from ..parser import parse_draft
from ..renderer import render_html
from ..routers.login_router import get_current_user, get_current_user_optional, get_current_teacher

router = APIRouter()
templates = Jinja2Templates(directory="tebook/templates")


@router.get("/", response_class=HTMLResponse)
async def list_drafts(request: Request, 
                     user: Annotated[User | None, Depends(get_current_user_optional)]):
    """Список всіх чернеток (доступний всім)"""
    drafts = get_all_drafts()
    is_teacher = user and user.role in ["teacher", "admin"] if user else False
    return templates.TemplateResponse("drafts_list.html", {
        "request": request,
        "drafts": drafts,
        "user": user,
        "is_teacher": is_teacher
    })


@router.get("/new", response_class=HTMLResponse)
async def new_draft_form(request: Request, 
                        user: Annotated[User, Depends(get_current_teacher)]):
    """Форма створення нової чернетки (тільки для викладачів)"""
    return templates.TemplateResponse("draft_edit.html", {
        "request": request,
        "draft": None,
        "action": "Створити",
        "user": user
    })


@router.get("/{draft_id}", response_class=HTMLResponse)
async def view_draft(request: Request, draft_id: int,
                    user: Annotated[User | None, Depends(get_current_user_optional)]):
    """Перегляд чернетки (доступний всім)"""
    draft = get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Чернетку не знайдено")
    
    is_teacher = user and user.role in ["teacher", "admin"] if user else False
    return templates.TemplateResponse("draft_view.html", {
        "request": request,
        "draft": draft,
        "user": user,
        "is_teacher": is_teacher
    })


@router.get("/{draft_id}/edit", response_class=HTMLResponse)
async def edit_draft_form(request: Request, draft_id: int,
                         user: Annotated[User, Depends(get_current_teacher)]):
    """Форма редагування чернетки (тільки для викладачів)"""
    draft = get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Чернетку не знайдено")
    
    return templates.TemplateResponse("draft_edit.html", {
        "request": request,
        "draft": draft,
        "action": "Редагувати",
        "user": user
    })


@router.post("/")
async def create_draft_post(request: Request,
                           user: Annotated[User, Depends(get_current_teacher)],
                           title: str = Form(...), 
                           content: str = Form(...), 
                           language: str = Form("python")):
    """Створює нову чернетку (тільки для викладачів)"""
    form_data = await request.form()
    doc_types = form_data.getlist("doc_types")
    view_modes_list = form_data.getlist("view_modes")
    
    if not doc_types:
        raise HTTPException(status_code=400, detail="Оберіть хоча б один тип документа")
    
    # Якщо view_modes не обрані, використовуємо всі за замовчуванням
    view_modes_str = ",".join(view_modes_list) if view_modes_list else None
    
    valid_formats = ["html-stu", "html-tut", "md"]
    created_drafts = []

    format_names = {
        "html-stu": "HTML (студентський)",
        "html-tut": "HTML (викладацький)",
        "md": "Markdown"
    }

    for i, doc_type in enumerate(doc_types):
        if doc_type in valid_formats:
            if len(doc_types) > 1:
                format_name = format_names.get(doc_type, doc_type)
                draft_title = f"{title} ({format_name})"
            else:
                draft_title = title
            
            draft = create_draft(draft_title, content, language, doc_type, view_modes_str)
            created_drafts.append(draft)
    
    if not created_drafts:
        raise HTTPException(status_code=400, detail="Невірний формат документа")

    return RedirectResponse(url=f"/drafts/{created_drafts[0].id}", status_code=303)


@router.post("/{draft_id}/duplicate")
async def duplicate_draft_post(draft_id: int,
                              user: Annotated[User, Depends(get_current_teacher)],
                              new_doc_type: str = Form(...)):
    """Дублює чернетку, можливо змінюючи тип документа (тільки для викладачів)"""
    original = get_draft(draft_id)
    if not original:
        raise HTTPException(status_code=404, detail="Чернетку не знайдено")

    if new_doc_type == original.doc_type:
        raise HTTPException(status_code=400, detail="Оберіть інший формат для дублювання")

    valid_formats = ["html-stu", "html-tut", "md"]
    if new_doc_type not in valid_formats:
        raise HTTPException(status_code=400, detail="Невірний формат документа")
    
    new_draft = duplicate_draft(draft_id, new_doc_type)
    if not new_draft:
        raise HTTPException(status_code=404, detail="Чернетку не знайдено")
    return RedirectResponse(url=f"/drafts/{new_draft.id}", status_code=303)


@router.post("/{draft_id}/delete")
async def delete_draft_post(draft_id: int,
                           user: Annotated[User, Depends(get_current_teacher)]):
    """Видаляє чернетку (тільки для викладачів)"""
    if not delete_draft(draft_id):
        raise HTTPException(status_code=404, detail="Чернетку не знайдено")
    return RedirectResponse(url="/drafts/", status_code=303)


@router.post("/{draft_id}")
async def update_draft_post(request: Request, draft_id: int,
                           user: Annotated[User, Depends(get_current_teacher)],
                           title: str = Form(...), 
                           content: str = Form(...),
                           language: str = Form("python")):
    """Оновлює чернетку (тільки для викладачів)"""
    original = get_draft(draft_id)
    if not original:
        raise HTTPException(status_code=404, detail="Чернетку не знайдено")

    form_data = await request.form()
    doc_types = form_data.getlist("doc_types")
    view_modes_list = form_data.getlist("view_modes")
    
    if not doc_types:
        raise HTTPException(status_code=400, detail="Оберіть хоча б один тип документа")
    
    # Якщо view_modes не обрані, використовуємо всі за замовчуванням
    view_modes_str = ",".join(view_modes_list) if view_modes_list else None
    
    valid_formats = ["html-stu", "html-tut", "md"]
    current_format = original.doc_type

    if current_format in doc_types:
        draft = update_draft(draft_id, title, content, language, None, view_modes_str)
        if not draft:
            raise HTTPException(status_code=404, detail="Чернетку не знайдено")

        for doc_type in doc_types:
            if doc_type in valid_formats and doc_type != current_format:
                duplicate_draft(draft_id, doc_type)
    else:
        new_format = doc_types[0] if doc_types else current_format
        draft = update_draft(draft_id, title, content, language, new_format, view_modes_str)
        if not draft:
            raise HTTPException(status_code=404, detail="Чернетку не знайдено")

        for doc_type in doc_types[1:]:
            if doc_type in valid_formats:
                duplicate_draft(draft_id, doc_type)
    
    return RedirectResponse(url=f"/drafts/{draft.id}", status_code=303)