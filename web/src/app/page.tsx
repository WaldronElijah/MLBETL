import Link from "next/link";
import { fetchGamesList } from "@/lib/api";

export const dynamic = "force-dynamic";

function fmtDate(iso: string | null): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}

export default async function Home() {
  let games: Awaited<ReturnType<typeof fetchGamesList>>;
  let error: string | null = null;
  try {
    games = await fetchGamesList({ limit: 50 });
  } catch (e) {
    games = [];
    error = e instanceof Error ? e.message : "Failed to load games";
  }

  return (
    <div className="min-h-full bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      <main className="mx-auto max-w-6xl px-4 py-10">
        <header className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight">MLB games</h1>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Read-only list from the MLBETL FastAPI (
            <code className="rounded bg-zinc-200/80 px-1 py-0.5 text-xs dark:bg-zinc-800">
              GET /api/games
            </code>
            ). Run the API on port 8000 or set{" "}
            <code className="rounded bg-zinc-200/80 px-1 py-0.5 text-xs dark:bg-zinc-800">
              NEXT_PUBLIC_API_URL
            </code>
            .
          </p>
        </header>

        {error ? (
          <div
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200"
            role="alert"
          >
            {error}
          </div>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="border-b border-zinc-200 bg-zinc-50 text-xs font-medium uppercase tracking-wide text-zinc-600 dark:border-zinc-800 dark:bg-zinc-800/50 dark:text-zinc-400">
                <tr>
                  <th className="px-3 py-2">Date</th>
                  <th className="px-3 py-2">Away</th>
                  <th className="px-3 py-2">Home</th>
                  <th className="px-3 py-2 text-right">Score</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Winner</th>
                  <th className="px-3 py-2 w-24" />
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {games.map((g) => (
                  <tr
                    key={g.game_id}
                    className="hover:bg-zinc-50/80 dark:hover:bg-zinc-800/40"
                  >
                    <td className="whitespace-nowrap px-3 py-2 text-zinc-600 dark:text-zinc-400">
                      {fmtDate(g.date_utc)}
                    </td>
                    <td className="px-3 py-2">{g.away_team ?? "—"}</td>
                    <td className="px-3 py-2">{g.home_team ?? "—"}</td>
                    <td className="whitespace-nowrap px-3 py-2 text-right tabular-nums">
                      {g.away_score ?? "—"} @ {g.home_score ?? "—"}
                    </td>
                    <td className="px-3 py-2">{g.status ?? g.game_status ?? "—"}</td>
                    <td className="px-3 py-2">{g.winner ?? "—"}</td>
                    <td className="px-3 py-2">
                      <Link
                        href={`/games/${g.game_id}`}
                        className="font-medium text-blue-600 hover:underline dark:text-blue-400"
                      >
                        Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {games.length === 0 && !error && (
              <p className="px-4 py-8 text-center text-sm text-zinc-500">
                No games returned. Ingest data or widen filters in the API.
              </p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
