"""
Milestone 4: Import historical SQLite records into Cloud SQL PostgreSQL.

Usage:
    python 003_import_sqlite_history.py --dry-run
    python 003_import_sqlite_history.py --apply

The script must run inside the API container, where the PostgreSQL
connection configuration is available.

No database credentials or historical records are stored in this script.
"""

import argparse
import sqlite3
from pathlib import Path

from backend.database import get_connection


SQLITE_PATH = Path("/tmp/historical-scanner.db")

EXPECTED_SOURCE_COUNTS = {
    "scans": 29,
    "indicators": 15,
    "llm_reports": 13,
}

EXPECTED_INITIAL_COUNTS = {
    "scans": 8,
    "indicators": 3,
    "llm_reports": 4,
}


def load_sqlite_records():
    """Read the historical backup without modifying it."""

    if not SQLITE_PATH.is_file():
        raise FileNotFoundError(
            f"Historical SQLite backup not found: {SQLITE_PATH}"
        )

    source = sqlite3.connect(
        f"file:{SQLITE_PATH}?mode=ro",
        uri=True,
    )
    source.row_factory = sqlite3.Row

    try:
        integrity = source.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        if integrity != "ok":
            raise RuntimeError("SQLite integrity check failed")

        records = {}

        for table in EXPECTED_SOURCE_COUNTS:
            records[table] = [
                dict(row)
                for row in source.execute(
                    f"SELECT * FROM {table} ORDER BY id"
                )
            ]

            actual = len(records[table])
            expected = EXPECTED_SOURCE_COUNTS[table]

            if actual != expected:
                raise RuntimeError(
                    f"SQLite {table}: expected {expected}, found {actual}"
                )

        source_scan_ids = {
            row["id"] for row in records["scans"]
        }

        for table in ("indicators", "llm_reports"):
            for row in records[table]:
                if row["scan_id"] not in source_scan_ids:
                    raise RuntimeError(
                        f"Orphaned SQLite {table} record: {row['id']}"
                    )

        return records

    finally:
        source.close()


def get_counts(cursor):
    """Read PostgreSQL table counts."""

    counts = {}

    for table in EXPECTED_SOURCE_COUNTS:
        cursor.execute(
            f"SELECT COUNT(*) AS total FROM {table}"
        )
        counts[table] = cursor.fetchone()["total"]

    return counts


def run_migration(apply_changes):
    records = load_sqlite_records()

    connection = get_connection()

    try:
        # Explicit transaction handling allows a dry-run rollback.
        if connection.autocommit:
            raise RuntimeError(
                "Expected PostgreSQL autocommit=False; "
                "refusing to run without rollback protection."
            )

        cursor = connection.cursor()

        # Prevent concurrent executions of this migration.
        cursor.execute(
            "SELECT pg_advisory_xact_lock(%s)",
            (20261019003,),
        )

        initial_counts = get_counts(cursor)

        print("=" * 65)
        print("MILESTONE 4 — SQLITE TO CLOUD SQL MIGRATION")
        print("=" * 65)

        print("Mode:", "APPLY" if apply_changes else "DRY RUN")
        print("\nPostgreSQL counts before migration:", initial_counts)

        if initial_counts != EXPECTED_INITIAL_COUNTS:
            raise RuntimeError(
                "PostgreSQL counts differ from the verified baseline. "
                "Migration stopped to prevent duplicate imports."
            )

        # Check identity sequences before generating new IDs.
        for table in EXPECTED_SOURCE_COUNTS:
            cursor.execute(
                f"SELECT COALESCE(MAX(id), 0) AS max_id FROM {table}"
            )
            max_id = cursor.fetchone()["max_id"]

            cursor.execute(
                """
                SELECT last_value
                FROM pg_sequences
                WHERE schemaname = 'public'
                  AND sequencename = %s
                """,
                (f"{table}_id_seq",),
            )

            sequence = cursor.fetchone()

            if sequence is None or sequence["last_value"] is None:
                raise RuntimeError(
                    f"Cannot verify identity sequence for {table}"
                )

            if sequence["last_value"] < max_id:
                raise RuntimeError(
                    f"Identity sequence behind existing IDs: {table}"
                )

        # Map original SQLite scan IDs to newly generated PostgreSQL IDs.
        scan_id_map = {}

        for scan in records["scans"]:
            cursor.execute(
                """
                INSERT INTO scans (
                    filename,
                    sha256,
                    file_type,
                    file_size,
                    risk_score,
                    risk_level,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    scan["filename"],
                    scan["sha256"],
                    scan["file_type"],
                    scan["file_size"],
                    scan["risk_score"],
                    scan["risk_level"],
                    scan["created_at"],
                ),
            )

            scan_id_map[scan["id"]] = cursor.fetchone()["id"]

        # Insert indicators using the remapped scan IDs.
        for indicator in records["indicators"]:
            cursor.execute(
                """
                INSERT INTO indicators (
                    scan_id,
                    indicator_type,
                    indicator_name,
                    severity
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    scan_id_map[indicator["scan_id"]],
                    indicator["indicator_type"],
                    indicator["indicator_name"],
                    indicator["severity"],
                ),
            )

        # Insert LLM reports using the remapped scan IDs.
        for report in records["llm_reports"]:
            cursor.execute(
                """
                INSERT INTO llm_reports (
                    scan_id,
                    model,
                    report,
                    created_at
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    scan_id_map[report["scan_id"]],
                    report["model"],
                    report["report"],
                    report["created_at"],
                ),
            )

        expected_final_counts = {
            table: (
                initial_counts[table] + EXPECTED_SOURCE_COUNTS[table]
            )
            for table in EXPECTED_SOURCE_COUNTS
        }

        actual_final_counts = get_counts(cursor)

        if actual_final_counts != expected_final_counts:
            raise RuntimeError(
                "Post-migration record count verification failed"
            )

        # Verify all newly imported child records point to imported scans.
        imported_scan_ids = set(scan_id_map.values())

        for table in ("indicators", "llm_reports"):
            cursor.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM {table}
                WHERE scan_id = ANY(%s)
                """,
                (list(imported_scan_ids),),
            )

            linked_count = cursor.fetchone()["total"]

            if linked_count != EXPECTED_SOURCE_COUNTS[table]:
                raise RuntimeError(
                    f"Relationship verification failed for {table}"
                )

        print("\nHistorical records processed:")
        for table, rows in records.items():
            print(f"  {table}: {len(rows)}")

        print("\nPostgreSQL counts after test:")
        for table, count in actual_final_counts.items():
            print(f"  {table}: {count}")

        print("\nParent-child relationship verification: PASSED")

        if apply_changes:
            connection.commit()
            print("\nSUCCESS: Migration committed to Cloud SQL.")
        else:
            connection.rollback()
            print("\nSUCCESS: Dry run passed. All inserts rolled back.")
            print("Note: PostgreSQL identity sequences may advance during")
            print("a dry run even though inserted rows are rolled back.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    mode = parser.add_mutually_exclusive_group(required=True)

    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Test migration and roll back",
    )

    mode.add_argument(
        "--apply",
        action="store_true",
        help="Commit migration after validation",
    )

    args = parser.parse_args()

    run_migration(apply_changes=args.apply)
