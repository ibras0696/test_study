from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str | None] = mapped_column(Text)  # nullable — ок написать так
    published: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Внешний ключ
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Обратная ссылка
    author: Mapped["User"] = relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post id={self.id} title={self.title!r}>"
