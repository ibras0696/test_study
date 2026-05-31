from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core import Base
from core.models.posts import Post


class User(Base):
    __tablename__ = "users"

    # mapped_column + Mapped[type] — стиль SQLAlchemy 2.0.
    # Тип в Mapped[...] определяет nullable:
    #   Mapped[str]        → NOT NULL
    #   Mapped[str | None] → nullable

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)

    # server_default — дата ставится на стороне БД (надёжнее для многих реплик)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now())

    # Relationship: один пользователь → много постов
    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan",  # удаление юзера удаляет его посты
        lazy="selectin",               # подгружать в отдельном SELECT (safe for async)
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"

