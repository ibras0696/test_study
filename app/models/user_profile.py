from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base


class UserProfile(Base):
    """Профиль пользователя (1 к 1 с User)."""

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,  # 🔑 ключевой момент для 1:1
        nullable=False,
    )

    bio: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255))

    # user: Mapped["User"] = relationship(
    #     back_populates="profile",
    # )

    def __repr__(self):
        return f"id={self.id} user_id={self.user_id} bio:{self.bio} avatar_url: {self.avatar_url}"