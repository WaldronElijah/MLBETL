import Link from "next/link";

export type HomeTab = "games" | "ats" | "line";

export function hrefForTab(
  tab: HomeTab,
  dates: { date_from?: string; date_to?: string },
): string {
  const p = new URLSearchParams();
  p.set("tab", tab);
  if (dates.date_from) {
    p.set("date_from", dates.date_from);
  }
  if (dates.date_to) {
    p.set("date_to", dates.date_to);
  }
  return `/?${p.toString()}`;
}

export function HomeTabNav(props: {
  active: HomeTab;
  dates: { date_from?: string; date_to?: string };
}) {
  const { active, dates } = props;
  const base =
    "inline-flex items-center rounded-md px-3 py-1.5 text-sm font-medium transition-colors";
  const idle =
    "text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800";
  const on =
    "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900";

  const items: { id: HomeTab; label: string }[] = [
    { id: "games", label: "Games" },
    { id: "ats", label: "Team ATS" },
    { id: "line", label: "Avg vs line" },
  ];

  return (
    <nav
      className="mb-6 flex flex-wrap gap-2 border-b border-zinc-200 pb-4 dark:border-zinc-800"
      aria-label="Data views"
    >
      {items.map((item) => (
        <Link
          key={item.id}
          href={hrefForTab(item.id, dates)}
          className={`${base} ${active === item.id ? on : idle}`}
          aria-current={active === item.id ? "page" : undefined}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
