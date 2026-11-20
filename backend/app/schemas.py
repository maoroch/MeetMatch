from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, AliasChoices

Goal = Literal[
    "find_job",
    "hire",
    "find_cofounder",
    "find_investor",
    "find_mentor",
    "offer_mentorship",
    "be_mentor",
    "exchange_experience",
]


class ProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(default="", max_length=120)
    role: str = Field(default="", max_length=160)
    goal: Goal
    skills: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("skills", "stack"),
        max_length=30,
    )
    interests: list[str] = Field(default_factory=list, max_length=30)
    experience_years: int = Field(
        default=0,
        validation_alias=AliasChoices("experience_years", "experience"),
        ge=0,
        le=60,
    )
    bio: str = Field(
        default="",
        validation_alias=AliasChoices("bio", "about"),
        max_length=1000,
    )
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=40)
    age: int | None = Field(default=None, ge=0, le=120)
    city: str | None = Field(default=None, max_length=120)
    exclude_ids: list[str] = Field(default_factory=list, max_length=100)
    preferred_slots: list[str] = Field(default_factory=list, max_length=20)


class MatchPerson(BaseModel):
    id: str
    name: str
    role: str
    score: int
    goal: str
    reason: str
    icebreaker: str
    available_slots: list[str] = Field(default_factory=list)
    suggested_slot: str = ""


class PartnerBooth(BaseModel):
    id: str
    name: str
    category: str
    location: str
    tags: list[str]
    reason: str
    match_score: int


class MatchResponse(BaseModel):
    matches: list[MatchPerson]
    processing_ms: int
    total_candidates: int
    fallback_used: bool
    recommended_booths: list[PartnerBooth] = Field(default_factory=list)


class ProfileResponse(BaseModel):
    profile: dict[str, object] | None


class FeedbackInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    match_id: str = Field(min_length=1, max_length=64)
    action: Literal["like", "dislike", "met", "not_fit"]


class TelegramCodeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str = Field(min_length=9, max_length=9)


class OrganizerStatItem(BaseModel):
    name: str
    count: int
    share: float


class OrganizerGoalItem(BaseModel):
    goal: str
    count: int
    share: float


class OrganizerBoothStat(BaseModel):
    id: str
    name: str
    category: str
    location: str
    tags: list[str]
    matching_participants: int


class OrganizerStatsResponse(BaseModel):
    total_participants: int
    total_feedback: int
    met_count: int
    not_fit_count: int
    goals: list[OrganizerGoalItem]
    top_skills: list[OrganizerStatItem]
    top_interests: list[OrganizerStatItem]
    top_roles: list[OrganizerStatItem]
    experience_buckets: list[OrganizerStatItem]
    booths: list[OrganizerBoothStat]
