"""FastAPI app for Prompt Gallery: API endpoints + serving the built frontend."""
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import game

app = FastAPI(title="Prompt Gallery")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request models -----------------------------------------------------------

class CreateRoomReq(BaseModel):
    nickname: str = "Host"


class JoinReq(BaseModel):
    nickname: str = "Player"


class PlayerReq(BaseModel):
    player_id: str


class SubmitReq(BaseModel):
    player_id: str
    text: str


class VoteReq(BaseModel):
    player_id: str
    real: int
    ai: int
    bluff: int


# --- API ----------------------------------------------------------------------

@app.post("/api/rooms")
def create_room(req: CreateRoomReq):
    code, host_id = game.create_room(req.nickname)
    return {"room_code": code, "player_id": host_id}


@app.post("/api/rooms/{room_code}/join")
def join_room(room_code: str, req: JoinReq):
    pid, err = game.join_room(room_code.upper(), req.nickname)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return {"player_id": pid, "room_code": room_code.upper()}


@app.get("/api/rooms/{room_code}/state")
def room_state(room_code: str, player_id: str = ""):
    state = game.get_state(room_code.upper(), player_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return state


@app.post("/api/rooms/{room_code}/start")
def start(room_code: str, req: PlayerReq):
    err = game.start_round(room_code.upper(), req.player_id)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return {"ok": True}


@app.post("/api/rooms/{room_code}/submit")
def submit(room_code: str, req: SubmitReq):
    err = game.submit_statement(room_code.upper(), req.player_id, req.text)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return {"ok": True}


@app.post("/api/rooms/{room_code}/vote")
def vote(room_code: str, req: VoteReq):
    err = game.submit_vote(room_code.upper(), req.player_id, req.real, req.ai, req.bluff)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return {"ok": True}


@app.post("/api/rooms/{room_code}/next-round")
def next_round(room_code: str, req: PlayerReq):
    err = game.start_round(room_code.upper(), req.player_id)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return {"ok": True}


@app.post("/api/rooms/{room_code}/reset")
def reset(room_code: str, req: PlayerReq):
    err = game.reset_room(room_code.upper(), req.player_id)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return {"ok": True}


@app.get("/api/health")
def health():
    return {"status": "ok", "gemini": bool(os.environ.get("GEMINI_API_KEY")
                                            or os.environ.get("GOOGLE_API_KEY"))}


# --- Serve frontend build (if present) ---------------------------------------

_FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
_FRONTEND_DIST = os.path.abspath(_FRONTEND_DIST)

if os.path.isdir(_FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(_FRONTEND_DIST, "assets")),
              name="assets")

    @app.get("/")
    def index():
        return FileResponse(os.path.join(_FRONTEND_DIST, "index.html"))

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        # Let real files through; otherwise serve the SPA entry for client routing.
        candidate = os.path.join(_FRONTEND_DIST, full_path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(_FRONTEND_DIST, "index.html"))
else:
    @app.get("/")
    def index_dev():
        return {"message": "Prompt Gallery API. Frontend build not found; run the Vite dev server."}
