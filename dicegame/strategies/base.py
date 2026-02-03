from __future__ import annotations

from typing import Protocol

from ..state import GameState


class Strategy(Protocol):
    def decide_bank(self, state: GameState, player_id: int) -> bool:
        """Return True if the player should bank in the current pre-roll window."""
