"""
PostgreSQL Database Module
File Security Scanner - Milestone 4

Purpose:
    Manage PostgreSQL database connections and operations
    for the File Security Scanner application.

Database:
    Google Cloud SQL - PostgreSQL

Required environment variables:
    DB_HOST
    DB_NAME
    DB_USER
    DB_PASSWORD

Optional environment variables:
    DB_PORT (default: 5432)
    DB_SSLMODE (default: require)

Security:
    Database credentials are provided through environment variables.
    The database password is retrieved from Google Secret Manager
    by the VM startup script.

Note:
    Database tables have already been created and populated.
    The application user does not need CREATE TABLE permissions.
"""

import os

import psycopg
from psycopg.rows import dict_row


# ============================================================
# 1. PostgreSQL Database Connection
# ============================================================

from contextlib import contextmanager
from functools import lru_cache
from psycopg_pool import ConnectionPool
from backend.secrets import secret_value


@lru_cache(maxsize=1)
def get_pool():
    return ConnectionPool(
        conninfo="",
        kwargs={
            "host": os.environ["DB_HOST"],
            "port": int(os.getenv("DB_PORT", "5432")),
            "dbname": os.environ["DB_NAME"],
            "user": os.environ["DB_USER"],
            "password": secret_value("DB_PASSWORD"),
            "sslmode": os.getenv("DB_SSLMODE", "require"),
            "row_factory": dict_row,
            "connect_timeout": 2,
            "options": "-c statement_timeout=2000 -c lock_timeout=1000",
        },
        min_size=0, max_size=int(os.getenv("DB_POOL_MAX", "5")),
        timeout=2, max_waiting=16, open=True,
        check=ConnectionPool.check_connection,
    )


@contextmanager
def get_connection():
    with get_pool().connection(timeout=2) as connection:
        yield connection


def check_database():
    # Dedicated short-lived connection: no waiting behind long scan requests.
    # First use resolves the configured secret; subsequent checks use cached credentials.
    pool = get_pool()
    with psycopg.connect(**pool.kwargs) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()


# ============================================================
# 2. Verify Database Tables
# ============================================================

def create_tables():
    """
    Verify that the required PostgreSQL tables exist.

    IMPORTANT:
        Tables were already created during the SQLite-to-
        PostgreSQL migration.

        The scanner_app database user has SELECT, INSERT,
        UPDATE, and DELETE permissions, but does not have
        CREATE TABLE permissions.

        Therefore, this function only verifies that the
        required tables are accessible.

    Raises:
        psycopg.Error:
            If a required table is missing or inaccessible.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:

            # Verify scans table.
            cursor.execute(
                "SELECT 1 FROM scans LIMIT 1"
            )

            # Verify indicators table.
            cursor.execute(
                "SELECT 1 FROM indicators LIMIT 1"
            )

            # Verify LLM reports table.
            cursor.execute(
                "SELECT 1 FROM llm_reports LIMIT 1"
            )


# ============================================================
# 3. Save File Scan Results
# ============================================================

def save_scan(
    filename,
    sha256,
    file_type,
    file_size,
    risk_score,
    risk_level,
):
    """
    Insert a new file scan record into PostgreSQL.

    Args:
        filename: Name of the uploaded file.
        sha256: SHA-256 hash of the file.
        file_type: Detected file type.
        file_size: File size in bytes.
        risk_score: Calculated security risk score.
        risk_level: Security risk classification.

    Returns:
        int: ID of the newly created scan record.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO scans (
                    filename,
                    sha256,
                    file_type,
                    file_size,
                    risk_score,
                    risk_level
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    filename,
                    sha256,
                    file_type,
                    file_size,
                    risk_score,
                    risk_level,
                ),
            )

            # PostgreSQL RETURNING retrieves the generated ID.
            scan_id = cursor.fetchone()["id"]

            return scan_id


# ============================================================
# 4. Save Security Indicators
# ============================================================

def save_indicator(
    scan_id,
    indicator_type,
    indicator_name,
    severity,
):
    """
    Save a security indicator associated with a file scan.

    Args:
        scan_id: ID of the related scan.
        indicator_type: Type of detected indicator.
        indicator_name: Name or description of the indicator.
        severity: Severity classification.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:

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
                    scan_id,
                    indicator_type,
                    indicator_name,
                    severity,
                ),
            )


# ============================================================
# 5. Save Gemini AI Reports
# ============================================================

def save_llm_report(
    scan_id,
    model,
    report,
):
    """
    Save an AI-generated security report.

    Args:
        scan_id: ID of the related scan.
        model: Name of the AI model.
        report: Generated security analysis.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO llm_reports (
                    scan_id,
                    model,
                    report
                )
                VALUES (%s, %s, %s)
                """,
                (
                    scan_id,
                    model,
                    report,
                ),
            )


# ============================================================
# 6. Retrieve Scan History
# ============================================================

def get_all_scans():
    """
    Retrieve all file scan records.

    Results are ordered from newest to oldest.

    Returns:
        list[dict]: File scan records.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT *
                FROM scans
                ORDER BY created_at DESC
                """
            )

            scans = cursor.fetchall()

            return scans
