from __future__ import annotations

import os
from dataclasses import dataclass


def _env_float(key: str, default: float) -> float:
    raw = os.environ.get(key)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_str(key: str, default: str) -> str:
    return os.environ.get(key) or default


@dataclass(frozen=True)
class Settings:
    """Load from environment (optional `python-dotenv` in entrypoints)."""

    espn_summary_url: str = _env_str(
        "ESPN_SUMMARY_URL",
        "https://site.web.api.espn.com/apis/site/v2/sports/baseball/mlb/summary",
    )
    espn_scoreboard_url: str = _env_str(
        "ESPN_SCOREBOARD_URL",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
    )
    request_timeout_s: float = _env_float("ESPN_TIMEOUT_S", 20.0)
    request_delay_s: float = _env_float("ESPN_REQUEST_DELAY_S", 0.35)
    cors_origins: str = _env_str("CORS_ORIGINS", "http://localhost:3000")


def get_settings() -> Settings:
    return Settings()
