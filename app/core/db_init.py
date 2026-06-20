"""Create database tables on startup (production-safe, idempotent)."""

import logging

from sqlalchemy import inspect, text

from core.database import Base, engine

logger = logging.getLogger(__name__)


def init_database() -> None:
    import models  # noqa: F401 — register models on Base.metadata

    with engine.begin() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))

    Base.metadata.create_all(bind=engine)

    tables = inspect(engine).get_table_names()
    logger.info("Database ready — tables: %s", ", ".join(tables) or "(none)")
