from __future__ import annotations

import os

from chess_coach.infrastructure.lichess_client import LichessClient
from chess_coach.infrastructure.stockfish_engine import StockfishEngine
from chess_coach.infrastructure.sqlite_repo import SqliteGameRepository


def get_repo() -> SqliteGameRepository:
    db_path = os.getenv("CHESS_COACH_DB", "chess_coach.db")
    return SqliteGameRepository(db_path=db_path)


def get_lichess() -> LichessClient:
    return LichessClient()
_ENGINE: StockfishEngine | None = None

def get_engine() -> StockfishEngine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = StockfishEngine(
            path=os.getenv("STOCKFISH_PATH", "stockfish"),
            depth=int(os.getenv("STOCKFISH_DEPTH", "8")),
        )
    return _ENGINE

from chess_coach.application.ports.llm_port import LLMPort
from chess_coach.infrastructure.llm.ollama_adapter import OllamaLLMAdapter
from chess_coach.infrastructure.llm.openai_adapter import OpenAILLMAdapter


_LLM: LLMPort | None = None

def get_llm() -> LLMPort | None:
    """Configured LLM adapter or None (fallback deterministic)."""
    global _LLM
    if _LLM is not None:
        return _LLM
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    if provider == "ollama":
        _LLM = OllamaLLMAdapter()
        return _LLM
    if provider == "openai":
        _LLM = OpenAILLMAdapter()
        return _LLM
    return None

from chess_coach.infrastructure.chesscom_client import ChessComClient


_CHESSCOM: ChessComClient | None = None

def get_chesscom() -> ChessComClient:
    global _CHESSCOM
    if _CHESSCOM is None:
        _CHESSCOM = ChessComClient()
    return _CHESSCOM

def get_game_source(platform: str):
    p = (platform or "lichess").lower()
    if p in ("lichess", "li"):
        return get_lichess()
    if p in ("chesscom", "chess.com", "chess"):
        return get_chesscom()
    return get_lichess()
