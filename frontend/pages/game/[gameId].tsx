import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/router";
import styles from "../../styles/Game.module.css";
import { bank, getGame, roll } from "../../lib/api";
import { EventDTO, GameResponse, GameStateDTO, ValidActionsDTO } from "../../lib/types";

interface SummaryInfo {
  title: string;
  details: string[];
  seq: number;
}

function formatEvent(event: EventDTO): string {
  const ts = new Date(event.ts_iso).toLocaleTimeString();
  const payload = event.payload as Record<string, unknown>;
  switch (event.type) {
    case "roll":
      return `${ts} — Roll by P${payload.player_id}: ${payload.die}`;
    case "bank":
      return `${ts} — Bank by P${payload.player_id}: +${payload.amount}`;
    case "bust":
      return `${ts} — Bust! Round score reset.`;
    case "round_end":
      return `${ts} — Round ${payload.round_index} ended (${payload.reason}).`;
    case "match_end":
      return `${ts} — Match ${payload.match_index} summary ready.`;
    case "game_end":
      return `${ts} — Game over.`;
    default:
      return `${ts} — ${event.type}`;
  }
}

function computeSummary(state: GameStateDTO, event: EventDTO): SummaryInfo {
  const totals = state.players.map((p) => `${p.name}: ${p.total_score}`);
  const stats = state.stats;
  const maxBy = (values: number[]) => values.indexOf(Math.max(...values));
  const avgBankIndex = maxBy(stats.map((s) => s.avg_voluntary_bank));
  const patienceIndex = maxBy(stats.map((s) => s.avg_rolls_elapsed_before_bank));
  const onesIndex = maxBy(stats.map((s) => s.ones_rolled));
  const missedIndex = maxBy(stats.map((s) => s.missed_points));

  return {
    seq: event.seq,
    title: event.type === "game_end" ? "Final Summary" : `Match ${state.match_number} Summary`,
    details: [
      "Scores:",
      ...totals,
      `Greediest (avg bank): ${state.players[avgBankIndex]?.name ?? "-"}`,
      `Greediest (patience): ${state.players[patienceIndex]?.name ?? "-"}`,
      `Most ones rolled: ${state.players[onesIndex]?.name ?? "-"}`,
      `Most points missed: ${state.players[missedIndex]?.name ?? "-"}`
    ]
  };
}

export default function GamePage() {
  const router = useRouter();
  const { gameId } = router.query;
  const [state, setState] = useState<GameStateDTO | null>(null);
  const [validActions, setValidActions] = useState<ValidActionsDTO | null>(null);
  const [events, setEvents] = useState<EventDTO[]>([]);
  const [latestSeq, setLatestSeq] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<SummaryInfo | null>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const updateFromResponse = useCallback(
    (response: GameResponse, append: boolean) => {
      setState(response.state);
      setValidActions(response.valid_actions);
      setLatestSeq(response.latest_seq);
      if (append) {
        const newEvents = [...response.events].reverse();
        setEvents((prev) => [...newEvents, ...prev]);
        const summaryEvent = response.events.find(
          (event) => event.type === "match_end" || event.type === "game_end"
        );
        if (summaryEvent) {
          setSummary(computeSummary(response.state, summaryEvent));
        }
      } else {
        setEvents([...response.events].reverse());
      }
    },
    []
  );

  const loadGame = useCallback(
    async (sinceSeq?: number) => {
      if (!gameId || Array.isArray(gameId)) return;
      try {
        const response = await getGame(gameId, sinceSeq);
        updateFromResponse(response, sinceSeq !== undefined);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load game.");
      }
    },
    [gameId, updateFromResponse]
  );

  useEffect(() => {
    if (!gameId || Array.isArray(gameId)) return;
    loadGame();
  }, [gameId, loadGame]);

  useEffect(() => {
    if (!gameId || Array.isArray(gameId)) return;
    pollingRef.current = setInterval(() => {
      loadGame(latestSeq);
    }, 1000);
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [gameId, latestSeq, loadGame]);

  const canRoll = validActions?.can_roll ?? false;
  const bankableIds = useMemo(
    () => new Set(validActions?.bankable_player_ids ?? []),
    [validActions]
  );

  const performBank = async (playerId: number) => {
    if (!gameId || Array.isArray(gameId)) return;
    try {
      const response = await bank(gameId, playerId);
      updateFromResponse(response, true);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Bank failed.");
    }
  };

  const performRoll = async () => {
    if (!gameId || Array.isArray(gameId)) return;
    try {
      const response = await roll(gameId);
      updateFromResponse(response, true);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Roll failed.");
    }
  };

  if (!state) {
    return <div className={styles.container}>Loading game...</div>;
  }

  const currentRoller = state.players.find((p) => p.id === state.current_roller_id);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.headerCard}>
          <h2 className={styles.headerTitle}>
            Match {state.match_number} / Round {state.round_number}
          </h2>
          <p className={styles.headerMeta}>Round score: {state.round_score}</p>
          <p className={styles.headerMeta}>
            Current roller: {currentRoller ? currentRoller.name : "-"}
          </p>
        </div>
        <div className={styles.actions}>
          <button className={styles.rollButton} onClick={performRoll} disabled={!canRoll}>
            Roll
          </button>
        </div>
      </div>

      <div className={styles.grid}>
        <div className={styles.players}>
          {state.players.map((player) => (
            <div key={player.id} className={styles.playerCard}>
              <h3 className={styles.playerName}>{player.name}</h3>
              <p className={styles.playerMeta}>Total: {player.total_score}</p>
              <p className={styles.playerMeta}>Status: {player.round_status}</p>
              <button
                className={styles.bankButton}
                onClick={() => performBank(player.id)}
                disabled={!bankableIds.has(player.id)}
              >
                Bank
              </button>
            </div>
          ))}
        </div>
        <div className={styles.logPanel}>
          <h3 className={styles.logTitle}>Event Log</h3>
          {events.length === 0 && <div className={styles.logItem}>No events yet.</div>}
          {events.map((event) => (
            <div key={event.seq} className={styles.logItem}>
              {formatEvent(event)}
            </div>
          ))}
        </div>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {summary && (
        <div className={styles.modalBackdrop}>
          <div className={styles.modal}>
            <h3 className={styles.modalTitle}>{summary.title}</h3>
            <ul className={styles.modalList}>
              {summary.details.map((detail, index) => (
                <li key={`${summary.seq}-${index}`}>{detail}</li>
              ))}
            </ul>
            <div style={{ marginTop: "16px" }}>
              <button className={styles.rollButton} onClick={() => setSummary(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
