from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:

    def load_dotenv(*args, **kwargs):
        return False


from mlbetl.clean import clean_game
from mlbetl.config import get_settings
from mlbetl.db import batting_lines, create_tables, get_engine, pitching_lines, replace_lines, upsert_game
from mlbetl.espn import fetch_game_summary, fetch_scoreboard_event_ids, parse_boxscore_lines, parse_game_core
from mlbetl.http import HttpClient, HttpConfig


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ESPN MLB ETL -> Postgres")
    p.add_argument(
        "--mode",
        choices=["range", "schedule"],
        default="range",
        help="Ingest by numeric gameId range or by scoreboard date(s)",
    )
    p.add_argument("--start", type=int, default=None, help="First ESPN gameId (inclusive), range mode")
    p.add_argument("--end", type=int, default=None, help="Last ESPN gameId (inclusive), range mode")
    p.add_argument(
        "--dates",
        type=str,
        default=None,
        help="Comma-separated dates YYYYMMDD (schedule mode), e.g. 20260330,20260331",
    )
    p.add_argument("--db", type=str, default=None, help="SQLAlchemy DB url (or use DATABASE_URL)")
    p.add_argument(
        "--save-raw",
        type=str,
        default=None,
        metavar="DIR",
        help="If set, write each summary JSON to DIR/<game_id>.json",
    )
    p.add_argument(
        "--sleep",
        type=float,
        default=None,
        help="Seconds to sleep between ESPN requests (default ESPN_REQUEST_DELAY_S or 0.35)",
    )
    return p.parse_args()


def _game_ids_for_args(args: argparse.Namespace) -> list[int]:
    if args.mode == "range":
        if args.start is None or args.end is None:
            print("--start and --end are required for --mode range", file=sys.stderr)
            sys.exit(2)
        return list(range(args.start, args.end + 1))
    if not args.dates:
        print("--dates is required for --mode schedule", file=sys.stderr)
        sys.exit(2)
    return [d.strip() for d in args.dates.split(",") if d.strip()]


def main() -> None:
    load_dotenv()
    args = _parse_args()
    settings = get_settings()
    delay = args.sleep if args.sleep is not None else settings.request_delay_s

    engine = get_engine(args.db)
    create_tables(engine)

    client = HttpClient(HttpConfig(timeout_s=settings.request_timeout_s))

    raw_root: Path | None = Path(args.save_raw) if args.save_raw else None
    if raw_root:
        raw_root.mkdir(parents=True, exist_ok=True)

    spec = _game_ids_for_args(args)

    if args.mode == "schedule":
        game_ids: list[int] = []
        for day in spec:
            try:
                game_ids.extend(fetch_scoreboard_event_ids(client, day))
            except Exception:
                continue
            if delay:
                time.sleep(delay)
        game_ids = sorted(set(game_ids))
    else:
        game_ids = spec  # type: ignore[assignment]

    for game_id in game_ids:
        try:
            summary = fetch_game_summary(client, game_id)
        except Exception:
            continue

        if raw_root:
            (raw_root / f"{game_id}.json").write_text(
                json.dumps(summary, default=str, indent=2),
                encoding="utf-8",
            )

        core = parse_game_core(summary, game_id)
        bat, pit = parse_boxscore_lines(summary)
        cleaned = clean_game(core)

        now = datetime.now(tz=timezone.utc)
        game_row = {
            **asdict(core),
            **cleaned,
            "ingested_at_utc": now,
        }
        upsert_game(engine, game_row)

        bat_rows = [
            {
                "game_id": game_id,
                "team_id": r.get("team_id"),
                "team_name": r.get("team_name"),
                "player_id": r.get("player_id"),
                "player_name": r.get("player_name"),
                "stats": {
                    k: v
                    for k, v in r.items()
                    if k not in {"team_id", "team_name", "player_id", "player_name"}
                },
            }
            for r in bat
        ]
        pit_rows = [
            {
                "game_id": game_id,
                "team_id": r.get("team_id"),
                "team_name": r.get("team_name"),
                "player_id": r.get("player_id"),
                "player_name": r.get("player_name"),
                "stats": {
                    k: v
                    for k, v in r.items()
                    if k not in {"team_id", "team_name", "player_id", "player_name"}
                },
            }
            for r in pit
        ]

        replace_lines(engine, table=batting_lines, game_id=game_id, lines=bat_rows)
        replace_lines(engine, table=pitching_lines, game_id=game_id, lines=pit_rows)

        if delay:
            time.sleep(delay)


if __name__ == "__main__":
    main()
