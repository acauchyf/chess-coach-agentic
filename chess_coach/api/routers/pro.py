from __future__ import annotations
import json
from datetime import date
from fastapi import APIRouter
from chess_coach.api.deps import get_repo
from chess_coach.application.pro_diagnostics_engine import build_pro_diagnostics
from chess_coach.application.weekly_curriculum import build_weekly_curriculum, curriculum_to_dict

router = APIRouter(tags=["pro"])

@router.get("/pro/diagnostics")
def pro_diagnostics(username: str):
    repo = get_repo()
    return build_pro_diagnostics(repo, username)

@router.get("/pro/curriculum/weekly")
def weekly_curriculum(username: str):
    repo = get_repo()
    start = date.today()
    existing = repo.get_weekly_curriculum(username, str(start))
    if existing:
        return existing
    c = build_weekly_curriculum(repo, username, start=start)
    payload = curriculum_to_dict(c)
    repo.save_weekly_curriculum(username, str(start), json.dumps(payload, ensure_ascii=False))
    return payload

@router.get("/pro/reviews/due")
def due_reviews(username: str, due_date: str):
    repo = get_repo()
    return {"items": repo.list_due_reviews(username=username, due_date=due_date, limit=30)}

@router.post("/pro/reviews/done")
def mark_done(review_id: int):
    repo = get_repo()
    repo.mark_review_done(review_id)
    return {"ok": True}
