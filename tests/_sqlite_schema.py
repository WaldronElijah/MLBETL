"""SQLite copies of ORM tables (JSON instead of JSONB) for API tests."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
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
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

metadata_sqlite = MetaData()

games_sqlite = Table(
    "games",
    metadata_sqlite,
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
    Column("starting_pitchers", JSON, nullable=False),
    Column("opening_spread", Float, nullable=True),
    Column("opening_total", Float, nullable=True),
    Column("pickcenter", JSON, nullable=False),
    Column("draftkings_lines", JSON, nullable=True),
    Column("records_before_game", JSON, nullable=False),
    Column("home_record", String, nullable=True),
    Column("away_record", String, nullable=True),
    Column("umpires", JSON, nullable=False),
    Column("total_runs", Integer, nullable=True),
    Column("margin", Integer, nullable=True),
    Column("winner", String, nullable=True),
    Column("loser", String, nullable=True),
    Column("rl_winner", String, nullable=True),
    Column("ou_result", String, nullable=True),
    Column("ingested_at_utc", DateTime(timezone=True), nullable=False),
)

batting_lines_sqlite = Table(
    "batting_lines",
    metadata_sqlite,
    Column("game_id", Integer, nullable=False),
    Column("team_id", Integer, nullable=True),
    Column("team_name", String, nullable=True),
    Column("player_id", Integer, nullable=True),
    Column("player_name", String, nullable=True),
    Column("stats", JSON, nullable=False),
)

pitching_lines_sqlite = Table(
    "pitching_lines",
    metadata_sqlite,
    Column("game_id", Integer, nullable=False),
    Column("team_id", Integer, nullable=True),
    Column("team_name", String, nullable=True),
    Column("player_id", Integer, nullable=True),
    Column("player_name", String, nullable=True),
    Column("stats", JSON, nullable=False),
)

Index("ix_games_date_utc", games_sqlite.c.date_utc)
Index("ix_games_status", games_sqlite.c.status)
Index("ix_games_home_team", games_sqlite.c.home_team)
Index("ix_games_away_team", games_sqlite.c.away_team)
Index("ix_games_winner", games_sqlite.c.winner)
Index("ix_batting_lines_game_id", batting_lines_sqlite.c.game_id)
Index("ix_pitching_lines_game_id", pitching_lines_sqlite.c.game_id)


def make_sqlite_session_factory():
    # StaticPool: one shared in-memory DB across connections (default :memory: is per-connection).
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    metadata_sqlite.create_all(engine)
    return engine, sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )


def sample_game_row(*, game_id: int = 401814703) -> dict:
    now = datetime.now(tz=timezone.utc)
    return {
        "game_id": game_id,
        "date_utc": now,
        "game_status": "Final",
        "status": "final",
        "home_team": "New York Yankees",
        "away_team": "Boston Red Sox",
        "home_score": 5,
        "away_score": 3,
        "venue_name": "Yankee Stadium",
        "venue_city": "Bronx",
        "venue_state": "NY",
        "location": "Yankee Stadium - Bronx, NY",
        "starting_pitchers": {"home": {"id": 1, "name": "A"}, "away": {"id": 2, "name": "B"}},
        "opening_spread": -1.5,
        "opening_total": 8.5,
        "pickcenter": [],
        "draftkings_lines": None,
        "records_before_game": {"home": {}, "away": {}},
        "home_record": "10-5",
        "away_record": "8-7",
        "umpires": [],
        "total_runs": 8,
        "margin": 2,
        "winner": "New York Yankees",
        "loser": "Boston Red Sox",
        "rl_winner": "home",
        "ou_result": "under",
        "ingested_at_utc": now,
    }


def seed_game(conn, row: dict | None = None) -> None:
    conn.execute(insert(games_sqlite).values(**(row or sample_game_row())))


def seed_boxscore(conn, game_id: int) -> None:
    conn.execute(
        insert(batting_lines_sqlite).values(
            game_id=game_id,
            team_id=10,
            team_name="New York Yankees",
            player_id=1001,
            player_name="Sample Hitter",
            stats={"ab": "4", "h": "2"},
        )
    )
    conn.execute(
        insert(pitching_lines_sqlite).values(
            game_id=game_id,
            team_id=10,
            team_name="New York Yankees",
            player_id=2001,
            player_name="Sample Pitcher",
            stats={"ip": "6.0", "er": "1"},
        )
    )
