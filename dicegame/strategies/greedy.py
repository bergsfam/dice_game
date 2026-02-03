from __future__ import annotations

from dataclasses import dataclass

from .base import Strategy
from ..state import GameState


@dataclass
class GreedyStrategy(Strategy):
    def decide_bank(self, state: GameState, player_id: int) -> bool:
        return state.round_state.round_score >= 999999
