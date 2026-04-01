from __future__ import annotations

from dataclasses import dataclass

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter


@dataclass(frozen=True)
class HttpConfig:
    timeout_s: float = 20.0
    user_agent: str = (
        "MLBETL/0.1 (+https://example.invalid; contact=local) "
        "requests"
    )


class HttpClient:
    def __init__(self, config: HttpConfig | None = None) -> None:
        self.config = config or HttpConfig()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.config.user_agent,
                "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
            }
        )

    @retry(
        reraise=True,
        retry=retry_if_exception_type((requests.RequestException,)),
        wait=wait_exponential_jitter(initial=1.0, max=15.0),
        stop=stop_after_attempt(5),
    )
    def get_json(self, url: str, *, params: dict | None = None) -> dict:
        resp = self.session.get(url, params=params, timeout=self.config.timeout_s)
        resp.raise_for_status()
        return resp.json()

