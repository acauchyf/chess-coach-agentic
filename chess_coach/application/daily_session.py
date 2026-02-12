from __future__ import annotations
from dataclasses import dataclass
from typing import List
import chess

from chess_coach.application.puzzle_classifier import classify_puzzle


@dataclass(frozen=True)
class PuzzleItem:
    game_id: str
    ply: int
    fen: str
    best_uci: str
    hint: str
    area: str


def _hint_from_fen(fen: str, area: str) -> str:
    board = chess.Board(fen)
    turn = "Blancas" if board.turn else "Negras"

    if area == "mate":
        return f"Juegan {turn}. Hay táctica decisiva: busca MATE o ganancia forzada (checks primero)."
    if area == "endgame":
        return f"Juegan {turn}. Final técnico: prioriza rey activo, peones pasados y cálculo corto."
    if area == "opening":
        return f"Juegan {turn}. Apertura: desarrollo, seguridad del rey y castigos a imprecisiones."
    return f"Juegan {turn}. Táctica: checks, captures, threats. Busca la jugada más forzante."


def build_daily_session(puzzle_rows, limit: int = 10) -> List[PuzzleItem]:
    items: List[PuzzleItem] = []
    for (game_id, ply, fen, played, best, swing) in puzzle_rows[:limit]:
        area = classify_puzzle(fen=fen, ply=ply, swing_cp=swing)
        items.append(
            PuzzleItem(
                game_id=game_id,
                ply=ply,
                fen=fen,
                best_uci=best,
                hint=_hint_from_fen(fen, area),
                area=area,
            )
        )
    return items
