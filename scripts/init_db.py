#!/usr/bin/env python3
"""Apply db/init.sql to PostgreSQL (useful when not using docker-entrypoint-initdb.d)."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_URL = "postgresql://inventory:inventory@localhost:5433/inventory"


def apply_via_psql(db_url: str, sql_path: Path) -> bool:
    psql = shutil.which("psql")
    if not psql:
        return False
    subprocess.run(
        [psql, db_url, "-v", "ON_ERROR_STOP=1", "-f", str(sql_path)],
        check=True,
    )
    return True


def apply_via_sync_db() -> None:
    sync_script = Path(__file__).resolve().parent / "sync_db.py"
    subprocess.run([sys.executable, str(sync_script)], check=True)


def main() -> None:
    db_url = os.getenv("DATABASE_URL", DEFAULT_URL)
    sql_path = Path(__file__).resolve().parent.parent / "db" / "init.sql"
    host = db_url.split("@")[-1] if "@" in db_url else db_url
    print(f"Applying schema to {host}")

    if apply_via_psql(db_url, sql_path):
        print("init.sql applied successfully via psql.")
        return

    print("psql not found — creating tables via sync_db.py instead.")
    apply_via_sync_db()
    print("Schema ready (triggers skipped; use Docker or psql for full init.sql).")


if __name__ == "__main__":
    main()
