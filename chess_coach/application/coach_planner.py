from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
from collections import Counter

from chess_coach.domain.training_taxonomy import PatternTag, StructureTag, CourseSuggestion


@dataclass(frozen=True)
class TrainingBlock:
    area: str
    title: str
    duration_min: int
    why: str


@dataclass(frozen=True)
class PersonalizedPlan:
    headline: str
    fatigue: int
    blocks: List[TrainingBlock]
    courses: List[CourseSuggestion]
    focus_tags: List[str]


def build_personalized_plan(
    username: str,
    fatigue: int,
    tag_stats: Dict[str, Tuple[int, int]],  # tag -> (attempts, solved)
    structures: List[StructureTag],
    available_minutes: int = 45,  # ✅ default va al final
) -> PersonalizedPlan:

    # --- detectar debilidades
    scored = []
    for tag, (attempts, solved) in tag_stats.items():
        rate = solved / max(1, attempts)
        scored.append((rate, attempts, tag))

    scored.sort(key=lambda x: (x[0], -x[1]))  # peor ratio primero

    weak = [t for _, _, t in scored[:3]] if scored else ["hanging_piece", "check"]
    strong = [t for _, _, t in scored[-2:]] if len(scored) >= 2 else weak

    # --- política por fatiga
    if fatigue >= 8:
        headline = f"Plan suave para {username}: consolidar confianza (fatiga {fatigue}/10)"
        blocks = [
            TrainingBlock("tactics", f"Repetición guiada: {strong[0]}", 15,
                          "Buscamos flow con patrones dominados."),
            TrainingBlock("tactics", f"Revisión corta: {weak[0]}", 10,
                          "Un toque de reto, sin saturar."),
            TrainingBlock("endgames", "Finales básicos: rey activo + peones pasados", 10,
                          "Conceptos simples, alto retorno."),
        ]

    elif fatigue >= 4:
        headline = f"Plan equilibrado para {username} (fatiga {fatigue}/10)"
        blocks = [
            TrainingBlock("tactics", f"Patrón débil: {weak[0]}", 20,
                          "Atacamos tu punto débil."),
            TrainingBlock("tactics", f"Refuerzo: {strong[0]}", 10,
                          "Consolidamos confianza."),
            TrainingBlock("openings", "Repaso apertura frecuente + trampa típica", 15,
                          "Estabilidad práctica."),
        ]

    else:
        headline = f"Plan intenso para {username} (fatiga {fatigue}/10)"
        blocks = [
            TrainingBlock("tactics",
                          f"Debilidades: {weak[0]} + {weak[1] if len(weak)>1 else weak[0]}",
                          25,
                          "Energía alta: trabajamos lo incómodo."),
            TrainingBlock("analysis", "Análisis 1 partida: 3 decisiones críticas", 20,
                          "Convertimos errores en reglas."),
            TrainingBlock("endgames", "Finales técnicos: oposición + zugzwang", 15,
                          "Sube ELO rápido."),
        ]

    # --- Ajustar a minutos disponibles
    budget = max(10, int(available_minutes))
    fitted = []
    used = 0

    for b in blocks:
        if used >= budget:
            break
        remaining = budget - used
        if b.duration_min <= remaining:
            fitted.append(b)
            used += b.duration_min
        else:
            fitted.append(
                TrainingBlock(
                    b.area,
                    b.title,
                    remaining,
                    b.why + " (ajustado por tiempo disponible)"
                )
            )
            break

    blocks = fitted

    # --- Cursos según estructuras
    courses: List[CourseSuggestion] = []

    for s in structures:
        if s == StructureTag.ISOLATED_QUEEN_PAWN:
            courses.append(CourseSuggestion(
                topic="Curso: Peón aislado (IQP)",
                structure=s,
                why="Detecté IQP en tus partidas recientes.",
                recommended_minutes=35,
            ))

        if s == StructureTag.HANGING_PAWNS:
            courses.append(CourseSuggestion(
                topic="Curso: Peones colgantes",
                structure=s,
                why="Aparece estructura de peones colgantes.",
                recommended_minutes=30,
            ))

    return PersonalizedPlan(
        headline=headline,
        fatigue=fatigue,
        blocks=blocks,
        courses=courses,
        focus_tags=weak,
    )
