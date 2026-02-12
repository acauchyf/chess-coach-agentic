.PHONY: venv api web

venv:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

api:
	. .venv/bin/activate && uvicorn chess_coach.api.app:app --reload --port 8000

web:
	cd web/chess-coach-web && npm install && npm run dev
