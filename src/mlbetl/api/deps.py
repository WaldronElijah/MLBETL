from __future__ import annotations

from collections.abc import Generator
from typing import Optional

from sqlalchemy.orm import Session, sessionmaker

from mlbetl.db import get_engine, make_session_factory

_factory: Optional[sessionmaker] = None


def get_session_factory() -> sessionmaker:
    global _factory
    if _factory is None:
        _factory = make_session_factory(get_engine())
    return _factory


def get_db() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
