from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from typing import Optional
from pydantic import BaseModel


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    
    username: Mapped[str] = mapped_column(String, primary_key=True)
    hashed_password: Mapped[bytes] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)


class Draft(Base):
    __tablename__ = "drafts"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(20), default="python")
    doc_type: Mapped[str] = mapped_column(String(20), default="html-stu")
    view_modes: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[str] = mapped_column(String(50))
    updated_at: Mapped[str] = mapped_column(String(50))


class DraftCreate(BaseModel):
    title: str
    content: str
    language: str = "python"
    doc_type: str = "html-stu"


class DraftUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    language: Optional[str] = None
    doc_type: Optional[str] = None