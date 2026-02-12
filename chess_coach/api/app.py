from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chess_coach.api.routers import coach
from chess_coach.api.routers import puzzles
from chess_coach.api.routers import courses
from chess_coach.api.routers import diagnostics
from chess_coach.api.routers import pro

app = FastAPI(title="Chess Coach Agentic MVP")

# --- CORS (permite que el frontend en :3000 se conecte al backend :8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers principales
app.include_router(coach.router, prefix="/v1")
app.include_router(puzzles.router, prefix="/v1")
app.include_router(courses.router, prefix="/v1")
app.include_router(diagnostics.router, prefix="/v1")
app.include_router(pro.router, prefix="/v1")


# --- Health check
@app.get("/health")
def health():
    return {"status": "ok"}
