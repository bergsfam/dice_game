from dicegame.actions import Bank, Roll
from dicegame.engine import GameEngine
from dicegame.types import FixedDice


def test_roller_banks_roller_advances_before_roll():
    engine = GameEngine(["A", "B", "C"], FixedDice([3, 4]))
    engine.step(Roll())
    # round_score is now 3, roller still 0
    engine.step(Bank(0))
    events = engine.step(Roll())
    roll_events = [e for e in events if e.type == "roll"]
    assert roll_events
    assert roll_events[0].data["player_id"] == 1
