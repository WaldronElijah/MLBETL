from __future__ import annotations

from dataclasses import replace

from mlbetl.clean import clean_game
from mlbetl.espn import GameCore


def _core(**kwargs) -> GameCore:
    base = GameCore(
        game_id=1,
        date_utc=None,
        game_status="Final",
        home_team="Home Town",
        away_team="Away Town",
        home_score=4,
        away_score=2,
        venue_name=None,
        venue_city=None,
        venue_state=None,
        location=None,
        starting_pitchers={"home": None, "away": None},
        opening_spread=-1.5,
        opening_total=7.5,
        pickcenter=[],
        draftkings_lines=None,
        records_before_game={"home": {}, "away": {}},
        umpires=[],
    )
    return replace(base, **kwargs)


def test_clean_game_push_run_line():
    core = _core(home_score=3, away_score=2, opening_spread=-1.0)
    out = clean_game(core)
    assert out["rl_winner"] == "push"


def test_clean_game_push_total():
    core = _core(home_score=4, away_score=3, opening_total=7.0)
    out = clean_game(core)
    assert out["ou_result"] == "push"


def test_clean_game_scheduled_no_winner():
    core = _core(game_status="Scheduled", home_score=None, away_score=None)
    out = clean_game(core)
    assert out["status"] == "scheduled"
    assert out["winner"] is None
    assert out["rl_winner"] is None
    assert out["ou_result"] is None


def test_clean_game_tie_no_winner():
    core = _core(home_score=3, away_score=3)
    out = clean_game(core)
    assert out["winner"] is None
    assert out["loser"] is None
