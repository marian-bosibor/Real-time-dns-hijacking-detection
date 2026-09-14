"""
Recovery Logging Module

Stores DNS recovery actions in the SQLite database.
"""

import sqlite3
from datetime import datetime


DATABASE_PATH = r"database\dns_monitor.db"


def log_recovery(
    interface_alias,
    previous_dns,
    trusted_dns,
    recovery_status
):
    """
    Store a DNS recovery action in SQLite.
    """

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO recovery_actions
        (
            timestamp,
            interface_alias,
            previous_dns,
            trusted_dns,
            recovery_status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            interface_alias,
            str(previous_dns),
            str(trusted_dns),
            recovery_status
        )
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":

    log_recovery(
        interface_alias="WiFi",
        previous_dns=["192.168.1.100"],
        trusted_dns=["8.8.8.8", "8.8.4.4"],
        recovery_status="SUCCESS"
    )

    print("Recovery action logged successfully.")