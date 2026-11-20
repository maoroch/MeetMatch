from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TelegramCodeInput
from app.security import Actor, resolve_actor
from app.services.telegram import confirm_code, issue_code

router = APIRouter(prefix="/api/telegram", tags=["telegram"])


@router.post("/link")
def telegram_link(
    payload: TelegramCodeInput | None = None,
    actor: Actor = Depends(resolve_actor),
    db: Session = Depends(get_db),
    x_telegram_user_id: Annotated[str | None, Header()] = None,
) -> dict[str, object]:
    if actor.is_bot:
        if payload is None or not x_telegram_user_id:
            raise HTTPException(status_code=422, detail="Bot confirmation requires code and Telegram user ID")
        confirm_code(db, payload.code, x_telegram_user_id)
        return {"linked": True}
    code = issue_code(db, actor.user_id)
    return {"code": code, "expires_in": 600, "expires_in_seconds": 600}
