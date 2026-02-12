from fastapi import APIRouter
from chess_coach.api.deps import get_repo

router = APIRouter(tags=["games"])

@router.get("/games/recent")
def recent_games(username: str, limit: int = 20):
    repo = get_repo()
    games = repo.list_recent_games(username=username, limit=limit)
    return {
        "items": [
            {
                "platform": g.platform,
                "game_id": g.game_id,
                "played_at": g.played_at.isoformat(),
                "white": g.white,
                "black": g.black,
                "result": g.result,
                "opening": g.opening,
                "time_control": g.time_control,
            }
            for g in games
        ]
    }
