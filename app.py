"""
DNS Hijacking Detection System Application

Provides:
- Continuous DNS monitoring
- Flask web dashboard
- Automatic DNS recovery
"""

import threading
import time

from flask import Flask, render_template

from main import run_dns_check
from scripts.database import (
    initialize_database,
    get_system_state,
    get_incidents,
    get_dns_history
)


app = Flask(__name__)


# ---------------------------------------------------------
# Continuous DNS monitoring
# ---------------------------------------------------------

def monitor_dns():
    """
    Continuously monitor the WiFi DNS configuration.
    """

    while True:

        try:
            run_dns_check("WiFi")

        except Exception as error:
            print("Monitoring error:", error)

        time.sleep(5)


# ---------------------------------------------------------
# Dashboard route
# ---------------------------------------------------------

@app.route("/")
def dashboard():

    system_state = get_system_state()
    incidents = get_incidents()
    dns_history = get_dns_history("WiFi")

    return render_template(
        "dashboard.html",
        system_state=system_state,
        incidents=incidents,
        dns_history=dns_history
    )


# ---------------------------------------------------------
# Start application
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("DNS HIJACKING DETECTION SYSTEM")
    print("=" * 60)

    print("\nInitializing database...")

    initialize_database()

    print("Database ready.")

    print("\nStarting continuous DNS monitoring...")

    monitoring_thread = threading.Thread(
        target=monitor_dns,
        daemon=True
    )

    monitoring_thread.start()

    print("DNS monitoring started.")

    print("\nStarting Flask dashboard...")
    print("Dashboard: http://127.0.0.1:5000")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )