from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.config import get_settings
from app.db.connection import create_database_engine
from app.db.store import PostgresTournamentStore
from app.services.storage import MemoryTournamentStore, TournamentStore

logger = logging.getLogger(__name__)


def create_app(store: TournamentStore | None = None) -> FastAPI:
    settings = get_settings()
    owned_store = store is None
    if store is None:
        store = (
            PostgresTournamentStore(create_database_engine(settings.database_url))
            if settings.database_url
            else MemoryTournamentStore()
        )

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        try:
            yield
        finally:
            if owned_store:
                application.state.tournament_store.close()

    application = FastAPI(
        title="Game Theory Simulator API",
        version="0.1.0",
        description="Configure and analyze reproducible strategy tournaments.",
        lifespan=lifespan,
    )
    application.state.tournament_store = store
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.frontend_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, error: SQLAlchemyError) -> JSONResponse:
        logger.error("Database operation failed (%s)", type(error).__name__)
        return JSONResponse(
            status_code=503, content={"detail": "Database operation failed"}
        )

    application.include_router(api_router, prefix="/api/v1")
    return application


app = create_app()
