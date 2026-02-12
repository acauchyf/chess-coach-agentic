from __future__ import annotations
from typing import List, Set
import io
import chess
import chess.pgn

from chess_coach.domain.models import Game
from chess_coach.domain.training_taxonomy import StructureTag


def _pawn_files(board: chess.Board, color: chess.Color):
    files = []
    for sq, pc in board.piece_map().items():
        if pc.color == color and pc.piece_type == chess.PAWN:
            files.append(chess.square_file(sq))
    return sorted(files)

def _has_isolated_pawn_on_file(board: chess.Board, color: chess.Color, file_idx: int) -> bool:
    # any pawn on that file?
    pawns_on_file = [sq for sq, pc in board.piece_map().items()
                     if pc.color == color and pc.piece_type == chess.PAWN and chess.square_file(sq) == file_idx]
    if not pawns_on_file:
        return False
    adj = [file_idx - 1, file_idx + 1]
    for a in adj:
        if 0 <= a <= 7:
            if any(pc.color == color and pc.piece_type == chess.PAWN and chess.square_file(sq) == a
                   for sq, pc in board.piece_map().items()):
                return False
    return True

def detect_structures_from_games(games: List[Game], sample_move: int = 20) -> List[StructureTag]:
    tags: Set[StructureTag] = set()
    for g in games:
        game = chess.pgn.read_game(io.StringIO(g.pgn))
        if not game:
            continue
        board = game.board()
        ply = 0
        for mv in game.mainline_moves():
            board.push(mv)
            ply += 1
            if ply >= sample_move:
                break

        # IQP: isolated pawn on d-file
        if _has_isolated_pawn_on_file(board, chess.WHITE, 3) or _has_isolated_pawn_on_file(board, chess.BLACK, 3):
            tags.add(StructureTag.ISOLATED_QUEEN_PAWN)

        # Hanging pawns: pawns on c+d files with no e/b pawn support and no c/d pawn support? simple
        def _hanging(color: chess.Color) -> bool:
            has_c = any(pc.color==color and pc.piece_type==chess.PAWN and chess.square_file(sq)==2 for sq,pc in board.piece_map().items())
            has_d = any(pc.color==color and pc.piece_type==chess.PAWN and chess.square_file(sq)==3 for sq,pc in board.piece_map().items())
            if not (has_c and has_d):
                return False
            # no b/e pawns
            has_b = any(pc.color==color and pc.piece_type==chess.PAWN and chess.square_file(sq)==1 for sq,pc in board.piece_map().items())
            has_e = any(pc.color==color and pc.piece_type==chess.PAWN and chess.square_file(sq)==4 for sq,pc in board.piece_map().items())
            return (not has_b) and (not has_e)

        if _hanging(chess.WHITE) or _hanging(chess.BLACK):
            tags.add(StructureTag.HANGING_PAWNS)

    return list(tags)
