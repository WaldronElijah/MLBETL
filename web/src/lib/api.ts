import type { GameDetailOut, GameOut } from "./types";

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

export async function fetchGamesList(params?: {
  limit?: number;
  offset?: number;
}): Promise<GameOut[]> {
  const u = new URL(`${getApiBaseUrl()}/api/games`);
  u.searchParams.set("limit", String(params?.limit ?? 50));
  if (params?.offset != null) {
    u.searchParams.set("offset", String(params.offset));
  }
  const res = await fetch(u.toString(), { cache: "no-store" });
  return readJson<GameOut[]>(res);
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
