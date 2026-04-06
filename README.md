# MLBETL (ESPN → Postgres → FastAPI)

Ingest MLB game and boxscore data from ESPN’s **JSON summary** API, normalize into Postgres, and read it back through a small **FastAPI** service.

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Copy `.env.example` to `.env` and set `DATABASE_URL`.

After pulling parser changes, prefer **`pip install -e .`** (or `PYTHONPATH=src` on every command) so Python does not import an older `mlbetl` from another path.

### Troubleshooting: venue / starters / records stay NULL in Postgres

The parser fills those from ESPN’s `gameInfo.venue`, `competitors[].probables`, and `competitors[].record`. If **odds and scores update** but those columns stay NULL, the run is often using **stale code** (wrong `mlbetl` on `PYTHONPATH`).

1. Verify which module file runs:

   ```bash
   PYTHONPATH=src python -c "import mlbetl.espn as e; print(e.__file__, getattr(e, 'PARSER_EXTRACT_REVISION', 0))"
   ```

   You should see your project’s `src/mlbetl/espn.py` and **`PARSER_EXTRACT_REVISION` 2** (or higher).

2. Re-run ingest with diagnostics:

   ```bash
   PYTHONPATH=src python -m mlbetl.run --mode range --start 401814703 --end 401814703 -v
   ```

   Stderr should show non-null `venue_name` and starter names when ESPN returns them.

3. If `(base)` conda and `.venv` are both active, ensure **`which python`** points at `.venv/bin/python` before `pip install -e .`.

## Database schema

Create tables with Alembic (recommended):

```bash
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/mlb"
source .venv/bin/activate
PYTHONPATH=src alembic upgrade head
```

For quick local experiments you can also rely on `create_tables` in the ingest command, but **Alembic is the source of truth** for the expected schema.

## Ingest (ETL)

From the project root, **`PYTHONPATH` must include `src`** so `mlbetl` imports resolve.

**Game ID range** (404s skipped):

```bash
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/mlb"
PYTHONPATH=src python -m mlbetl.run --mode range --start 401814703 --end 401814733 --db "$DATABASE_URL"
```

**Scoreboard by date** (one or more `YYYYMMDD`, comma-separated):

```bash
PYTHONPATH=src python -m mlbetl.run --mode schedule --dates 20260330,20260331
```

Options:

- `--save-raw DIR` — write each raw ESPN summary JSON to `DIR/<game_id>.json`.
- `--sleep SECONDS` — delay between requests (default from `ESPN_REQUEST_DELAY_S` or `0.35`).
- `--db URL` — override `DATABASE_URL`.
- `-q` / `--quiet` — suppress discovery and final `done:` summary lines on stderr.

**Schedule run summaries (stderr):** After resolving the scoreboard, the CLI prints how many unique game IDs were found, e.g. `[mlbetl] schedule: dates=20260401 unique_game_ids=12`. When the loop finishes, it prints `[mlbetl] done: scheduled=N ok=K failed=M`. Counts come from ESPN for that day (nothing is hardcoded).

### Daily automation (cron & GitHub Actions)

**GitHub Actions:** [.github/workflows/etl-daily.yml](.github/workflows/etl-daily.yml) runs on a UTC `schedule` (default 11:00 UTC) and on `workflow_dispatch`. Add a repository secret **`DATABASE_URL`** with your SQLAlchemy URL. The workflow ingests the **previous** Eastern calendar day so a morning run targets the completed slate: `DATES=$(TZ=America/New_York date -d yesterday +%Y%m%d)` (GNU `date`, as on `ubuntu-latest`). The runner must be able to reach your Postgres host (Supabase pooler, public host, or a self-hosted runner if the DB is IP-restricted). GitHub’s `schedule` event can be delayed; it is not real-time. This workflow does not run `alembic upgrade`; apply migrations where you deploy the database.

**Cron (VPS or Linux host):** Same as Actions — **yesterday** in Eastern time (GNU `date`):

```bash
# 6:05 AM America/New_York daily — adjust path and how you load DATABASE_URL
5 6 * * * cd /path/to/MLBETL && . .venv/bin/activate && export DATABASE_URL="postgresql+psycopg2://..." && DATES=$(TZ=America/New_York date -d yesterday +%Y%m%d) && PYTHONPATH=src python -m mlbetl.run --mode schedule --dates "$DATES" --db "$DATABASE_URL"
```

**macOS cron:** BSD `date` has no `-d`; use e.g. `DATES=$(TZ=America/New_York date -v-1d +%Y%m%d)`.

To also refresh the current Eastern day (e.g. late games), pass two comma-separated `YYYYMMDD` values (yesterday and today). On GNU/Linux: `$(TZ=America/New_York date -d yesterday +%Y%m%d),$(TZ=America/New_York date +%Y%m%d)`; on macOS use `date -v-1d` for yesterday and plain `date` for today. That doubles scoreboard requests for those runs.

## Read API (FastAPI)

```bash
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/mlb"
PYTHONPATH=src uvicorn mlbetl.api.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: `http://localhost:8000/docs`
- `GET /api/games` — filters: `date_from`, `date_to`, `team`, `status`, `winner`, `rl_winner`, `ou_result`, `limit`, `offset`
- `GET /api/games/{game_id}?include_boxscore=true`
- `GET /api/teams/{team}/games` — same date/status filters; `team` is a substring match on home or away name.

CORS for local Next.js: set `CORS_ORIGINS` in `.env` (comma-separated).

## Data model (high level)

- **`games`**: metadata, venue fields, starters, pickcenter JSON, DraftKings blob if found, umpires, normalized `status`, derived `winner` / `margin` / `total_runs` / `rl_winner` / `ou_result` when the game is final and lines exist.
- **`batting_lines` / `pitching_lines`**: one row per player line; `stats` is JSONB.

Run line convention in `clean_game`: `opening_spread` is the **home** team’s line from ESPN (e.g. -1.5 = home favored 1.5). Home covers when \((home\_score - away\_score) > -spread\).

## Next.js frontend

Use `NEXT_PUBLIC_API_URL=http://localhost:8000` and call only the FastAPI routes above (no ESPN from the browser). Scaffold with `create-next-app` in a sibling directory when you are ready.
