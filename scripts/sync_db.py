#!/usr/bin/env python3
"""
Sync PostgreSQL schema with SQLAlchemy models.

Creates missing tables and adds any new columns automatically.
Run after changing models:

    cd backend
    python scripts/sync_db.py

Requires DATABASE_URL (or defaults to local docker-compose Postgres).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow imports from app/
APP_DIR = Path(__file__).resolve().parent.parent / "app"
sys.path.insert(0, str(APP_DIR))

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateTable

from core.config import get_settings
from core.database import Base, engine
import models  # noqa: F401 — register all models on Base.metadata


def get_existing_columns(conn, table_name: str) -> dict[str, dict]:
    result = conn.execute(
        text(
            """
            SELECT column_name, data_type, character_maximum_length,
                   numeric_precision, numeric_scale, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = :table
            ORDER BY ordinal_position
            """
        ),
        {"table": table_name},
    )
    return {row.column_name: dict(row._mapping) for row in result}


def column_sql_type(column) -> str:
    compiled = column.type.compile(dialect=engine.dialect)
    return str(compiled)


def build_add_column_sql(table_name: str, column) -> str:
    col_type = column_sql_type(column)
    parts = [f'ALTER TABLE "{table_name}" ADD COLUMN IF NOT EXISTS "{column.name}" {col_type}']

    if column.server_default is not None:
        default = str(column.server_default.arg)
        parts.append(f"DEFAULT {default}")
    elif not column.nullable and not column.primary_key:
        if hasattr(column.type, "python_type") and column.type.python_type is str:
            parts.append("DEFAULT ''")
        elif hasattr(column.type, "python_type") and column.type.python_type is int:
            parts.append("DEFAULT 0")

    if not column.nullable and not column.primary_key:
        parts.append("NOT NULL")

    return " ".join(parts)


def sync_schema(db_engine: Engine) -> None:
    inspector = inspect(db_engine)
    existing_tables = set(inspector.get_table_names(schema="public"))

    with db_engine.begin() as conn:
        # Create extension used by init.sql
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))

        for table_name, table in Base.metadata.tables.items():
            if table_name not in existing_tables:
                ddl = CreateTable(table).compile(dialect=db_engine.dialect)
                print(f"[CREATE TABLE] {table_name}")
                conn.execute(text(str(ddl)))
                continue

            db_cols = get_existing_columns(conn, table_name)
            model_cols = {c.name: c for c in table.columns}

            for col_name, column in model_cols.items():
                if col_name not in db_cols:
                    sql = build_add_column_sql(table_name, column)
                    print(f"[ADD COLUMN] {table_name}.{col_name}")
                    conn.execute(text(sql))
                else:
                    model_type = column_sql_type(column).upper()
                    db_type = db_cols[col_name]["data_type"].upper()
                    if model_type.split("(")[0] not in db_type and db_type not in model_type:
                        print(
                            f"[WARN] Type mismatch on {table_name}.{col_name}: "
                            f"db={db_type}, model={model_type} — manual migration may be needed"
                        )

    print("Schema sync complete.")


def main() -> None:
    settings = get_settings()
    print(f"Connecting to: {settings.database_url.split('@')[-1]}")
    sync_schema(engine)


if __name__ == "__main__":
    main()
