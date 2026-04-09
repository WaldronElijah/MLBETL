import {
  fetchGamesList,
  fetchRunLineTeamStats,
} from "@/lib/api";
import { DateRangeFilter } from "./_components/date-range-filter";
import { GameListTable } from "./_components/game-list-table";
import { HomeTabNav, type HomeTab } from "./_components/home-tab-nav";
import { RunLineStatsTable } from "./_components/run-line-stats-table";

export const dynamic = "force-dynamic";

function firstString(
  v: string | string[] | undefined,
): string | undefined {
  if (v == null) return undefined;
  return Array.isArray(v) ? v[0] : v;
}

function normalizeTab(raw: string | undefined): HomeTab {
  if (raw === "ats" || raw === "line") return raw;
  return "games";
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const sp = await searchParams;
  const tab = normalizeTab(firstString(sp.tab));
  const date_from = firstString(sp.date_from);
  const date_to = firstString(sp.date_to);
  const dates = { date_from, date_to };

  const listParams = {
    limit: 50,
    ...(date_from ? { date_from } : {}),
    ...(date_to ? { date_to } : {}),
  };

  const statsParams = {
    ...(date_from ? { date_from } : {}),
    ...(date_to ? { date_to } : {}),
    min_games: 1,
  };

  let error: string | null = null;
  let games: Awaited<ReturnType<typeof fetchGamesList>> = [];
  let stats: Awaited<ReturnType<typeof fetchRunLineTeamStats>> = [];

  try {
    if (tab === "games") {
      games = await fetchGamesList(listParams);
    } else {
      stats = await fetchRunLineTeamStats(statsParams);
    }
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load data";
  }

  return (
    <div className="min-h-full bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      <main className="mx-auto max-w-6xl px-4 py-10">
        <header className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight">MLB games</h1>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Read-only data from the MLBETL FastAPI. Run the API on port 8000 or
            set{" "}
            <code className="rounded bg-zinc-200/80 px-1 py-0.5 text-xs dark:bg-zinc-800">
              NEXT_PUBLIC_API_URL
            </code>
            .
          </p>
        </header>

        <HomeTabNav active={tab} dates={dates} />
        <DateRangeFilter tab={tab} date_from={date_from} date_to={date_to} />

        {error ? (
          <div
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200"
            role="alert"
          >
            {error}
          </div>
        ) : tab === "games" ? (
          <GameListTable games={games} />
        ) : tab === "ats" ? (
          <RunLineStatsTable rows={stats} variant="ats" />
        ) : (
          <RunLineStatsTable rows={stats} variant="line" />
        )}
      </main>
    </div>
  );
}
