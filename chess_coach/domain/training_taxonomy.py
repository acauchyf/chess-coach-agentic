from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class PatternTag(str, Enum):
    MATE = "mate"
    CHECK = "check"
    FORK = "fork"
    PIN = "pin"
    SKEWER = "skewer"
    DISCOVERED_ATTACK = "discovered_attack"
    HANGING_PIECE = "hanging_piece"
    BACK_RANK = "back_rank"
    DEFLECTION = "deflection"
    ATTRACTION = "attraction"


class StructureTag(str, Enum):
    ISOLATED_QUEEN_PAWN = "isolated_queen_pawn"
    HANGING_PAWNS = "hanging_pawns"
    CARLSBAD = "carlsbad"
    OPEN_FILE = "open_file"
    OPPOSITE_SIDE_CASTLING = "opposite_side_castling"


@dataclass(frozen=True)
class TaggedPuzzle:
    puzzle_id: int
    game_id: str
    ply: int
    fen: str
    pv_uci: List[str]
    tags: List[PatternTag]
    swing_cp: int
    attempts: int = 0
    solved: int = 0


@dataclass(frozen=True)
class CourseSuggestion:
    topic: str
    structure: Optional[StructureTag]
    why: str
    recommended_minutes: int
