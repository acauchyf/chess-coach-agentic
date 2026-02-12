from __future__ import annotations
import chess


def classify_puzzle(fen: str, ply: int, swing_cp: int) -> str:
    if swing_cp >= 90000:
        return "mate"

    board = chess.Board(fen)
    piece_count = len(board.piece_map())

    if piece_count <= 8:
        return "endgame"

    if ply <= 20:
        return "opening"

    return "tactics"
