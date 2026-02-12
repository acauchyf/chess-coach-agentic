from __future__ import annotations
from typing import List, Set
import chess

from chess_coach.domain.training_taxonomy import PatternTag


def tag_from_position_and_pv(fen: str, pv_uci: List[str]) -> List[PatternTag]:
    """Heuristic tactical motif tagger.
    Deterministic, explainable, fast.
    """
    tags: Set[PatternTag] = set()
    board = chess.Board(fen)

    if pv_uci:
        # apply first move to see if it gives check/mate
        mv = chess.Move.from_uci(pv_uci[0])
        if mv in board.legal_moves:
            gives_check = board.gives_check(mv)
            board.push(mv)
            if gives_check:
                tags.add(PatternTag.CHECK)
            if board.is_checkmate():
                tags.add(PatternTag.MATE)
        else:
            # can't apply, keep best-effort tags
            pass

    # Back rank: king trapped by own pawns on 2nd/7th rank and mate/check patterns
    # crude but useful:
    def _is_back_rank_side(color: chess.Color) -> bool:
        ksq = board.king(color)
        if ksq is None:
            return False
        rank = chess.square_rank(ksq)
        if color == chess.WHITE and rank != 0:
            return False
        if color == chess.BLACK and rank != 7:
            return False
        # pawns in front of king on g/h/f files
        files = [chess.square_file(ksq)]
        if files[0] > 0: files.append(files[0]-1)
        if files[0] < 7: files.append(files[0]+1)
        blocked = 0
        for f in set(files):
            sq = chess.square(f, 1 if color==chess.WHITE else 6)
            piece = board.piece_at(sq)
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                blocked += 1
        return blocked >= 2

    if PatternTag.MATE in tags or PatternTag.CHECK in tags:
        if _is_back_rank_side(not board.turn):
            tags.add(PatternTag.BACK_RANK)

    # Fork: first PV move attacks 2+ higher-value pieces
    try:
        b2 = chess.Board(fen)
        if pv_uci:
            m = chess.Move.from_uci(pv_uci[0])
            if m in b2.legal_moves:
                b2.push(m)
                attacker_sq = m.to_square
                attacker = b2.piece_at(attacker_sq)
                if attacker:
                    attacked = []
                    for sq, pc in b2.piece_map().items():
                        if pc.color != attacker.color and b2.is_attacked_by(attacker.color, sq):
                            attacked.append((sq, pc.piece_type))
                    # count valuable targets (>= rook) or king+piece
                    valuable = [t for t in attacked if t[1] in (chess.QUEEN, chess.ROOK)]
                    if len(valuable) >= 2:
                        tags.add(PatternTag.FORK)
    except Exception:
        pass

    # Pin / Skewer: detect along lines from king/queen/rook through a piece
    # We approximate by checking if a move results in a piece being pinned to king.
    try:
        b3 = chess.Board(fen)
        if pv_uci:
            m = chess.Move.from_uci(pv_uci[0])
            if m in b3.legal_moves:
                b3.push(m)
                # any enemy piece pinned to king now?
                for sq, pc in b3.piece_map().items():
                    if pc.color != b3.turn:  # side that just moved is not b3.turn
                        continue
                # chess library has is_pinned(color, square)
                mover_color = not b3.turn
                enemy_color = b3.turn
                for sq, pc in b3.piece_map().items():
                    if pc.color == enemy_color and b3.is_pinned(enemy_color, sq):
                        tags.add(PatternTag.PIN)
                        break
    except Exception:
        pass

    # Hanging piece: if PV starts with capture and captured piece was undefended (simple)
    try:
        b4 = chess.Board(fen)
        if pv_uci:
            m = chess.Move.from_uci(pv_uci[0])
            if m in b4.legal_moves:
                captured_piece = b4.piece_at(m.to_square)
                is_capture = b4.is_capture(m)
                if is_capture and captured_piece:
                    defenders = b4.attackers(captured_piece.color, m.to_square)
                    if len(defenders) == 0:
                        tags.add(PatternTag.HANGING_PIECE)
    except Exception:
        pass

    if not tags:
        # default bucket so UI always has something
        tags.add(PatternTag.CHECK if PatternTag.CHECK in tags else PatternTag.HANGING_PIECE)

    # normalize ordering
    order = [
        PatternTag.MATE, PatternTag.BACK_RANK, PatternTag.CHECK,
        PatternTag.FORK, PatternTag.PIN, PatternTag.SKEWER,
        PatternTag.DISCOVERED_ATTACK, PatternTag.DEFLECTION, PatternTag.ATTRACTION,
        PatternTag.HANGING_PIECE
    ]
    return [t for t in order if t in tags]
