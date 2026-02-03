# Dice Game Engine

A step-based dice game engine with a CLI simulator for strategy testing.

## Rules (Short Summary)
- 2+ players, fixed order, 30 rounds total grouped into 3 matches of 10.
- Each round starts with `round_score = 0` and all players ACTIVE.
- Any ACTIVE player may bank before the next roll (even out-of-turn).
  - Banking adds `round_score` to their total immediately and removes them from ACTIVE.
- If any ACTIVE player remains, the current roller rolls:
  - `1`: bust, round ends immediately; ACTIVE players get forced 0.
  - `2`: round_score doubles (or becomes 2 if it was 0).
  - `3-6`: add to round_score.
- Round ends on bust or when all players bank.
- Starter/roller rotates each round.

## CLI

Example simulation:

```bash
python -m dicegame.cli simulate --players Alice Bob Carol --strategy threshold:50 threshold:120 greedy --games 1000
```

Strategies:
- `threshold:T` bank when `round_score >= T`
- `greedy` bank only at a very high score (effectively never)
- `roll_limit:k` bank once `rolls_elapsed_in_round >= k`
