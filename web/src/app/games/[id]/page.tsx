import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchGame } from "@/lib/api";

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

export default async function GameDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { id: idRaw } = params;
  const gameId = Number.parseInt(idRaw, 10);
  if (!Number.isFinite(gameId)) {
    notFound();
  }

  let game: Awaited<ReturnType<typeof fetchGame>>;
  try {
    game = await fetchGame(gameId, true);
  } catch (e) {
    const msg = e instanceof Error ? e.message : "";
    if (msg.startsWith("API 404")) {
      notFound();
    }
    throw e;
  }

  return (
    <div className="min-h-full bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      <main className="mx-auto max-w-4xl px-4 py-10">
        <p className="mb-4">
          <Link
            href="/"
            className="text-sm font-medium text-blue-600 hover:underline dark:text-blue-400"
          >
            ← All games
          </Link>
        </p>

        <header className="mb-8 border-b border-zinc-200 pb-6 dark:border-zinc-800">
          <h1 className="text-2xl font-semibold tracking-tight">
            {game.away_team ?? "Away"} @ {game.home_team ?? "Home"}
          </h1>
          <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
            {fmtDate(game.date_utc)} · Game ID {game.game_id} ·{" "}
            {game.status ?? game.game_status ?? "—"}
          </p>
          <p className="mt-2 text-lg tabular-nums">
            <span className="font-medium">{game.away_score ?? "—"}</span>
            <span className="mx-2 text-zinc-400">—</span>
            <span className="font-medium">{game.home_score ?? "—"}</span>
          </p>
          {game.location && (
            <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
              {game.location}
            </p>
          )}
        </header>

        <section className="mb-10">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-zinc-500">
            Lines
          </h2>
          <dl className="grid grid-cols-1 gap-2 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-zinc-500">Opening spread</dt>
              <dd className="font-medium tabular-nums">
                {game.opening_spread ?? "—"}
              </dd>
            </div>
            <div>
              <dt className="text-zinc-500">Opening total</dt>
              <dd className="font-medium tabular-nums">
                {game.opening_total ?? "—"}
              </dd>
            </div>
            <div>
              <dt className="text-zinc-500">RL winner</dt>
              <dd className="font-medium">{game.rl_winner ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-zinc-500">O/U result</dt>
              <dd className="font-medium">{game.ou_result ?? "—"}</dd>
            </div>
          </dl>
        </section>

        <section className="mb-10">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-zinc-500">
            Batting ({game.batting_lines.length})
          </h2>
          <div className="overflow-x-auto rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
            <table className="w-full min-w-[480px] text-left text-sm">
              <thead className="border-b border-zinc-200 bg-zinc-50 text-xs font-medium uppercase text-zinc-600 dark:border-zinc-800 dark:bg-zinc-800/50 dark:text-zinc-400">
                <tr>
                  <th className="px-3 py-2">Player</th>
                  <th className="px-3 py-2">Team</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {game.batting_lines.map((row, i) => (
                  <tr key={`b-${row.player_id ?? i}-${i}`}>
                    <td className="px-3 py-2">{row.player_name ?? "—"}</td>
                    <td className="px-3 py-2">{row.team_name ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-zinc-500">
            Pitching ({game.pitching_lines.length})
          </h2>
          <div className="overflow-x-auto rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
            <table className="w-full min-w-[480px] text-left text-sm">
              <thead className="border-b border-zinc-200 bg-zinc-50 text-xs font-medium uppercase text-zinc-600 dark:border-zinc-800 dark:bg-zinc-800/50 dark:text-zinc-400">
                <tr>
                  <th className="px-3 py-2">Player</th>
                  <th className="px-3 py-2">Team</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {game.pitching_lines.map((row, i) => (
                  <tr key={`p-${row.player_id ?? i}-${i}`}>
                    <td className="px-3 py-2">{row.player_name ?? "—"}</td>
                    <td className="px-3 py-2">{row.team_name ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}
