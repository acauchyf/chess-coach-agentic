from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import io

import chess
import chess.pgn

from chess_coach.domain.models import Game
from chess_coach.infrastructure.stockfish_engine import StockfishEngine


@dataclass(frozen=True)
class Blunder:
    game_id: str
    ply: int
    fen_before: str
    move_uci: str
    best_move_uci: str
    pv_uci: List[str]
    swing_cp: int
    is_mate: bool


def _eval_to_int(cp: Optional[int], mate: Optional[int]) -> int:
    if mate is not None:
        return 100000 if mate > 0 else -100000
    return cp or 0


def find_blunders(games: List[Game], engine: StockfishEngine, max_blunders: int = 20) -> List[Blunder]:
    blunders: List[Blunder] = []

    for g in games:
        game = chess.pgn.read_game(io.StringIO(g.pgn))
        if not game:
            continue

        board = game.board()
        ply = 0

        for move in game.mainline_moves():
            ply += 1
            fen_before = board.fen()

            before = engine.analyze(board)
            before_score_mover = _eval_to_int(before.cp, before.mate)
            pv = before.pv_uci
            best = before.best_move_uci
            played_uci = move.uci()

            # push played
            board.push(move)

            # if played best, skip
            if best and played_uci == best:
                continue

            after = engine.analyze(board)
            after_score_side_to_move = _eval_to_int(after.cp, after.mate)
            after_score_mover = -after_score_side_to_move

            swing = before_score_mover - after_score_mover

            is_mate = before.mate is not None and abs(before.mate) <= 5

            # threshold: either large swing or mate patterns
            if best and (swing >= 250 or is_mate):
                blunders.append(
                    Blunder(
                        game_id=g.game_id,
                        ply=ply,
                        fen_before=fen_before,
                        move_uci=played_uci,
                        best_move_uci=best,
                        pv_uci=pv[:8],  # keep it short for training
                        swing_cp=int(swing),
                        is_mate=is_mate,
                    )
                )

            if len(blunders) >= max_blunders:
                return sorted(blunders, key=lambda b: (b.is_mate, b.swing_cp), reverse=True)

    return sorted(blunders, key=lambda b: (b.is_mate, b.swing_cp), reverse=True)
