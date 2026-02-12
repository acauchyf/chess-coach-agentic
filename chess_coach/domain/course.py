from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass(frozen=True)
class Lesson:
    title: str
    objectives: List[str]
    key_ideas: List[str]
    common_mistakes: List[str]
    mini_quiz: List[str]

@dataclass(frozen=True)
class Course:
    topic: str
    subtitle: str
    estimated_minutes: int
    lessons: List[Lesson]
    references: List[str]
    metadata: Dict[str, Any]
