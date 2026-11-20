from fastapi.testclient import TestClient

from app.main import app
from scripts.generate_profiles import generate_profiles


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_match_errors_use_common_envelope() -> None:
    with TestClient(app) as client:
        response = client.post("/api/match", json={"goal": "unknown", "unexpected": True})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert "message" in response.json()["error"]
    assert "details" in response.json()["error"]


def test_match_top5_and_performance() -> None:
    query = {"name": "Alex", "role": "Frontend Developer", "goal": "find_job", "skills": ["React", "TypeScript"], "interests": ["product"], "experience_years": 2}
    with TestClient(app) as client:
        response = client.post("/api/match", json=query)
    assert response.status_code == 200
    result = response.json()
    assert len(result["matches"]) == 5
    assert result["processing_ms"] < 3000
    assert result["matches"][0]["goal"] == "hire"
    assert len(result["recommended_booths"]) == 3
    assert len(result["matches"][0]["available_slots"]) >= 2
    assert result["matches"][0]["suggested_slot"] in result["matches"][0]["available_slots"]


def test_explanations_are_specific_and_private_fields_are_omitted() -> None:
    query = {"name": "Alex", "role": "Frontend Developer", "goal": "find_job", "skills": ["React", "TypeScript"], "interests": ["product"], "experience_years": 2}
    with TestClient(app) as client:
        matches = client.post("/api/match", json=query).json()["matches"]
    assert any(skill in matches[0]["reason"].lower() for skill in ("react", "typescript", "product"))
    assert matches[0]["name"] in matches[0]["icebreaker"]
    assert not ({"email", "phone", "age", "city"} & matches[0].keys())


def test_feedback_recalculates_matches_and_excludes_not_fit() -> None:
    query = {"name": "Dana", "role": "Backend Engineer", "goal": "find_job", "skills": ["Python", "FastAPI"], "interests": ["AI"], "experience_years": 3}
    with TestClient(app) as client:
        client.delete("/api/feedback")
        first_matches = client.post("/api/match", json=query).json()["matches"]
        rejected_id = first_matches[0]["id"]
        fb = client.post("/api/feedback", json={"match_id": rejected_id, "action": "not_fit"})
        assert fb.status_code == 200
        # Duplicate feedback upserts cleanly without IntegrityError
        fb_dup = client.post("/api/feedback", json={"match_id": rejected_id, "action": "not_fit"})
        assert fb_dup.status_code == 200
        second_matches = client.post("/api/match", json=query).json()["matches"]
        second_ids = [m["id"] for m in second_matches]
        assert rejected_id not in second_ids
        client.delete("/api/feedback")


def test_organizer_stats_hall_map() -> None:
    with TestClient(app) as client:
        response = client.get("/api/organizer/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_participants"] >= 180
    assert len(data["goals"]) >= 5
    assert len(data["top_skills"]) >= 5
    assert len(data["top_interests"]) >= 5
    assert len(data["booths"]) == 6


def test_generator_file_matches_seeded_output() -> None:
    import json
    from pathlib import Path

    checked_in = json.loads((Path(__file__).parents[1] / "data" / "profiles.json").read_text(encoding="utf-8"))
    assert checked_in == generate_profiles(seed=42)
