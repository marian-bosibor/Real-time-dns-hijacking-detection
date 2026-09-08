"""
Trusted DNS Baseline Management Module

This module defines and validates the trusted DNS configuration
used by the DNS hijacking detection system.
"""

from ipaddress import ip_address


def create_baseline(interface_alias, dns_servers):
    """
    Create a trusted DNS baseline for a network interface.

    Parameters:
        interface_alias (str): Windows network interface name.
        dns_servers (list): Trusted DNS server IP addresses.

    Returns:
        dict: Trusted DNS baseline.
    """

    if not interface_alias:
        raise ValueError("Interface alias cannot be empty.")

    if not dns_servers:
        raise ValueError("At least one DNS server is required.")

    validated_servers = []

    for server in dns_servers:
        try:
            ip_address(server)
            validated_servers.append(server)
        except ValueError:
            raise ValueError(f"Invalid DNS server IP address: {server}")

    return {
        "interface_alias": interface_alias,
        "dns_servers": validated_servers
    }


def compare_with_baseline(current_dns, trusted_dns):
    """
    Compare the current DNS configuration against the trusted baseline.

    Returns:
        bool: True if the DNS configuration matches the baseline,
              otherwise False.
    """

    current = set(current_dns)
    trusted = set(trusted_dns)

    return current == trusted