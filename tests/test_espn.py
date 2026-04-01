from __future__ import annotations

import json
from pathlib import Path

from mlbetl.clean import clean_game
from mlbetl.espn import parse_boxscore_lines, parse_game_core

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_parse_game_core_from_fixture():
    raw = json.loads((FIXTURES / "summary_minimal.json").read_text(encoding="utf-8"))
    core = parse_game_core(raw, game_id=401814703)

    assert core.game_id == 401814703
    assert core.home_team == "New York Yankees"
    assert core.away_team == "Boston Red Sox"
    assert core.home_score == 5
    assert core.away_score == 3
    assert core.game_status and "final" in core.game_status.lower()
    assert core.venue_name == "Yankee Stadium"
    assert core.venue_city == "Bronx"
    assert core.opening_spread == -1.5
    assert core.opening_total == 8.5
    assert core.draftkings_lines is not None
    assert "HP Umpire" in core.umpires


def test_parse_boxscore_lines_from_fixture():
    raw = json.loads((FIXTURES / "summary_minimal.json").read_text(encoding="utf-8"))
    bat, pit = parse_boxscore_lines(raw)

    assert len(bat) == 1
    assert bat[0]["player_name"] == "Sample Hitter"
    assert bat[0]["ab"] == "4"
    assert bat[0]["h"] == "2"

    assert len(pit) == 1
    assert pit[0]["player_name"] == "Sample Pitcher"
    assert pit[0]["ip"] == "6.0"


def test_clean_game_derived_from_fixture_core():
    raw = json.loads((FIXTURES / "summary_minimal.json").read_text(encoding="utf-8"))
    core = parse_game_core(raw, game_id=1)
    out = clean_game(core)

    assert out["status"] == "final"
    assert out["home_record"] == "10-5"
    assert out["away_record"] == "8-7"
    assert out["winner"] == "New York Yankees"
    assert out["loser"] == "Boston Red Sox"
    assert out["total_runs"] == 8
    assert out["margin"] == 2
    assert out["rl_winner"] == "home"
    assert out["ou_result"] == "under"
