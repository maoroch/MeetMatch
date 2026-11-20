from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Feedback
from app.schemas import FeedbackInput
from app.security import Actor, get_optional_user

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("")
def submit_feedback(
    payload: FeedbackInput,
    actor: Actor | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    user_id = actor.user_id if actor else "anonymous-query"
    existing = db.scalar(
        select(Feedback).where(
            Feedback.user_id == user_id,
            Feedback.match_id == payload.match_id,
        )
    )
    if existing is not None:
        existing.action = payload.action
    else:
        db.add(Feedback(user_id=user_id, match_id=payload.match_id, action=payload.action))
    db.commit()
    return {"ok": True}


@router.delete("")
def clear_feedback(
    actor: Actor | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    user_id = actor.user_id if actor else "anonymous-query"
    db.execute(delete(Feedback).where(Feedback.user_id == user_id))
    db.commit()
    return {"ok": True}
