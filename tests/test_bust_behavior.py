from dicegame.actions import Bank, Roll
from dicegame.engine import GameEngine
from dicegame.types import FixedDice


def test_bust_missed_points_applied_to_active_players():
    engine = GameEngine(["A", "B", "C"], FixedDice([6, 1]))
    engine.step(Roll())  # round_score = 6
    engine.step(Roll())  # bust
    assert engine.state.stats[0].missed_points == 6
    assert engine.state.stats[1].missed_points == 6
    assert engine.state.stats[2].missed_points == 6


def test_voluntary_vs_forced_banks_tracked_separately():
    engine = GameEngine(["A", "B", "C"], FixedDice([6, 1]))
    engine.step(Roll())  # round_score = 6
    engine.step(Bank(0))
    engine.step(Roll())  # bust for B and C
    assert engine.state.stats[0].voluntary_banks_count == 1
    assert engine.state.stats[0].forced_zero_banks_count == 0
    assert engine.state.stats[1].forced_zero_banks_count == 1
    assert engine.state.stats[2].forced_zero_banks_count == 1
