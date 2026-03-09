from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.config import settings
from app.db import SessionLocal
from app.models import Link, ExpiredLinkHistory


scheduler = BackgroundScheduler()


def cleanup_expired_links():
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()

        expired_links = db.query(Link).filter(
            (Link.expires_at.is_not(None)) & (Link.expires_at <= now)
        ).all()

        for link in expired_links:
            db.add(
                ExpiredLinkHistory(
                    original_url=link.original_url,
                    short_code=link.short_code,
                    click_count=link.click_count,
                    created_at=link.created_at,
                    last_used_at=link.last_used_at,
                    expired_at=now
                )
            )
            db.delete(link)

        threshold = now - timedelta(days=settings.DEFAULT_UNUSED_DAYS)

        unused_links = db.query(Link).filter(
            (Link.last_used_at.is_not(None)) &
            (Link.last_used_at <= threshold)
        ).all()

        for link in unused_links:
            db.add(
                ExpiredLinkHistory(
                    original_url=link.original_url,
                    short_code=link.short_code,
                    click_count=link.click_count,
                    created_at=link.created_at,
                    last_used_at=link.last_used_at,
                    expired_at=now
                )
            )
            db.delete(link)

        db.commit()
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(cleanup_expired_links, "interval", minutes=1)
    scheduler.start()