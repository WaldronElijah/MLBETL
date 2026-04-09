/** Shapes returned by FastAPI JSON (ISO datetimes are strings). */

export type GameOut = {
  game_id: number;
  date_utc: string | null;
  game_status: string | null;
  status: string | null;
  home_team: string | null;
  away_team: string | null;
  home_score: number | null;
  away_score: number | null;
  venue_name: string | null;
  venue_city: string | null;
  venue_state: string | null;
  location: string | null;
  starting_pitchers: Record<string, unknown>;
  opening_spread: number | null;
  opening_total: number | null;
  pickcenter: unknown[];
  draftkings_lines: Record<string, unknown> | null;
  records_before_game: Record<string, unknown>;
  home_record: string | null;
  away_record: string | null;
  umpires: unknown[];
  total_runs: number | null;
  margin: number | null;
  winner: string | null;
  loser: string | null;
  rl_winner: string | null;
  ou_result: string | null;
  ingested_at_utc: string;
};

export type BoxscoreLineOut = {
  game_id: number;
  team_id: number | null;
  team_name: string | null;
  player_id: number | null;
  player_name: string | null;
  stats: Record<string, unknown>;
};

export type GameDetailOut = GameOut & {
  batting_lines: BoxscoreLineOut[];
  pitching_lines: BoxscoreLineOut[];
};

/** GET /api/stats/run-line-by-team */
export type TeamRunLineStatsOut = {
  team: string;
  games: number;
  covers: number;
  losses: number;
  pushes: number;
  ats_pct: number | null;
  avg_margin_vs_line: number | null;
};
