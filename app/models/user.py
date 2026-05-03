from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base


class User(Base):
    """Пользователь системы."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    test: Mapped[str] = mapped_column(
        String(100),
        default='test',
        nullable=True
    )

    new_int: Mapped[int] = mapped_column(
        Integer,
        default=1

    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )

    # profile: Mapped[Optional["UserProfile"]] = relationship(
    #     back_populates="user",
    #     uselist=False,  # 🔑 говорит ORM что это 1:1
    #     cascade="all, delete-orphan",
    # )

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"