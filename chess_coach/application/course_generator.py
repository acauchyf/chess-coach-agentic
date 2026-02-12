from __future__ import annotations
from typing import Optional, Dict, Any
from dataclasses import asdict

from chess_coach.domain.course import Course, Lesson
from chess_coach.application.ports.llm_port import LLMPort, ChatMessage


def _iqp_template() -> Course:
    lessons = [
        Lesson(
            title="Qué es el peón aislado (IQP) y por qué importa",
            objectives=["Reconocer IQP", "Ventajas dinámicas vs debilidades estáticas"],
            key_ideas=[
                "El IQP da líneas abiertas y actividad a cambio de una debilidad fija.",
                "La casilla delante del peón (d5/d4) es el punto de bloqueo.",
                "Si el ataque no progresa, el final suele favorecer al defensor."
            ],
            common_mistakes=[
                "Cambiar demasiadas piezas cuando tienes el IQP.",
                "Empujar el peón sin preparación."
            ],
            mini_quiz=[
                "¿Qué casilla se bloquea contra el IQP?",
                "¿Qué bando suele preferir cambios en finales?"
            ],
        ),
        Lesson(
            title="Planes típicos para el bando con IQP",
            objectives=["Plan de piezas", "Cuándo atacar"],
            key_ideas=[
                "Torres en e/c; dama e2; alfil d3/c2.",
                "Caballo a e5/c5 según estructura.",
                "Busca actividad; evita simplificar sin compensación."
            ],
            common_mistakes=["Atacar sin abrir líneas", "Ignorar transiciones a final"],
            mini_quiz=["Nombra 2 colocaciones típicas de torres con IQP."],
        ),
        Lesson(
            title="Cómo defender contra el IQP",
            objectives=["Bloqueo", "Simplificación", "Captura del peón"],
            key_ideas=[
                "Bloquea d5/d4 con pieza estable.",
                "Cambia piezas menores si estás bien coordinado.",
                "Captura el peón cuando el bando activo pierda iniciativa."
            ],
            common_mistakes=["Capturar demasiado pronto", "Permitir ruptura liberadora"],
            mini_quiz=["¿Qué pasa si capturas el IQP demasiado pronto?"],
        ),
        Lesson(
            title="Ejercicios (desde tus partidas)",
            objectives=["Convertir errores en reglas", "Aplicar en 3 posiciones típicas"],
            key_ideas=[
                "Revisa posiciones: antes de empujar, antes de sacrificar, transición a final.",
                "Escribe 2 reglas personales para repetir."
            ],
            common_mistakes=["Analizar sin objetivo"],
            mini_quiz=["Escribe 2 reglas personales para IQP."],
        ),
    ]
    return Course(
        topic="Peón aislado (IQP)",
        subtitle="Planes, casillas clave, defensa y práctica",
        estimated_minutes=40,
        lessons=lessons,
        references=["Tarrasch Defense, Panov Attack, QGD Exchange"],
        metadata={"structure_tag": "isolated_queen_pawn"},
    )


def _hanging_pawns_template() -> Course:
    lessons = [
        Lesson(
            title="Peones colgantes: definición y evaluación",
            objectives=["Reconocer estructura", "Entender dinámica avance/bloqueo"],
            key_ideas=[
                "Peones en c+d sin soporte b/e.",
                "Son fuertes si pueden avanzar; débiles si se bloquean."
            ],
            common_mistakes=["Avanzar sin soporte", "Permitir bloqueo fijo"],
            mini_quiz=["¿Cuál es el plan defensivo típico contra colgantes?"],
        ),
        Lesson(
            title="Planes de avance (c5/d5) y rupturas",
            objectives=["Elegir el momento", "Coordinar piezas"],
            key_ideas=["Prepara con piezas detrás del avance.", "Tras avanzar, busca actividad y columnas."],
            common_mistakes=["Avanzar mal coordinado"],
            mini_quiz=["¿Qué indica que es buen momento para avanzar?"],
        ),
        Lesson(
            title="Jugar contra peones colgantes",
            objectives=["Bloqueo", "Ataque a peones", "Simplificación"],
            key_ideas=["Bloquea casillas clave.", "Ataca peones con piezas y torres."],
            common_mistakes=["Cambiar el bloqueador"],
            mini_quiz=["¿Qué pieza suele ser el mejor bloqueador?"],
        ),
    ]
    return Course(
        topic="Peones colgantes",
        subtitle="Cuándo avanzar, cuándo mantener, y cómo defender",
        estimated_minutes=30,
        lessons=lessons,
        references=["QGD, Nimzo, Catalana (estructuras con cxd)"],
        metadata={"structure_tag": "hanging_pawns"},
    )


def generate_course(topic: str, llm: Optional[LLMPort] = None) -> Course:
    t = topic.strip().lower()
    if "iqp" in t or "aislado" in t:
        base = _iqp_template()
    elif "colgante" in t or "hanging" in t:
        base = _hanging_pawns_template()
    else:
        base = Course(
            topic=topic,
            subtitle="Curso (plantilla) — se ampliará con IA y tus partidas",
            estimated_minutes=25,
            lessons=[Lesson(
                title="Introducción",
                objectives=["Entender el tema", "Detectarlo en tus partidas"],
                key_ideas=["Lo convertiremos en reglas accionables."],
                common_mistakes=["No anotar decisiones críticas"],
                mini_quiz=["¿Qué quieres mejorar exactamente con este tema?"],
            )],
            references=[],
            metadata={},
        )

    if llm is None:
        return base

    messages = [
        ChatMessage(role="system", content="Eres un entrenador de ajedrez. Responde en español. Sé concreto."),
        ChatMessage(role="user", content=f"Dame 5 reglas prácticas y 3 errores típicos sobre: {base.topic}. Formato: viñetas."),
    ]
    try:
        extra = llm.chat(messages, temperature=0.3).strip()
        meta = dict(base.metadata)
        meta["llm_rules_and_mistakes"] = extra
        return Course(
            topic=base.topic,
            subtitle=base.subtitle,
            estimated_minutes=base.estimated_minutes,
            lessons=base.lessons,
            references=base.references,
            metadata=meta,
        )
    except Exception:
        return base


def course_to_dict(c: Course) -> Dict[str, Any]:
    return {
        "topic": c.topic,
        "subtitle": c.subtitle,
        "estimated_minutes": c.estimated_minutes,
        "lessons": [asdict(l) for l in c.lessons],
        "references": c.references,
        "metadata": c.metadata,
    }
