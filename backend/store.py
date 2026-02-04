from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Protocol
from uuid import uuid4

from dicegame.actions import Bank, Roll
from dicegame.engine import GameEngine

from .adapter import build_engine, event_to_dto
from .models import EventDTO


@dataclass
class GameSession:
    game_id: str
    engine: GameEngine
    events: List[EventDTO] = field(default_factory=list)
    latest_seq: int = 0


class GameStore(Protocol):
    def get(self, game_id: str) -> GameSession:
        ...

    def create(self, players: List[str]) -> GameSession:
        ...

    def apply_action(self, game_id: str, action: object) -> List[EventDTO]:
        ...

    def reset(self, game_id: str) -> GameSession:
        ...


class InMemoryGameStore:
    def __init__(self) -> None:
        self._games: Dict[str, GameSession] = {}

    def get(self, game_id: str) -> GameSession:
        if game_id not in self._games:
            raise KeyError("Game not found")
        return self._games[game_id]

    def create(self, players: List[str]) -> GameSession:
        game_id = str(uuid4())
        engine = build_engine(players)
        session = GameSession(game_id=game_id, engine=engine)
        self._games[game_id] = session
        return session

    def apply_action(self, game_id: str, action: object) -> List[EventDTO]:
        session = self.get(game_id)
        events = session.engine.step(action)
        dto_events: List[EventDTO] = []
        for event in events:
            session.latest_seq += 1
            dto = event_to_dto(session.latest_seq, event)
            session.events.append(dto)
            dto_events.append(dto)
        return dto_events

    def reset(self, game_id: str) -> GameSession:
        session = self.get(game_id)
        players = [player.name for player in session.engine.players]
        session.engine = build_engine(players)
        session.events = []
        session.latest_seq = 0
        return session
