from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class BoxscoreLineOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    game_id: int
    team_id: Optional[int] = None
    team_name: Optional[str] = None
    player_id: Optional[int] = None
    player_name: Optional[str] = None
    stats: dict[str, Any]


class GameOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    game_id: int
    date_utc: Optional[datetime] = None
    game_status: Optional[str] = None
    status: Optional[str] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    venue_name: Optional[str] = None
    venue_city: Optional[str] = None
    venue_state: Optional[str] = None
    location: Optional[str] = None
    starting_pitchers: dict[str, Any]
    opening_spread: Optional[float] = None
    opening_total: Optional[float] = None
    pickcenter: list[Any]
    draftkings_lines: Optional[dict[str, Any]] = None
    records_before_game: dict[str, Any]
    home_record: Optional[str] = None
    away_record: Optional[str] = None
    umpires: list[Any]
    total_runs: Optional[int] = None
    margin: Optional[int] = None
    winner: Optional[str] = None
    loser: Optional[str] = None
    rl_winner: Optional[str] = None
    ou_result: Optional[str] = None
    ingested_at_utc: datetime


class GameDetailOut(GameOut):
    batting_lines: list[BoxscoreLineOut] = []
    pitching_lines: list[BoxscoreLineOut] = []


class TeamRunLineStatsOut(BaseModel):
    """Per-team aggregates over final games with an opening run line."""

    team: str
    games: int
    covers: int
    losses: int
    pushes: int
    ats_pct: Optional[float] = None
    avg_margin_vs_line: Optional[float] = None
