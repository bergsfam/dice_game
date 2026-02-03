from dicegame.actions import Bank, Roll
from dicegame.engine import GameEngine
from dicegame.types import FixedDice


def test_first_roll_is_one_forced_zero():
    engine = GameEngine(["A", "B"], FixedDice([1]))
    engine.step(Roll())
    assert engine.state.totals == [0, 0]
    assert engine.state.stats[0].forced_zero_banks_count == 1
    assert engine.state.stats[1].forced_zero_banks_count == 1


def test_first_roll_is_two_sets_round_score():
    engine = GameEngine(["A", "B"], FixedDice([2]))
    engine.step(Roll())
    assert engine.state.round_state.round_score == 2


def test_out_of_turn_banking_awards_score():
    engine = GameEngine(["A", "B", "C", "D", "E"], FixedDice([6]))
    engine.step(Roll())
    engine.step(Bank(4))
    assert engine.state.totals[4] == 6
