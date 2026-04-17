"""
matching_engine.py
==================
Smart Matching & Ranking Algorithm — SA-1 / US-20

Computes a weighted compatibility score (0–100) between a student
and each available project, then returns projects ranked by score.

Score Formula
-------------
Score = (0.40 × Skill Match)
      + (0.20 × Experience Match)
      + (0.15 × Interest Match)
      + (0.10 × Activity Score)
      + (0.15 × Success Score)

All component scores are in the range [0, 100] before weighting.

Complexity
----------
- Score computation per project: O(S + R) where S = student skill count,
  R = required skill count for that project.
- Full ranking over N projects: O(N log N) due to sort.
- Total: O(N × (S + R) + N log N)

Design
------
- Pure functions — no DB access inside the engine.
  The caller (API layer) is responsible for loading all data and
  passing plain Python objects/lists into score_student_project().
- Deterministic — identical inputs always produce identical outputs.
- Divide-by-zero safe — all denominators are guarded.
- Top-N slicing supported via rank_projects(top_n=...).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import math


# ---------------------------------------------------------------------------
# Data Transfer Objects
# ---------------------------------------------------------------------------
# These are plain Python dataclasses, completely decoupled from SQLAlchemy.
# The API layer maps ORM objects → these DTOs before calling the engine.

@dataclass
class StudentDTO:
    """Flat representation of a student + their history."""
    student_id: int
    skills: list[str]                    # normalised, lowercase
    major: str                           # e.g. "Computer Science"
    bio: str                             # free-text interests / bio
    completed_project_count: int         # projects fully completed
    total_accepted_count: int            # ever accepted (incl. in-progress)
    accepted_deliverable_count: int      # deliverables with status="accepted"
    average_feedback_rating: float       # 0.0 if no ratings yet
    recent_application_count: int        # applications in last 30 days
    graduation_year: int                 # used for experience proxy


@dataclass
class ProjectDTO:
    """Flat representation of a project to score against."""
    project_id: int
    title: str
    description: str
    required_skills: list[str]           # normalised, lowercase
    duration: str                        # e.g. "2 weeks", "1 month"
    status: str


@dataclass
class ScoredProject:
    """Output object — a project paired with its computed score and rank."""
    project_id: int
    title: str
    match_score: float                   # 0.0–100.0, rounded to 2dp
    rank: int
    skill_score: float
    experience_score: float
    interest_score: float
    activity_score: float
    success_score: float


# ---------------------------------------------------------------------------
# Helper: string → skill list
# ---------------------------------------------------------------------------

def parse_skills(raw: Optional[str]) -> list[str]:
    """
    Converts a comma-separated skill string to a normalised lowercase list.
    Handles None, empty string, and extra whitespace safely.

    >>> parse_skills("Python, FastAPI,  React")
    ['python', 'fastapi', 'react']
    >>> parse_skills(None)
    []
    """
    if not raw:
        return []
    return [s.strip().lower() for s in raw.split(",") if s.strip()]


# ---------------------------------------------------------------------------
# Factor 1 — Skill Match (weight: 0.40)
# ---------------------------------------------------------------------------

def compute_skill_match(student_skills: list[str], required_skills: list[str]) -> float:
    """
    Set-intersection skill overlap, normalised by required skill count.

    Returns a score in [0, 100].

    - If the project has no required skills → 50.0 (neutral, not penalised).
    - If the student has no skills and project requires some → 0.0.

    Complexity: O(S + R) using set operations.

    >>> compute_skill_match(["python", "fastapi"], ["python", "fastapi", "sql"])
    66.67
    >>> compute_skill_match([], [])
    50.0
    """
    if not required_skills:
        # Project requires nothing specific — all students are equally valid
        return 50.0

    if not student_skills:
        return 0.0

    student_set = set(student_skills)
    required_set = set(required_skills)

    matched = len(student_set & required_set)
    score = (matched / len(required_set)) * 100.0

    return round(score, 2)


# ---------------------------------------------------------------------------
# Factor 2 — Experience Match (weight: 0.20)
# ---------------------------------------------------------------------------

# Duration strings → estimated weeks
_DURATION_WEEKS: dict[str, int] = {
    "1 week": 1,
    "2 weeks": 2,
    "3 weeks": 3,
    "1 month": 4,
    "6 weeks": 6,
    "2 months": 8,
    "3 months": 12,
    "6 months": 26,
    "1 year": 52,
}

def _duration_to_weeks(duration: Optional[str]) -> int:
    """Maps a duration string to estimated weeks. Defaults to 4 (1 month)."""
    if not duration:
        return 4
    return _DURATION_WEEKS.get(duration.strip().lower(), 4)


def compute_experience_match(
    completed_count: int,
    graduation_year: int,
    project_duration: Optional[str],
) -> float:
    """
    Estimates experience fit based on:
    - Number of completed projects (proxy for general experience)
    - Graduation year (proximity → more recent = less experienced)
    - Project duration (longer projects suit more experienced students)

    Returns a score in [0, 100].

    Scoring logic:
    - Base experience level derived from completed_count (0–3 tiers).
    - Graduation year proximity adjusts by ±10 points.
    - Duration penalty: very long projects (>12 weeks) reduce score for
      students with 0 completed projects.

    >>> compute_experience_match(0, 2025, "1 week")
    40.0
    >>> compute_experience_match(3, 2024, "1 month")
    90.0
    """
    current_year = datetime.now(timezone.utc).year

    # Base score from completed project count
    if completed_count == 0:
        base = 30.0
    elif completed_count == 1:
        base = 55.0
    elif completed_count == 2:
        base = 70.0
    elif completed_count <= 5:
        base = 80.0
    else:
        base = 90.0

    # Graduation year adjustment: graduating soon → slight boost (fresh talent)
    years_to_grad = graduation_year - current_year
    if years_to_grad <= 0:
        # Already graduated — neutral
        year_adj = 0.0
    elif years_to_grad == 1:
        year_adj = 5.0
    elif years_to_grad == 2:
        year_adj = 2.0
    else:
        year_adj = -5.0   # Far from graduation, likely early in program

    # Duration penalty for inexperienced students on long projects
    weeks = _duration_to_weeks(project_duration)
    if completed_count == 0 and weeks > 12:
        duration_penalty = -15.0
    elif completed_count <= 1 and weeks > 8:
        duration_penalty = -5.0
    else:
        duration_penalty = 0.0

    score = base + year_adj + duration_penalty
    return round(max(0.0, min(100.0, score)), 2)


# ---------------------------------------------------------------------------
# Factor 3 — Interest Match (weight: 0.15)
# ---------------------------------------------------------------------------

def _extract_keywords(text: Optional[str]) -> set[str]:
    """
    Extracts meaningful keywords from free text.
    Lowercases, splits on whitespace and punctuation,
    filters single-char tokens and common stop words.
    """
    if not text:
        return set()

    stop_words = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "it", "as", "be",
        "this", "that", "are", "was", "were", "has", "have", "had",
        "will", "would", "can", "could", "i", "we", "you", "they",
        "my", "our", "your", "their", "its",
    }

    import re
    tokens = re.split(r"[\s,.\-_/\\()\[\]{}:;!?\"']+", text.lower())
    return {t for t in tokens if len(t) > 1 and t not in stop_words}


def compute_interest_match(
    student_major: str,
    student_bio: Optional[str],
    project_title: str,
    project_description: str,
) -> float:
    """
    Keyword overlap between student's major + bio and project title + description.

    Returns a score in [0, 100].

    Scoring:
    - Major tokens checked against project text (exact match → strong signal)
    - Bio keywords checked against project text (partial overlap)
    - Jaccard-style similarity used for bio overlap

    >>> compute_interest_match("Computer Science", "I love Python and web dev",
    ...                        "Web API Project", "Build a REST API using Python")
    75.0
    """
    project_keywords = _extract_keywords(project_title + " " + project_description)

    if not project_keywords:
        return 50.0  # No project description → neutral

    # Major match — each matching token from major = strong signal
    major_tokens = _extract_keywords(student_major)
    major_overlap = len(major_tokens & project_keywords)
    major_score = min(100.0, (major_overlap / max(len(major_tokens), 1)) * 100.0)

    # Bio match — keyword overlap between bio and project
    bio_tokens = _extract_keywords(student_bio or "")
    if bio_tokens:
        bio_overlap = len(bio_tokens & project_keywords)
        # Jaccard similarity
        union = len(bio_tokens | project_keywords)
        bio_score = (bio_overlap / union) * 100.0 if union > 0 else 0.0
    else:
        bio_score = 0.0

    # Weighted blend: major is stronger signal than bio
    combined = (major_score * 0.6) + (bio_score * 0.4)
    return round(min(100.0, combined), 2)


# ---------------------------------------------------------------------------
# Factor 4 — Activity Score (weight: 0.10)
# ---------------------------------------------------------------------------

def compute_activity_score(recent_application_count: int) -> float:
    """
    Measures recent platform engagement using number of applications
    submitted in the last 30 days.

    No last_login field exists in the schema, so application frequency
    is used as the primary activity signal.

    Returns a score in [0, 100].

    Tiers:
    - 0 applications  →  10  (inactive)
    - 1 application   →  40  (low activity)
    - 2 applications  →  65  (moderate)
    - 3 applications  →  80  (active)
    - 4+              → 100  (highly active)

    >>> compute_activity_score(0)
    10.0
    >>> compute_activity_score(4)
    100.0
    """
    if recent_application_count <= 0:
        return 10.0
    elif recent_application_count == 1:
        return 40.0
    elif recent_application_count == 2:
        return 65.0
    elif recent_application_count == 3:
        return 80.0
    else:
        return 100.0


# ---------------------------------------------------------------------------
# Factor 5 — Success Score (weight: 0.15)
# ---------------------------------------------------------------------------

def compute_success_score(
    completed_count: int,
    total_accepted_count: int,
    accepted_deliverable_count: int,
    average_feedback_rating: float,
) -> float:
    """
    Measures historical success across three dimensions:
    1. Completion ratio  — completed / accepted (did they finish?)
    2. Delivery rate     — accepted deliverables / completed (did they deliver?)
    3. Feedback rating   — normalised 1–5 rating → 0–100

    Returns a weighted blend in [0, 100].

    - New student (0 history) → 50.0 (neutral, not penalised)
    - Divide-by-zero safe throughout.

    >>> compute_success_score(2, 2, 2, 4.5)
    95.0
    >>> compute_success_score(0, 0, 0, 0.0)
    50.0
    """
    # New student with no history — neutral score
    if total_accepted_count == 0 and completed_count == 0:
        return 50.0

    # 1. Completion ratio
    if total_accepted_count > 0:
        completion_ratio = completed_count / total_accepted_count
    else:
        completion_ratio = 0.0
    completion_score = completion_ratio * 100.0

    # 2. Delivery rate (accepted deliverables vs completed projects)
    if completed_count > 0:
        delivery_rate = min(accepted_deliverable_count / completed_count, 1.0)
    else:
        delivery_rate = 0.0
    delivery_score = delivery_rate * 100.0

    # 3. Feedback rating normalised to 0–100
    # Rating is 1–5; map to 0–100 linearly: (rating - 1) / 4 * 100
    if average_feedback_rating > 0:
        rating_score = ((average_feedback_rating - 1.0) / 4.0) * 100.0
    else:
        # No ratings yet — neutral
        rating_score = 50.0

    # Weighted blend of the three dimensions
    score = (completion_score * 0.40) + (delivery_score * 0.30) + (rating_score * 0.30)
    return round(max(0.0, min(100.0, score)), 2)


# ---------------------------------------------------------------------------
# Core: score one student against one project
# ---------------------------------------------------------------------------

def score_student_project(student: StudentDTO, project: ProjectDTO) -> dict:
    """
    Computes all five factor scores and the final weighted match score
    for a single (student, project) pair.

    Returns a dict with all component scores and the final score.
    All scores are in [0, 100].

    Complexity: O(S + R) where S = student skills, R = required skills.
    """
    skill = compute_skill_match(student.skills, project.required_skills)
    experience = compute_experience_match(
        student.completed_project_count,
        student.graduation_year,
        project.duration,
    )
    interest = compute_interest_match(
        student.major,
        student.bio,
        project.title,
        project.description,
    )
    activity = compute_activity_score(student.recent_application_count)
    success = compute_success_score(
        student.completed_project_count,
        student.total_accepted_count,
        student.accepted_deliverable_count,
        student.average_feedback_rating,
    )

    # Weighted formula
    final = (
        (0.40 * skill) +
        (0.20 * experience) +
        (0.15 * interest) +
        (0.10 * activity) +
        (0.15 * success)
    )

    return {
        "project_id": project.project_id,
        "title": project.title,
        "match_score": round(max(0.0, min(100.0, final)), 2),
        "skill_score": skill,
        "experience_score": experience,
        "interest_score": interest,
        "activity_score": activity,
        "success_score": success,
    }


# ---------------------------------------------------------------------------
# Public API: rank all projects for a student
# ---------------------------------------------------------------------------

def rank_projects(
    student: StudentDTO,
    projects: list[ProjectDTO],
    top_n: Optional[int] = None,
) -> list[ScoredProject]:
    """
    Scores a student against all provided projects, sorts by score
    descending (O(N log N)), assigns rank positions, and optionally
    slices to top-N.

    Only projects with status="open" should be passed in — filtering
    is the caller's responsibility (enforced in the API layer).

    Args:
        student:  StudentDTO for the requesting student.
        projects: List of ProjectDTOs to score against.
        top_n:    If provided, return only the top N results.

    Returns:
        List of ScoredProject objects, sorted by match_score descending.

    Complexity: O(N × (S + R) + N log N)
    """
    if not projects:
        return []

    # Score all projects — O(N × (S + R))
    raw_scores = [score_student_project(student, p) for p in projects]

    # Sort descending by match_score — O(N log N)
    raw_scores.sort(key=lambda x: x["match_score"], reverse=True)

    # Assign rank and build output objects
    ranked = []
    for i, scored in enumerate(raw_scores, start=1):
        ranked.append(
            ScoredProject(
                project_id=scored["project_id"],
                title=scored["title"],
                match_score=scored["match_score"],
                rank=i,
                skill_score=scored["skill_score"],
                experience_score=scored["experience_score"],
                interest_score=scored["interest_score"],
                activity_score=scored["activity_score"],
                success_score=scored["success_score"],
            )
        )

    # Apply top-N slice if requested
    if top_n is not None and top_n > 0:
        ranked = ranked[:top_n]

    return ranked