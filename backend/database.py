import os
import sqlite3


DATABASE = os.getenv("DATABASE_PATH", "scanner.db")


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        filename TEXT NOT NULL,

        sha256 TEXT NOT NULL,

        file_type TEXT,

        file_size INTEGER,

        risk_score INTEGER,

        risk_level TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS indicators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        scan_id INTEGER,

        indicator_type TEXT,

        indicator_name TEXT,

        severity TEXT,

        FOREIGN KEY(scan_id) REFERENCES scans(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS llm_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        scan_id INTEGER,

        model TEXT,

        report TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(scan_id) REFERENCES scans(id)
    )
    """)

    connection.commit()
    connection.close()


def save_scan(
    filename,
    sha256,
    file_type,
    file_size,
    risk_score,
    risk_level
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO scans
    (
        filename,
        sha256,
        file_type,
        file_size,
        risk_score,
        risk_level
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        filename,
        sha256,
        file_type,
        file_size,
        risk_score,
        risk_level
    ))

    connection.commit()

    scan_id = cursor.lastrowid

    connection.close()

    return scan_id


def save_indicator(
    scan_id,
    indicator_type,
    indicator_name,
    severity
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO indicators
    (
        scan_id,
        indicator_type,
        indicator_name,
        severity
    )
    VALUES (?, ?, ?, ?)
    """, (
        scan_id,
        indicator_type,
        indicator_name,
        severity
    ))

    connection.commit()
    connection.close()


def save_llm_report(
    scan_id,
    model,
    report
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO llm_reports
    (
        scan_id,
        model,
        report
    )
    VALUES (?, ?, ?)
    """, (
        scan_id,
        model,
        report
    ))

    connection.commit()
    connection.close()


def get_all_scans():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
    SELECT *
    FROM scans
    ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]