from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import RowMapping, or_, select
from sqlalchemy.orm import Session

from mlbetl.api.deps import get_db
from mlbetl.api.schemas import BoxscoreLineOut, GameDetailOut, GameOut
from mlbetl.db import batting_lines, games, pitching_lines

router = APIRouter(prefix="/games", tags=["games"])


def _day_start_utc(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


def _day_end_utc(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, 23, 59, 59, 999999, tzinfo=timezone.utc)


def _row_to_game_out(row: RowMapping) -> GameOut:
    d = dict(row)
    return GameOut.model_validate(d)


@router.get("/{game_id}", response_model=GameDetailOut)
def get_game(
    game_id: int,
    db: Session = Depends(get_db),
    include_boxscore: bool = Query(False, description="Include batting and pitching lines"),
) -> GameDetailOut:
    row = db.execute(select(games).where(games.c.game_id == game_id)).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="game not found")
    base = _row_to_game_out(row).model_dump()
    detail: dict[str, Any] = {**base, "batting_lines": [], "pitching_lines": []}

    if include_boxscore:
        bats = db.execute(select(batting_lines).where(batting_lines.c.game_id == game_id)).mappings().all()
        pits = db.execute(select(pitching_lines).where(pitching_lines.c.game_id == game_id)).mappings().all()
        detail["batting_lines"] = [BoxscoreLineOut.model_validate(dict(r)).model_dump() for r in bats]
        detail["pitching_lines"] = [BoxscoreLineOut.model_validate(dict(r)).model_dump() for r in pits]

    return GameDetailOut.model_validate(detail)


def _games_list_query(
    *,
    date_from: Optional[date],
    date_to: Optional[date],
    team: Optional[str],
    status: Optional[str],
    winner: Optional[str],
    rl_winner: Optional[str],
    ou_result: Optional[str],
):
    q = select(games)
    if date_from is not None:
        q = q.where(games.c.date_utc >= _day_start_utc(date_from))
    if date_to is not None:
        q = q.where(games.c.date_utc <= _day_end_utc(date_to))
    if team:
        pat = f"%{team}%"
        q = q.where(or_(games.c.home_team.ilike(pat), games.c.away_team.ilike(pat)))
    if status:
        q = q.where(games.c.status == status)
    if winner:
        q = q.where(games.c.winner == winner)
    if rl_winner:
        q = q.where(games.c.rl_winner == rl_winner)
    if ou_result:
        q = q.where(games.c.ou_result == ou_result)
    return q.order_by(games.c.date_utc.desc(), games.c.game_id.desc())


@router.get("", response_model=list[GameOut])
def list_games(
    db: Session = Depends(get_db),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    team: Optional[str] = Query(None, description="Substring match on home or away team name"),
    status: Optional[str] = Query(None),
    winner: Optional[str] = Query(None),
    rl_winner: Optional[str] = Query(None),
    ou_result: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[GameOut]:
    q = _games_list_query(
        date_from=date_from,
        date_to=date_to,
        team=team,
        status=status,
        winner=winner,
        rl_winner=rl_winner,
        ou_result=ou_result,
    )
    q = q.limit(limit).offset(offset)
    rows = db.execute(q).mappings().all()
    return [GameOut.model_validate(dict(r)) for r in rows]
