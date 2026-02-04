import { ErrorResponse, GameResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options
  });

  if (!response.ok) {
    let detail = "Request failed";
    try {
      const data = (await response.json()) as ErrorResponse | { detail: string };
      if (typeof data.detail === "string") {
        detail = data.detail;
      } else if (data.detail) {
        detail = data.detail;
      }
    } catch {
      // Ignore JSON parse failures.
    }
    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export function createGame(players: string[]): Promise<GameResponse> {
  return request<GameResponse>("/api/games", {
    method: "POST",
    body: JSON.stringify({ players })
  });
}

export function getGame(gameId: string, sinceSeq?: number): Promise<GameResponse> {
  const query = sinceSeq !== undefined ? `?since_seq=${sinceSeq}` : "";
  return request<GameResponse>(`/api/games/${gameId}${query}`, {
    method: "GET"
  });
}

export function bank(gameId: string, playerId: number): Promise<GameResponse> {
  return request<GameResponse>(`/api/games/${gameId}/bank`, {
    method: "POST",
    body: JSON.stringify({ player_id: playerId })
  });
}

export function roll(gameId: string): Promise<GameResponse> {
  return request<GameResponse>(`/api/games/${gameId}/roll`, {
    method: "POST",
    body: JSON.stringify({})
  });
}
