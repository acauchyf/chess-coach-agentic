from __future__ import annotations
from dataclasses import asdict
from typing import Dict, Any, List

from chess_coach.domain.diagnostics import Diagnostics, SkillSignal


def _norm_need(attempts: int, solved: int) -> float:
    if attempts <= 0:
        return 0.2
    ratio = solved / max(1, attempts)
    need = 1.0 - ratio
    damp = min(1.0, attempts / 10.0)
    return max(0.0, min(1.0, need * (0.5 + 0.5 * damp)))


def build_diagnostics(repo, username: str) -> Diagnostics:
    signals: List[SkillSignal] = []

    # Tactics weakness from puzzle tags
    tag_stats = repo.aggregate_tag_stats(username=username)
    for row in tag_stats:
        tag = row.get("tag") or ""
        attempts = int(row.get("attempts") or 0)
        solved = int(row.get("solved") or 0)
        if not tag:
            continue
        need = _norm_need(attempts, solved)
        signals.append(SkillSignal(
            key=f"tactics.{tag}",
            label=f"Táctica: {tag}",
            score=need,
            evidence={"attempts": attempts, "solved": solved, "solve_rate": (solved/max(1,attempts))},
        ))

    # Structures frequency
    games = repo.list_recent_games(username, limit=80)
    try:
        from chess_coach.application.structure_detector import detect_structures_from_games
        structures = detect_structures_from_games(games, sample_move=25)
    except Exception:
        structures = []
    total_struct = sum([int(s.get("count", 0)) for s in structures]) or 0
    for s in structures:
        key = s.get("key") or s.get("structure") or "structure"
        count = int(s.get("count", 0))
        freq = (count / total_struct) if total_struct else 0.0
        need = min(1.0, 0.3 + 0.7 * freq)
        signals.append(SkillSignal(
            key=f"structure.{key}",
            label=f"Estructura: {s.get('name', key)}",
            score=need,
            evidence={"count": count, "frequency": freq},
        ))

    # Openings frequency if stored
    opening_stats = []
    try:
        opening_stats = repo.aggregate_openings(username=username)
    except Exception:
        opening_stats = []
    total_open = sum([int(o.get("count", 0)) for o in opening_stats]) or 0
    for o in opening_stats[:8]:
        name = o.get("opening") or "Unknown"
        count = int(o.get("count", 0))
        freq = (count / total_open) if total_open else 0.0
        need = min(1.0, 0.25 + 0.75 * freq)
        signals.append(SkillSignal(
            key=f"opening.{name.lower().replace(' ', '_')}",
            label=f"Apertura: {name}",
            score=need,
            evidence={"count": count, "frequency": freq},
        ))

    signals = sorted(signals, key=lambda s: s.score, reverse=True)
    meta = {"tag_count": len(tag_stats), "structures_detected": len(structures), "openings_detected": len(opening_stats)}
    return Diagnostics(username=username, signals=signals, meta=meta)


def diagnostics_to_dict(d: Diagnostics) -> Dict[str, Any]:
    return {"username": d.username, "meta": d.meta, "signals": [asdict(s) for s in d.signals]}
