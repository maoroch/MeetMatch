import json
from typing import Any
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.matching import MatchingIndex
from app.models import Profile
from app.schemas import ProfileInput
from app.security import Actor, require_user

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _to_dict(profile: Profile) -> dict[str, Any]:
    return {
        "id": profile.id,
        "name": profile.name,
        "role": profile.role,
        "goal": profile.goal,
        "skills": json.loads(profile.skills_json),
        "interests": json.loads(profile.interests_json),
        "experience_years": profile.experience_years,
        "bio": profile.bio,
        "email": profile.email,
        "phone": profile.phone,
        "age": profile.age,
        "city": profile.city,
    }


@router.get("/me")
def get_profile(actor: Actor = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, object]:
    profile = db.scalar(select(Profile).where(Profile.user_id == actor.user_id))
    return {"profile": _to_dict(profile) if profile else None}


@router.put("/me")
def save_profile(payload: ProfileInput, request: Request, actor: Actor = Depends(require_user), db: Session = Depends(get_db)) -> dict[str, object]:
    profile = db.scalar(select(Profile).where(Profile.user_id == actor.user_id))
    fields = payload.model_dump()
    if profile is None:
        profile = Profile(id=f"user:{actor.user_id}", user_id=actor.user_id, name=fields["name"], role=fields["role"], goal=fields["goal"])
        db.add(profile)
    profile.name = fields["name"]
    profile.role = fields["role"]
    profile.goal = fields["goal"]
    profile.skills_json = json.dumps(fields["skills"], ensure_ascii=False)
    profile.interests_json = json.dumps(fields["interests"], ensure_ascii=False)
    profile.experience_years = fields["experience_years"]
    profile.bio = fields["bio"]
    if fields.get("email") is not None:
        profile.email = fields["email"]
    if fields.get("phone") is not None:
        profile.phone = fields["phone"]
    if fields.get("age") is not None:
        profile.age = fields["age"]
    if fields.get("city") is not None:
        profile.city = fields["city"]
    db.commit()
    db.refresh(profile)
    index: MatchingIndex = request.app.state.matching_index
    index.replace({"id": profile.id, "user_id": profile.user_id, **fields})
    return {"profile": _to_dict(profile)}
