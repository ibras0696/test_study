from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base


class Post(Base):
    """Пост пользователя."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    views: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    published: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    # Связь много постов принадлежит 1 пользователю
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Сложная но обратная связь
    author: Mapped["User"] = relationship(
        back_populates="posts",
    )

    def __repr__(self) -> str:
        return f"Post(id={self.id}, title={self.title!r})"