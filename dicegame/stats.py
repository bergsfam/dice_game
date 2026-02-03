from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class PlayerStats:
    ones_rolled: int = 0
    voluntary_banks_count: int = 0
    forced_zero_banks_count: int = 0
    voluntary_bank_amounts: List[int] = field(default_factory=list)
    missed_points: int = 0
    rolls_taken_as_roller: int = 0
    rolls_elapsed_before_voluntary_bank: List[int] = field(default_factory=list)

    @property
    def avg_voluntary_bank(self) -> float:
        if not self.voluntary_bank_amounts:
            return 0.0
        return sum(self.voluntary_bank_amounts) / len(self.voluntary_bank_amounts)

    @property
    def avg_rolls_elapsed_before_bank(self) -> float:
        if not self.rolls_elapsed_before_voluntary_bank:
            return 0.0
        return sum(self.rolls_elapsed_before_voluntary_bank) / len(
            self.rolls_elapsed_before_voluntary_bank
        )

    def snapshot(self) -> "PlayerStats":
        return PlayerStats(
            ones_rolled=self.ones_rolled,
            voluntary_banks_count=self.voluntary_banks_count,
            forced_zero_banks_count=self.forced_zero_banks_count,
            voluntary_bank_amounts=list(self.voluntary_bank_amounts),
            missed_points=self.missed_points,
            rolls_taken_as_roller=self.rolls_taken_as_roller,
            rolls_elapsed_before_voluntary_bank=list(self.rolls_elapsed_before_voluntary_bank),
        )


@dataclass
class PlayerStatsDelta:
    ones_rolled: int
    voluntary_banks_count: int
    forced_zero_banks_count: int
    voluntary_bank_amounts: List[int]
    missed_points: int
    rolls_taken_as_roller: int
    rolls_elapsed_before_voluntary_bank: List[int]


def diff_stats(current: PlayerStats, previous: PlayerStats) -> PlayerStatsDelta:
    return PlayerStatsDelta(
        ones_rolled=current.ones_rolled - previous.ones_rolled,
        voluntary_banks_count=current.voluntary_banks_count - previous.voluntary_banks_count,
        forced_zero_banks_count=current.forced_zero_banks_count
        - previous.forced_zero_banks_count,
        voluntary_bank_amounts=current.voluntary_bank_amounts[
            len(previous.voluntary_bank_amounts) :
        ],
        missed_points=current.missed_points - previous.missed_points,
        rolls_taken_as_roller=current.rolls_taken_as_roller
        - previous.rolls_taken_as_roller,
        rolls_elapsed_before_voluntary_bank=current.rolls_elapsed_before_voluntary_bank[
            len(previous.rolls_elapsed_before_voluntary_bank) :
        ],
    )
