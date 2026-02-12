from fastapi import APIRouter, HTTPException
from chess_coach.api.deps import get_repo
from chess_coach.api.schemas import AttemptRequest, AttemptResponse

router = APIRouter(tags=["puzzles"])

@router.get("/puzzles")
def list_puzzles(username: str, limit: int = 50):
    repo = get_repo()
    ids = repo.list_puzzle_ids(username=username, limit=limit)
    items = []
    for pid in ids:
        row = repo.get_puzzle_by_id(pid)
        if not row:
            continue
        items.append({
            "puzzle_id": row["id"],
            "game_id": row["game_id"],
            "ply": row["ply"],
            "fen": row["fen_before"],
            "best_uci": row["best_uci"],
            "pv_uci": (row.get("pv_uci") or "").split(),
            "swing_cp": row["swing_cp"],
            "attempts": row["attempts"],
            "solved": row["solved"],
        })
    return {"items": items}

@router.post("/puzzles/{puzzle_id}/attempt", response_model=AttemptResponse)
def attempt(puzzle_id: int, req: AttemptRequest):
    repo = get_repo()
    row = repo.get_puzzle_by_id(puzzle_id)
    if not row:
        raise HTTPException(status_code=404, detail="Puzzle not found")

    pv = (row.get("pv_uci") or "").split()
    if not pv:
        pv = [row["best_uci"]]

    step = int(req.step)
    if step < 0 or step >= len(pv):
        return AttemptResponse(correct=False, done=False, message="Step fuera de rango.", expected=pv[0])

    move = req.move_uci.strip().lower()
    expected = pv[step].lower()

    if move == expected:
        done = (step == len(pv) - 1)
        repo.record_attempt(puzzle_id=puzzle_id, solved=done)
        return AttemptResponse(
            correct=True,
            done=done,
            message="✅ Correcto." + (" Puzzle completado." if done else " Sigue la línea."),
            expected=(None if done else pv[step + 1]),
        )

    repo.record_attempt(puzzle_id=puzzle_id, solved=False)
    return AttemptResponse(
        correct=False,
        done=False,
        message=f"❌ No. En este paso la jugada correcta era {pv[step]}.",
        expected=pv[step],
    )
