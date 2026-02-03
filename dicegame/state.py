from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set

from .types import Player
from .stats import PlayerStats


@dataclass
class RoundState:
    round_index: int
    match_index: int
    round_score: int
    active_players: Set[int]
    roller_index: int
    starter_index: int
    rolls_elapsed_in_round: int


@dataclass
class GameState:
    players: List[Player]
    totals: List[int]
    stats: List[PlayerStats]
    round_state: RoundState
    match_summaries: List[object] = field(default_factory=list)
    game_over: bool = False

    @property
    def n_players(self) -> int:
        return len(self.players)
