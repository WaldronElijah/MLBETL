from __future__ import annotations

import math
from collections import defaultdict
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from mlbetl.api.deps import get_db
from mlbetl.api.routers import games as games_mod
from mlbetl.api.routers.games import _games_list_query
from mlbetl.api.schemas import TeamRunLineStatsOut

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/run-line-by-team", response_model=list[TeamRunLineStatsOut])
def run_line_by_team(
    db: Session = Depends(get_db),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    min_games: int = Query(1, ge=1, le=500),
) -> list[TeamRunLineStatsOut]:
    """
    Aggregate run-line ATS and average margin vs opening line per team.

    Uses the same home run line and ``rl_winner`` rules as ETL (``clean_game``).
    ``avg_margin_vs_line`` is the mean signed excess vs the line from that team's
    perspective (positive = beat the line on average).
    """
    q = _games_list_query(
        date_from=date_from,
        date_to=date_to,
        team=None,
        status="final",
        winner=None,
        rl_winner=None,
        ou_result=None,
    )
    g = games_mod.games
    q = q.where(
        g.c.margin.isnot(None),
        g.c.opening_spread.isnot(None),
        g.c.rl_winner.isnot(None),
        g.c.home_team.isnot(None),
        g.c.away_team.isnot(None),
    )
    rows = db.execute(q).mappings().all()

    covers: dict[str, int] = defaultdict(int)
    losses: dict[str, int] = defaultdict(int)
    pushes: dict[str, int] = defaultdict(int)
    sum_dev: dict[str, float] = defaultdict(float)
    n_games: dict[str, int] = defaultdict(int)

    for r in rows:
        hs_raw = r["home_team"]
        aws_raw = r["away_team"]
        if not hs_raw or not aws_raw:
            continue
        hs, aws = hs_raw.strip(), aws_raw.strip()
        if not hs or not aws:
            continue
        sp = r["opening_spread"]
        margin = r["margin"]
        rl = r["rl_winner"]
        if sp is None or margin is None or rl is None:
            continue
        if isinstance(sp, float) and math.isnan(sp):
            continue
        thr = -float(sp)
        home_dev = float(margin) - thr
        away_dev = thr - float(margin)

        n_games[hs] += 1
        n_games[aws] += 1
        sum_dev[hs] += home_dev
        sum_dev[aws] += away_dev

        if rl == "home":
            covers[hs] += 1
            losses[aws] += 1
        elif rl == "away":
            covers[aws] += 1
            losses[hs] += 1
        else:
            pushes[hs] += 1
            pushes[aws] += 1

    teams = set(n_games)
    out: list[TeamRunLineStatsOut] = []
    for t in sorted(teams):
        ng = n_games[t]
        if ng < min_games:
            continue
        c, l, p = covers[t], losses[t], pushes[t]
        decided = c + l
        ats_pct = (c / decided) if decided > 0 else None
        avg_dev = sum_dev[t] / ng
        out.append(
            TeamRunLineStatsOut(
                team=t,
                games=ng,
                covers=c,
                losses=l,
                pushes=p,
                ats_pct=ats_pct,
                avg_margin_vs_line=avg_dev,
            )
        )
    return out
