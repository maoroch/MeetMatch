import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Profile, TelegramLink


def issue_code(db: Session, user_id: str) -> str:
    db.query(TelegramLink).filter(TelegramLink.user_id == user_id).delete()
    raw = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(8))
    link = TelegramLink(user_id=user_id, code_hash=hashlib.sha256(raw.encode()).hexdigest(), code_prefix=raw[:4], expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10), attempts=0)
    db.add(link)
    db.commit()
    return f"{raw[:4]}-{raw[4:]}"


def confirm_code(db: Session, code: str, telegram_user_id: str) -> None:
    normalized = code.replace("-", "").upper()
    if len(normalized) != 8:
        raise HTTPException(status_code=400, detail="Invalid or expired link code")
    digest = hashlib.sha256(normalized.encode()).hexdigest()
    link = db.scalar(select(TelegramLink).where(TelegramLink.code_hash == digest))
    if link is None:
        prefix = normalized[:4]
        pending = db.scalar(select(TelegramLink).where(TelegramLink.code_prefix == prefix)) if len(normalized) == 8 else None
        if pending is not None:
            pending.attempts += 1
            if pending.attempts >= 5:
                db.delete(pending)
            db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired link code")
    if link.attempts >= 5 or link.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        db.delete(link)
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired link code")
    profile = db.scalar(select(Profile).where(Profile.user_id == link.user_id))
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile.telegram_user_id = telegram_user_id
    db.delete(link)
    db.commit()
