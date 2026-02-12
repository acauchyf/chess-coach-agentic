from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Any, List, Optional, Callable
import json

from chess_coach.application.pattern_tagger import tag_from_position_and_pv
from chess_coach.application.structure_detector import detect_structures_from_games
from chess_coach.application.coach_planner import build_personalized_plan
from chess_coach.application.ports.llm_port import ChatMessage, LLMPort


def _call(repo, name: str, *args, **kwargs):
    """Call repo method if exists, else return None."""
    fn = getattr(repo, name, None)
    if callable(fn):
        return fn(*args, **kwargs)
    return None


class CoachAgent:
    """Teacher-like orchestrator (Cap-6 style).

    - Core (DDD-ish): deterministic diagnostics/plan/curriculum decisions.
    - LLM is optional: used to express + tool-call + explain.
    """

    # ---------------------------
    # Fatigue
    # ---------------------------
    def infer_fatigue(self, repo, username: str, explicit: Optional[int]) -> int:
        if explicit is not None:
            _call(repo, "save_checkin", username=username, fatigue=int(explicit))
            return int(explicit)

        saved = _call(repo, "get_today_fatigue", username)
        if saved is not None:
            return int(saved)

        inferred = _call(repo, "infer_fatigue_from_recent_performance", username)
        if inferred is None:
            inferred = 5  # safe default
        _call(repo, "save_checkin", username=username, fatigue=int(inferred), note="inferred")
        return int(inferred)

    # ---------------------------
    # Puzzles tagging
    # ---------------------------
    def tag_puzzles_if_missing(self, repo, username: str, limit: int = 200) -> int:
        ids = _call(repo, "list_puzzle_ids", username=username, limit=limit) or []
        updated = 0
        for pid in ids:
            row = _call(repo, "get_puzzle_by_id", pid)
            if not row or row.get("tags"):
                continue
            pv = (row.get("pv_uci") or "").split()
            tags = tag_from_position_and_pv(row["fen_before"], pv)
            _call(repo, "update_puzzle_tags", pid, ",".join([t.value for t in tags]))
            updated += 1
        return updated

    # ---------------------------
    # Core plan builder
    # ---------------------------
    def _plan_payload(self, repo, username: str, fatigue: int, minutes: int, games: List[Any]) -> Dict[str, Any]:
        tag_stats = _call(repo, "aggregate_tag_stats", username=username) or {}
        structures = detect_structures_from_games(games, sample_move=20)

        plan = build_personalized_plan(
            username=username,
            fatigue=fatigue,
            tag_stats=tag_stats,
            structures=structures,
            available_minutes=minutes,
        )

        payload = {
            "headline": plan.headline,
            "fatigue": plan.fatigue,
            "minutes": minutes,
            "blocks": [asdict(b) for b in plan.blocks],
            "courses": [asdict(c) for c in plan.courses],
            "focus_tags": plan.focus_tags,
        }

        # Best-effort: add course recommendations from diagnostics if available
        try:
            from chess_coach.application.diagnostics_engine import build_diagnostics
            from chess_coach.application.curriculum_engine import recommend_courses, recommendations_to_dict

            diag = build_diagnostics(repo, username)
            recs = recommend_courses(diag, max_items=4)
            payload["recommended_courses"] = recommendations_to_dict(recs)
        except Exception:
            pass

        return payload

    # ---------------------------
    # Public plans
    # ---------------------------
    def daily_plan(
        self,
        repo,
        username: str,
        minutes: int = 45,
        explicit_fatigue: Optional[int] = None,
    ) -> Dict[str, Any]:
        fatigue = self.infer_fatigue(repo, username, explicit_fatigue)
        games = _call(repo, "list_recent_games", username, limit=50) or []
        plan = self._plan_payload(repo, username, fatigue, int(minutes), games)
        _call(repo, "trace", username, "today_plan", fatigue, {"minutes": minutes, "plan": plan})
        return plan

    def weekly_plan(self, repo, username: str, explicit_fatigue: Optional[int] = None) -> Dict[str, Any]:
        fatigue = self.infer_fatigue(repo, username, explicit_fatigue)
        games = _call(repo, "list_recent_games", username, limit=80) or []
        plan = self._plan_payload(repo, username, fatigue, 45, games)
        _call(repo, "trace", username, "weekly_plan", fatigue, {"plan": plan})
        return plan

    # ---------------------------
    # Bootstrap / ingestion (platform)
    # ---------------------------
    def bootstrap(
        self,
        repo,
        username: str,
        platform: str = "lichess",
        games: int = 50,
        **kwargs,
    ) -> Dict[str, Any]:
        """High-level: import games + optionally mine puzzles.

        This method is tolerant: if repo doesn't implement parts, it returns what it can.
        """
        platform = (platform or "lichess").lower().strip()
        games = int(games)

        # 1) import games
        imported = 0
        try:
            # If repo has unified importer:
            r = _call(repo, "import_games", username=username, platform=platform, limit=games)
            if isinstance(r, int):
                imported = r
            elif isinstance(r, dict) and "imported" in r:
                imported = int(r["imported"])
        except Exception:
            pass

        # 2) fallback: use fetchers if repo has them
        if imported == 0:
            try:
                if platform in ("lichess", "li"):
                    r = _call(repo, "import_lichess_games", username=username, limit=games)
                else:
                    r = _call(repo, "import_chesscom_games", username=username, limit=games)
                if isinstance(r, int):
                    imported = r
                elif isinstance(r, dict) and "imported" in r:
                    imported = int(r["imported"])
            except Exception:
                pass

        # 3) mine puzzles (best effort)
        mined = 0
        try:
            r = _call(repo, "mine_puzzles", username=username, limit_games=games)
            if isinstance(r, int):
                mined = r
            elif isinstance(r, dict) and "mined" in r:
                mined = int(r["mined"])
        except Exception:
            pass

        # 4) tag puzzles
        tagged = 0
        try:
            tagged = self.tag_puzzles_if_missing(repo, username=username, limit=300)
        except Exception:
            tagged = 0

        payload = {
            "username": username,
            "platform": platform,
            "games_requested": games,
            "imported_games": imported,
            "mined_puzzles": mined,
            "tagged_puzzles": tagged,
        }
        _call(repo, "trace", username, "bootstrap", 5, payload)
        return payload

    # ---------------------------
    # Chat (deterministic baseline)
    # ---------------------------
    def _deterministic_chat(self, repo, username: str, message: str) -> Dict[str, Any]:
        msg = (message or "").lower().strip()
        fatigue = self.infer_fatigue(repo, username, None)

        # quick commands
        if "plan" in msg and ("hoy" in msg or "diario" in msg):
            minutes = 45
            for token in msg.split():
                if token.isdigit():
                    minutes = int(token)
                    break
            plan = self.daily_plan(repo, username, minutes=minutes)
            return {"reply": plan["headline"], "plan": plan, "fatigue": fatigue}

        if "plan" in msg and ("semana" in msg or "semanal" in msg):
            plan = self.weekly_plan(repo, username)
            return {"reply": plan["headline"], "plan": plan, "fatigue": fatigue}

        if "bootstrap" in msg or "importa" in msg:
            # naive parse
            platform = "lichess" if "lichess" in msg else ("chesscom" if "chess" in msg else "lichess")
            out = self.bootstrap(repo, username=username, platform=platform, games=50)
            return {"reply": f"Bootstrap hecho: {out}", "fatigue": fatigue, "bootstrap": out}

        if "iqp" in msg or "peon aislado" in msg or "peón aislado" in msg:
            return {
                "reply": (
                    "IQP (peón aislado) — como profe: 1) defensor bloquea (d5) y cambia piezas; "
                    "2) atacante busca actividad: torres en e/c, dama e2, alfil d3/c2, salto a e5; "
                    "3) si no hay ataque, el peón cae. Si quieres, te genero un mini-curso desde TUS partidas."
                ),
                "fatigue": fatigue,
            }

        return {
            "reply": "Dime: 'plan hoy 30', 'plan hoy 45', 'plan semanal', 'bootstrap lichess', o 'curso IQP'.",
            "fatigue": fatigue,
        }

    # ---------------------------
    # Chat with LLM tool-calling
    # ---------------------------
    def chat(self, repo, username: str, message: str, llm: Optional[LLMPort] = None) -> Dict[str, Any]:
        if llm is None:
            out = self._deterministic_chat(repo, username, message)
            _call(repo, "trace", username, "chat:deterministic", out.get("fatigue", 5), {"message": message})
            return out

        fatigue = self.infer_fatigue(repo, username, None)

        system = ChatMessage(
            role="system",
            content=(
                "Eres un profesor de ajedrez (coach) extremadamente profesional. "
                "Tu misión: dirigir el entrenamiento del alumno con tareas diarias, tiempos y explicaciones. "
                "Hablas en español. No inventes datos: si necesitas datos reales del usuario, llama herramientas.\n\n"
                "DEVUELVE SIEMPRE JSON válido:\n"
                "{\n"
                '  "reply": string,\n'
                '  "tool_calls": [{"name": string, "args": object}] | []\n'
                "}\n\n"
                "Herramientas disponibles:\n"
                "- get_today_plan(username, minutes)\n"
                "- get_weekly_plan(username)\n"
                "- bootstrap(username, platform, games)\n"
                "- get_traces(username, limit)\n"
                "- get_course(topic)\n"
                "Si no necesitas herramientas: tool_calls=[]"
            ),
        )

        messages: List[ChatMessage] = [
            system,
            ChatMessage(role="user", content=f"Usuario: {username}\nFatiga estimada: {fatigue}/10\nMensaje: {message}"),
        ]

        def run_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
            if name == "get_today_plan":
                mins = int(args.get("minutes", 45))
                u = str(args.get("username", username))
                return self.daily_plan(repo, username=u, minutes=mins)

            if name == "get_weekly_plan":
                u = str(args.get("username", username))
                return self.weekly_plan(repo, username=u)

            if name == "bootstrap":
                u = str(args.get("username", username))
                platform = str(args.get("platform", "lichess"))
                games = int(args.get("games", 50))
                return self.bootstrap(repo, username=u, platform=platform, games=games)

            if name == "get_traces":
                u = str(args.get("username", username))
                lim = int(args.get("limit", 10))
                items = _call(repo, "list_traces", username=u, limit=lim) or []
                return {"items": items}

            if name == "get_course":
                # best-effort course generation (if module exists)
                try:
                    from chess_coach.application.course_generator import generate_course, course_to_dict

                    topic = str(args.get("topic", ""))
                    c = generate_course(topic, llm=llm)
                    return course_to_dict(c)
                except Exception:
                    return {"error": "course_generator_not_available"}

            return {"error": "unknown_tool"}

        # up to 2 tool rounds
        for _ in range(2):
            raw = llm.chat(messages, temperature=0.4)
            try:
                obj = json.loads(raw)
            except Exception:
                _call(repo, "trace", username, "chat:llm_parse_error", fatigue, {"raw": raw})
                return {"reply": raw.strip(), "fatigue": fatigue}

            tool_calls = obj.get("tool_calls") or []
            reply = obj.get("reply") or ""

            if not tool_calls:
                _call(repo, "trace", username, "chat:llm", fatigue, {"message": message, "reply": reply})
                try:
                    _call(repo, "save_message", username, "assistant", reply)
                except Exception:
                    pass
                return {"reply": reply, "fatigue": fatigue}

            for tc in tool_calls:
                name = tc.get("name")
                args = tc.get("args") or {}
                result = run_tool(name, args)
                messages.append(ChatMessage(role="tool", name=name, content=json.dumps(result, ensure_ascii=False)))

        out = self._deterministic_chat(repo, username, message)
        _call(repo, "trace", username, "chat:fallback", fatigue, {"message": message})
        return out
