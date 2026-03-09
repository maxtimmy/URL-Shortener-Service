from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    links: Mapped[list["Link"]] = relationship("Link", back_populates="owner")


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    original_url: Mapped[str] = mapped_column(Text)
    short_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    custom_alias: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_guest: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    owner: Mapped["User | None"] = relationship("User", back_populates="links")


class ExpiredLinkHistory(Base):
    __tablename__ = "expired_link_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    original_url: Mapped[str] = mapped_column(Text)
    short_code: Mapped[str] = mapped_column(String(64))
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expired_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)