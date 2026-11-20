from collections import Counter
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "reactjs": "react",
    "py": "python",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "pm": "product management",
}
SKILL_GROUPS = (
    {"javascript", "typescript", "react", "vue", "angular", "frontend"},
    {"python", "fastapi", "django", "backend"},
    {"machine learning", "artificial intelligence", "data science"},
    {"product management", "product strategy", "roadmapping"},
    {"sales", "business development", "partnerships"},
)
STRICT_PAIRS = {
    "find_job": {"hire"},
    "hire": {"find_job"},
    "find_mentor": {"offer_mentorship", "be_mentor"},
    "offer_mentorship": {"find_mentor"},
    "be_mentor": {"find_mentor"},
    "find_cofounder": {"find_cofounder", "find_investor", "exchange_experience"},
    "find_investor": {"find_investor", "find_cofounder"},
    "exchange_experience": {"exchange_experience", "find_cofounder", "find_mentor"},
}
CONFERENCE_SLOTS = (
    "11:30–11:45",
    "12:15–12:30",
    "13:30–13:45",
    "14:45–15:00",
    "16:00–16:15",
    "17:00–17:15",
)
PARTNER_BOOTHS: tuple[dict[str, Any], ...] = (
    {
        "id": "booth-qazaq-it",
        "name": "Qazaq IT Community Hub",
        "category": "Community & Mentorship",
        "location": "Зал A · Стенд A1",
        "tags": ["python", "react", "typescript", "community", "mentorship", "architecture", "open source"],
        "goals": ["find_mentor", "offer_mentorship", "be_mentor", "exchange_experience"],
    },
    {
        "id": "booth-aiid-lab",
        "name": "AIID Smart Business & AI Lab",
        "category": "AI & Applied Research",
        "location": "Зал A · Стенд A2",
        "tags": ["artificial intelligence", "machine learning", "data science", "llm", "nlp", "python", "analytics"],
        "goals": ["exchange_experience", "find_cofounder", "find_job", "hire"],
    },
    {
        "id": "booth-talent-arena",
        "name": "Tech Talent & Career Zone",
        "category": "Hiring & Career",
        "location": "Зал B · Стенд B1",
        "tags": ["frontend", "backend", "react", "typescript", "python", "java", "go", "career", "hiring"],
        "goals": ["find_job", "hire"],
    },
    {
        "id": "booth-startup-alley",
        "name": "Startup & Venture Alley",
        "category": "Startups & Investment",
        "location": "Зал B · Стенд B2",
        "tags": ["startups", "product", "product management", "fintech", "edtech", "growth", "sales", "partnerships"],
        "goals": ["find_cofounder", "find_investor", "exchange_experience"],
    },
    {
        "id": "booth-cloud-devops",
        "name": "Cloud, DevOps & Highload Stand",
        "category": "Infrastructure & SRE",
        "location": "Зал C · Стенд C1",
        "tags": ["devops", "docker", "kubernetes", "aws", "cloud", "highload", "security", "backend"],
        "goals": ["exchange_experience", "find_job", "hire", "find_mentor"],
    },
    {
        "id": "booth-product-design",
        "name": "Product & UX Design Corner",
        "category": "Product & Design",
        "location": "Зал C · Стенд C2",
        "tags": ["design", "ux", "ui", "figma", "product", "product strategy", "mobile", "frontend"],
        "goals": ["exchange_experience", "find_cofounder", "find_mentor", "find_job"],
    },
)
TOKEN_RE = re.compile(r"[a-z0-9+#.]+", re.I)


def normalize(value: str) -> str:
    return " ".join(ALIASES.get(token, token) for token in TOKEN_RE.findall(value.casefold()))


def _items(profile: dict[str, Any], key: str) -> set[str]:
    raw = profile.get(key, [])
    if not isinstance(raw, list):
        return set()
    return {normalize(str(value)) for value in raw if str(value).strip()}


def _expanded(values: set[str]) -> set[str]:
    expanded = set(values)
    for group in SKILL_GROUPS:
        if expanded & group:
            expanded.update(group)
    return expanded


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
    dot = sum(weight * right.get(term, 0.0) for term, weight in left.items())
    left_norm = math.sqrt(sum(weight * weight for weight in left.values()))
    right_norm = math.sqrt(sum(weight * weight for weight in right.values()))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


def _tfidf(texts: list[str]) -> list[dict[str, float]]:
    docs = [normalize(text).split() for text in texts]
    df: dict[str, int] = {}
    for terms in docs:
        for term in set(terms):
            df[term] = df.get(term, 0) + 1
    vectors: list[dict[str, float]] = []
    count = max(1, len(docs))
    for terms in docs:
        frequencies: dict[str, int] = {}
        for term in terms:
            frequencies[term] = frequencies.get(term, 0) + 1
        vectors.append({term: (1.0 + math.log(freq)) * (math.log((1 + count) / (1 + df[term])) + 1) for term, freq in frequencies.items()})
    return vectors


