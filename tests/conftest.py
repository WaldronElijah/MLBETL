from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import mlbetl.api.routers.games as games_mod
from mlbetl.api.deps import get_db
from mlbetl.api.main import create_app
from tests._sqlite_schema import (
    batting_lines_sqlite,
    games_sqlite,
    make_sqlite_session_factory,
    pitching_lines_sqlite,
    sample_game_row,
    seed_boxscore,
    seed_game,
)


@pytest.fixture
def client_empty(monkeypatch):
    _, SessionLocal = make_sqlite_session_factory()
    monkeypatch.setattr(games_mod, "games", games_sqlite)
    monkeypatch.setattr(games_mod, "batting_lines", batting_lines_sqlite)
    monkeypatch.setattr(games_mod, "pitching_lines", pitching_lines_sqlite)

    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client_seeded(monkeypatch):
    engine, SessionLocal = make_sqlite_session_factory()
    monkeypatch.setattr(games_mod, "games", games_sqlite)
    monkeypatch.setattr(games_mod, "batting_lines", batting_lines_sqlite)
    monkeypatch.setattr(games_mod, "pitching_lines", pitching_lines_sqlite)
    with engine.begin() as conn:
        seed_game(conn)

    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client_seeded_boxscore(monkeypatch):
    engine, SessionLocal = make_sqlite_session_factory()
    monkeypatch.setattr(games_mod, "games", games_sqlite)
    monkeypatch.setattr(games_mod, "batting_lines", batting_lines_sqlite)
    monkeypatch.setattr(games_mod, "pitching_lines", pitching_lines_sqlite)
    gid = 401814703
    with engine.begin() as conn:
        seed_game(conn, sample_game_row(game_id=gid))
        seed_boxscore(conn, gid)

    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
