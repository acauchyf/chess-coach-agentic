from __future__ import annotations
from typing import List, Dict, Any
from datetime import date, timedelta

DEFAULT_OFFSETS_DAYS = [2, 7, 21]

def schedule_reviews(repo, username: str, puzzle_ids: List[int], offsets_days: List[int] = DEFAULT_OFFSETS_DAYS) -> int:
    created = 0
    today = date.today()
    for pid in puzzle_ids:
        for d in offsets_days:
            due = today + timedelta(days=d)
            if repo.review_exists(username=username, puzzle_id=pid, due_date=str(due)):
                continue
            repo.add_review(username=username, puzzle_id=pid, due_date=str(due))
            created += 1
    return created

def due_reviews(repo, username: str, due_date: str, limit: int = 20) -> List[Dict[str, Any]]:
    return repo.list_due_reviews(username=username, due_date=due_date, limit=limit)
