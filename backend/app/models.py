from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(128), unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(160))
    goal: Mapped[str] = mapped_column(String(40), index=True)
    skills_json: Mapped[str] = mapped_column(Text, default="[]")
    interests_json: Mapped[str] = mapped_column(Text, default="[]")
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    bio: Mapped[str] = mapped_column(Text, default="")
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    telegram_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    match_id: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (UniqueConstraint("user_id", "match_id", "action"),)


class TelegramLink(Base):
    __tablename__ = "telegram_links"
    user_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    code_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    code_prefix: Mapped[str] = mapped_column(String(4), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
