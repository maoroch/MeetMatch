import json
import time
from typing import Annotated, Any
from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.matching import MatchingIndex
from app.models import Profile
from app.schemas import MatchResponse, ProfileInput
from app.security import Actor, get_optional_user, identify_actor

router = APIRouter(prefix="/api", tags=["matching"])


def _profile_dict(profile: Profile) -> dict[str, Any]:
    return {"id": profile.id, "user_id": profile.user_id, "name": profile.name, "role": profile.role, "goal": profile.goal, "skills": json.loads(profile.skills_json), "interests": json.loads(profile.interests_json), "experience_years": profile.experience_years, "bio": profile.bio, "email": profile.email, "phone": profile.phone, "age": profile.age, "city": profile.city}


@router.post("/match", response_model=MatchResponse)
def match_profiles(
    request: Request,
    payload: Annotated[ProfileInput | None, Body()] = None,
    db: Session = Depends(get_db),
    optional_actor: Actor | None = Depends(get_optional_user),
    x_bot_key: str | None = Header(default=None),
    x_telegram_user_id: str | None = Header(default=None),
) -> dict[str, Any]:
    started = time.perf_counter()
    if payload is not None:
        seeker = payload.model_dump()
        seeker["id"] = optional_actor.user_id if optional_actor else "anonymous-query"
    else:
        actor = identify_actor(optional_actor, x_bot_key, x_telegram_user_id)
        if actor is None:
            raise HTTPException(status_code=422, detail="A profile body is required")
        if actor.is_bot and x_telegram_user_id:
            profile = db.scalar(select(Profile).where(Profile.telegram_user_id == x_telegram_user_id))
        else:
            profile = db.scalar(select(Profile).where(Profile.user_id == actor.user_id))
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        seeker = _profile_dict(profile)
    index: MatchingIndex = request.app.state.matching_index
    matches, total, fallback = index.match(seeker, limit=5)
    elapsed = int((time.perf_counter() - started) * 1000)
    return {"matches": matches, "processing_ms": elapsed, "total_candidates": total, "fallback_used": fallback}
