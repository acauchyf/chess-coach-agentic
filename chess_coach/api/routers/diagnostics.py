from __future__ import annotations
from fastapi import APIRouter
from chess_coach.api.deps import get_repo, get_llm
from chess_coach.application.diagnostics_engine import build_diagnostics, diagnostics_to_dict
from chess_coach.application.curriculum_engine import recommend_courses, recommendations_to_dict, build_adaptive_course

router = APIRouter(tags=["diagnostics"])

@router.get("/diagnostics")
def diagnostics(username: str):
    repo = get_repo()
    d = build_diagnostics(repo, username)
    return diagnostics_to_dict(d)

@router.get("/diagnostics/recommendations")
def recommendations(username: str, max_items: int = 6):
    repo = get_repo()
    d = build_diagnostics(repo, username)
    recs = recommend_courses(d, max_items=max_items)
    return {"items": recommendations_to_dict(recs)}

@router.get("/courses/adaptive")
def adaptive_course(topic: str):
    llm = get_llm()
    return build_adaptive_course(topic, llm=llm)


@router.get("/courses/adaptive/user")
def adaptive_user_course(username: str, topic: str, limit_examples: int = 6):
    repo = get_repo()
    llm = get_llm()
    from chess_coach.application.adaptive_course_builder import build_adaptive_course_for_user
    return build_adaptive_course_for_user(repo, username=username, topic=topic, llm=llm, limit_examples=limit_examples)
