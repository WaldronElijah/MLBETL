from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from dateutil import parser as date_parser

from mlbetl.config import get_settings
from mlbetl.http import HttpClient


def _dig(obj: Any, *path: Any) -> Any:
    cur = obj
    for key in path:
        if cur is None:
            return None
        if isinstance(cur, dict):
            cur = cur.get(key)
        elif isinstance(cur, list) and isinstance(key, int):
            if 0 <= key < len(cur):
                cur = cur[key]
            else:
                return None
        else:
            return None
    return cur


def _as_int(x: Any) -> Optional[int]:
    if x is None:
        return None
    try:
        return int(x)
    except Exception:
        return None


def _as_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except Exception:
        return None


def _parse_iso_dt(x: Any) -> Optional[datetime]:
    if not x:
        return None
    try:
        return date_parser.isoparse(str(x))
    except Exception:
        return None


@dataclass(frozen=True)
class GameCore:
    game_id: int
    date_utc: Optional[datetime]
    game_status: Optional[str]
    home_team: Optional[str]
    away_team: Optional[str]
    home_score: Optional[int]
    away_score: Optional[int]
    venue_name: Optional[str]
    venue_city: Optional[str]
    venue_state: Optional[str]
    location: Optional[str]
    starting_pitchers: dict
    opening_spread: Optional[float]
    opening_total: Optional[float]
    pickcenter: list
    draftkings_lines: Optional[dict]
    records_before_game: dict
    umpires: list[str]


def fetch_game_summary(client: HttpClient, game_id: int, *, summary_url: str | None = None) -> dict:
    url = summary_url or get_settings().espn_summary_url
    return client.get_json(url, params={"event": str(game_id)})


def fetch_scoreboard_event_ids(client: HttpClient, yyyymmdd: str, *, scoreboard_url: str | None = None) -> list[int]:
    """yyyymmdd e.g. 20260330. Returns ESPN event ids for that MLB scoreboard day."""
    url = scoreboard_url or get_settings().espn_scoreboard_url
    data = client.get_json(url, params={"dates": yyyymmdd})
    events = data.get("events") or []
    out: list[int] = []
    for e in events:
        eid = e.get("id")
        if eid is not None:
            try:
                out.append(int(eid))
            except (TypeError, ValueError):
                continue
    return out


def _parse_umpires(summary: dict) -> list[str]:
    officials = (
        _dig(summary, "gameInfo", "officials")
        or _dig(summary, "header", "competitions", 0, "officials")
        or []
    )
    names: list[str] = []
    if not isinstance(officials, list):
        officials = [officials]
    for o in officials:
        if isinstance(o, dict):
            name = o.get("displayName") or o.get("fullName") or o.get("shortDisplayName")
            if name:
                names.append(str(name))
        elif isinstance(o, str):
            names.append(o)
    return names


