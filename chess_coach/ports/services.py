from __future__ import annotations
from typing import Protocol, List
from chess_coach.domain.models import Game


class GameSource(Protocol):
    def fetch_games(self, username: str, limit: int) -> List[Game]: ...
