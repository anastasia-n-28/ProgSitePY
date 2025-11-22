from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..dal import get_draft
from ..parser import parse_draft
from ..renderer import render_html, render_markdown

router = APIRouter()
templates = Jinja2Templates(directory="tebook/templates")


@router.get("/{draft_id}")
async def view_presentation(draft_id: int, view_mode: str = "slides"):
    """
    Перегляд презентації
    
    Args:
        draft_id: ID чернетки
        view_mode: Режим відображення 
            - "slides" (слайди з навігацією)
            - "document" (документ з блоків, з'являються по кліку)
            - "full-document" (повний документ, всі слайди відразу)
    """
    draft = get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Чернетку не знайдено")
    
    slides = parse_draft(draft.content)
    
    if draft.doc_type == "md":
        content = render_markdown(slides)
        return HTMLResponse(content=content)
    else:
        content = render_html(slides, draft.language, draft.doc_type, view_mode)
        return HTMLResponse(content=content)


@router.get("/{draft_id}/export")
async def export_presentation(draft_id: int, format: str = "html"):
    """Експорт презентації у різних форматах"""
    draft = get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Чернетку не знайдено")
    
    slides = parse_draft(draft.content)
    
    if format == "md" or draft.doc_type == "md":
        content = render_markdown(slides)
        from fastapi.responses import Response
        return Response(content=content, media_type="text/markdown",
                      headers={"Content-Disposition": f'attachment; filename="presentation_{draft_id}.md"'})
    else:
        content = render_html(slides, draft.language, draft.doc_type)
        return HTMLResponse(content=content)