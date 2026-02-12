from __future__ import annotations

import re
import requests
from datetime import datetime, timezone
from typing import List, Optional
import io

import chess.pgn

from chess_coach.domain.models import Game
from chess_coach.ports.services import GameSource

CHESSCOM_BASE = "https://api.chess.com/pub"

_RE_URL_ID = re.compile(r"/game/(?:live|daily|computer|analysis)/([0-9]+)")
_RE_LINK = re.compile(r'^\[(Link|Site)\s+\"(.*)\"\]\s*$')


def _extract_game_id_from_headers(pgn_text: str) -> str:
    # Try Link/Site header
    link = None
    for line in pgn_text.splitlines():
        m = _RE_LINK.match(line.strip())
        if m:
            link = m.group(2)
            break
        if line.strip() == "" and link:
            break
    if link:
        m2 = _RE_URL_ID.search(link)
        if m2:
            return m2.group(1)
        # fallback stable hash
        import hashlib
        return hashlib.sha1(link.encode("utf-8")).hexdigest()[:16]
    import hashlib
    return hashlib.sha1(pgn_text.encode("utf-8")).hexdigest()[:16]


def _played_at_from_pgn(game: chess.pgn.Game) -> datetime:
    h = game.headers
    # Chess.com often provides UTCDate + UTCTime
    utc_date = h.get("UTCDate")
    utc_time = h.get("UTCTime")
    if utc_date and utc_time:
        try:
            # UTCDate is YYYY.MM.DD, UTCTime is HH:MM:SS
            dt = datetime.strptime(f"{utc_date} {utc_time}", "%Y.%m.%d %H:%M:%S").replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    date = h.get("Date")
    if date and date != "????.??.??":
        try:
            dt = datetime.strptime(date, "%Y.%m.%d").replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            pass
    return datetime.now(timezone.utc)


def _result(h: dict) -> str:
    r = (h.get("Result") or "").strip()
    return r or "*"


def _opening(h: dict) -> Optional[str]:
    # Chess.com PGNs may contain Opening / ECO
    opening = (h.get("Opening") or "").strip()
    if opening:
        return opening
    eco = (h.get("ECO") or "").strip()
    return f"ECO {eco}" if eco else None


def _time_control(h: dict) -> Optional[str]:
    tc = (h.get("TimeControl") or "").strip()
    return tc or None


class ChessComClient(GameSource):
    """Outbound adapter for Chess.com Published Data API.

    It loads games by pulling monthly PGNs from most recent months until it reaches 'limit'.
    """

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self._http = session or requests.Session()

    def _archives(self, username: str) -> List[str]:
        url = f"{CHESSCOM_BASE}/player/{username}/games/archives"
        r = self._http.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("archives", [])

    def _pgn_month(self, archive_url: str) -> str:
        # archive_url: .../games/YYYY/MM
        url = archive_url + "/pgn"
        r = self._http.get(url, timeout=60)
        r.raise_for_status()
        return r.text

    def fetch_games(self, username: str, limit: int) -> List[Game]:
        archives = self._archives(username)
        if not archives:
            return []

        games: List[Game] = []
        # newest months last in archives list
        for archive_url in reversed(archives):
            if len(games) >= limit:
                break
            pgn_text = self._pgn_month(archive_url)
            pgn_io = io.StringIO(pgn_text)

            while len(games) < limit:
                g = chess.pgn.read_game(pgn_io)
                if g is None:
                    break
                headers = g.headers
                pgn_str = str(g).strip()
                game_id = _extract_game_id_from_headers(pgn_str)
                played_at = _played_at_from_pgn(g)
                games.append(Game(
                    platform="chesscom",
                    game_id=game_id,
                    played_at=played_at,
                    white=headers.get("White", ""),
                    black=headers.get("Black", ""),
                    result=_result(headers),
                    pgn=pgn_str,
                    opening=_opening(headers),
                    time_control=_time_control(headers),
                ))

        return games
