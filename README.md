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
