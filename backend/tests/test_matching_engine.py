"""
test_matching_engine.py
=======================
Unit tests for the Smart Matching & Ranking Algorithm (SA-1).

Coverage targets:
- Each factor helper function independently
- Weighted formula integration
- Edge cases: empty inputs, zero denominators, single project, all zero scores
- Ranking order correctness
- Determinism (same inputs → same outputs)
- Top-N slicing
"""

import pytest
from app.services.matching_engine import (
    parse_skills,
    compute_skill_match,
    compute_experience_match,
    compute_activity_score,
    compute_interest_match,
    compute_success_score,
    score_student_project,
    rank_projects,
    StudentDTO,
    ProjectDTO,
    ScoredProject,
)


# ---------------------------------------------------------------------------
# Fixtures — reusable student and project objects
# ---------------------------------------------------------------------------

@pytest.fixture
def base_student():
    return StudentDTO(
        student_id=1,
        skills=["python", "fastapi", "sql"],
        major="Computer Science",
        bio="I enjoy backend development and APIs",
        completed_project_count=2,
        total_accepted_count=2,
        accepted_deliverable_count=2,
        average_feedback_rating=4.5,
        recent_application_count=3,
        graduation_year=2025,
    )


@pytest.fixture
def base_project():
    return ProjectDTO(
        project_id=1,
        title="Build a REST API",
        description="FastAPI backend project with SQL database",
        required_skills=["python", "fastapi", "sql"],
        duration="1 month",
        status="open",
    )


@pytest.fixture
def new_student():
    """Student with zero history."""
    return StudentDTO(
        student_id=2,
        skills=[],
        major="Business",
        bio="",
        completed_project_count=0,
        total_accepted_count=0,
        accepted_deliverable_count=0,
        average_feedback_rating=0.0,
        recent_application_count=0,
        graduation_year=2028,
    )


# ---------------------------------------------------------------------------
# parse_skills
# ---------------------------------------------------------------------------

def test_parse_skills_normal():
    assert parse_skills("Python, FastAPI, React") == ["python", "fastapi", "react"]


def test_parse_skills_none():
    assert parse_skills(None) == []


def test_parse_skills_empty_string():
    assert parse_skills("") == []


def test_parse_skills_extra_whitespace():
    assert parse_skills("  python ,  sql  ") == ["python", "sql"]


def test_parse_skills_single():
    assert parse_skills("Python") == ["python"]


# ---------------------------------------------------------------------------
# Factor 1 — Skill Match
# ---------------------------------------------------------------------------

def test_skill_match_full_overlap():
    score = compute_skill_match(["python", "sql"], ["python", "sql"])
    assert score == 100.0


def test_skill_match_partial_overlap():
    score = compute_skill_match(["python", "fastapi"], ["python", "fastapi", "sql"])
    assert score == pytest.approx(66.67, abs=0.01)


def test_skill_match_no_overlap():
    score = compute_skill_match(["react", "css"], ["python", "sql"])
    assert score == 0.0


def test_skill_match_no_required_skills():
    """Project with no required skills returns neutral 50."""
    score = compute_skill_match(["python"], [])
    assert score == 50.0


def test_skill_match_empty_student_skills():
    score = compute_skill_match([], ["python", "sql"])
    assert score == 0.0


def test_skill_match_both_empty():
    score = compute_skill_match([], [])
    assert score == 50.0


def test_skill_match_student_has_extra_skills():
    """Extra student skills beyond required don't inflate score past 100."""
    score = compute_skill_match(
        ["python", "sql", "react", "docker", "kubernetes"],
        ["python", "sql"]
    )
    assert score == 100.0


def test_skill_match_score_range():
    score = compute_skill_match(["python"], ["python", "sql", "react"])
    assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# Factor 2 — Experience Match
# ---------------------------------------------------------------------------

def test_experience_match_no_history():
    from datetime import datetime, timezone
    current_year = datetime.now(timezone.utc).year
    score = compute_experience_match(0, current_year + 1, "1 week")
    assert score == pytest.approx(35.0, abs=0.01)

def test_experience_match_some_experience():
    score = compute_experience_match(3, 2025, "1 month")
    assert score >= 70.0


def test_experience_match_high_experience():
    score = compute_experience_match(6, 2024, "2 weeks")
    assert score >= 85.0


def test_experience_match_long_project_no_experience_penalty():
    """Long project with zero completed projects gets a lower score."""
    short = compute_experience_match(0, 2025, "1 week")
    long = compute_experience_match(0, 2025, "6 months")
    assert short > long


