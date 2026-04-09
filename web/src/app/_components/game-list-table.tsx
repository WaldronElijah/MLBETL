import Link from "next/link";
import type { GameOut } from "@/lib/types";

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

export function GameListTable(props: { games: GameOut[] }) {
  const { games } = props;

  return (
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
            <th className="w-24 px-3 py-2" />
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
              <td className="px-3 py-2">
                {g.status ?? g.game_status ?? "—"}
              </td>
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
      {games.length === 0 && (
        <p className="px-4 py-8 text-center text-sm text-zinc-500">
          No games returned. Ingest data or widen filters in the API.
        </p>
      )}
    </div>
  );
}
