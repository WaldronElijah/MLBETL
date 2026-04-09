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
- **Next.js** (`web/`): read-only UI over the API
- **Pytest + GitHub Actions**: tests/CI

## Quick start

Create a venv and install:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Copy [`.env.example`](.env.example) to `.env` and set `DATABASE_URL` (and optional `CORS_ORIGINS`).

Run the read API:

```bash
PYTHONPATH=src uvicorn mlbetl.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend (`web/`)

Next.js app that lists games and shows detail + boxscore lines. See [`web/README.md`](web/README.md).