def test_experience_match_no_duration():
    """None duration should not raise — defaults to 4 weeks."""
    score = compute_experience_match(1, 2025, None)
    assert 0.0 <= score <= 100.0


def test_experience_match_score_range():
    score = compute_experience_match(2, 2026, "3 months")
    assert 0.0 <= score <= 100.0


def test_experience_match_graduating_soon_boost():
    """Student graduating in 1 year gets slight boost over distant grad."""
    from datetime import datetime, timezone
    current_year = datetime.now(timezone.utc).year
    soon = compute_experience_match(1, current_year + 1, "1 month")  # +5 adj
    late = compute_experience_match(1, current_year + 4, "1 month")  # -5 adj
    assert soon > late


# ---------------------------------------------------------------------------
# Factor 3 — Interest Match
# ---------------------------------------------------------------------------

def test_interest_match_high_overlap():
    relevant = compute_interest_match(
        "Computer Science",
        "I love Python and web development",
        "Web API Development",
        "Build a Python-based web API"
    )
    irrelevant = compute_interest_match(
        "Medieval History",
        "I study ancient manuscripts and archaeology",
        "Web API Development",
        "Build a Python-based web API"
    )
    assert relevant > irrelevant


def test_interest_match_no_overlap():
    score = compute_interest_match(
        "Medieval History",
        "I enjoy studying ancient manuscripts",
        "Machine Learning Pipeline",
        "Train neural networks on large datasets"
    )
    assert score < 50.0


def test_interest_match_empty_bio():
    """Empty bio should not raise — falls back to major-only matching."""
    score = compute_interest_match(
        "Computer Science",
        None,
        "Software Engineering Project",
        "Build scalable software systems"
    )
    assert 0.0 <= score <= 100.0


def test_interest_match_empty_description():
    """Empty project description returns neutral score."""
    score = compute_interest_match(
        "Computer Science",
        "Python developer",
        "",
        ""
    )
    assert score == 50.0


def test_interest_match_score_range():
    score = compute_interest_match(
        "Data Science",
        "Machine learning and statistics",
        "Data Analysis Project",
        "Analyze datasets using Python"
    )
    assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# Factor 4 — Activity Score
# ---------------------------------------------------------------------------

def test_activity_score_inactive():
    assert compute_activity_score(0) == 10.0


def test_activity_score_low():
    assert compute_activity_score(1) == 40.0


def test_activity_score_moderate():
    assert compute_activity_score(2) == 65.0


def test_activity_score_active():
    assert compute_activity_score(3) == 80.0


def test_activity_score_highly_active():
    assert compute_activity_score(4) == 100.0
    assert compute_activity_score(10) == 100.0


def test_activity_score_negative_input():
    """Negative input treated same as 0."""
    assert compute_activity_score(-1) == 10.0


def test_activity_score_range():
    for n in range(6):
        score = compute_activity_score(n)
        assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# Factor 5 — Success Score
# ---------------------------------------------------------------------------

def test_success_score_new_student():
    """Brand-new student with no history gets neutral 50."""
    score = compute_success_score(0, 0, 0, 0.0)
    assert score == 50.0


def test_success_score_perfect_record():
    score = compute_success_score(3, 3, 3, 5.0)
    assert score >= 90.0


def test_success_score_good_record():
    score = compute_success_score(2, 2, 2, 4.5)
    assert score >= 80.0


def test_success_score_partial_completion():
    """Completed 1 out of 2 accepted — lower than perfect."""
    full = compute_success_score(2, 2, 2, 4.0)
    partial = compute_success_score(1, 2, 1, 4.0)
    assert full > partial


def test_success_score_no_ratings():
    """No feedback rating → neutral 50 contribution from rating component."""
    score = compute_success_score(1, 1, 1, 0.0)
    assert 0.0 <= score <= 100.0


def test_success_score_range():
    score = compute_success_score(2, 3, 2, 3.5)
    assert 0.0 <= score <= 100.0


def test_success_score_divide_by_zero_safe():
    """accepted=0 but completed=1 should not raise."""
    score = compute_success_score(1, 0, 1, 4.0)
    assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# score_student_project — integration of all five factors
# ---------------------------------------------------------------------------

def test_score_returns_all_fields(base_student, base_project):
    result = score_student_project(base_student, base_project)
    assert "match_score" in result
    assert "skill_score" in result
    assert "experience_score" in result
    assert "interest_score" in result
    assert "activity_score" in result
    assert "success_score" in result
    assert "project_id" in result
    assert "title" in result


def test_score_range(base_student, base_project):
    result = score_student_project(base_student, base_project)
    assert 0.0 <= result["match_score"] <= 100.0


