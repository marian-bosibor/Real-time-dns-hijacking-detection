"""
DNS Hijacking Detection Module

Compares the current Windows DNS configuration against
the trusted DNS baseline.
"""


def normalize_dns_servers(dns_servers):
    """
    Convert DNS server values into a consistent format.

    This prevents differences such as ordering or whitespace
    from causing incorrect comparison results.
    """
    if dns_servers is None:
        return []

    return sorted(
        str(server).strip()
        for server in dns_servers
        if str(server).strip()
    )


def compare_dns_configuration(current_dns, trusted_dns):
    """
    Compare the current DNS configuration with the trusted baseline.

    Returns True when both configurations match.
    Returns False when they are different.
    """

    current = normalize_dns_servers(current_dns)
    trusted = normalize_dns_servers(trusted_dns)

    return current == trusted


def detect_dns_change(current_dns, trusted_dns):
    """
    Detect whether the current DNS configuration differs
    from the trusted DNS baseline.

    Returns:
        'NORMAL' when the configurations match.
        'DISCREPANCY_DETECTED' when they do not match.
    """

    if compare_dns_configuration(current_dns, trusted_dns):
        return "NORMAL"

    return "DISCREPANCY_DETECTED"


def verify_dns_change(current_dns, trusted_dns):
    """
    Verify a DNS discrepancy.

    A DNS configuration that does not match the trusted
    baseline is treated as an unauthorized change for
    the current prototype.

    Returns:
        True  -> confirmed unauthorized DNS change
        False -> no confirmed change
    """

    return not compare_dns_configuration(current_dns, trusted_dns)


if __name__ == "__main__":
    # Example test data for the detection module.
    trusted_dns = ["8.8.8.8", "8.8.4.4"]

    current_dns_normal = ["8.8.8.8", "8.8.4.4"]
    current_dns_changed = ["1.1.1.1", "8.8.4.4"]

    print("Normal configuration:")
    print(detect_dns_change(current_dns_normal, trusted_dns))

    print("\nChanged configuration:")
    print(detect_dns_change(current_dns_changed, trusted_dns))

    print("\nVerification of changed configuration:")
    print(verify_dns_change(current_dns_changed, trusted_dns))