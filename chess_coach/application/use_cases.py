from __future__ import annotations
from collections import Counter
from typing import List

from chess_coach.domain.models import Game
from chess_coach.domain.training_plan import WeeklyPlan, TrainingItem
from chess_coach.ports.services import GameSource
from chess_coach.ports.repositories import GameRepository


class ImportGamesUseCase:
    def __init__(self, source: GameSource, repo: GameRepository) -> None:
        self.source = source
        self.repo = repo

    def execute(self, username: str, limit: int) -> List[Game]:
        games = self.source.fetch_games(username=username, limit=limit)
        self.repo.save_games(games, username=username)
        return games


class BuildWeeklyPlanUseCase:
    def execute(self, username: str, games: List[Game]) -> WeeklyPlan:
        openings = [g.opening for g in games if g.opening]
        opening_top = Counter(openings).most_common(2)

        results = Counter(g.result for g in games)
        draws = results.get("1/2-1/2", 0)

        headline = f"Plan semanal para {username}: consistencia + puntos críticos"
        items: List[TrainingItem] = []

        if opening_top:
            items.append(
                TrainingItem(
                    area="openings",
                    title=f"Repertorio: repasar {opening_top[0][0]} — líneas críticas",
                    why="Es tu apertura más frecuente: dominar 5-8 ideas clave sube tu estabilidad.",
                    duration_min=25,
                )
            )

        items.append(
            TrainingItem(
                area="tactics",
                title="Táctica: patrones básicos (checks, captures, threats)",
                why="Base universal. En fases siguientes lo haremos 100% desde tus blunders.",
                duration_min=20,
            )
        )

        items.append(
            TrainingItem(
                area="endgames",
                title="Finales: rey activo + peones pasados (5 posiciones tipo)",
                why="Mejora técnica sin requerir cálculo brutal. Ideal para días flojos.",
                duration_min=20,
            )
        )

        items.append(
            TrainingItem(
                area="strategy",
                title="Estrategia: un plan típico en estructura recurrente (1 tema)",
                why="Aprender 1 plan por semana te da claridad en medio juego.",
                duration_min=20,
            )
        )

        if draws > 0:
            items.append(
                TrainingItem(
                    area="strategy",
                    title="Convertir ventaja: cómo empujar sin sobreextender",
                    why="Tus tablas sugieren que te falta un plan de conversión en posiciones iguales/mejores.",
                    duration_min=15,
                )
            )

        return WeeklyPlan(headline=headline, items=items)
