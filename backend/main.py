from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from dicegame.actions import Bank, Roll

from .adapter import game_state_dto, valid_actions_dto
from .models import BankRequest, CreateGameRequest, ErrorResponse, GameResponse
from .store import InMemoryGameStore

app = FastAPI(title="Dice Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

store = InMemoryGameStore()


def build_response(game_id: str, events, latest_seq: int) -> GameResponse:
    session = store.get(game_id)
    state = game_state_dto(session.engine)
    valid_actions = valid_actions_dto(session.engine)
    return GameResponse(
        game_id=game_id,
        state=state,
        events=events,
        valid_actions=valid_actions,
        latest_seq=latest_seq,
    )


@app.post("/api/games", response_model=GameResponse, responses={400: {"model": ErrorResponse}})
def create_game(payload: CreateGameRequest):
    try:
        session = store.create(payload.players)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return build_response(session.game_id, session.events, session.latest_seq)


@app.get("/api/games/{game_id}", response_model=GameResponse, responses={404: {"model": ErrorResponse}})
def get_game(game_id: str, since_seq: Optional[int] = None):
    try:
        session = store.get(game_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Game not found") from exc
    if since_seq is None:
        events = list(session.events)
    else:
        events = [event for event in session.events if event.seq > since_seq]
    return build_response(game_id, events, session.latest_seq)


@app.post(
    "/api/games/{game_id}/bank",
    response_model=GameResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def bank(game_id: str, payload: BankRequest):
    try:
        events = store.apply_action(game_id, Bank(payload.player_id))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Game not found") from exc
    except ValueError as exc:
        session = store.get(game_id)
        state = game_state_dto(session.engine)
        valid_actions = valid_actions_dto(session.engine)
        payload = ErrorResponse(
            detail=str(exc),
            state=state,
            valid_actions=valid_actions,
        ).model_dump()
        return JSONResponse(status_code=400, content=payload)
    session = store.get(game_id)
    return build_response(game_id, events, session.latest_seq)


@app.post(
    "/api/games/{game_id}/roll",
    response_model=GameResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def roll(game_id: str):
    try:
        events = store.apply_action(game_id, Roll())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Game not found") from exc
    except ValueError as exc:
        session = store.get(game_id)
        state = game_state_dto(session.engine)
        valid_actions = valid_actions_dto(session.engine)
        payload = ErrorResponse(
            detail=str(exc),
            state=state,
            valid_actions=valid_actions,
        ).model_dump()
        return JSONResponse(status_code=400, content=payload)
    session = store.get(game_id)
    return build_response(game_id, events, session.latest_seq)


@app.post(
    "/api/games/{game_id}/reset",
    response_model=GameResponse,
    responses={404: {"model": ErrorResponse}},
)
def reset(game_id: str):
    try:
        session = store.reset(game_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Game not found") from exc
    return build_response(session.game_id, session.events, session.latest_seq)
