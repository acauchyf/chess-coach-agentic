from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass(frozen=True)
class CourseExample:
    game_id: str
    ply: int
    fen: str
    move_uci: Optional[str]
    best_move_uci: Optional[str]
    tags: List[str]
    swing_cp: Optional[int]
    note: str
    meta: Dict[str, Any]
