from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional

class BootstrapRequest(BaseModel):
    platform: str = Field('lichess', description='lichess | chesscom')
    username: str = Field(..., min_length=2)
    fatigue: Optional[int] = Field(None, ge=0, le=10, description="0=full energy, 10=exhausted")
    import_games: int = Field(50, ge=1, le=200)
    mine_blunders_from_games: int = Field(30, ge=1, le=200)
    max_new_puzzles: int = Field(30, ge=1, le=200)
    daily_limit: int = Field(10, ge=1, le=50)

class CheckinRequest(BaseModel):
    username: str
    fatigue: int = Field(..., ge=0, le=10)
    note: Optional[str] = None

class DailyPuzzleOut(BaseModel):
    puzzle_id: int
    area: str
    game_id: str
    ply: int
    fen: str
    hint: str
    pv_uci: List[str]

class AttemptRequest(BaseModel):
    move_uci: str = Field(..., min_length=4, max_length=6)
    step: int = Field(..., ge=0, le=40)

class AttemptResponse(BaseModel):
    correct: bool
    done: bool
    message: str
    expected: Optional[str]
