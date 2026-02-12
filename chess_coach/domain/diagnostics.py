from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass(frozen=True)
class SkillSignal:
    key: str
    label: str
    score: float  # 0..1 higher => more urgent
    evidence: Dict[str, Any]

@dataclass(frozen=True)
class Diagnostics:
    username: str
    signals: List[SkillSignal]
    meta: Dict[str, Any]