def _candidate_slots(candidate_id: str) -> list[str]:
    digest = hashlib.sha256(candidate_id.encode("utf-8")).digest()
    first = digest[0] % len(CONFERENCE_SLOTS)
    second = (first + 1 + (digest[1] % (len(CONFERENCE_SLOTS) - 1))) % len(CONFERENCE_SLOTS)
    third = (second + 1 + (digest[2] % (len(CONFERENCE_SLOTS) - 2))) % len(CONFERENCE_SLOTS)
    indices = sorted({first, second, third})
    return [CONFERENCE_SLOTS[i] for i in indices]


def recommend_booths(seeker: dict[str, Any], limit: int = 3) -> list[dict[str, Any]]:
    goal = str(seeker.get("goal", ""))
    seeker_terms = (
        _expanded(_items(seeker, "skills"))
        | _items(seeker, "interests")
        | set(normalize(str(seeker.get("role", ""))).split())
        | set(normalize(str(seeker.get("bio", ""))).split())
    )
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for booth in PARTNER_BOOTHS:
        booth_tags = {normalize(tag) for tag in booth["tags"]}
        matched = sorted(seeker_terms & booth_tags)
        goal_match = goal in booth["goals"]
        raw_score = min(98, 45 + 14 * len(matched) + (15 if goal_match else 0))
        if matched:
            reason = f"Matches your profile topics: {', '.join(matched[:3])}."
        elif goal_match:
            reason = f"Recommended for your goal ({goal}) and networking track."
        else:
            reason = "Popular conference partner hub for cross-team networking."
        item = {
            "id": booth["id"],
            "name": booth["name"],
            "category": booth["category"],
            "location": booth["location"],
            "tags": list(booth["tags"][:4]),
            "reason": reason,
            "match_score": raw_score,
        }
        scored.append((raw_score, booth["id"], item))
    scored.sort(key=lambda row: (-row[0], row[1]))
    return [row[2] for row in scored[:limit]]


