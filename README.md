# Chess Coach (MVP) — Lichess → Stockfish → Puzzles → Daily Session

This MVP:
- Downloads your last N games from Lichess (PGN export).
- Stores them in SQLite.
- Runs Stockfish to mine blunders (evaluation swing).
- Stores blunder positions as "puzzles".
- Prints a daily session with categorized puzzles (mate/tactics/endgame/opening).

## Requirements
- Python 3.10+ (tested with 3.12)
- Ubuntu: `sudo apt install stockfish`
- Internet access for Lichess API

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
python -m chess_coach.main --username <LICHESS_USERNAME> --games 50 --depth 12
```

If stockfish is not in PATH:
```bash
python -m chess_coach.main --username <LICHESS_USERNAME> --games 50 --depth 12 --stockfish /usr/games/stockfish
```

## Next
- Convert best move UCI -> SAN
- Generate explanations per puzzle (coach voice)
- Frontend (web) + login + progress tracking
- Agentic layer (CoachAgent + Planner + PsychologyAgent)
