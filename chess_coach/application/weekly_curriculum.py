from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import date, timedelta

from chess_coach.application.diagnostics_engine import build_diagnostics
from chess_coach.application.curriculum_engine import recommend_courses
from chess_coach.application.spaced_review import schedule_reviews

@dataclass(frozen=True)
class DailyBlock:
    day: str
    blocks: List[Dict[str, Any]]

@dataclass(frozen=True)
class WeeklyCurriculum:
    username: str
    start_date: str
    goals: List[str]
    days: List[DailyBlock]
    meta: Dict[str, Any]

def build_weekly_curriculum(repo, username: str, start: date | None = None) -> WeeklyCurriculum:
    start = start or date.today()
    diag = build_diagnostics(repo, username)
    recs = recommend_courses(diag, max_items=6)

    goals = [
        "Reducir blunders en el motivo principal",
        "Dominar la estructura/apertura más frecuente",
        "Mejorar conversión: cerrar partidas con ventaja",
    ]

    weakest = [s for s in diag.signals if s.key.startswith("tactics.")][:6]
    weak_tags = [s.key.split(".",1)[1] for s in weakest]

    puzzle_ids = repo.pick_puzzles_by_tags(username=username, tags=weak_tags, limit=12)
    scheduled = schedule_reviews(repo, username, puzzle_ids)

    days: List[DailyBlock] = []
    for i in range(7):
        d = start + timedelta(days=i)
        fix = recs[0] if recs else None
        second = recs[1] if len(recs) > 1 else None

        blocks = []
        if fix:
            blocks.append({"type": "fix_urgent", "title": fix.topic, "minutes": fix.minutes, "why": fix.rationale})
        if second:
            blocks.append({"type": "build_skill", "title": second.topic, "minutes": max(20, second.minutes-5), "why": second.rationale})
        blocks.append({"type": "spaced_review", "title": "Revisión espaciada (puzzles)", "minutes": 15, "why": "Reforzar patrones con repetición programada."})

        days.append(DailyBlock(day=str(d), blocks=blocks))

    meta = {
        "recommended_topics": [r.topic for r in recs[:4]],
        "weak_tags": weak_tags,
        "scheduled_reviews": scheduled,
    }
    return WeeklyCurriculum(username=username, start_date=str(start), goals=goals, days=days, meta=meta)

def curriculum_to_dict(c: WeeklyCurriculum) -> Dict[str, Any]:
    return {
        "username": c.username,
        "start_date": c.start_date,
        "goals": c.goals,
        "days": [{"day": d.day, "blocks": d.blocks} for d in c.days],
        "meta": c.meta,
    }
