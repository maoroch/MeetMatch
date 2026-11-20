from typing import Any
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.matching import MatchingIndex
from app.models import Feedback
from app.schemas import OrganizerStatsResponse

router = APIRouter(prefix="/api/organizer", tags=["organizer"])


@router.get("/stats", response_model=OrganizerStatsResponse)
def get_organizer_stats(
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rows = db.scalars(select(Feedback)).all()
    met_count = sum(1 for r in rows if r.action in ("like", "met"))
    not_fit_count = sum(1 for r in rows if r.action in ("dislike", "not_fit"))
    index: MatchingIndex = request.app.state.matching_index
    return index.hall_analytics({"met": met_count, "not_fit": not_fit_count})
