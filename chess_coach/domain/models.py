from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Game:
    platform: str
    game_id: str
    played_at: datetime
    white: str
    black: str
    result: str
    pgn: str
    opening: Optional[str] = None
    time_control: Optional[str] = None
