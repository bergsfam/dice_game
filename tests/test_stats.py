from dicegame.actions import Bank
from dicegame.engine import GameEngine
from dicegame.types import FixedDice


def bank_all(engine: GameEngine) -> None:
    active = sorted(engine.state.round_state.active_players)
    for pid in active:
        engine.step(Bank(pid))


def test_round_ends_when_all_bank_without_roll():
    engine = GameEngine(["A", "B"], FixedDice([]))
    bank_all(engine)
    assert engine.state.round_state.round_index == 2


def test_starter_rotation_across_rounds_and_matches():
    engine = GameEngine(["A", "B", "C"], FixedDice([]))
    expected_starters = []
    for _ in range(10):
        expected_starters.append(engine.state.round_state.starter_index)
        bank_all(engine)
    # After 10 rounds, match 1 should be complete and round 11 should start
    assert engine.state.round_state.round_index == 11
    assert engine.state.round_state.match_index == 2
    assert expected_starters == [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]
    assert engine.state.round_state.starter_index == 1
