from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any, List, Optional

from dicegame.actions import Bank, Roll
from dicegame.engine import GameEngine, Event
from dicegame.types import RandomDice

from .models import EventDTO, GameStateDTO, PlayerDTO, PlayerStatsDTO, ValidActionsDTO


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_engine(players: List[str]) -> GameEngine:
    return GameEngine(players=players, dice=RandomDice())


def next_active_player_id(engine: GameEngine) -> Optional[int]:
    rs = engine.state.round_state
    if engine.state.game_over:
        return None
    if not rs.active_players:
        return None
    if rs.roller_index in rs.active_players:
        return rs.roller_index
    n = engine.state.n_players
    for offset in range(1, n + 1):
        idx = (rs.roller_index + offset) % n
        if idx in rs.active_players:
            return idx
    return None


def game_state_dto(engine: GameEngine) -> GameStateDTO:
    rs = engine.state.round_state
    players: List[PlayerDTO] = []
    stats: List[PlayerStatsDTO] = []
    for player in engine.players:
        status = "ACTIVE" if player.id in rs.active_players else "BANKED"
        players.append(
            PlayerDTO(
                id=player.id,
                name=player.name,
                total_score=engine.state.totals[player.id],
                round_status=status,
            )
        )
        stat = engine.state.stats[player.id]
        stats.append(
            PlayerStatsDTO(
                ones_rolled=stat.ones_rolled,
                voluntary_banks_count=stat.voluntary_banks_count,
                forced_zero_banks_count=stat.forced_zero_banks_count,
                missed_points=stat.missed_points,
                rolls_taken_as_roller=stat.rolls_taken_as_roller,
                avg_voluntary_bank=stat.avg_voluntary_bank,
                avg_rolls_elapsed_before_bank=stat.avg_rolls_elapsed_before_bank,
            )
        )
    return GameStateDTO(
        players=players,
        stats=stats,
        round_score=rs.round_score,
        round_number=rs.round_index,
        match_number=rs.match_index,
        current_roller_id=next_active_player_id(engine),
        starter_id=rs.starter_index,
        is_round_over=False,
        is_game_over=engine.state.game_over,
    )


def valid_actions_dto(engine: GameEngine) -> ValidActionsDTO:
    actions = engine.valid_actions()
    can_roll = any(isinstance(action, Roll) for action in actions)
    bankable_player_ids = [
        action.player_id for action in actions if isinstance(action, Bank)
    ]
    return ValidActionsDTO(
        can_roll=can_roll,
        bankable_player_ids=bankable_player_ids,
    )


def _serialize_payload(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _serialize_payload(val) for key, val in asdict(value).items()}
    if isinstance(value, dict):
        return {key: _serialize_payload(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_serialize_payload(item) for item in value]
    return value


def event_to_dto(seq: int, event: Event) -> EventDTO:
    payload = _serialize_payload(dict(event.data))
    return EventDTO(seq=seq, ts_iso=utc_now_iso(), type=event.type, payload=payload)
