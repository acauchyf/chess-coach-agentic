from __future__ import annotations

import argparse

from chess_coach.infrastructure.lichess_client import LichessClient
from chess_coach.infrastructure.sqlite_repo import SqliteGameRepository
from chess_coach.application.use_cases import ImportGamesUseCase, BuildWeeklyPlanUseCase


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--db", default="chess_coach.db")
    parser.add_argument("--stockfish", default="stockfish")
    parser.add_argument("--depth", type=int, default=12)
    parser.add_argument("--daily", type=int, default=10)
    args = parser.parse_args()

    source = LichessClient()
    repo = SqliteGameRepository(db_path=args.db)

    imported = ImportGamesUseCase(source=source, repo=repo).execute(
        username=args.username,
        limit=args.games
    )

    plan = BuildWeeklyPlanUseCase().execute(
        username=args.username,
        games=imported
    )

    print("\n" + "=" * 60)
    print(plan.headline)
    print("=" * 60)
    for i, item in enumerate(plan.items, start=1):
        print(f"{i}. [{item.area}] {item.title} — {item.duration_min} min")
        print(f"   - Por qué: {item.why}")
    print("=" * 60)
    print(f"Partidas analizadas: {len(imported)}")

    print("\n" + "=" * 60)
    print("Analizando blunders (Stockfish)...")
    print("=" * 60)

    try:
        from chess_coach.infrastructure.stockfish_engine import StockfishEngine
        from chess_coach.application.blunder_mining import find_blunders
        from chess_coach.application.daily_session import build_daily_session

        engine = StockfishEngine(path=args.stockfish, depth=args.depth)
        blunders = find_blunders(imported, engine, max_blunders=50)

        if not blunders:
            print("No se detectaron blunders claros con el umbral actual.")
            print("\nProceso completado.\n")
            return

        print("\nTop blunders encontrados:\n")
        for b in blunders[:5]:
            print(f"Game {b.game_id}")
            print(f"Ply {b.ply}")
            print(f"Jugaste: {b.move_uci}")
            print(f"Mejor era: {b.best_move_uci}")
            if b.swing_cp >= 90000:
                print("Swing: MATE / táctica decisiva")
            else:
                print(f"Swing: {b.swing_cp} cp")
            print(f"FEN: {b.fen_before}")
            print("-" * 40)

        tuples = [
            (b.game_id, b.ply, b.fen_before, b.move_uci, b.best_move_uci, b.swing_cp)
            for b in blunders
        ]
        repo.save_puzzles(username=args.username, platform="lichess", puzzles=tuples)

        rows = repo.list_puzzles(username=args.username, limit=args.daily)
        session = build_daily_session(rows, limit=args.daily)

        print("\n" + "=" * 60)
        print(f"Sesión diaria ({args.daily} puzzles de tus blunders)")
        print("=" * 60)
        for i, p in enumerate(session, start=1):
            print(f"{i}. [{p.area}] Game {p.game_id} ply {p.ply}")
            print(f"   FEN: {p.fen}")
            print(f"   Hint: {p.hint}")
            print(f"   Solución (UCI): {p.best_uci}")
            print("-" * 40)

    except FileNotFoundError:
        print("⚠ Stockfish no encontrado. Instala con:")
        print("sudo apt install stockfish")
        print("O pasa la ruta con --stockfish /usr/games/stockfish")

    except Exception as e:
        print(f"⚠ Error en análisis de blunders / sesión diaria: {e}")

    print("\nProceso completado.\n")


if __name__ == "__main__":
    main()
