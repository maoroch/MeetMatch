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


class MatchPerson(BaseModel):
    id: str
    name: str
    role: str
    score: int
    goal: str
    reason: str
    icebreaker: str


class MatchResponse(BaseModel):
    matches: list[MatchPerson]
    processing_ms: int
    total_candidates: int
    fallback_used: bool


class ProfileResponse(BaseModel):
    profile: dict[str, object] | None


class FeedbackInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    match_id: str = Field(min_length=1, max_length=64)
    action: Literal["like", "dislike", "met", "not_fit"]


class TelegramCodeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str = Field(min_length=9, max_length=9)
