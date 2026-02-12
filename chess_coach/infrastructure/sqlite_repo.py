from __future__ import annotations

import sqlite3
from datetime import datetime, date
from typing import List, Tuple, Optional, Dict, Any
import json

from chess_coach.domain.models import Game


class SqliteGameRepository:
    """SQLite repository (outbound adapter).

    Stores:
    - games
    - puzzles (with pv + tags)
    - puzzle_stats (attempts/solved)
    - daily checkins (fatigue)
    - coach traces
    - coach messages
    - spaced review queue
    - weekly curriculum
    """

    def __init__(self, db_path: str = "chess_coach.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _has_column(self, con: sqlite3.Connection, table: str, column: str) -> bool:
        rows = con.execute(f"PRAGMA table_info({table})").fetchall()
        return any(r["name"] == column for r in rows)

    def _init_db(self) -> None:
        with self._connect() as con:
            # IMPORTANT: executescript allows multiple CREATE statements.
            con.executescript(
                """
                PRAGMA foreign_keys=ON;
                PRAGMA journal_mode=WAL;

                CREATE TABLE IF NOT EXISTS games (
                    username TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    game_id TEXT NOT NULL,
                    played_at TEXT NOT NULL,
                    white TEXT NOT NULL,
                    black TEXT NOT NULL,
                    result TEXT,
                    opening_name TEXT NOT NULL DEFAULT 'Unknown',
                    pgn TEXT NOT NULL,
                    opening TEXT,
                    time_control TEXT,
                    PRIMARY KEY(username, platform, game_id)
                );

                CREATE TABLE IF NOT EXISTS puzzles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    game_id TEXT NOT NULL,
                    ply INTEGER NOT NULL,
                    fen_before TEXT NOT NULL,
                    played_uci TEXT NOT NULL,
                    best_uci TEXT NOT NULL,
                    pv_uci TEXT,
                    tags TEXT,
                    swing_cp INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS puzzle_stats (
                    puzzle_id INTEGER PRIMARY KEY,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    solved INTEGER NOT NULL DEFAULT 0,
                    last_attempt_at TEXT
                );

                CREATE TABLE IF NOT EXISTS checkins (
                    username TEXT NOT NULL,
                    day TEXT NOT NULL,
                    fatigue INTEGER NOT NULL,
                    note TEXT,
                    PRIMARY KEY(username, day)
                );

                CREATE TABLE IF NOT EXISTS coach_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS spaced_review_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    puzzle_id INTEGER NOT NULL,
                    due_date TEXT NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS weekly_curriculum (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS coach_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    fatigue INTEGER NOT NULL,
                    decision_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_puzzles_user_created ON puzzles(username, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_games_user_played ON games(username, played_at DESC);
                CREATE INDEX IF NOT EXISTS idx_stats_solved ON puzzle_stats(solved, attempts);
                CREATE INDEX IF NOT EXISTS idx_traces_user_created ON coach_traces(username, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_review_user_due ON spaced_review_queue(username, due_date);
                CREATE INDEX IF NOT EXISTS idx_weekly_user_start ON weekly_curriculum(username, start_date);
                CREATE INDEX IF NOT EXISTS idx_msgs_user_created ON coach_messages(username, created_at DESC);
                """
            )

            # migrations for old DBs (safe)
            if not self._has_column(con, "puzzles", "pv_uci"):
                con.execute("ALTER TABLE puzzles ADD COLUMN pv_uci TEXT")
            if not self._has_column(con, "puzzles", "tags"):
                con.execute("ALTER TABLE puzzles ADD COLUMN tags TEXT")

    # -----------------------
    # Games
    # -----------------------
    def save_games(self, games: List[Game], username: str) -> None:
        with self._connect() as con:
            for g in games:
                con.execute(
                    """
                    INSERT OR REPLACE INTO games
                      (username, platform, game_id, played_at, white, black, result, pgn, opening, time_control)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        username,
                        g.platform,
                        g.game_id,
                        g.played_at.isoformat(),
                        g.white,
                        g.black,
                        g.result,
                        g.pgn,
                        g.opening,
                        g.time_control,
                    ),
                )

    def list_recent_games(self, username: str, limit: int) -> List[Game]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT platform, game_id, played_at, white, black, result, pgn, opening, time_control
                FROM games
                WHERE username=?
                ORDER BY played_at DESC
                LIMIT ?
                """,
                (username, limit),
            ).fetchall()

        out: List[Game] = []
        for r in rows:
            out.append(
                Game(
                    platform=r["platform"],
                    game_id=r["game_id"],
                    played_at=datetime.fromisoformat(r["played_at"]),
                    white=r["white"],
                    black=r["black"],
                    result=r["result"],
                    pgn=r["pgn"],
                    opening=r["opening"],
                    time_control=r["time_control"],
                )
            )
        return out

    def count_games(self, username: str) -> int:
        with self._connect() as con:
            row = con.execute("SELECT COUNT(*) AS c FROM games WHERE username=?", (username,)).fetchone()
        return int(row["c"])

    # -----------------------
    # Puzzles
    # -----------------------
    def save_puzzles(self, username: str, platform: str, puzzles: List[Tuple]) -> None:
        """Puzzles tuples:
        (game_id, ply, fen_before, played_uci, best_uci, pv_uci, tags, swing_cp)
        where pv_uci is space-separated string, tags is comma-separated string.
        """
        now = datetime.utcnow().isoformat()
        with self._connect() as con:
            for (game_id, ply, fen_before, played_uci, best_uci, pv_uci, tags, swing_cp) in puzzles:
                con.execute(
                    """
                    INSERT INTO puzzles
                      (username, platform, game_id, ply, fen_before, played_uci, best_uci, pv_uci, tags, swing_cp, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        username,
                        platform,
                        game_id,
                        int(ply),
                        fen_before,
                        played_uci,
                        best_uci,
                        pv_uci,
                        tags,
                        int(swing_cp),
                        now,
                    ),
                )

    def count_puzzles(self, username: str) -> int:
        with self._connect() as con:
            row = con.execute("SELECT COUNT(*) AS c FROM puzzles WHERE username=?", (username,)).fetchone()
        return int(row["c"])

    def list_puzzle_ids(self, username: str, limit: int = 50) -> List[int]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT id FROM puzzles WHERE username=? ORDER BY created_at DESC, swing_cp DESC LIMIT ?",
                (username, limit),
            ).fetchall()
        return [int(r["id"]) for r in rows]

    def get_puzzle_by_id(self, puzzle_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as con:
            r = con.execute(
                """
                SELECT p.id, p.username, p.game_id, p.ply, p.fen_before, p.played_uci, p.best_uci, p.pv_uci, p.tags, p.swing_cp,
                       COALESCE(s.attempts,0) AS attempts, COALESCE(s.solved,0) AS solved
                FROM puzzles p
                LEFT JOIN puzzle_stats s ON s.puzzle_id = p.id
                WHERE p.id=?
                """,
                (puzzle_id,),
            ).fetchone()
        return dict(r) if r else None

    def update_puzzle_tags(self, puzzle_id: int, tags: str) -> None:
        with self._connect() as con:
            con.execute("UPDATE puzzles SET tags=? WHERE id=?", (tags, puzzle_id))

    def record_attempt(self, puzzle_id: int, solved: bool) -> None:
        now = datetime.utcnow().isoformat()
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO puzzle_stats(puzzle_id, attempts, solved, last_attempt_at)
                VALUES (?, 1, ?, ?)
                ON CONFLICT(puzzle_id) DO UPDATE SET
                    attempts = attempts + 1,
                    solved = CASE WHEN excluded.solved=1 THEN 1 ELSE solved END,
                    last_attempt_at = excluded.last_attempt_at
                """,
                (puzzle_id, 1 if solved else 0, now),
            )

    def list_puzzles_for_session(self, username: str, limit: int, fatigue: int) -> List[Dict[str, Any]]:
        if fatigue >= 8:
            order = "COALESCE(s.solved,0) DESC, p.swing_cp ASC, COALESCE(s.attempts,0) ASC"
        elif fatigue >= 4:
            order = "COALESCE(s.solved,0) ASC, p.swing_cp DESC"
        else:
            order = "COALESCE(s.solved,0) ASC, p.swing_cp DESC, COALESCE(s.attempts,0) ASC"

        q = f"""
            SELECT p.id, p.game_id, p.ply, p.fen_before, p.best_uci, p.pv_uci, p.tags, p.swing_cp,
                   COALESCE(s.attempts,0) AS attempts, COALESCE(s.solved,0) AS solved
            FROM puzzles p
            LEFT JOIN puzzle_stats s ON s.puzzle_id = p.id
            WHERE p.username=?
            ORDER BY {order}
            LIMIT ?
        """
        with self._connect() as con:
            rows = con.execute(q, (username, limit)).fetchall()
        return [dict(r) for r in rows]

    def aggregate_tag_stats(self, username: str, limit_puzzles: int = 200) -> Dict[str, tuple[int, int]]:
        """Return tag -> (attempts, solved)"""
        q = """
            SELECT p.tags, COALESCE(s.attempts,0) AS attempts, COALESCE(s.solved,0) AS solved
            FROM puzzles p
            LEFT JOIN puzzle_stats s ON s.puzzle_id = p.id
            WHERE p.username=?
            ORDER BY p.created_at DESC
            LIMIT ?
        """
        stats: Dict[str, list[int]] = {}
        with self._connect() as con:
            rows = con.execute(q, (username, limit_puzzles)).fetchall()

        for r in rows:
            tags = (r["tags"] or "").split(",") if r["tags"] else []
            for t in tags:
                t = t.strip()
                if not t:
                    continue
                if t not in stats:
                    stats[t] = [0, 0]
                stats[t][0] += int(r["attempts"])
                stats[t][1] += int(r["solved"])

        return {k: (v[0], v[1]) for k, v in stats.items()}

    # -----------------------
    # Fatigue checkins
    # -----------------------
    def save_checkin(self, username: str, fatigue: int, note: str | None = None) -> None:
        d = date.today().isoformat()
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO checkins(username, day, fatigue, note)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(username, day) DO UPDATE SET fatigue=excluded.fatigue, note=excluded.note
                """,
                (username, d, int(fatigue), note),
            )

    def get_today_fatigue(self, username: str) -> Optional[int]:
        d = date.today().isoformat()
        with self._connect() as con:
            r = con.execute("SELECT fatigue FROM checkins WHERE username=? AND day=?", (username, d)).fetchone()
        return int(r["fatigue"]) if r else None

    def infer_fatigue_from_recent_performance(self, username: str) -> int:
        """Heuristic: if recent attempts show low solve rate, infer higher fatigue."""
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT COALESCE(SUM(attempts),0) AS a, COALESCE(SUM(solved),0) AS s
                FROM puzzle_stats
                WHERE puzzle_id IN (SELECT id FROM puzzles WHERE username=? ORDER BY created_at DESC LIMIT 30)
                """,
                (username,),
            ).fetchone()
        a = int(rows["a"])
        s = int(rows["s"])
        if a == 0:
            return 5
        rate = s / a
        if rate < 0.10 and a >= 8:
            return 8
        if rate < 0.20 and a >= 6:
            return 7
        if rate < 0.35 and a >= 5:
            return 6
        return 5

    # -----------------------
    # Tracing (6_mcp-style)
    # -----------------------
    def trace(self, username: str, intent: str, fatigue: int, decision: Dict[str, Any]) -> None:
        now = datetime.utcnow().isoformat()
        payload = json.dumps(decision, ensure_ascii=False)
        with self._connect() as con:
            con.execute(
                "INSERT INTO coach_traces(username, created_at, intent, fatigue, decision_json) VALUES (?, ?, ?, ?, ?)",
                (username, now, intent, int(fatigue), payload),
            )

    def list_traces(self, username: str, limit: int = 30) -> List[Dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT created_at, intent, fatigue, decision_json FROM coach_traces WHERE username=? ORDER BY created_at DESC LIMIT ?",
                (username, limit),
            ).fetchall()
        out: List[Dict[str, Any]] = []
        for r in rows:
            out.append(
                {
                    "created_at": r["created_at"],
                    "intent": r["intent"],
                    "fatigue": r["fatigue"],
                    "decision": json.loads(r["decision_json"]),
                }
            )
        return out

    # -----------------------
    # Chat memory
    # -----------------------
    def save_message(self, username: str, role: str, content: str) -> None:
        now = datetime.utcnow().isoformat()
        with self._connect() as con:
            con.execute(
                "INSERT INTO coach_messages(username, created_at, role, content) VALUES (?, ?, ?, ?)",
                (username, now, role, content),
            )

    def list_messages(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT created_at, role, content FROM coach_messages WHERE username=? ORDER BY created_at DESC LIMIT ?",
                (username, limit),
            ).fetchall()
        out: List[Dict[str, Any]] = []
        for r in reversed(rows):
            out.append({"created_at": r["created_at"], "role": r["role"], "content": r["content"]})
        return out

    # -----------------------
    # Openings / exploration helpers
    # -----------------------
    def aggregate_openings(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT COALESCE(opening_name, 'Unknown') as opening, COUNT(*) as count
                FROM games
                WHERE username=?
                GROUP BY opening
                ORDER BY count DESC
                LIMIT ?
                """,
                (username, limit),
            ).fetchall()
        return [{"opening": r["opening"], "count": int(r["count"])} for r in rows]

    def find_puzzles_by_tag(self, username: str, tag: str, limit: int = 10) -> List[Dict[str, Any]]:
        # tags stored as comma-separated; use LIKE safely with delimiters
        tag = (tag or "").strip()
        if not tag:
            return []

        pattern1 = f"{tag},%"
        pattern2 = f"%,{tag},%"
        pattern3 = f"%,{tag}"
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT p.id, p.game_id, p.ply, p.fen_before, p.played_uci, p.best_uci, p.pv_uci, p.tags, p.swing_cp,
                       COALESCE(s.attempts,0) AS attempts, COALESCE(s.solved,0) AS solved
                FROM puzzles p
                LEFT JOIN puzzle_stats s ON s.puzzle_id = p.id
                WHERE p.username=? AND (p.tags=? OR p.tags LIKE ? OR p.tags LIKE ? OR p.tags LIKE ?)
                ORDER BY p.swing_cp DESC
                LIMIT ?
                """,
                (username, tag, pattern1, pattern2, pattern3, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def find_puzzles_by_game(self, username: str, game_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT p.id, p.game_id, p.ply, p.fen_before, p.played_uci, p.best_uci, p.pv_uci, p.tags, p.swing_cp,
                       COALESCE(s.attempts,0) AS attempts, COALESCE(s.solved,0) AS solved
                FROM puzzles p
                LEFT JOIN puzzle_stats s ON s.puzzle_id = p.id
                WHERE p.username=? AND p.game_id=?
                ORDER BY p.ply ASC
                LIMIT ?
                """,
                (username, game_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def list_games_by_opening(self, username: str, opening: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT game_id, played_at, opening_name, result
                FROM games
                WHERE username=? AND COALESCE(opening_name,'Unknown') = ?
                ORDER BY played_at DESC
                LIMIT ?
                """,
                (username, opening, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    # -----------------------
    # Spaced review queue
    # -----------------------
    def review_exists(self, username: str, puzzle_id: int, due_date: str) -> bool:
        with self._connect() as con:
            r = con.execute(
                "SELECT 1 FROM spaced_review_queue WHERE username=? AND puzzle_id=? AND due_date=? LIMIT 1",
                (username, puzzle_id, due_date),
            ).fetchone()
        return r is not None

    def add_review(self, username: str, puzzle_id: int, due_date: str) -> None:
        with self._connect() as con:
            con.execute(
                "INSERT INTO spaced_review_queue(username, puzzle_id, due_date, done) VALUES (?, ?, ?, 0)",
                (username, puzzle_id, due_date),
            )

    def list_due_reviews(self, username: str, due_date: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT id, puzzle_id, due_date, done
                FROM spaced_review_queue
                WHERE username=? AND due_date<=? AND done=0
                ORDER BY due_date ASC
                LIMIT ?
                """,
                (username, due_date, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def mark_review_done(self, review_id: int) -> None:
        with self._connect() as con:
            con.execute("UPDATE spaced_review_queue SET done=1 WHERE id=?", (review_id,))

    # -----------------------
    # Weekly curriculum
    # -----------------------
    def save_weekly_curriculum(self, username: str, start_date: str, payload_json: str) -> None:
        now = datetime.utcnow().isoformat()
        with self._connect() as con:
            con.execute(
                "INSERT INTO weekly_curriculum(username, start_date, payload_json, created_at) VALUES (?, ?, ?, ?)",
                (username, start_date, payload_json, now),
            )

    def get_weekly_curriculum(self, username: str, start_date: str) -> Optional[Dict[str, Any]]:
        with self._connect() as con:
            r = con.execute(
                """
                SELECT payload_json
                FROM weekly_curriculum
                WHERE username=? AND start_date=?
                ORDER BY id DESC
                LIMIT 1
                """,
                (username, start_date),
            ).fetchone()
        return json.loads(r["payload_json"]) if r else None

    # -----------------------
    # Puzzle picking helpers
    # -----------------------
    def pick_puzzles_by_tags(self, username: str, tags: List[str], limit: int = 12) -> List[int]:
        tags = [t.strip() for t in (tags or []) if t and t.strip()]
        if not tags:
            return []

        placeholders = " OR ".join(["p.tags LIKE ?"] * len(tags))
        like = [f"%{t}%" for t in tags]

        q = f"""
            SELECT p.id
            FROM puzzles p
            LEFT JOIN puzzle_stats s ON s.puzzle_id = p.id
            WHERE p.username=? AND (COALESCE(s.solved,0) = 0) AND ({placeholders})
            ORDER BY COALESCE(s.attempts,0) DESC, p.swing_cp DESC
            LIMIT ?
        """
        with self._connect() as con:
            rows = con.execute(q, (username, *like, limit)).fetchall()
        return [int(r["id"]) for r in rows]
