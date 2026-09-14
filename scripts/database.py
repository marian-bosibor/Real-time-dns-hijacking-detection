"""
SQLite Database and Event Logging Module

This module manages the local SQLite database used by the
DNS hijacking detection and auto-recovery system.

The database stores:
- Trusted DNS baselines
- DNS configuration history
- Detected DNS incidents
- Recovery actions
- Current system state
"""

import json
import sqlite3
from pathlib import Path


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Default location of the SQLite database
DEFAULT_DB_PATH = PROJECT_ROOT / "database" / "dns_monitor.db"


def get_connection(db_path=DEFAULT_DB_PATH):
    """
    Create and return a connection to the SQLite database.

    The database directory is created automatically if it
    does not already exist.
    """

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    # Enable foreign-key relationships.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(db_path=DEFAULT_DB_PATH):
    """
    Create all required database tables if they do not already exist.
    """

    with get_connection(db_path) as connection:

        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS trusted_baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interface_alias TEXT NOT NULL,
                dns_servers TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS dns_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interface_alias TEXT NOT NULL,
                dns_servers TEXT NOT NULL,
                recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interface_alias TEXT NOT NULL,
                current_dns TEXT NOT NULL,
                trusted_dns TEXT NOT NULL,
                detected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS recovery_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                result TEXT NOT NULL,
                performed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (incident_id)
                    REFERENCES incidents(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS system_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                status TEXT NOT NULL,
                interface_alias TEXT,
                dns_servers TEXT,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        connection.commit()


def save_trusted_baseline(interface_alias, dns_servers, db_path=DEFAULT_DB_PATH):
    """
    Save a trusted DNS baseline.

    Returns:
        int: ID of the saved baseline.
    """

    with get_connection(db_path) as connection:

        cursor = connection.execute(
            """
            INSERT INTO trusted_baselines
                (interface_alias, dns_servers)
            VALUES (?, ?)
            """,
            (
                interface_alias,
                json.dumps(dns_servers)
            )
        )

        connection.commit()

        return cursor.lastrowid


def record_dns_history(interface_alias, dns_servers, db_path=DEFAULT_DB_PATH):
    """
    Record the current DNS configuration in the DNS history table.

    Returns:
        int: ID of the history record.
    """

    with get_connection(db_path) as connection:

        cursor = connection.execute(
            """
            INSERT INTO dns_history
                (interface_alias, dns_servers)
            VALUES (?, ?)
            """,
            (
                interface_alias,
                json.dumps(dns_servers)
            )
        )

        connection.commit()

        return cursor.lastrowid


def record_incident(
    interface_alias,
    current_dns,
    trusted_dns,
    status="detected",
    db_path=DEFAULT_DB_PATH
):
    """
    Record a detected DNS security incident.

    Returns:
        int: ID of the incident.
    """

    with get_connection(db_path) as connection:

        cursor = connection.execute(
            """
            INSERT INTO incidents
                (interface_alias, current_dns, trusted_dns, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                interface_alias,
                json.dumps(current_dns),
                json.dumps(trusted_dns),
                status
            )
        )

        connection.commit()

        return cursor.lastrowid


def record_recovery_action(
    incident_id,
    action,
    result,
    db_path=DEFAULT_DB_PATH
):
    """
    Record an automatic DNS recovery action.

    Returns:
        int: ID of the recovery record.
    """

    with get_connection(db_path) as connection:

        cursor = connection.execute(
            """
            INSERT INTO recovery_actions
                (incident_id, action, result)
            VALUES (?, ?, ?)
            """,
            (
                incident_id,
                action,
                result
            )
        )

        connection.commit()

        return cursor.lastrowid


def update_system_state(
    status,
    interface_alias=None,
    dns_servers=None,
    db_path=DEFAULT_DB_PATH
):
    """
    Store the current state of the DNS monitoring system.
    """

    with get_connection(db_path) as connection:

        connection.execute(
            """
            INSERT INTO system_state
                (id, status, interface_alias, dns_servers)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                status = excluded.status,
                interface_alias = excluded.interface_alias,
                dns_servers = excluded.dns_servers,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                status,
                interface_alias,
                json.dumps(dns_servers) if dns_servers is not None else None
            )
        )

        connection.commit()


def get_active_baseline(interface_alias, db_path=DEFAULT_DB_PATH):
    """
    Retrieve the active trusted DNS baseline for an interface.

    Returns:
        dict or None
    """

    with get_connection(db_path) as connection:

        row = connection.execute(
            """
            SELECT *
            FROM trusted_baselines
            WHERE interface_alias = ?
              AND is_active = 1
            ORDER BY id DESC
            LIMIT 1
            """,
            (interface_alias,)
        ).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "interface_alias": row["interface_alias"],
        "dns_servers": json.loads(row["dns_servers"]),
        "created_at": row["created_at"],
        "is_active": bool(row["is_active"])
    }


def get_dns_history(interface_alias=None, db_path=DEFAULT_DB_PATH):
    """
    Retrieve DNS configuration history.

    If interface_alias is provided, only records for that
    interface are returned.
    """

    with get_connection(db_path) as connection:

        if interface_alias:
            rows = connection.execute(
                """
                SELECT *
                FROM dns_history
                WHERE interface_alias = ?
                ORDER BY id ASC
                """,
                (interface_alias,)
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM dns_history
                ORDER BY id ASC
                """
            ).fetchall()

    return [
        {
            "id": row["id"],
            "interface_alias": row["interface_alias"],
            "dns_servers": json.loads(row["dns_servers"]),
            "recorded_at": row["recorded_at"]
        }
        for row in rows
    ]


def get_incidents(db_path=DEFAULT_DB_PATH):
    """
    Retrieve all recorded DNS incidents.
    """

    with get_connection(db_path) as connection:

        rows = connection.execute(
            """
            SELECT *
            FROM incidents
            ORDER BY id ASC
            """
        ).fetchall()

    return [
        {
            "id": row["id"],
            "interface_alias": row["interface_alias"],
            "current_dns": json.loads(row["current_dns"]),
            "trusted_dns": json.loads(row["trusted_dns"]),
            "detected_at": row["detected_at"],
            "status": row["status"]
        }
        for row in rows
    ]


def get_recovery_actions(incident_id, db_path=DEFAULT_DB_PATH):
    """
    Retrieve recovery actions associated with an incident.
    """

    with get_connection(db_path) as connection:

        rows = connection.execute(
            """
            SELECT *
            FROM recovery_actions
            WHERE incident_id = ?
            ORDER BY id ASC
            """,
            (incident_id,)
        ).fetchall()

    return [
        {
            "id": row["id"],
            "incident_id": row["incident_id"],
            "action": row["action"],
            "result": row["result"],
            "performed_at": row["performed_at"]
        }
        for row in rows
    ]


def get_system_state(db_path=DEFAULT_DB_PATH):
    """
    Retrieve the current system state.

    Returns:
        dict or None
    """

    with get_connection(db_path) as connection:

        row = connection.execute(
            """
            SELECT *
            FROM system_state
            WHERE id = 1
            """
        ).fetchone()

    if row is None:
        return None

    return {
        "status": row["status"],
        "interface_alias": row["interface_alias"],
        "dns_servers": (
            json.loads(row["dns_servers"])
            if row["dns_servers"]
            else None
        ),
        "updated_at": row["updated_at"]
    }


if __name__ == "__main__":
    initialize_database()
    print("SQLite database initialized successfully.")
    print(f"Database location: {DEFAULT_DB_PATH}")