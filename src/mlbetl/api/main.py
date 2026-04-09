from __future__ import annotations

from contextlib import asynccontextmanager

try:
    from dotenv import load_dotenv
except ImportError:

    def load_dotenv(*args, **kwargs):
        return False


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mlbetl.api.routers import games, stats, teams
from mlbetl.config import get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    load_dotenv()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="MLBETL API",
        version="0.1.0",
        lifespan=lifespan,
    )
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(games.router, prefix="/api")
    app.include_router(teams.router, prefix="/api")
    app.include_router(stats.router, prefix="/api")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
