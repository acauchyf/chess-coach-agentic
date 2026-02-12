# Chess Coach — Fullstack (Agentic + Hexagonal/DDD-ish)

Este ZIP añade:
- **Outbound adapter**: SQLite repo (`chess_coach/infrastructure/sqlite_repo.py`)
- **Inbound adapter**: FastAPI (`chess_coach/api/*`)
- **Frontend**: Next.js + tablero interactivo (`web/chess-coach-web`)

## 0) Requisitos
- Python 3.10+
- Node 18+
- Stockfish instalado (en Linux normalmente: `sudo apt install stockfish`)

## 1) Backend API
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# opcional
export STOCKFISH_PATH=stockfish
export CHESS_COACH_DB=chess_coach.db

uvicorn chess_coach.api.app:app --reload --port 8000
```

Probar:
```bash
curl http://localhost:8000/v1/health
```

## 2) Front
```bash
cd web/chess-coach-web
cp .env.local.example .env.local
npm install
npm run dev
```

Abrir:
- http://localhost:3000/session

Pulsa **Bootstrap**:
- Importa partidas desde Lichess si no hay
- Mina blunders (Stockfish) si no hay puzzles suficientes
- Genera sesión diaria y permite resolver con tablero interactivo

## 3) Hexagonal / DDD (lo que queda preparado)
- Domain: `chess_coach/domain`
- Ports: `chess_coach/ports`
- Application: `chess_coach/application`
- Agents (orquestación cap 6): `chess_coach/agents`
- Adapters:
  - Inbound: `chess_coach/api`
  - Outbound: `chess_coach/infrastructure/*` (Lichess, Stockfish, SQLite)

## 4) Próximos pasos (microservicios)
- Separar en:
  1) ingestion-service (lichess import)
  2) analysis-service (stockfish + blunder mining)
  3) training-service (puzzles + sessions)
  4) coach-service (agent/orchestrator)
- Mantener contratos (DTOs) y puertos como “anti-corruption layer”.


## v3: Multi-move + personalización por fatiga
- Puzzles guardan PV (línea) y el front valida paso a paso.
- Campo 'Fatiga' (0-10) para que el coach adapte selección (más fácil cuando estás cansado).
- Se guardan stats básicos de puzzles (attempts/solved).


## v4: B1+B2+B3 (tagging + plan personalizado + tracing + chat)
- B1: tagging de puzzles por motivos tácticos (mate/check/fork/pin/hanging_piece...)
- B2: plan semanal personalizado en base a stats por tags + estructuras de peones (IQP/hanging pawns)
- B3: tracing estilo 6_mcp (coach_traces en SQLite) y UI /traces
- Chat: /coach/chat (reglas deterministas) + panel en /session
- Fatiga: inferida por rendimiento reciente si no se indica.


## Performance (Bootstrap speed)
Set env vars before running backend:

```bash
export STOCKFISH_DEPTH=8
export STOCKFISH_THREADS=2
export STOCKFISH_HASH_MB=128
```

Tip: reduce mine_blunders_from_games/max_new_puzzles in /session bootstrap payload for even faster runs.


## v6: Profe real (coach = núcleo) + IA opcional (Ollama/OpenAI)

### Plan diario controlado por el coach
- UI: `/today`
- API: `POST /v1/coach/today` con `{username, minutes}`

### Activar IA (opcional)
Si no configuras IA, el coach responde en modo determinista (sin tokens).

#### Ollama (barato/local)
```bash
export LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=qwen2.5:7b-instruct
```

#### OpenAI (mejor/rápido pero cuesta)
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=...
export OPENAI_MODEL=gpt-4o-mini
```

Notas:
- El chat usa un contrato JSON para “tool-calling” compatible con ambos proveedores.
- El dominio/planificación siguen siendo deterministas (DDD); la IA se usa para explicar y conversar.


## v7: Cursos + Memoria + Voz (a la vez)
- Cursos: UI `/courses` y API `GET /v1/courses/course?topic=...` (IQP / peones colgantes).
- Memoria: historial en SQLite `coach_messages` (últimos 12 mensajes se reinyectan al LLM).
- Voz: botón "Voz ON/OFF" en `/session` usando Web Speech API del navegador (sin backend).


## v8: Cursos adaptativos por urgencia (profe profesional)
- UI: `/diagnostics` muestra señales (táctica/estructuras/aperturas) y recomendaciones por urgencia.
- API: `GET /v1/diagnostics` y `GET /v1/diagnostics/recommendations`
- Plan diario añade `recommended_courses` calculado por diagnóstico.
- Endpoint: `GET /v1/courses/adaptive?topic=...`


## v9: Import multi-fuente (Lichess + Chess.com)
- Bootstrap ahora acepta `platform`: `lichess` | `chesscom`.
- Front `/session` tiene selector de fuente.


## v10: Cursos adaptativos con ejemplos reales del alumno
- Endpoint: `GET /v1/courses/adaptive/user?username=...&topic=...`
  - Devuelve `{ course, examples }`
  - `examples` son posiciones (FEN) extraídas de tus blunders/puzzles guardados.
- UI `/courses` ahora genera el curso adaptativo (por usuario) y muestra los tableros de ejemplos.


## v11+v12: MVP 1 PRO (diagnóstico fuerte + curriculum semanal)
- Pro Dashboard: `/pro`
- API:
  - `GET /v1/pro/diagnostics?username=...`
  - `GET /v1/pro/curriculum/weekly?username=...`
  - `GET /v1/pro/reviews/due?username=...&due_date=YYYY-MM-DD`

Notas:
- El diagnóstico por fases es un **proxy** barato basado en blunders/puzzles ya minados.
- Suficiente para MVP 1 pro; próxima iteración: eval por move (más caro, más preciso).
