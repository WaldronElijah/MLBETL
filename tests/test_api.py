from __future__ import annotations


def test_health(client_empty):
    r = client_empty.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_games_empty(client_empty):
    r = client_empty.get("/api/games")
    assert r.status_code == 200
    assert r.json() == []


def test_list_games_seeded(client_seeded):
    r = client_seeded.get("/api/games")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["game_id"] == 401814703
    assert data[0]["home_team"] == "New York Yankees"
    assert data[0]["status"] == "final"


def test_get_game_not_found(client_empty):
    r = client_empty.get("/api/games/999")
    assert r.status_code == 404


def test_get_game_detail(client_seeded):
    r = client_seeded.get("/api/games/401814703")
    assert r.status_code == 200
    body = r.json()
    assert body["game_id"] == 401814703
    assert body["batting_lines"] == []
    assert body["pitching_lines"] == []


def test_get_game_include_boxscore(client_seeded_boxscore):
    r = client_seeded_boxscore.get(
        "/api/games/401814703",
        params={"include_boxscore": "true"},
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body["batting_lines"]) == 1
    assert body["batting_lines"][0]["player_name"] == "Sample Hitter"
    assert len(body["pitching_lines"]) == 1


def test_team_games_filter(client_seeded):
    r = client_seeded.get("/api/teams/Yankees/games")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert "Yankees" in data[0]["home_team"]
