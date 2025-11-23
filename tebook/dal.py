import datetime as dt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import List, Optional
from .models import Draft, User, Base

DATA_BASE = "tebook.db"
engine = create_engine(f"sqlite:///{DATA_BASE}", echo=False)


def init_db():
    """Ініціалізує базу даних, створюючи всі таблиці"""
    Base.metadata.create_all(engine)


# CRUD операції для чернеток
def create_draft(title: str, content: str, language: str = "python", doc_type: str = "html-stu", view_modes: Optional[str] = None) -> Draft:
    """Створює нову чернетку"""
    now = dt.datetime.now().isoformat()
    draft = Draft(
        title=title,
        content=content,
        language=language,
        doc_type=doc_type,
        view_modes=view_modes,
        created_at=now,
        updated_at=now
    )
    with Session(engine) as db:
        db.add(draft)
        db.commit()
        db.refresh(draft)
    return draft


def get_draft(draft_id: int) -> Optional[Draft]:
    """Отримує чернетку за ID"""
    with Session(engine) as db:
        return db.get(Draft, draft_id)


def get_all_drafts() -> List[Draft]:
    """Отримує всі чернетки"""
    with Session(engine) as db:
        return db.query(Draft).all()


def update_draft(draft_id: int, title: Optional[str] = None, content: Optional[str] = None,
                 language: Optional[str] = None, doc_type: Optional[str] = None, view_modes: Optional[str] = None) -> Optional[Draft]:
    """Оновлює чернетку"""
    with Session(engine) as db:
        draft = db.get(Draft, draft_id)
        if not draft:
            return None
        
        if title is not None:
            draft.title = title
        if content is not None:
            draft.content = content
        if language is not None:
            draft.language = language
        if doc_type is not None:
            draft.doc_type = doc_type
        if view_modes is not None:
            draft.view_modes = view_modes
        
        draft.updated_at = dt.datetime.now().isoformat()
        db.commit()
        db.refresh(draft)
        return draft


def delete_draft(draft_id: int) -> bool:
    """Видаляє чернетку"""
    with Session(engine) as db:
        draft = db.get(Draft, draft_id)
        if not draft:
            return False
        db.delete(draft)
        db.commit()
        return True


def duplicate_draft(draft_id: int, new_doc_type: str = None) -> Optional[Draft]:
    """Дублює чернетку, можливо змінюючи тип документа"""
    original = get_draft(draft_id)
    if not original:
        return None
    
    new_doc_type = new_doc_type if new_doc_type else original.doc_type

    format_names = {
        "html-stu": "HTML (студентський)",
        "html-tut": "HTML (викладацький)",
        "md": "Markdown"
    }
    format_name = format_names.get(new_doc_type, new_doc_type)

    if "(копія" in original.title:
        new_title = f"{original.title.split('(копія')[0].strip()} (копія - {format_name})"
    else:
        new_title = f"{original.title} (копія - {format_name})"
    
    return create_draft(
        title=new_title,
        content=original.content,
        language=original.language,
        doc_type=new_doc_type,
        view_modes=original.view_modes
    )