from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List

from .actions import Bank, Roll
from .engine import GameEngine
from .strategies import GreedyStrategy, RollLimitStrategy, ThresholdStrategy, Strategy
from .types import RandomDice


@dataclass
class SimulationResult:
    totals: List[int]
    wins: List[int]
    games: int


def parse_strategy(spec: str) -> Strategy:
    if spec.startswith("threshold:"):
        value = int(spec.split(":", 1)[1])
        return ThresholdStrategy(value)
    if spec.startswith("roll_limit:"):
        value = int(spec.split(":", 1)[1])
        return RollLimitStrategy(value)
    if spec == "greedy":
        return GreedyStrategy()
    raise ValueError(f"Unknown strategy: {spec}")


def run_single_game(players: List[str], strategies: List[Strategy]) -> List[int]:
    engine = GameEngine(players, RandomDice())
    while not engine.state.game_over:
        rs = engine.state.round_state
        decisions: List[int] = []
        for pid in range(len(players)):
            if pid in rs.active_players and strategies[pid].decide_bank(engine.state, pid):
                decisions.append(pid)
        for pid in decisions:
            if engine.state.game_over:
                break
            if pid in engine.state.round_state.active_players:
                engine.step(Bank(pid))
        if engine.state.game_over:
            break
        if not engine.state.round_state.active_players:
            continue
        engine.step(Roll())
    return list(engine.state.totals)


def simulate(players: List[str], strategies: List[Strategy], games: int) -> SimulationResult:
    totals = [0 for _ in players]
    wins = [0 for _ in players]
    for _ in range(games):
        scores = run_single_game(players, strategies)
        for i, score in enumerate(scores):
            totals[i] += score
        max_score = max(scores)
        winners = [i for i, score in enumerate(scores) if score == max_score]
        for i in winners:
            wins[i] += 1
    return SimulationResult(totals=totals, wins=wins, games=games)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dice game simulator")
    sub = parser.add_subparsers(dest="command", required=True)
    sim = sub.add_parser("simulate", help="Simulate games")
    sim.add_argument("--players", nargs="+", required=True)
    sim.add_argument("--strategy", nargs="+", required=True)
    sim.add_argument("--games", type=int, default=1000)
    args = parser.parse_args()

    if args.command == "simulate":
        players: List[str] = args.players
        if len(args.strategy) != len(players):
            raise ValueError("Number of strategies must match number of players")
        strategies = [parse_strategy(s) for s in args.strategy]
        result = simulate(players, strategies, args.games)
        print(f"Games: {result.games}")
        for i, name in enumerate(players):
            win_rate = result.wins[i] / result.games
            avg_score = result.totals[i] / result.games
            print(f"{name}: win_rate={win_rate:.3f} avg_score={avg_score:.2f}")


if __name__ == "__main__":
    main()
