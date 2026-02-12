from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass(frozen=True)
class PhaseStats:
    game_id: str
    opening_avg_swing: float
    middlegame_avg_swing: float
    endgame_avg_swing: float
    opening_blunders: int
    middlegame_blunders: int
    endgame_blunders: int
    meta: Dict[str, Any]

@dataclass(frozen=True)
class OpeningBreakpoint:
    opening_name: str
    move_number: int
    count: int
    avg_swing: float

@dataclass(frozen=True)
class ConversionStats:
    total_advantaged: int
    failed_conversions: int
    conversion_rate: float

@dataclass(frozen=True)
class ProDiagnostics:
    username: str
    phase_summary: Dict[str, Any]
    opening_breakpoints: List[Dict[str, Any]]
    conversion: Dict[str, Any]
