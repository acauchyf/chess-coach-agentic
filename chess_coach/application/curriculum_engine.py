from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from chess_coach.domain.diagnostics import Diagnostics
from chess_coach.application.course_generator import generate_course, course_to_dict

@dataclass(frozen=True)
class CourseRecommendation:
    topic: str
    urgency: float
    minutes: int
    rationale: str
    source_keys: List[str]

def recommend_courses(diag: Diagnostics, max_items: int = 6) -> List[CourseRecommendation]:
    recs: List[CourseRecommendation] = []
    tactics = [s for s in diag.signals if s.key.startswith("tactics.")]
    structures = [s for s in diag.signals if s.key.startswith("structure.")]
    openings = [s for s in diag.signals if s.key.startswith("opening.")]

    for s in tactics[:2]:
        tag = s.key.split(".", 1)[1]
        recs.append(CourseRecommendation(
            topic=f"Táctica: {tag}",
            urgency=float(s.score),
            minutes=20 if s.score > 0.6 else 15,
            rationale=f"Subimos tu consistencia en '{tag}' (ratio actual mejorable).",
            source_keys=[s.key],
        ))

    if structures:
        s = structures[0]
        topic = "Peón aislado (IQP)" if ("isolated" in s.key or "iqp" in s.key or "isolated_queen_pawn" in s.key) else                 ("Peones colgantes" if "hanging" in s.key else s.label.replace("Estructura: ", "Estructura: "))
        recs.append(CourseRecommendation(
            topic=topic,
            urgency=float(s.score),
            minutes=40 if float(s.score) > 0.6 else 30,
            rationale="Estructura frecuente en tus partidas: dominar planes te da puntos rápidos.",
            source_keys=[s.key],
        ))

    if openings:
        o = openings[0]
        name = o.label.replace("Apertura: ", "")
        recs.append(CourseRecommendation(
            topic=f"Apertura: {name}",
            urgency=float(o.score),
            minutes=25,
            rationale="Es tu apertura más frecuente: trabajamos planes + líneas críticas.",
            source_keys=[o.key],
        ))

    recs = sorted(recs, key=lambda r: r.urgency, reverse=True)[:max_items]
    return recs

def recommendations_to_dict(items: List[CourseRecommendation]) -> List[Dict[str, Any]]:
    return [asdict(x) for x in items]

def build_adaptive_course(topic: str, llm=None) -> Dict[str, Any]:
    c = generate_course(topic, llm=llm)
    return course_to_dict(c)
