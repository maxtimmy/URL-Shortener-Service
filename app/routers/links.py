from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Link, ExpiredLinkHistory
from app.schemas import (
    LinkCreateRequest,
    LinkResponse,
    LinkUpdateRequest,
    LinkStatsResponse,
    MessageResponse,
    SearchResponse
)
from app.deps import get_current_user, require_user
from app.utils import generate_short_code, is_expired
from app.config import settings
from app.cache import get_cached_url, set_cached_url, delete_cached_url


router = APIRouter(tags=["links"])


@router.post("/links/shorten", response_model=LinkResponse)
def create_short_link(
    data: LinkCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if data.custom_alias:
        exists = db.query(Link).filter(Link.short_code == data.custom_alias).first()
        if exists:
            raise HTTPException(status_code=400, detail="Alias already exists")
        short_code = data.custom_alias
    else:
        short_code = generate_short_code()
        while db.query(Link).filter(Link.short_code == short_code).first():
            short_code = generate_short_code()

    link = Link(
        original_url=str(data.original_url),
        short_code=short_code,
        custom_alias=data.custom_alias,
        expires_at=data.expires_at,
        owner_id=user.id if user else None,
        is_guest=user is None
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return LinkResponse(
        original_url=link.original_url,
        short_code=link.short_code,
        short_url=f"{settings.BASE_URL}/{link.short_code}",
        created_at=link.created_at,
        expires_at=link.expires_at,
        is_guest=link.is_guest
    )


@router.get("/links/search", response_model=SearchResponse)
def search_by_original_url(original_url: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.original_url == original_url).first()
    if not link:
        return SearchResponse(found=False)

    return SearchResponse(
        found=True,
        short_code=link.short_code,
        short_url=f"{settings.BASE_URL}/{link.short_code}"
    )


@router.get("/links/{short_code}/stats", response_model=LinkStatsResponse)
def get_stats(short_code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    return LinkStatsResponse(
        original_url=link.original_url,
        short_code=link.short_code,
        created_at=link.created_at,
        click_count=link.click_count,
        last_used_at=link.last_used_at,
        expires_at=link.expires_at
    )


@router.put("/links/{short_code}", response_model=LinkResponse)
def update_link(
    short_code: str,
    data: LinkUpdateRequest,
    db: Session = Depends(get_db),
    user=Depends(require_user)
):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if data.original_url:
        link.original_url = str(data.original_url)

    if data.new_short_code and data.new_short_code != link.short_code:
        exists = db.query(Link).filter(Link.short_code == data.new_short_code).first()
        if exists:
            raise HTTPException(status_code=400, detail="New short code already exists")
        old_code = link.short_code
        link.short_code = data.new_short_code
        delete_cached_url(old_code)

    db.commit()
    db.refresh(link)
    delete_cached_url(link.short_code)

    return LinkResponse(
        original_url=link.original_url,
        short_code=link.short_code,
        short_url=f"{settings.BASE_URL}/{link.short_code}",
        created_at=link.created_at,
        expires_at=link.expires_at,
        is_guest=link.is_guest
    )


@router.delete("/links/{short_code}", response_model=MessageResponse)
def delete_link(
    short_code: str,
    db: Session = Depends(get_db),
    user=Depends(require_user)
):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    delete_cached_url(short_code)
    db.delete(link)
    db.commit()

    return MessageResponse(message="Link deleted")


@router.get("/links/expired/history")
def expired_history(db: Session = Depends(get_db)):
    rows = db.query(ExpiredLinkHistory).order_by(ExpiredLinkHistory.expired_at.desc()).all()
    return rows


@router.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    cached = get_cached_url(short_code)
    if cached:
        link = db.query(Link).filter(Link.short_code == short_code).first()
        if link:
            link.click_count += 1
            link.last_used_at = datetime.utcnow()
            db.commit()
        return RedirectResponse(url=cached, status_code=307)

    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if is_expired(link.expires_at):
        db.add(
            ExpiredLinkHistory(
                original_url=link.original_url,
                short_code=link.short_code,
                click_count=link.click_count,
                created_at=link.created_at,
                last_used_at=link.last_used_at,
                expired_at=datetime.utcnow()
            )
        )
        db.delete(link)
        db.commit()
        raise HTTPException(status_code=404, detail="Link expired")

    link.click_count += 1
    link.last_used_at = datetime.utcnow()
    db.commit()

    if link.click_count >= 3:
        set_cached_url(short_code, link.original_url)

    return RedirectResponse(url=link.original_url, status_code=307)