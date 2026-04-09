import type { TeamRunLineStatsOut } from "@/lib/types";

function fmtPct(x: number | null): string {
  if (x == null) return "—";
  return `${(100 * x).toFixed(1)}%`;
}

function fmtRuns(x: number | null): string {
  if (x == null) return "—";
  const s = x.toFixed(2);
  if (x > 0) return `+${s}`;
  return s;
}

export function RunLineStatsTable(props: {
  rows: TeamRunLineStatsOut[];
  variant: "ats" | "line";
}) {
  const { rows, variant } = props;

  const sorted =
    variant === "ats"
      ? [...rows].sort((a, b) => {
          const pa = a.ats_pct ?? -1;
          const pb = b.ats_pct ?? -1;
          if (pb !== pa) return pb - pa;
          return b.games - a.games;
        })
      : [...rows].sort((a, b) => {
          const ma = a.avg_margin_vs_line ?? 0;
          const mb = b.avg_margin_vs_line ?? 0;
          if (mb !== ma) return mb - ma;
          return b.games - a.games;
        });

  return (
    <div className="overflow-x-auto rounded-lg border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <table className="w-full min-w-[560px] text-left text-sm">
        <thead className="border-b border-zinc-200 bg-zinc-50 text-xs font-medium uppercase tracking-wide text-zinc-600 dark:border-zinc-800 dark:bg-zinc-800/50 dark:text-zinc-400">
          <tr>
            <th className="px-3 py-2">Team</th>
            <th className="px-3 py-2 text-right tabular-nums">Games</th>
            {variant === "ats" ? (
              <>
                <th className="px-3 py-2 text-right tabular-nums">Covers</th>
                <th className="px-3 py-2 text-right tabular-nums">Losses</th>
                <th className="px-3 py-2 text-right tabular-nums">Pushes</th>
                <th className="px-3 py-2 text-right tabular-nums">ATS%</th>
                <th className="px-3 py-2 text-right tabular-nums">
                  Avg vs line
                </th>
              </>
            ) : (
              <th className="px-3 py-2 text-right tabular-nums">
                Avg margin vs line
              </th>
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
          {sorted.map((r) => (
            <tr
              key={r.team}
              className="hover:bg-zinc-50/80 dark:hover:bg-zinc-800/40"
            >
              <td className="px-3 py-2 font-medium">{r.team}</td>
              <td className="px-3 py-2 text-right tabular-nums">{r.games}</td>
              {variant === "ats" ? (
                <>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {r.covers}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {r.losses}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {r.pushes}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {fmtPct(r.ats_pct)}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {fmtRuns(r.avg_margin_vs_line)}
                  </td>
                </>
              ) : (
                <td className="px-3 py-2 text-right tabular-nums">
                  {fmtRuns(r.avg_margin_vs_line)}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
      {sorted.length === 0 && (
        <p className="px-4 py-8 text-center text-sm text-zinc-500">
          No final games with run line data in this range.
        </p>
      )}
      <p className="border-t border-zinc-100 px-3 py-2 text-xs text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
        ATS uses opening run line and final score (same rules as ETL). Avg margin
        vs line is per team, signed runs vs the line (positive = beat the line
        on average).
      </p>
    </div>
  );
}
