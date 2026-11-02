import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# Project root: PhishGuard-AI/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Store the database in the project root.
DATABASE_PATH = PROJECT_ROOT / "scan_history.db"


def get_connection():
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the scan history table if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                predicted_class INTEGER NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                model TEXT,
                scanned_at TEXT NOT NULL
            )
            """
        )


def save_scan(result: dict):
    """Save a successful URL scan and return its database ID."""
    predicted_class = int(result["predicted_class"])

    # Dataset mapping: 0 = Phishing, 1 = Legitimate.
    prediction = (
        "Phishing"
        if predicted_class == 0
        else "Legitimate"
    )

    confidence = float(
        result["predicted_class_probability"]
    )

    scanned_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO scan_history (
                url,
                predicted_class,
                prediction,
                confidence,
                model,
                scanned_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                result["url"],
                predicted_class,
                prediction,
                confidence,
                result.get("model", "SVD + MLP"),
                scanned_at,
            ),
        )

        return cursor.lastrowid


def get_recent_scans(limit: int = 50):
    """Retrieve the most recent scans."""
    limit = max(1, min(limit, 500))

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                url,
                predicted_class,
                prediction,
                confidence,
                model,
                scanned_at
            FROM scan_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [dict(row) for row in rows]


def get_scan_statistics():
    """Calculate statistics from actual saved scans."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total_scans,
                COALESCE(
                    SUM(CASE WHEN predicted_class = 0
                        THEN 1 ELSE 0 END),
                    0
                ) AS phishing_detected,
                COALESCE(
                    SUM(CASE WHEN predicted_class = 1
                        THEN 1 ELSE 0 END),
                    0
                ) AS legitimate_detected
            FROM scan_history
            """
        ).fetchone()

        return dict(row)
