from __future__ import annotations

from fastapi import APIRouter

from chess_coach.api.deps import get_repo, get_game_source, get_engine, get_llm
from chess_coach.api.schemas import BootstrapRequest, CheckinRequest
from chess_coach.api.schemas_chat import ChatRequest
from chess_coach.api.schemas_teacher import TodayPlanRequest
from chess_coach.application.use_cases import ImportGamesUseCase
from chess_coach.application.blunder_mining import find_blunders
from chess_coach.agents.coach_agent import CoachAgent
from chess_coach.application.pattern_tagger import tag_from_position_and_pv

router = APIRouter(tags=["coach"])

@router.post("/coach/checkin")
def checkin(req: CheckinRequest):
    repo = get_repo()
    repo.save_checkin(username=req.username, fatigue=req.fatigue, note=req.note)
    return {"ok": True, "fatigue": req.fatigue}

@router.post("/coach/bootstrap")
def bootstrap(req: BootstrapRequest):
    repo = get_repo()
    source = get_game_source(req.platform)
    engine = get_engine()
    agent = CoachAgent()

    fatigue = agent.infer_fatigue(repo, req.username, req.fatigue)

    imported = 0
    if repo.count_games(req.username) == 0:
        ImportGamesUseCase(source=source, repo=repo).execute(username=req.username, limit=req.import_games)
        imported = req.import_games

    mined = 0
    if repo.count_puzzles(req.username) < req.daily_limit:
        games = repo.list_recent_games(req.username, limit=req.mine_blunders_from_games)
        blunders = find_blunders(games, engine, max_blunders=req.max_new_puzzles)
        tuples = []
        for b in blunders:
            tags = tag_from_position_and_pv(b.fen_before, b.pv_uci)
            tuples.append((
                b.game_id, b.ply, b.fen_before, b.move_uci, b.best_move_uci,
                " ".join(b.pv_uci), ",".join([t.value for t in tags]), b.swing_cp
            ))
        repo.save_puzzles(username=req.username, platform="lichess", puzzles=tuples)
        mined = len(tuples)

    tagged = agent.tag_puzzles_if_missing(repo, req.username, limit=200)

    rows = repo.list_puzzles_for_session(req.username, limit=req.daily_limit, fatigue=fatigue)
    puzzles = []
    for r in rows:
        tags = (r.get("tags") or "").split(",") if r.get("tags") else []
        area = "mate" if "mate" in tags else "tactics"
        hint = "Checks primero. Busca MATE o ganancia forzada."
        puzzles.append({
            "puzzle_id": r["id"],
            "area": area,
            "game_id": r["game_id"],
            "ply": r["ply"],
            "fen": r["fen_before"],
            "hint": hint,
            "pv_uci": (r.get("pv_uci") or "").split(),
            "tags": tags,
            "attempts": r["attempts"],
            "solved": r["solved"],
        })

    decision = {"fatigue": fatigue, "imported": imported, "mined": mined, "tagged_existing": tagged, "session_limit": req.daily_limit}
    repo.trace(req.username, "bootstrap", fatigue, decision)

    return {
        "username": req.username,
        "fatigue": fatigue,
        "puzzles": puzzles,
        "counts": {"games": repo.count_games(req.username), "puzzles": repo.count_puzzles(req.username)},
        "decision": decision,
    }

@router.post("/coach/today")
def today(req: TodayPlanRequest):
    repo = get_repo()
    agent = CoachAgent()
    return agent.daily_plan(repo, username=req.username, minutes=req.minutes, explicit_fatigue=req.fatigue)

@router.get("/coach/weekly-plan")
def weekly_plan_personalized(username: str):
    repo = get_repo()
    agent = CoachAgent()
    return agent.weekly_plan(repo, username=username)

@router.post("/coach/chat")
def chat(req: ChatRequest):
    repo = get_repo()
    agent = CoachAgent()
    llm = get_llm()
    return agent.chat(repo, req.username, req.message, llm=llm)

@router.get("/coach/traces")
def traces(username: str, limit: int = 30):
    repo = get_repo()
    return {"items": repo.list_traces(username=username, limit=limit)}
