import { useState } from "react";
import { useRouter } from "next/router";
import styles from "../styles/CreateGame.module.css";
import { createGame } from "../lib/api";

export default function CreateGamePage() {
  const [players, setPlayers] = useState<string[]>(["Alice", "Bob"]);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const updatePlayer = (index: number, value: string) => {
    setPlayers((prev) => prev.map((name, idx) => (idx === index ? value : name)));
  };

  const addPlayer = () => setPlayers((prev) => [...prev, ""]);

  const removePlayer = (index: number) => {
    setPlayers((prev) => prev.filter((_, idx) => idx !== index));
  };

  const startGame = async () => {
    setError(null);
    const cleaned = players.map((name) => name.trim()).filter(Boolean);
    if (cleaned.length < 2) {
      setError("Enter at least two player names.");
      return;
    }
    try {
      setIsSubmitting(true);
      const response = await createGame(cleaned);
      await router.push(`/game/${response.game_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start game.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Dice Game Control Room</h1>
        <p className={styles.subtitle}>
          Single-screen match setup. Add players and launch a new game.
        </p>
        {players.map((name, index) => (
          <div key={`${index}-${name}`} className={styles.playerRow}>
            <input
              className={styles.playerInput}
              value={name}
              onChange={(event) => updatePlayer(index, event.target.value)}
              placeholder={`Player ${index + 1}`}
            />
            {players.length > 2 && (
              <button
                className={`${styles.button} ${styles.buttonSecondary}`}
                onClick={() => removePlayer(index)}
                type="button"
              >
                Remove
              </button>
            )}
          </div>
        ))}
        <div className={styles.actions}>
          <button className={styles.buttonSecondary} onClick={addPlayer} type="button">
            Add Player
          </button>
          <button className={styles.button} onClick={startGame} disabled={isSubmitting}>
            {isSubmitting ? "Starting..." : "Start Game"}
          </button>
        </div>
        {error && <div className={styles.error}>{error}</div>}
      </div>
    </div>
  );
}
