export type RoundStatus = "ACTIVE" | "BANKED";

export interface PlayerDTO {
  id: number;
  name: string;
  total_score: number;
  round_status: RoundStatus;
}

export interface PlayerStatsDTO {
  ones_rolled: number;
  voluntary_banks_count: number;
  forced_zero_banks_count: number;
  missed_points: number;
  rolls_taken_as_roller: number;
  avg_voluntary_bank: number;
  avg_rolls_elapsed_before_bank: number;
}

export interface GameStateDTO {
  players: PlayerDTO[];
  stats: PlayerStatsDTO[];
  round_score: number;
  round_number: number;
  match_number: number;
  current_roller_id: number | null;
  starter_id: number;
  is_round_over: boolean;
  is_game_over: boolean;
}

export interface ValidActionsDTO {
  can_roll: boolean;
  bankable_player_ids: number[];
}

export interface EventDTO {
  seq: number;
  ts_iso: string;
  type: string;
  payload: Record<string, unknown>;
}

export interface GameResponse {
  game_id: string;
  state: GameStateDTO;
  events: EventDTO[];
  valid_actions: ValidActionsDTO;
  latest_seq: number;
}

export interface ErrorResponse {
  detail: string;
  state?: GameStateDTO;
  valid_actions?: ValidActionsDTO;
}
