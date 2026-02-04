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

## Web UI (FastAPI + Next.js)

This repo now includes a scaffolded single-screen web UI designed to grow into multi-client play later.

### Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000`.

To point the UI at a different backend URL, set `NEXT_PUBLIC_API_BASE` (see `frontend/.env.local.example`).

### Notes

- The backend exposes an append-only event log with `since_seq` polling support.
- In-memory game storage is isolated behind a `GameStore` interface so it can be swapped for Redis/Postgres later.
- `POST /api/games/{game_id}/reset` resets the existing game in-place using the same player list.

<!-- Sample screenshot: Create game screen with player list and start button. -->
<!-- Sample screenshot: Game screen with player cards, roll/bank buttons, and event log. -->
