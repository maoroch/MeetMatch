from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Feedback
from app.schemas import FeedbackInput
from app.security import Actor, require_user

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("")
def submit_feedback(payload: FeedbackInput, actor: Actor = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, bool]:
    db.add(Feedback(user_id=actor.user_id, match_id=payload.match_id, action=payload.action))
    db.commit()
    return {"ok": True}
