"""
Main DNS Hijacking Detection System

Coordinates DNS monitoring, baseline comparison,
incident logging, recovery, and recovery verification.
"""

from scripts.dns_monitor import get_dns_configuration
from scripts.dns_detection import (
    detect_dns_change,
    verify_dns_change
)
from scripts.dns_recovery import recover_dns
from scripts.dns_recovery_verification import verify_dns_recovery
from flask import Flask, render_template
from scripts.database import (
    initialize_database,
    get_active_baseline,
    record_dns_history,
    record_incident,
    record_recovery_action,
    update_system_state,
    get_system_state,
    get_incidents,
    get_dns_history
)

app = Flask(__name__)


@app.route("/")
def dashboard():
    """
    Display the DNS monitoring dashboard.
    """

    system_state = get_system_state()
    incidents = get_incidents()
    dns_history = get_dns_history()

    return render_template(
        "dashboard.html",
        system_state=system_state,
        incidents=incidents,
        dns_history=dns_history
    )


def run_dns_check(interface_alias):
    """
    Perform one complete DNS monitoring cycle.

    The cycle:
    1. Collects current DNS configuration.
    2. Retrieves the trusted baseline.
    3. Records DNS history.
    4. Compares current DNS with the baseline.
    5. Detects and verifies changes.
    6. Recovers DNS if an unauthorized change is detected.
    7. Verifies recovery.
    8. Records the result in the database.
    """

    print("=" * 60)
    print("DNS HIJACKING DETECTION SYSTEM")
    print("=" * 60)

    # ---------------------------------------------------------
    # Step 1: Collect current DNS configuration
    # ---------------------------------------------------------

    print("\n[1] Collecting current DNS configuration...")

    dns_configuration = get_dns_configuration()

    current_dns = []

    for entry in dns_configuration:
        if (
            entry["InterfaceAlias"] == interface_alias
            and entry["AddressFamily"] == 2
        ):
            current_dns.extend(entry["ServerAddresses"])

    print("Current DNS:", current_dns)

    # ---------------------------------------------------------
    # Step 2: Retrieve trusted baseline
    # ---------------------------------------------------------

    print("\n[2] Loading trusted DNS baseline...")

    baseline = get_active_baseline(interface_alias)

    if baseline is None:
        print("ERROR: No trusted DNS baseline found.")
        return

    trusted_dns = baseline["dns_servers"]

    print("Trusted DNS:", trusted_dns)

    # ---------------------------------------------------------
    # Step 3: Record DNS history
    # ---------------------------------------------------------

    record_dns_history(
        interface_alias,
        current_dns
    )

    # ---------------------------------------------------------
    # Step 4: Detect DNS change
    # ---------------------------------------------------------

    print("\n[3] Checking DNS configuration...")

    status = detect_dns_change(
        current_dns,
        trusted_dns
    )

    print("Detection result:", status)

    # ---------------------------------------------------------
    # Step 5: Normal configuration
    # ---------------------------------------------------------

    if status == "NORMAL":

        print("\nDNS configuration is trusted.")
        print("No recovery required.")

        update_system_state(
            status="NORMAL",
            interface_alias=interface_alias,
            dns_servers=current_dns
        )

        return

    # ---------------------------------------------------------
    # Step 6: Verify detected change
    # ---------------------------------------------------------

    print("\n[4] Verifying DNS discrepancy...")

    confirmed = verify_dns_change(
        current_dns,
        trusted_dns
    )

    if not confirmed:

        print("DNS change could not be confirmed.")

        update_system_state(
            status="VERIFICATION_FAILED",
            interface_alias=interface_alias,
            dns_servers=current_dns
        )

        return

    print("DNS discrepancy confirmed.")

    # ---------------------------------------------------------
    # Step 7: Record incident
    # ---------------------------------------------------------

    incident_id = record_incident(
        interface_alias=interface_alias,
        current_dns=current_dns,
        trusted_dns=trusted_dns,
        status="detected"
    )

    print("Incident recorded:", incident_id)

    # ---------------------------------------------------------
    # Step 8: Recover DNS
    # ---------------------------------------------------------

    print("\n[5] Attempting automatic DNS recovery...")

    recovery_result = recover_dns(
        interface_alias=interface_alias,
        trusted_dns=trusted_dns,
        dry_run=False
    )

    if recovery_result["success"]:

        print("DNS recovery command executed.")

        recovery_status = "SUCCESS"

    else:

        print("DNS recovery failed.")

        recovery_status = "FAILED"

    # ---------------------------------------------------------
    # Step 9: Log recovery action
    # ---------------------------------------------------------

    record_recovery_action(
        incident_id=incident_id,
        action="DNS recovery",
        result=recovery_status
    )

    # ---------------------------------------------------------
    # Step 10: Verify recovery
    # ---------------------------------------------------------

    print("\n[6] Verifying DNS recovery...")

    if recovery_result["success"]:

        verification = verify_dns_recovery(
            interface_alias=interface_alias,
            trusted_dns=trusted_dns
        )

        if verification["verified"]:

            print("RECOVERY VERIFIED")

            update_system_state(
                status="RECOVERED",
                interface_alias=interface_alias,
                dns_servers=verification["current_dns"]
            )

        else:

            print("RECOVERY VERIFICATION FAILED")

            update_system_state(
                status="RECOVERY_VERIFICATION_FAILED",
                interface_alias=interface_alias,
                dns_servers=verification["current_dns"]
            )

    else:

        update_system_state(
            status="RECOVERY_FAILED",
            interface_alias=interface_alias,
            dns_servers=current_dns
        )


if __name__ == "__main__":

    # Make sure the database exists.
    initialize_database()

    # Interface used for the prototype.
    run_dns_check("WiFi")