def parse_game_core(summary: dict, game_id: int) -> GameCore:
    header = _dig(summary, "header") or {}
    competition = _dig(header, "competitions", 0) or {}
    competitors = _dig(competition, "competitors") or []

    def team_side(home_away: str) -> dict:
        for c in competitors:
            if _dig(c, "homeAway") == home_away:
                return c
        return {}

    home = team_side("home")
    away = team_side("away")

    home_team = _dig(home, "team", "displayName") or _dig(home, "team", "shortDisplayName")
    away_team = _dig(away, "team", "displayName") or _dig(away, "team", "shortDisplayName")

    home_score = _as_int(_dig(home, "score"))
    away_score = _as_int(_dig(away, "score"))

    status = _dig(competition, "status", "type", "description") or _dig(
        header, "status", "type", "description"
    )

    date_utc = _parse_iso_dt(_dig(competition, "date") or _dig(header, "competitions", 0, "date"))

    venue = _dig(competition, "venue") or {}
    venue_name = venue.get("fullName") or venue.get("name")
    address = venue.get("address") or {}
    venue_city = address.get("city")
    venue_state = address.get("state")
    if not venue_name:
        gv = _dig(summary, "gameInfo", "venue") or {}
        venue_name = gv.get("fullName") or gv.get("name")
        gaddr = gv.get("address") or {}
        venue_city = venue_city or gaddr.get("city")
        venue_state = venue_state or gaddr.get("state")

    location = None
    if venue_name and (venue_city or venue_state):
        location = (
            f"{venue_name} - {venue_city or ''}"
            f"{', ' if venue_city and venue_state else ''}{venue_state or ''}"
        ).strip()
    elif venue_name:
        location = venue_name

    def _athlete_from_probables(side: dict) -> Optional[dict]:
        probables = side.get("probables")
        if not isinstance(probables, list):
            return None
        for p in probables:
            if not isinstance(p, dict):
                continue
            if p.get("name") == "probableStartingPitcher" and isinstance(p.get("athlete"), dict):
                return p["athlete"]
        for p in probables:
            if isinstance(p, dict) and isinstance(p.get("athlete"), dict):
                return p["athlete"]
        return None

    # starting pitchers: MLB uses probables[]; fallback to competitor.starter (other feeds)
    starters: dict[str, Any] = {}
    for side_name, side in [("home", home), ("away", away)]:
        athlete = _athlete_from_probables(side)
        if not isinstance(athlete, dict):
            sp = _dig(side, "starter") or _dig(side, "leaders", 0)
            athlete = _dig(sp, "athlete") or _dig(sp, "athlete", 0)
        if isinstance(athlete, dict):
            starters[side_name] = {
                "id": _as_int(athlete.get("id")),
                "name": athlete.get("displayName") or athlete.get("fullName"),
            }
        else:
            starters[side_name] = None

    # records: ESPN MLB uses "record" (singular) on competitors; some feeds use "records"
    recs: dict[str, Any] = {}
    for side_name, side in [("home", home), ("away", away)]:
        combined: list[Any] = []
        for key in ("records", "record"):
            chunk = side.get(key)
            if isinstance(chunk, list):
                combined.extend(chunk)
        chosen = None
        for r in combined:
            if _dig(r, "type") in ("total", "overall"):
                chosen = r
                break
        chosen = chosen or (combined[0] if combined else None)
        recs[side_name] = chosen or {}

    # odds: pickcenter may include multiple providers; try to find DraftKings
    pickcenters = _dig(competition, "odds") or _dig(summary, "pickcenter") or []
    if isinstance(pickcenters, dict):
        pickcenters = [pickcenters]
    pickcenter_copy: list = [
        copy.deepcopy(pc) if isinstance(pc, dict) else pc for pc in pickcenters
    ]
    opening_spread = None
    opening_total = None
    dk_raw = None
    for pc in pickcenters:
        provider = (pc.get("provider") or {}).get("name") or pc.get("provider", {}).get("id")
        details = pc.get("details") or ""
        over_under = pc.get("overUnder")
        spread = pc.get("spread")

        # Opening lines: best-effort; ESPN doesn't consistently flag "open" vs "current"
        if opening_total is None:
            opening_total = _as_float(over_under)
        if opening_spread is None:
            opening_spread = _as_float(spread)

        if provider and isinstance(provider, str) and provider.lower() == "draftkings":
            dk_raw = pc

        # Sometimes DraftKings appears only in details string
        if dk_raw is None and isinstance(details, str) and "DraftKings" in details:
            dk_raw = pc

    umpires = _parse_umpires(summary)

    return GameCore(
        game_id=game_id,
        date_utc=date_utc,
        game_status=status,
        home_team=home_team,
        away_team=away_team,
        home_score=home_score,
        away_score=away_score,
        venue_name=venue_name,
        venue_city=venue_city,
        venue_state=venue_state,
        location=location,
        starting_pitchers=starters,
        opening_spread=opening_spread,
        opening_total=opening_total,
        pickcenter=pickcenter_copy,
        draftkings_lines=dk_raw,
        records_before_game=recs,
        umpires=umpires,
    )


def parse_boxscore_lines(summary: dict) -> tuple[list[dict], list[dict]]:
    """
    Returns (batting_lines, pitching_lines).
    Each item is a flat dict with game/team/player identifiers + raw stat strings.
    """
    box = _dig(summary, "boxscore") or {}
    players = box.get("players") or []

    batting: list[dict] = []
    pitching: list[dict] = []

    for team_block in players:
        team = team_block.get("team") or {}
        team_id = _as_int(team.get("id"))
        team_name = team.get("displayName") or team.get("shortDisplayName")
        statistics = team_block.get("statistics") or []

        for stat_group in statistics:
            name = (stat_group.get("name") or "").lower()
            athletes = stat_group.get("athletes") or []
            keys = stat_group.get("keys") or []

            for a in athletes:
                athlete = a.get("athlete") or {}
                row = a.get("stats") or []
                line = {
                    "team_id": team_id,
                    "team_name": team_name,
                    "player_id": _as_int(athlete.get("id")),
                    "player_name": athlete.get("displayName") or athlete.get("fullName"),
                }
                for k, v in zip(keys, row):
                    line[str(k)] = v

                if name == "batting":
                    batting.append(line)
                elif name == "pitching":
                    pitching.append(line)

    return batting, pitching

