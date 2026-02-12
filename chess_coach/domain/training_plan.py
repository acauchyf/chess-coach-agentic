from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class TrainingItem:
    area: str
    title: str
    why: str
    duration_min: int


@dataclass(frozen=True)
class WeeklyPlan:
    headline: str
    items: List[TrainingItem]
