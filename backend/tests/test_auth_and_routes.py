from datetime import datetime, timedelta, timezone
from collections.abc import Generator
import uuid

import jwt
import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


@pytest.fixture
def credentials(monkeypatch: pytest.MonkeyPatch) -> Generator[tuple[str, str], None, None]:
    secret = "offline-test-secret"
    bot_key = "offline-test-bot-key"
    monkeypatch.setenv("SUPABASE_JWT_SECRET", secret)
    monkeypatch.setenv("BOT_API_KEY", bot_key)
    monkeypatch.setenv("ENV", "test")
    get_settings.cache_clear()
    yield secret, bot_key
    get_settings.cache_clear()


def _token(secret: str, user_id: str) -> str:
    return jwt.encode({"sub": user_id, "aud": "authenticated", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}, secret, algorithm="HS256")


def test_profile_auth_feedback_and_telegram_link(credentials: tuple[str, str]) -> None:
    secret, bot_key = credentials
    user_id = f"test-{uuid.uuid4()}"
    authorization = {"Authorization": f"Bearer {_token(secret, user_id)}"}
    profile_body = {"name": "Test Person", "role": "Engineer", "goal": "find_job", "skills": ["Python"], "interests": ["AI"], "experience_years": 3}
    with TestClient(app) as client:
        assert client.get("/api/profile/me").status_code == 401
        saved = client.put("/api/profile/me", headers=authorization, json=profile_body)
        assert saved.status_code == 200
        assert saved.json()["profile"]["name"] == "Test Person"
        assert client.put("/api/profile/me", headers=authorization, json={**profile_body, "user_id": "victim"}).status_code == 422
        match_id = client.post("/api/match", json={**profile_body, "name": "Another Person"}).json()["matches"][0]["id"]
        feedback = client.post("/api/feedback", headers=authorization, json={"match_id": match_id, "action": "like"})
        assert feedback.status_code == 200
        issued = client.post("/api/telegram/link", headers=authorization)
        assert issued.status_code == 200
        code = issued.json()["code"]
        linked = client.post("/api/telegram/link", headers={"X-Bot-Key": bot_key, "X-Telegram-User-Id": "987654"}, json={"code": code})
        assert linked.status_code == 200
        assert linked.json() == {"linked": True}


def test_invalid_jwt_is_rejected(credentials: tuple[str, str]) -> None:
    with TestClient(app) as client:
        response = client.get("/api/profile/me", headers={"Authorization": "Bearer invalid.token.value"})
    assert response.status_code == 401
