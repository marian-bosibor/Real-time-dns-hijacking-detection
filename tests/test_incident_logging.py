
import sqlite3

from scripts.database import (
    initialize_database,
    record_incident,
    get_connection,
)


def test_incident_is_saved_to_database(tmp_path):
    """A detected DNS incident should be stored in SQLite."""

    test_db = tmp_path / "test_dns_monitor.db"

    initialize_database(test_db)

    incident_id = record_incident(
        interface_alias="WiFi",
        current_dns=["1.1.1.1", "8.8.4.4"],
        trusted_dns=["8.8.8.8", "8.8.4.4"],
        status="detected",
        db_path=test_db,
    )

    with get_connection(test_db) as connection:
        row = connection.execute(
            "SELECT * FROM incidents WHERE id = ?",
            (incident_id,),
        ).fetchone()

    assert row is not None
    assert row["interface_alias"] == "WiFi"
    assert row["status"] == "detected"
    assert row["current_dns"] == '["1.1.1.1", "8.8.4.4"]'
    assert row["trusted_dns"] == '["8.8.8.8", "8.8.4.4"]'


def test_recovery_action_is_saved_to_database(tmp_path):
    """A recovery action should be linked to its incident."""

    test_db = tmp_path / "test_recovery.db"

    initialize_database(test_db)

    incident_id = record_incident(
        interface_alias="WiFi",
        current_dns=["1.1.1.1"],
        trusted_dns=["8.8.8.8", "8.8.4.4"],
        status="detected",
        db_path=test_db,
    )

    from scripts.database import record_recovery_action

    record_recovery_action(
        incident_id=incident_id,
        action="Restore trusted DNS configuration",
        result="SUCCESS",
        db_path=test_db,
    )

    with get_connection(test_db) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM recovery_actions
            WHERE incident_id = ?
            """,
            (incident_id,),
        ).fetchone()

    assert row is not None
    assert row["incident_id"] == incident_id
    assert row["action"] == "Restore trusted DNS configuration"
    assert row["result"] == "SUCCESS"
