# MeetMatch AI Backend Specification (derived)

> This document was reconstructed from the implementation prompt because the original `backend/BACKEND_SPEC.md` was absent from `main`. API details omitted by that prompt are explicitly fixed here as implementation assumptions; confirm them with the product/frontend owner before treating this contract as final.

## 1. Runtime and boundaries

Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2, SQLite, pytest. The API listens on port 8000. CORS defaults to `http://localhost:5173`; `CORS_ORIGINS` is a comma-separated override. No external AI/network calls. All application Python lives under `app/`; backend artifacts remain inside `backend/`.

## 2. Goals and profile model

Assumed goal enum: `find_job`, `hire`, `find_cofounder`, `find_investor`, `find_mentor`, `offer_mentorship`. A profile has `id`, `name`, `role`, `goal`, `skills[]`, `interests[]`, `experience_years`, optional `bio`, and optional private contact fields `email`, `phone`, `age`, `city`. Persisted profiles are keyed by authenticated `user_id`; public match results never expose private fields. Generator emits 180 deterministic synthetic profiles using seed 42 with coverage of all goals and role archetypes.

## 3. API contract

- `GET /api/health`: `{"status":"ok"}`.
- `POST /api/match`: accepts a profile-like JSON object (goal required; other fields optional with empty defaults) and returns `{matches:[{id,name,role,score,goal,reason,icebreaker}],processing_ms,total_candidates,fallback_used}`. Always return up to five ranked matches; the seeded dataset ensures at least five compatible candidates per goal. An empty body is allowed only for a resolved authenticated actor and uses their stored profile.
- `GET /api/profile/me`: current caller's profile or `{"profile":null}`.
- `PUT /api/profile/me`: upserts caller's profile; unknown fields are rejected and caller identity cannot be supplied in the body.
- `POST /api/feedback`: accepts `{match_id, action}` where action is `like` or `dislike`; returns `{"ok":true}`.
- `POST /api/telegram/link`: Bearer caller requests a one-time link code; bot confirms using `X-Bot-Key` and `X-Telegram-User-Id` with the code. Codes are 8 characters displayed `XXXX-XXXX`, stored hashed, expire after 10 minutes, are single-use, and have bounded attempts.

All errors use `{error:{code,message,details}}`; validation errors use HTTP 422 and this same shape. Authentication errors are 401/403. Match output excludes `email`, `phone`, `age`, `city`.

## 4. Matching

Normalize case, whitespace, punctuation, and aliases (e.g. `ts` → `typescript`, `js` → `javascript`). Compare skills by exact canonical values and declared skill groups. Goal compatibility is determined by explicit directional pairs: `find_job`↔`hire`, `find_mentor`↔`offer_mentorship`; cofounder and investor seekers match same-goal peers. The strict pass uses compatible pairs; if it yields fewer than five, expand to same-goal and then all other goals and set `fallback_used=true`.

Each pair gets four normalized [0,1] components: skill overlap (Jaccard over canonical skills), interest overlap (Jaccard), experience proximity (1 minus capped relative difference), and semantic similarity (cosine similarity using a pure-Python TF-IDF vectorizer over role, bio, skills, interests). Final score is rounded integer percent: `40*skills + 25*interests + 20*experience + 15*semantic`. Ties break deterministically by score descending, then canonical name and ID. Reasons identify actual shared skills/interests or complementary goals. Icebreakers use shared pair facts and address the candidate by name; no generic fixed scoring or random route data.

## 5. Auth and storage

Supabase JWT HS256 validation uses `SUPABASE_JWT_SECRET`; optional JWKS verification may be added without network access in tests. `DEV_AUTH_BYPASS=true` is honored only when `ENV=dev`. Bot authentication compares `BOT_API_KEY` with `hmac.compare_digest` and requires a Telegram user ID. SQLite URL defaults to `sqlite:///./data/meetmatch.db`; tables are created on startup. User IDs come only from verified claims. Telegram codes are SHA-256 hashed at rest.

## 6. Errors and operational behavior

Validation errors and handled HTTP errors are converted to the common envelope. `processing_ms` measures match work via `time.perf_counter()`. Candidate index is loaded at startup and refreshed after profile writes. CORS allows configured origins only. Environment secrets are never committed; `backend/.env.example` documents names without real secrets.

## 7. Dataset generation

`python scripts/generate_profiles.py --out PATH` writes deterministic UTF-8 JSON (180 profiles, seed 42). The checked-in `data/profiles.json` must byte-match generated output. Data is synthetic and must be labeled as such.

## 8. Acceptance checklist

- Six goals produce five results when fixture candidate count permits; seeded dataset covers each goal.
- Repeated identical requests return identical matches and distinct scores occur for the frontend example.
- Explanations are grounded in profile facts and outputs contain no private fields.
- Auth, profile ownership, feedback validation, and single-use Telegram linking have isolated tests.
- Pytest passes offline; generator is reproducible; Docker builds when Docker is available.
- Only files under `backend/` are changed.

## 9. Inferred decisions

The exact original field schemas, goal enum, thresholds, compatibility matrix, and generator archetype taxonomy were not present in the prompt. This reconstruction uses the smallest coherent contract compatible with the explicit examples and constraints above. Treat these choices as provisional until the frontend/product owner confirms them.
