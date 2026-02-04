from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


RoundStatus = Literal["ACTIVE", "BANKED"]


class PlayerDTO(BaseModel):
    id: int
    name: str
    total_score: int
    round_status: RoundStatus


class PlayerStatsDTO(BaseModel):
    ones_rolled: int
    voluntary_banks_count: int
    forced_zero_banks_count: int
    missed_points: int
    rolls_taken_as_roller: int
    avg_voluntary_bank: float
    avg_rolls_elapsed_before_bank: float


class GameStateDTO(BaseModel):
    players: List[PlayerDTO]
    stats: List[PlayerStatsDTO]
    round_score: int
    round_number: int
    match_number: int
    current_roller_id: Optional[int]
    starter_id: int
    is_round_over: bool
    is_game_over: bool


class ValidActionsDTO(BaseModel):
    can_roll: bool
    bankable_player_ids: List[int]


class EventDTO(BaseModel):
    seq: int
    ts_iso: str
    type: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class CreateGameRequest(BaseModel):
    players: List[str]


class BankRequest(BaseModel):
    player_id: int


class GameResponse(BaseModel):
    game_id: str
    state: GameStateDTO
    events: List[EventDTO]
    valid_actions: ValidActionsDTO
    latest_seq: int


class ErrorResponse(BaseModel):
    detail: str
    state: Optional[GameStateDTO] = None
    valid_actions: Optional[ValidActionsDTO] = None
