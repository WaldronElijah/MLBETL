from __future__ import annotations

import os
from typing import Any, Iterable, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    insert,
)
from sqlalchemy.dialects.postgresql import JSONB, insert as pg_insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

metadata = MetaData()

games = Table(
    "games",
    metadata,
    Column("game_id", Integer, primary_key=True),
    Column("date_utc", DateTime(timezone=True), nullable=True),
    Column("game_status", String, nullable=True),
    Column("status", String, nullable=True),
    Column("home_team", String, nullable=True),
    Column("away_team", String, nullable=True),
    Column("home_score", Integer, nullable=True),
    Column("away_score", Integer, nullable=True),
    Column("venue_name", String, nullable=True),
    Column("venue_city", String, nullable=True),
    Column("venue_state", String, nullable=True),
    Column("location", String, nullable=True),
    Column("starting_pitchers", JSONB, nullable=False),
    Column("opening_spread", Float, nullable=True),
    Column("opening_total", Float, nullable=True),
    Column("pickcenter", JSONB, nullable=False),
    Column("draftkings_lines", JSONB, nullable=True),
    Column("records_before_game", JSONB, nullable=False),
    Column("home_record", String, nullable=True),
    Column("away_record", String, nullable=True),
    Column("umpires", JSONB, nullable=False),
    Column("total_runs", Integer, nullable=True),
    Column("margin", Integer, nullable=True),
    Column("winner", String, nullable=True),
    Column("loser", String, nullable=True),
    Column("rl_winner", String, nullable=True),
    Column("ou_result", String, nullable=True),
    Column("ingested_at_utc", DateTime(timezone=True), nullable=False),
)

Index("ix_games_date_utc", games.c.date_utc)
Index("ix_games_status", games.c.status)
Index("ix_games_home_team", games.c.home_team)
Index("ix_games_away_team", games.c.away_team)
Index("ix_games_winner", games.c.winner)

batting_lines = Table(
    "batting_lines",
    metadata,
    Column("game_id", Integer, nullable=False),
    Column("team_id", Integer, nullable=True),
    Column("team_name", String, nullable=True),
    Column("player_id", Integer, nullable=True),
    Column("player_name", String, nullable=True),
    Column("stats", JSONB, nullable=False),
)

pitching_lines = Table(
    "pitching_lines",
    metadata,
    Column("game_id", Integer, nullable=False),
    Column("team_id", Integer, nullable=True),
    Column("team_name", String, nullable=True),
    Column("player_id", Integer, nullable=True),
    Column("player_name", String, nullable=True),
    Column("stats", JSONB, nullable=False),
)

Index("ix_batting_lines_game_id", batting_lines.c.game_id)
Index("ix_pitching_lines_game_id", pitching_lines.c.game_id)


def get_engine(db_url: Optional[str] = None) -> Engine:
    url = db_url or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Missing DATABASE_URL (or pass --db).")
    return create_engine(url, pool_pre_ping=True)


def make_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def create_tables(engine: Engine) -> None:
    metadata.create_all(engine)


def upsert_game(engine: Engine, row: dict[str, Any]) -> None:
    allowed = {c.name for c in games.c}
    clean_row = {k: v for k, v in row.items() if k in allowed}
    stmt = pg_insert(games).values(**clean_row)
    stmt = stmt.on_conflict_do_update(
        index_elements=[games.c.game_id],
        set_={
            k: getattr(stmt.excluded, k)
            for k in clean_row
            if k != "game_id"
        },
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def replace_lines(
    engine: Engine,
    *,
    table: Table,
    game_id: int,
    lines: Iterable[dict[str, Any]],
) -> None:
    with engine.begin() as conn:
        conn.execute(table.delete().where(table.c.game_id == game_id))
        payload = list(lines)
        if payload:
            conn.execute(table.insert(), payload)
