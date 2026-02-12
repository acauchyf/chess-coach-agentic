from __future__ import annotations
from typing import List, Optional, Dict, Any
from dataclasses import asdict

from chess_coach.domain.course import Course, Lesson
from chess_coach.domain.course_examples import CourseExample
from chess_coach.application.ports.llm_port import LLMPort, ChatMessage


def _examples_for_topic(repo, username: str, topic: str, limit: int = 6) -> List[CourseExample]:
    t = topic.strip()

    # Táctica: tag
    if t.lower().startswith("táctica:") or t.lower().startswith("tactica:"):
        tag = t.split(":", 1)[1].strip().lower()
        rows = repo.find_puzzles_by_tag(username=username, tag=tag, limit=limit)
        return [_row_to_example(r, note=f"Motivo '{tag}'") for r in rows]

    # IQP / colgantes: try map to tags first
    if "iqp" in t.lower() or "aislado" in t.lower():
        # try common tags: iqp, isolated, isolated_pawn
        for tag in ["iqp", "isolated", "isolated_pawn", "isolated_queen_pawn"]:
            rows = repo.find_puzzles_by_tag(username=username, tag=tag, limit=limit)
            if rows:
                return [_row_to_example(r, note="Ejemplo desde tu blunder en IQP") for r in rows]

    if "colgante" in t.lower() or "hanging" in t.lower():
        for tag in ["hanging", "hanging_pawns", "colgantes"]:
            rows = repo.find_puzzles_by_tag(username=username, tag=tag, limit=limit)
            if rows:
                return [_row_to_example(r, note="Ejemplo desde tu blunder en peones colgantes") for r in rows]

    # Apertura: pick opening games then first puzzle from each game
    if t.lower().startswith("apertura:"):
        opening = t.split(":", 1)[1].strip()
        games = repo.list_games_by_opening(username=username, opening=opening, limit=15)
        examples: List[CourseExample] = []
        for g in games:
            rows = repo.find_puzzles_by_game(username=username, game_id=g["game_id"], limit=3)
            if not rows:
                continue
            examples.append(_row_to_example(rows[0], note=f"Error típico dentro de {opening}", meta={"opening": opening}))
            if len(examples) >= limit:
                break
        return examples

    # Fallback: take toughest puzzles overall
    rows = repo.list_puzzles_for_session(username=username, limit=limit, fatigue=5)
    return [_row_to_example(r, note="Ejemplo general desde tus blunders") for r in rows]


def _row_to_example(r: Dict[str, Any], note: str, meta: Optional[Dict[str, Any]] = None) -> CourseExample:
    tags = (r.get("tags") or "")
    tag_list = [x for x in tags.split(",") if x] if tags else []
    return CourseExample(
        game_id=str(r.get("game_id") or ""),
        ply=int(r.get("ply") or 0),
        fen=str(r.get("fen_before") or r.get("fen") or ""),
        move_uci=r.get("move_uci"),
        best_move_uci=r.get("best_move_uci"),
        tags=tag_list,
        swing_cp=int(r.get("swing_cp")) if r.get("swing_cp") is not None else None,
        note=note,
        meta=meta or {},
    )


def build_adaptive_course_for_user(repo, username: str, topic: str, llm: Optional[LLMPort] = None, limit_examples: int = 6) -> Dict[str, Any]:
    examples = _examples_for_topic(repo, username, topic, limit=limit_examples)

    # Base skeleton (teacher structure)
    lessons: List[Lesson] = [
        Lesson(
            title="Diagnóstico rápido (tu patrón)",
            objectives=["Entender qué te está costando", "Convertirlo en una regla accionable"],
            key_ideas=["Vamos a usar tus posiciones reales, no teoría genérica."],
            common_mistakes=["Jugar rápido sin checklist", "No identificar el 'momento crítico'"],
            mini_quiz=["¿Cuál fue tu primera candidata aquí? ¿y por qué?"],
        ),
        Lesson(
            title="Reglas + Checklist",
            objectives=["Crear 3-5 reglas", "Aplicarlas bajo presión"],
            key_ideas=["Checklist de 20-30s antes de jugar el movimiento crítico."],
            common_mistakes=["Buscar táctica donde no existe", "Ignorar amenazas del rival"],
            mini_quiz=["Escribe tu checklist (3 items)."],
        ),
        Lesson(
            title="Ejercicios desde tus partidas",
            objectives=["Resolver 4-6 posiciones tuyas", "Comparar con la mejor línea"],
            key_ideas=["Repetición espaciada: hoy / +2 días / +7 días."],
            common_mistakes=["Resolver sin calcular variantes", "No justificar por qué el rival no tiene recurso"],
            mini_quiz=["¿Qué recurso defensivo tenía el rival en el ejemplo 1?"],
        ),
    ]

    course = Course(
        topic=topic,
        subtitle=f"Curso adaptativo para {username} (con posiciones reales)",
        estimated_minutes=40,
        lessons=lessons,
        references=["Tus propias partidas + Stockfish", "Repetición espaciada"],
        metadata={"username": username, "examples_count": len(examples)},
    )

    # If LLM present: craft professional teacher notes tailored to the examples
    teacher_notes = None
    if llm is not None:
        # keep prompt compact and tool-safe
        ex_lines = []
        for i, ex in enumerate(examples, start=1):
            ex_lines.append(f"{i}) FEN: {ex.fen} | move: {ex.move_uci} | best: {ex.best_move_uci} | tags: {','.join(ex.tags)} | swing: {ex.swing_cp}")
        prompt = (
            "Actúa como entrenador profesional (nivel Maestro/IM). "
            "Crea una mini-lección para este alumno basada en SUS ejemplos reales.\n"
            f"Tema: {topic}\n"
            f"Alumno: {username}\n"
            "Devuelve:\n"
            "- 5 reglas prácticas (cortas)\n"
            "- 3 errores típicos del alumno (inferidos de ejemplos)\n"
            "- 1 checklist de 20 segundos\n"
            "- Para los 2 primeros ejemplos: explica el plan correcto en 4-6 líneas cada uno\n"
            "No inventes partidas; usa solo los ejemplos listados.\n\n"
            "EJEMPLOS:\n" + "\n".join(ex_lines)
        )
        messages = [
            ChatMessage(role="system", content="Eres un entrenador de ajedrez profesional. Responde en español. Sé preciso."),
            ChatMessage(role="user", content=prompt),
        ]
        try:
            teacher_notes = llm.chat(messages, temperature=0.25).strip()
        except Exception:
            teacher_notes = None

    return {
        "course": {
            "topic": course.topic,
            "subtitle": course.subtitle,
            "estimated_minutes": course.estimated_minutes,
            "lessons": [asdict(l) for l in course.lessons],
            "references": course.references,
            "metadata": {**course.metadata, **({"teacher_notes": teacher_notes} if teacher_notes else {})},
        },
        "examples": [asdict(e) for e in examples],
    }
