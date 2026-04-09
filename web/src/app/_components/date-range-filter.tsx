import Link from "next/link";
import type { HomeTab } from "./home-tab-nav";
import { hrefForTab } from "./home-tab-nav";

export function DateRangeFilter(props: {
  tab: HomeTab;
  date_from?: string;
  date_to?: string;
}) {
  const { tab, date_from, date_to } = props;

  return (
    <form
      method="get"
      className="mb-6 flex flex-wrap items-end gap-3 rounded-lg border border-zinc-200 bg-white p-3 dark:border-zinc-800 dark:bg-zinc-900"
    >
      <input type="hidden" name="tab" value={tab} />
      <label className="flex flex-col gap-1 text-xs font-medium text-zinc-600 dark:text-zinc-400">
        From
        <input
          type="date"
          name="date_from"
          defaultValue={date_from ?? ""}
          className="rounded border border-zinc-300 bg-white px-2 py-1.5 text-sm text-zinc-900 dark:border-zinc-600 dark:bg-zinc-950 dark:text-zinc-100"
        />
      </label>
      <label className="flex flex-col gap-1 text-xs font-medium text-zinc-600 dark:text-zinc-400">
        To
        <input
          type="date"
          name="date_to"
          defaultValue={date_to ?? ""}
          className="rounded border border-zinc-300 bg-white px-2 py-1.5 text-sm text-zinc-900 dark:border-zinc-600 dark:bg-zinc-950 dark:text-zinc-100"
        />
      </label>
      <button
        type="submit"
        className="rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white dark:bg-zinc-100 dark:text-zinc-900"
      >
        Apply range
      </button>
      {(date_from || date_to) && (
        <Link
          href={hrefForTab(tab, {})}
          className="text-sm text-blue-600 hover:underline dark:text-blue-400"
        >
          Clear dates
        </Link>
      )}
    </form>
  );
}
