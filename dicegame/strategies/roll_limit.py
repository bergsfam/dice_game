from __future__ import annotations

from dataclasses import dataclass

from .base import Strategy
from ..state import GameState


@dataclass
class RollLimitStrategy(Strategy):
    roll_limit: int

    def decide_bank(self, state: GameState, player_id: int) -> bool:
        return state.round_state.rolls_elapsed_in_round >= self.roll_limit
