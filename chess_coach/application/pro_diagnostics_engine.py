from __future__ import annotations
from typing import Dict, Any, List
from collections import defaultdict
import statistics

OPENING_MAX_MOVE = 12
ENDGAME_MIN_MOVE = 40
BREAKPOINT_SWING_CP = 150
ADVANTAGE_CP = 150

def _move_number_from_ply(ply: int) -> int:
    return max(1, (ply + 1)//2)

def build_phase_stats(repo, username: str) -> Dict[str, Any]:
    rows = repo.list_puzzles(username=username, limit=5000)
    by_game = defaultdict(list)
    for r in rows:
        by_game[r["game_id"]].append(r)

    game_stats = []
    opening_swings = []
    middle_swings = []
    end_swings = []
    opening_bl = middle_bl = end_bl = 0

    for game_id, items in by_game.items():
        o=[]; m=[]; e=[]
        ob=mb=eb=0
        for it in items:
            ply = int(it.get("ply") or 0)
            swing = abs(float(it.get("swing_cp") or 0.0))
            move = _move_number_from_ply(ply)
            if move <= OPENING_MAX_MOVE:
                o.append(swing)
                if swing >= BREAKPOINT_SWING_CP: ob += 1
            elif move >= ENDGAME_MIN_MOVE:
                e.append(swing)
                if swing >= BREAKPOINT_SWING_CP: eb += 1
            else:
                m.append(swing)
                if swing >= BREAKPOINT_SWING_CP: mb += 1

        if o: opening_swings += o
        if m: middle_swings += m
        if e: end_swings += e
        opening_bl += ob; middle_bl += mb; end_bl += eb

        def avg(x): return float(statistics.mean(x)) if x else 0.0
        game_stats.append({
            "game_id": game_id,
            "opening_avg_swing": avg(o),
            "middlegame_avg_swing": avg(m),
            "endgame_avg_swing": avg(e),
            "opening_blunders": ob,
            "middlegame_blunders": mb,
            "endgame_blunders": eb,
        })

    summary = {
        "opening_avg_swing": float(statistics.mean(opening_swings)) if opening_swings else 0.0,
        "middlegame_avg_swing": float(statistics.mean(middle_swings)) if middle_swings else 0.0,
        "endgame_avg_swing": float(statistics.mean(end_swings)) if end_swings else 0.0,
        "opening_blunders": opening_bl,
        "middlegame_blunders": middle_bl,
        "endgame_blunders": end_bl,
        "games_analyzed": len(game_stats),
    }
    return {"summary": summary, "per_game": game_stats}

def build_opening_breakpoints(repo, username: str, limit_games: int = 200) -> List[Dict[str, Any]]:
    games = repo.list_recent_games(username, limit=limit_games)
    puzzles = repo.list_puzzles(username=username, limit=5000)
    by_game = defaultdict(list)
    for p in puzzles:
        by_game[p["game_id"]].append(p)

    breakpoints = defaultdict(lambda: {"count": 0, "swings": []})
    for g in games:
        opening = (g.get("opening_name") or "Unknown")
        items = sorted(by_game.get(g["game_id"], []), key=lambda x: int(x.get("ply") or 0))
        bp_move = None; bp_swing=None
        for it in items:
            ply = int(it.get("ply") or 0)
            move = _move_number_from_ply(ply)
            if move > OPENING_MAX_MOVE:
                break
            swing = abs(float(it.get("swing_cp") or 0.0))
            if swing >= BREAKPOINT_SWING_CP:
                bp_move = move; bp_swing=swing
                break
        if bp_move is not None:
            key=(opening, bp_move)
            breakpoints[key]["count"] += 1
            breakpoints[key]["swings"].append(bp_swing)

    out=[]
    for (opening, move), v in breakpoints.items():
        out.append({
            "opening_name": opening,
            "move_number": move,
            "count": v["count"],
            "avg_swing": float(statistics.mean(v["swings"])) if v["swings"] else 0.0,
        })
    out.sort(key=lambda x: (x["count"], x["avg_swing"]), reverse=True)
    return out[:25]

def build_conversion_stats(repo, username: str) -> Dict[str, Any]:
    games = repo.list_recent_games(username, limit=300)
    puzzles = repo.list_puzzles(username=username, limit=5000)
    by_game = defaultdict(list)
    for p in puzzles:
        by_game[p["game_id"]].append(p)

    total_adv = 0
    failed = 0
    u = username.lower()

    for g in games:
        res = (g.get("result") or "").strip()
        white = (g.get("white") or "").lower()
        black = (g.get("black") or "").lower()
        player_is_white = (white == u)
        won = (res == "1-0" and player_is_white) or (res == "0-1" and (not player_is_white))

        items = by_game.get(g["game_id"], [])
        had_adv = any(abs(float(it.get("swing_cp") or 0.0)) >= ADVANTAGE_CP for it in items)
        if had_adv:
            total_adv += 1
            if not won:
                failed += 1

    rate = ((total_adv - failed) / total_adv) if total_adv else 0.0
    return {"total_advantaged": total_adv, "failed_conversions": failed, "conversion_rate": rate}

def build_pro_diagnostics(repo, username: str) -> Dict[str, Any]:
    return {
        "username": username,
        "phase": build_phase_stats(repo, username),
        "opening_breakpoints": build_opening_breakpoints(repo, username),
        "conversion": build_conversion_stats(repo, username),
    }
