from __future__ import annotations

import requests
from datetime import datetime, timezone
from typing import List, Optional
import re

from chess_coach.domain.models import Game
from chess_coach.ports.services import GameSource


_RE_TAG = re.compile(r'^\[(\w+)\s+\"(.*)\"\]\s*$')


def _split_pgn_games(pgn_text: str) -> List[str]:
    chunks: List[str] = []
    current: List[str] = []

    for line in pgn_text.splitlines():
        if line.startswith("[Event ") and current:
            chunks.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)

    if current:
        last = "\n".join(current).strip()
        if last:
            chunks.append(last)

    return chunks


def _get_tag(pgn: str, name: str) -> Optional[str]:
    for line in pgn.splitlines():
        m = _RE_TAG.match(line.strip())
        if not m:
            continue
        if m.group(1) == name:
            return m.group(2)
    return None


class LichessClient(GameSource):
    BASE = "https://lichess.org"

    def fetch_games(self, username: str, limit: int) -> List[Game]:
        url = f"{self.BASE}/api/games/user/{username}"
        headers = {"Accept": "application/x-chess-pgn"}
        params = {"max": limit, "opening": "true", "clocks": "true"}

        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code == 404:
            raise ValueError(f"Usuario '{username}' no encontrado en Lichess (404).")
        r.raise_for_status()

        games: List[Game] = []
        for pgn in _split_pgn_games(r.text):
            site = _get_tag(pgn, "Site") or ""
            game_id = site.rsplit("/", 1)[-1] if "/" in site else (site or "unknown")

            utc_date = _get_tag(pgn, "UTCDate")
            utc_time = _get_tag(pgn, "UTCTime")
            played_at = datetime.now(tz=timezone.utc)
            if utc_date and utc_time:
                try:
                    played_at = datetime.strptime(
                        f"{utc_date} {utc_time}", "%Y.%m.%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc)
                except ValueError:
                    pass

            white = _get_tag(pgn, "White") or "white"
            black = _get_tag(pgn, "Black") or "black"
            result = _get_tag(pgn, "Result") or "*"
            opening = _get_tag(pgn, "Opening")
            time_control = _get_tag(pgn, "TimeControl")
            if time_control == "-":
                time_control = None

            games.append(
                Game(
                    platform="lichess",
                    game_id=game_id,
                    played_at=played_at,
                    white=white,
                    black=black,
                    result=result,
                    pgn=pgn,
                    opening=opening,
                    time_control=time_control,
                )
            )

        return games
