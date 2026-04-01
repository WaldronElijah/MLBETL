from __future__ import annotations

import math
from typing import Any, Optional

from mlbetl.espn import GameCore

# Run line `opening_spread` is interpreted as the **home team's** line from ESPN pickcenter:
# e.g. -1.5 means home favored by 1.5; +1.5 means home getting 1.5.
# Home covers iff (home_score - away_score) > (-opening_spread), up to float tolerance.


def _norm_status(game_status: Optional[str]) -> Optional[str]:
    if not game_status:
        return None
    g = game_status.strip().lower()
    if "final" in g:
        return "final"
    if "postponed" in g or "canceled" in g or "cancelled" in g:
        return "canceled_or_pp"
    if "scheduled" in g:
        return "scheduled"
    if any(
        x in g
        for x in (
            "live",
            "in progress",
            "inning",
            "top ",
            "bot ",
            "bottom",
            "middle",
        )
    ):
        return "live"
    return "other"


def _record_summary(side_block: dict[str, Any]) -> Optional[str]:
    if not side_block:
        return None
    summ = side_block.get("summary")
    if isinstance(summ, str) and summ.strip():
        return summ.strip()
    return None


def clean_game(core: GameCore) -> dict[str, Any]:
    """
    Pure: add normalized status, venue/coerced fields already on core, records strings,
    and derived final-game betting fields. Does not mutate `core`.
    """
    status = _norm_status(core.game_status)

    home_rec = _record_summary(core.records_before_game.get("home") or {})
    away_rec = _record_summary(core.records_before_game.get("away") or {})

    hs, asc = core.home_score, core.away_score
    total_runs: Optional[int] = None
    margin: Optional[int] = None
    winner: Optional[str] = None
    loser: Optional[str] = None

    if status == "final" and hs is not None and asc is not None:
        total_runs = hs + asc
        margin = hs - asc
        if margin > 0:
            winner, loser = core.home_team, core.away_team
        elif margin < 0:
            winner, loser = core.away_team, core.home_team
        else:
            winner, loser = None, None

    rl_winner: Optional[str] = None
    ou_result: Optional[str] = None

    sp = core.opening_spread
    tot = core.opening_total

    if status == "final" and hs is not None and asc is not None and sp is not None and not math.isnan(sp):
        diff = hs - asc
        thr = -float(sp)
        if math.isclose(diff, thr, rel_tol=0.0, abs_tol=1e-6):
            rl_winner = "push"
        elif diff > thr:
            rl_winner = "home"
        else:
            rl_winner = "away"

    if status == "final" and hs is not None and asc is not None and tot is not None and not math.isnan(tot):
        tr = float(hs + asc)
        if math.isclose(tr, float(tot), rel_tol=0.0, abs_tol=1e-6):
            ou_result = "push"
        elif tr > float(tot):
            ou_result = "over"
        else:
            ou_result = "under"

    return {
        "status": status,
        "home_record": home_rec,
        "away_record": away_rec,
        "total_runs": total_runs,
        "margin": margin,
        "winner": winner,
        "loser": loser,
        "rl_winner": rl_winner,
        "ou_result": ou_result,
    }