def test_score_high_match(base_student, base_project):
    """Student with matching skills, good history → high score."""
    result = score_student_project(base_student, base_project)
    assert result["match_score"] >= 60.0


def test_score_zero_match(new_student, base_project):
    """Student with no skills, no history → low score."""
    result = score_student_project(new_student, base_project)
    assert result["match_score"] < 50.0


def test_score_deterministic(base_student, base_project):
    """Same inputs always produce identical output."""
    r1 = score_student_project(base_student, base_project)
    r2 = score_student_project(base_student, base_project)
    assert r1["match_score"] == r2["match_score"]


def test_score_formula_weights(base_student, base_project):
    """
    Manually verify the weighted formula holds.
    Score = 0.40×skill + 0.20×exp + 0.15×interest + 0.10×activity + 0.15×success
    """
    result = score_student_project(base_student, base_project)
    expected = (
        0.40 * result["skill_score"] +
        0.20 * result["experience_score"] +
        0.15 * result["interest_score"] +
        0.10 * result["activity_score"] +
        0.15 * result["success_score"]
    )
    assert result["match_score"] == pytest.approx(expected, abs=0.01)


# ---------------------------------------------------------------------------
# rank_projects — ranking and sorting
# ---------------------------------------------------------------------------

def test_rank_projects_returns_sorted(base_student):
    """Projects should be ranked highest score first."""
    p_high = ProjectDTO(
        project_id=1,
        title="Python API",
        description="FastAPI and SQL backend",
        required_skills=["python", "fastapi", "sql"],
        duration="1 month",
        status="open",
    )
    p_low = ProjectDTO(
        project_id=2,
        title="Design Project",
        description="UI/UX and graphic design work",
        required_skills=["photoshop", "illustrator", "figma"],
        duration="2 months",
        status="open",
    )
    results = rank_projects(base_student, [p_low, p_high])
    assert len(results) == 2
    assert results[0].match_score >= results[1].match_score


def test_rank_projects_rank_assigned(base_student, base_project):
    results = rank_projects(base_student, [base_project])
    assert results[0].rank == 1


def test_rank_projects_multiple_ranks(base_student):
    projects = [
        ProjectDTO(project_id=i, title=f"Project {i}", description="desc",
                   required_skills=["python"], duration="1 month", status="open")
        for i in range(1, 6)
    ]
    results = rank_projects(base_student, projects)
    ranks = [r.rank for r in results]
    assert ranks == list(range(1, 6))


def test_rank_projects_top_n(base_student):
    projects = [
        ProjectDTO(project_id=i, title=f"Project {i}", description="desc",
                   required_skills=["python"], duration="1 month", status="open")
        for i in range(1, 11)
    ]
    results = rank_projects(base_student, projects, top_n=3)
    assert len(results) == 3


def test_rank_projects_empty_list(base_student):
    results = rank_projects(base_student, [])
    assert results == []


def test_rank_projects_returns_scored_project_type(base_student, base_project):
    results = rank_projects(base_student, [base_project])
    assert isinstance(results[0], ScoredProject)


def test_rank_projects_best_skill_match_ranks_first(base_student):
    """Project with best skill overlap should rank #1."""
    perfect_match = ProjectDTO(
        project_id=1,
        title="Perfect Match",
        description="Python FastAPI SQL project",
        required_skills=["python", "fastapi", "sql"],
        duration="1 month",
        status="open",
    )
    no_match = ProjectDTO(
        project_id=2,
        title="No Match",
        description="Hardware engineering project",
        required_skills=["verilog", "fpga", "embedded"],
        duration="1 month",
        status="open",
    )
    results = rank_projects(base_student, [no_match, perfect_match])
    assert results[0].project_id == perfect_match.project_id


def test_rank_projects_deterministic(base_student):
    """Calling rank_projects twice returns same order."""
    projects = [
        ProjectDTO(project_id=i, title=f"Project {i}", description="test",
                   required_skills=["python"], duration="1 month", status="open")
        for i in range(1, 6)
    ]
    r1 = [p.project_id for p in rank_projects(base_student, projects)]
    r2 = [p.project_id for p in rank_projects(base_student, projects)]
    assert r1 == r2


def test_rank_top_n_zero_returns_all(base_student, base_project):
    """
    top_n=0 is not a valid API input (rejected with 422 at the endpoint level).
    At the engine level, 0 is treated as 'no limit' — all results returned.
    Valid top_n usage starts at 1.
    """
    results = rank_projects(base_student, [base_project], top_n=0)
    assert len(results) == 1  # all results returned, no slice applied