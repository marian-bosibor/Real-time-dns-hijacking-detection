"""
DNS Recovery Verification Module

Checks whether the Windows DNS configuration matches
the trusted DNS configuration after recovery.
"""

import subprocess


def get_current_dns(interface_alias):
    """
    Retrieve the current IPv4 DNS servers for
    a Windows network interface.
    """

    command = [
        "powershell",
        "-Command",
        (
            f'(Get-DnsClientServerAddress '
            f'-InterfaceAlias "{interface_alias}" '
            f'-AddressFamily IPv4).ServerAddresses'
        )
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    dns_servers = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]

    return dns_servers


def verify_dns_recovery(interface_alias, trusted_dns):
    """
    Compare current Windows DNS settings with
    the trusted DNS baseline.
    """

    current_dns = get_current_dns(interface_alias)

    current_dns = sorted(
        server.strip() for server in current_dns
    )

    trusted_dns = sorted(
        str(server).strip() for server in trusted_dns
    )

    return {
        "verified": current_dns == trusted_dns,
        "current_dns": current_dns,
        "trusted_dns": trusted_dns
    }


if __name__ == "__main__":

    result = verify_dns_recovery(
        interface_alias="WiFi",
        trusted_dns=[
            "8.8.8.8",
            "8.8.4.4"
        ]
    )

    print("DNS Recovery Verification")
    print("-------------------------")
    print("Current DNS:", result["current_dns"])
    print("Trusted DNS:", result["trusted_dns"])

    if result["verified"]:
        print("RECOVERY VERIFIED")
    else:
        print("RECOVERY FAILED")