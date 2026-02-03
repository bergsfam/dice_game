from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Bank:
    player_id: int


@dataclass(frozen=True)
class Roll:
    pass
