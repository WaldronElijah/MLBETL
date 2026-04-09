import type { GameDetailOut, GameOut, TeamRunLineStatsOut } from "./types";

export function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  return raw.replace(/\/$/, "");
}

async function readJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text || res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export type GamesListParams = {
  limit?: number;
  offset?: number;
  date_from?: string;
  date_to?: string;
  team?: string;
  status?: string;
  winner?: string;
  rl_winner?: string;
  ou_result?: string;
};

function appendGamesQueryParams(
  u: URL,
  params: GamesListParams | undefined,
): void {
  u.searchParams.set("limit", String(params?.limit ?? 50));
  if (params?.offset != null) {
    u.searchParams.set("offset", String(params.offset));
  }
  if (params?.date_from) {
    u.searchParams.set("date_from", params.date_from);
  }
  if (params?.date_to) {
    u.searchParams.set("date_to", params.date_to);
  }
  if (params?.team) {
    u.searchParams.set("team", params.team);
  }
  if (params?.status) {
    u.searchParams.set("status", params.status);
  }
  if (params?.winner) {
    u.searchParams.set("winner", params.winner);
  }
  if (params?.rl_winner) {
    u.searchParams.set("rl_winner", params.rl_winner);
  }
  if (params?.ou_result) {
    u.searchParams.set("ou_result", params.ou_result);
  }
}

export async function fetchGamesList(
  params?: GamesListParams,
): Promise<GameOut[]> {
  const u = new URL(`${getApiBaseUrl()}/api/games`);
  appendGamesQueryParams(u, params);
  const res = await fetch(u.toString(), { cache: "no-store" });
  return readJson<GameOut[]>(res);
}

export type RunLineTeamStatsParams = {
  date_from?: string;
  date_to?: string;
  min_games?: number;
};

export async function fetchRunLineTeamStats(
  params?: RunLineTeamStatsParams,
): Promise<TeamRunLineStatsOut[]> {
  const u = new URL(`${getApiBaseUrl()}/api/stats/run-line-by-team`);
  if (params?.date_from) {
    u.searchParams.set("date_from", params.date_from);
  }
  if (params?.date_to) {
    u.searchParams.set("date_to", params.date_to);
  }
  if (params?.min_games != null) {
    u.searchParams.set("min_games", String(params.min_games));
  }
  const res = await fetch(u.toString(), { cache: "no-store" });
  return readJson<TeamRunLineStatsOut[]>(res);
}

export async function fetchGame(
  gameId: number,
  includeBoxscore: boolean,
): Promise<GameDetailOut> {
  const u = new URL(`${getApiBaseUrl()}/api/games/${gameId}`);
  if (includeBoxscore) {
    u.searchParams.set("include_boxscore", "true");
  }
  const res = await fetch(u.toString(), { cache: "no-store" });
  return readJson<GameDetailOut>(res);
}
