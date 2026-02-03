from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, List
import random


@dataclass(frozen=True)
class Player:
    id: int
    name: str


class Dice(Protocol):
    def roll(self) -> int:
        """Return a die roll in the range 1..6."""


@dataclass
class RandomDice:
    rng: random.Random | None = None

    def roll(self) -> int:
        rng = self.rng or random
        return rng.randint(1, 6)


@dataclass
class FixedDice:
    rolls: List[int]
    index: int = 0

    def roll(self) -> int:
        if self.index >= len(self.rolls):
            raise IndexError("FixedDice exhausted")
        value = self.rolls[self.index]
        self.index += 1
        return value
