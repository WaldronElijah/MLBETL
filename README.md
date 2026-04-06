# MLBETL (ESPN → Postgres → FastAPI)

This project is a small end-to-end pipeline for MLB games:

- Pull game + boxscore data from ESPN’s JSON “summary” endpoint
- Normalize it into a Postgres schema (games + player lines)
- Serve it back through a lightweight FastAPI read API

It’s basically “grab messy sports JSON, turn it into tables, then make it easy to query”.

## Tech stack

- **Python**: ETL + API
- **Postgres**: storage
- **SQLAlchemy + Alembic**: models/migrations
- **FastAPI + Uvicorn**: read API
- **Pytest + GitHub Actions**: tests/CI

## Quick start

Create a venv and install:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Set env vars:

```bash
cp .env.example .env
# set DATABASE_URL in .env
```

Run migrations:

```bash
set -a && source .env && set +a
PYTHONPATH=src alembic upgrade head
```

## Run the ETL

Two common modes:

- **Game ID range** (skips 404s):

```bash
set -a && source .env && set +a
PYTHONPATH=src python -m mlbetl.run --mode range --start 401814703 --end 401814733 --db "$DATABASE_URL"
```

- **Scoreboard by date** (`YYYYMMDD`, comma-separated):

```bash
set -a && source .env && set +a
PYTHONPATH=src python -m mlbetl.run --mode schedule --dates 20260330,20260331 --db "$DATABASE_URL"
```

- **Calendar range** (inclusive; good for backfills), with polite pacing:

```bash
set -a && source .env && set +a
# Example: fill opening week through 2026-03-29 if your DB already starts at 2026-03-30
PYTHONPATH=src python -m mlbetl.run --mode schedule --date-from 20260326 --date-to 20260329 --db "$DATABASE_URL" --sleep 0.35
```

**GitHub Actions:** [.github/workflows/etl-daily.yml](.github/workflows/etl-daily.yml) runs on a daily UTC cron and ingests **yesterday’s calendar date in `America/New_York`** (same convention as MLB’s Eastern scoreboard day). Set the `DATABASE_URL` repository secret. Manual runs can pass comma-separated `dates` under **workflow_dispatch**.

Useful flags:

- `--save-raw DIR` to write raw ESPN JSON files
- `--sleep SECONDS` to slow down requests

## Run the API

```bash
set -a && source .env && set +a
PYTHONPATH=src uvicorn mlbetl.api.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: `http://localhost:8000/docs`
- Main endpoints:
  - `GET /api/games`
  - `GET /api/games/{game_id}?include_boxscore=true`
  - `GET /api/teams/{team}/games`

If you’re calling it from a local frontend, set `CORS_ORIGINS` in `.env`.

## Automation / CI

- **Daily ingest**: GitHub Actions workflow (scheduled + manual). It expects a repo secret named `DATABASE_URL` pointing to a hosted Postgres instance (not `localhost`).
- **Tests**: `.github/workflows/test.yml` runs `pytest` on pushes/PRs.