class MatchingIndex:
    def __init__(self, profiles: list[dict[str, Any]]) -> None:
        self.profiles = [dict(profile) for profile in profiles]

    @classmethod
    def from_file(cls, path: str | Path) -> "MatchingIndex":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Profiles file must contain a JSON array")
        return cls(data)

    def replace(self, profile: dict[str, Any]) -> None:
        profile_id = str(profile["id"])
        self.profiles = [item for item in self.profiles if str(item.get("id")) != profile_id]
        self.profiles.append(dict(profile))

    def match(
        self,
        seeker: dict[str, Any],
        limit: int = 5,
        excluded_ids: set[str] | None = None,
        met_ids: set[str] | None = None,
    ) -> tuple[list[dict[str, Any]], int, bool]:
        goal = str(seeker.get("goal", ""))
        extra_excluded = {str(x) for x in seeker.get("exclude_ids", []) if str(x).strip()}
        blocked = {str(seeker.get("id", "")), str(seeker.get("user_id", ""))} | (excluded_ids or set()) | extra_excluded
        met_set = {str(x) for x in (met_ids or set()) if str(x).strip()}
        candidates = [p for p in self.profiles if str(p.get("id", "")) not in blocked and p.get("user_id") not in blocked]
        compatible_targets = STRICT_PAIRS.get(goal, set())
        compatible = [p for p in candidates if p.get("goal") in compatible_targets]
        fallback = len(compatible) < limit
        if fallback:
            compatible_ids = {p.get("id") for p in compatible}
            compatible += [p for p in candidates if p.get("id") not in compatible_ids and p.get("goal") == goal]
            compatible_ids = {p.get("id") for p in compatible}
            if len(compatible) < limit:
                compatible += [p for p in candidates if p.get("id") not in compatible_ids]
        query_text = " ".join([str(seeker.get("role", "")), str(seeker.get("bio", "")), *map(str, seeker.get("skills", [])), *map(str, seeker.get("interests", []))])
        scored: list[tuple[int, float, dict[str, Any], set[str], set[str]]] = []
        texts = [query_text] + [" ".join([str(p.get("role", "")), str(p.get("bio", "")), *map(str, p.get("skills", [])), *map(str, p.get("interests", []))]) for p in compatible]
        vectors = _tfidf(texts)
        seeker_skills = _expanded(_items(seeker, "skills"))
        seeker_interests = _items(seeker, "interests")
        seeker_years = max(0, int(seeker.get("experience_years", 0) or 0))
        preferred_slots = [str(s) for s in seeker.get("preferred_slots", []) if str(s).strip()]
        for offset, candidate in enumerate(compatible, start=1):
            skills = _expanded(_items(candidate, "skills"))
            interests = _items(candidate, "interests")
            years = max(0, int(candidate.get("experience_years", 0) or 0))
            skill_score = _jaccard(seeker_skills, skills)
            interest_score = _jaccard(seeker_interests, interests)
            experience_score = max(0.0, 1.0 - abs(seeker_years - years) / max(3, seeker_years, years))
            semantic_score = _cosine(vectors[0], vectors[offset])
            score = 100 * (0.40 * skill_score + 0.25 * interest_score + 0.20 * experience_score + 0.15 * semantic_score)
            actual_shared_skills = _items(seeker, "skills") & _items(candidate, "skills")
            is_met = 1 if str(candidate.get("id", "")) in met_set else 0
            scored.append((is_met, score, candidate, actual_shared_skills, seeker_interests & interests))
        scored.sort(key=lambda row: (row[0], -row[1], normalize(str(row[2].get("name", ""))), str(row[2].get("id", ""))))
        results: list[dict[str, Any]] = []
        for _is_met, score, candidate, common_skills, common_interests in scored[:limit]:
            facts = sorted(common_skills or common_interests)
            if facts:
                reason = "Shared " + ("skills" if common_skills else "interests") + ": " + ", ".join(facts[:3]) + "."
            else:
                reason = f"Goal compatibility: {goal} pairs with {candidate.get('goal')}; role and experience are considered."
            topic = facts[0] if facts else str(candidate.get("role", "your work"))
            name = str(candidate.get("name", "there"))
            cid = str(candidate.get("id", ""))
            slots = _candidate_slots(cid)
            overlapping = [s for s in slots if s in preferred_slots]
            suggested_slot = overlapping[0] if overlapping else slots[0]
            results.append({
                "id": cid,
                "name": name,
                "role": str(candidate.get("role", "")),
                "score": round(score),
                "goal": str(candidate.get("goal", "")),
                "reason": reason,
                "icebreaker": f"Hi {name}, I noticed our connection around {topic}. What are you working on at the conference?",
                "available_slots": slots,
                "suggested_slot": suggested_slot,
            })
        return results, len(candidates), fallback

    def hall_analytics(self, feedback_counts: dict[str, int] | None = None) -> dict[str, Any]:
        total = max(1, len(self.profiles))
        goal_counter: Counter[str] = Counter()
        skill_counter: Counter[str] = Counter()
        interest_counter: Counter[str] = Counter()
        role_counter: Counter[str] = Counter()
        exp_buckets: Counter[str] = Counter({"0–1": 0, "2–4": 0, "5–7": 0, "8+": 0})

        for p in self.profiles:
            g = str(p.get("goal", "exchange_experience"))
            if g == "offer_mentorship":
                g = "be_mentor"
            goal_counter[g] += 1
            role = str(p.get("role", "")).strip()
            if role:
                role_counter[role] += 1
            for s in p.get("skills", []) or []:
                s_str = str(s).strip()
                if s_str:
                    skill_counter[s_str] += 1
            for i in p.get("interests", []) or []:
                i_str = str(i).strip()
                if i_str:
                    interest_counter[i_str] += 1
            years = max(0, int(p.get("experience_years", 0) or 0))
            if years <= 1:
                exp_buckets["0–1"] += 1
            elif years <= 4:
                exp_buckets["2–4"] += 1
            elif years <= 7:
                exp_buckets["5–7"] += 1
            else:
                exp_buckets["8+"] += 1

        booths_stats: list[dict[str, Any]] = []
        for booth in PARTNER_BOOTHS:
            b_tags = {normalize(tag) for tag in booth["tags"]}
            matching_count = 0
            for p in self.profiles:
                p_terms = _expanded(_items(p, "skills")) | _items(p, "interests")
                if p_terms & b_tags or p.get("goal") in booth["goals"]:
                    matching_count += 1
            booths_stats.append({
                "id": booth["id"],
                "name": booth["name"],
                "category": booth["category"],
                "location": booth["location"],
                "tags": list(booth["tags"][:4]),
                "matching_participants": matching_count,
            })

        fc = feedback_counts or {}
        met_count = fc.get("met", 0)
        not_fit_count = fc.get("not_fit", 0)

        return {
            "total_participants": len(self.profiles),
            "total_feedback": met_count + not_fit_count,
            "met_count": met_count,
            "not_fit_count": not_fit_count,
            "goals": [
                {"goal": k, "count": v, "share": round(v * 100 / total, 1)}
                for k, v in goal_counter.most_common()
            ],
            "top_skills": [
                {"name": k, "count": v, "share": round(v * 100 / total, 1)}
                for k, v in skill_counter.most_common(12)
            ],
            "top_interests": [
                {"name": k, "count": v, "share": round(v * 100 / total, 1)}
                for k, v in interest_counter.most_common(10)
            ],
            "top_roles": [
                {"name": k, "count": v, "share": round(v * 100 / total, 1)}
                for k, v in role_counter.most_common(8)
            ],
            "experience_buckets": [
                {"name": k, "count": exp_buckets[k], "share": round(exp_buckets[k] * 100 / total, 1)}
                for k in ("0–1", "2–4", "5–7", "8+")
            ],
            "booths": booths_stats,
        }
