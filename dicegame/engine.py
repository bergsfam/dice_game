from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from .actions import Bank, Roll
from .state import GameState, RoundState
from .stats import PlayerStats, PlayerStatsDelta, diff_stats
from .types import Dice, Player


@dataclass
class Event:
    type: str
    data: Dict[str, object]


@dataclass
class MatchSummary:
    match_index: int
    round_start: int
    round_end: int
    score_deltas: List[int]
    totals_after: List[int]
    stats_deltas: List[PlayerStatsDelta]


class GameEngine:
    """Pure step-based game engine."""

    def __init__(self, players: Sequence[str], dice: Dice):
        if len(players) < 2:
            raise ValueError("At least two players required")
        self.players: List[Player] = [Player(i, name) for i, name in enumerate(players)]
        self.dice = dice
        self.event_log: List[Event] = []
        self.state = GameState(
            players=self.players,
            totals=[0 for _ in self.players],
            stats=[PlayerStats() for _ in self.players],
            round_state=RoundState(
                round_index=1,
                match_index=1,
                round_score=0,
                active_players=set(range(len(self.players))),
                roller_index=0,
                starter_index=0,
                rolls_elapsed_in_round=0,
            ),
        )
        self._match_start_stats = [s.snapshot() for s in self.state.stats]
        self._match_start_totals = list(self.state.totals)

    def valid_actions(self) -> List[object]:
        if self.state.game_over:
            return []
        if not self.state.round_state.active_players:
            return []
        actions: List[object] = [Bank(pid) for pid in sorted(self.state.round_state.active_players)]
        actions.append(Roll())
        return actions

    def step(self, action: object) -> List[Event]:
        if self.state.game_over:
            return []
        if isinstance(action, Bank):
            return self._handle_bank(action)
        if isinstance(action, Roll):
            return self._handle_roll()
        raise ValueError("Unknown action")

    def _handle_bank(self, action: Bank) -> List[Event]:
        rs = self.state.round_state
        if action.player_id not in rs.active_players:
            raise ValueError("Player is not active")
        amount = rs.round_score
        rs.active_players.remove(action.player_id)
        self.state.totals[action.player_id] += amount
        stats = self.state.stats[action.player_id]
        stats.voluntary_banks_count += 1
        stats.voluntary_bank_amounts.append(amount)
        stats.rolls_elapsed_before_voluntary_bank.append(rs.rolls_elapsed_in_round)
        event = Event(
            type="bank",
            data={
                "player_id": action.player_id,
                "amount": amount,
                "round_score": rs.round_score,
                "total_score": self.state.totals[action.player_id],
                "rolls_elapsed_in_round": rs.rolls_elapsed_in_round,
            },
        )
        self._append_event(event)
        if not rs.active_players:
            self._end_round(reason="all_bank")
        return [event]

    def _handle_roll(self) -> List[Event]:
        rs = self.state.round_state
        if not rs.active_players:
            raise ValueError("No active players to roll")
        if rs.roller_index not in rs.active_players:
            rs.roller_index = self._next_active_index(rs.roller_index)
        roller_id = rs.roller_index
        self.state.stats[roller_id].rolls_taken_as_roller += 1
        die = self.dice.roll()
        round_score_before = rs.round_score
        events: List[Event] = []
        if die == 1:
            self.state.stats[roller_id].ones_rolled += 1
            for pid in rs.active_players:
                self.state.stats[pid].forced_zero_banks_count += 1
                self.state.stats[pid].missed_points += round_score_before
            roll_event = Event(
                type="roll",
                data={
                    "player_id": roller_id,
                    "die": die,
                    "round_score_before": round_score_before,
                    "round_score_after": 0,
                },
            )
            bust_event = Event(
                type="bust",
                data={
                    "player_id": roller_id,
                    "round_score_before": round_score_before,
                    "affected_players": sorted(rs.active_players),
                },
            )
            self._append_event(roll_event)
            self._append_event(bust_event)
            events.extend([roll_event, bust_event])
            rs.round_score = 0
            rs.rolls_elapsed_in_round += 1
            self._end_round(reason="bust")
            return events

        if die == 2:
            rs.round_score = 2 if rs.round_score == 0 else rs.round_score * 2
        else:
            rs.round_score += die
        rs.rolls_elapsed_in_round += 1
        roll_event = Event(
            type="roll",
            data={
                "player_id": roller_id,
                "die": die,
                "round_score_before": round_score_before,
                "round_score_after": rs.round_score,
            },
        )
        self._append_event(roll_event)
        events.append(roll_event)
        return events

    def _next_active_index(self, start_index: int) -> int:
        n = self.state.n_players
        for offset in range(1, n + 1):
            idx = (start_index + offset) % n
            if idx in self.state.round_state.active_players:
                return idx
        raise ValueError("No active players")

    def _end_round(self, reason: str) -> None:
        rs = self.state.round_state
        round_end_event = Event(
            type="round_end",
            data={
                "round_index": rs.round_index,
                "reason": reason,
                "totals": list(self.state.totals),
            },
        )
        self._append_event(round_end_event)
        if rs.round_index % 10 == 0:
            self._end_match(rs.match_index)
        if rs.round_index >= 30:
            self.state.game_over = True
            game_end_event = Event(
                type="game_end",
                data={
                    "totals": list(self.state.totals),
                },
            )
            self._append_event(game_end_event)
            return
        next_round_index = rs.round_index + 1
        next_starter_index = (rs.starter_index + 1) % self.state.n_players
        next_match_index = (next_round_index - 1) // 10 + 1
        self.state.round_state = RoundState(
            round_index=next_round_index,
            match_index=next_match_index,
            round_score=0,
            active_players=set(range(self.state.n_players)),
            roller_index=next_starter_index,
            starter_index=next_starter_index,
            rolls_elapsed_in_round=0,
        )

    def _end_match(self, match_index: int) -> None:
        stats_deltas = [
            diff_stats(current, previous)
            for current, previous in zip(self.state.stats, self._match_start_stats)
        ]
        score_deltas = [
            total - prev for total, prev in zip(self.state.totals, self._match_start_totals)
        ]
        summary = MatchSummary(
            match_index=match_index,
            round_start=match_index * 10 - 9,
            round_end=match_index * 10,
            score_deltas=score_deltas,
            totals_after=list(self.state.totals),
            stats_deltas=stats_deltas,
        )
        self.state.match_summaries.append(summary)
        self._append_event(
            Event(
                type="match_end",
                data={
                    "match_index": match_index,
                    "summary": summary,
                },
            )
        )
        self._match_start_stats = [s.snapshot() for s in self.state.stats]
        self._match_start_totals = list(self.state.totals)

    def _append_event(self, event: Event) -> None:
        self.event_log.append(event)

    def greediest_players(self) -> tuple[Player, Player]:
        by_avg_bank = self._max_by(
            lambda pid: self.state.stats[pid].avg_voluntary_bank
        )
        by_patience = self._max_by(
            lambda pid: self.state.stats[pid].avg_rolls_elapsed_before_bank
        )
        return self.players[by_avg_bank], self.players[by_patience]

    def _max_by(self, key_fn) -> int:
        best_pid: Optional[int] = None
        best_key: Optional[tuple[float, int, str]] = None
        for pid in range(self.state.n_players):
            key = (key_fn(pid), self.state.totals[pid], self.players[pid].name)
            if best_pid is None:
                best_pid = pid
                best_key = key
                continue
            if key[0] > best_key[0]:
                best_pid, best_key = pid, key
            elif key[0] == best_key[0]:
                if key[1] > best_key[1]:
                    best_pid, best_key = pid, key
                elif key[1] == best_key[1]:
                    if key[2] < best_key[2]:
                        best_pid, best_key = pid, key
        if best_pid is None:
            raise ValueError("No players")
        return best_pid
