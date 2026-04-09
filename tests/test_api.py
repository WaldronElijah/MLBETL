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


def test_run_line_by_team(client_seeded):
    r = client_seeded.get("/api/stats/run-line-by-team")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    by_team = {row["team"]: row for row in data}
    y = by_team["New York Yankees"]
    assert y["games"] == 1
    assert y["covers"] == 1
    assert y["losses"] == 0
    assert y["pushes"] == 0
    assert y["ats_pct"] == 1.0
    assert abs(y["avg_margin_vs_line"] - 0.5) < 1e-9
    b = by_team["Boston Red Sox"]
    assert b["covers"] == 0
    assert b["losses"] == 1
    assert b["ats_pct"] == 0.0
    assert abs(b["avg_margin_vs_line"] - (-0.5)) < 1e-9


def test_run_line_by_team_empty(client_empty):
    r = client_empty.get("/api/stats/run-line-by-team")
    assert r.status_code == 200
    assert r.json() == []
