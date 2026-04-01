from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from mlbetl.api.deps import get_db
from mlbetl.api.routers.games import _games_list_query
from mlbetl.api.schemas import GameOut

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/{team}/games", response_model=list[GameOut])
def team_games(
    team: str,
    db: Session = Depends(get_db),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[GameOut]:
    q = _games_list_query(
        date_from=date_from,
        date_to=date_to,
        team=team,
        status=status,
        winner=None,
        rl_winner=None,
        ou_result=None,
    )
    q = q.limit(limit).offset(offset)
    rows = db.execute(q).mappings().all()
    return [GameOut.model_validate(dict(r)) for r in rows]
