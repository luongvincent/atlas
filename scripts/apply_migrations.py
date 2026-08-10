"""Admin script: apply every /migrations/*.sql file, in filename order,
against the database at DATABASE_URL.

DATABASE_URL is a direct Postgres connection string (Project Settings ->
Database -> Connection string in Supabase) - deliberately NOT part of
config/settings.py or the app's runtime env var surface. It's a
migration-only credential, read straight from .env here, same spirit as
the service role key: admin/offline use only, never touched by request
handlers.

Usage:
    python scripts/apply_migrations.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import psycopg2
from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = PROJECT_ROOT / "migrations"

# Postgres error codes for "this object already exists" - safe to skip so
# the script is idempotent (re-running it re-applies only what's new).
ALREADY_EXISTS_CODES = {
    "42710",  # duplicate_object (e.g. CREATE POLICY on one that exists)
    "42P07",  # duplicate_table
    "42701",  # duplicate_column
    "42723",  # duplicate_function
}


def main() -> None:
    env = dotenv_values(PROJECT_ROOT / ".env")
    database_url = env.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not set in .env", file=sys.stderr)
        sys.exit(1)

    sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not sql_files:
        print("No .sql files found in migrations/", file=sys.stderr)
        sys.exit(1)

    conn = psycopg2.connect(database_url)
    conn.autocommit = False
    applied, skipped = 0, 0
    try:
        for path in sql_files:
            sql = path.read_text(encoding="utf-8")
            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
                conn.commit()
                print(f"Applied {path.name}")
                applied += 1
            except psycopg2.Error as exc:
                conn.rollback()
                if exc.pgcode in ALREADY_EXISTS_CODES:
                    print(f"Skipped {path.name} (already applied): {exc.pgerror.strip()}")
                    skipped += 1
                else:
                    raise
        print(f"\nDone: {applied} applied, {skipped} skipped.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
