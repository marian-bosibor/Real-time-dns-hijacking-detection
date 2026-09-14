"""
DNS Recovery Module

Restores Windows DNS configuration to the trusted
DNS baseline using PowerShell.
"""

import subprocess


def build_recovery_command(interface_alias, trusted_dns):
    """
    Build the PowerShell command used to restore
    the trusted DNS servers.
    """

    if not interface_alias:
        raise ValueError("Interface alias is required.")

    if not trusted_dns:
        raise ValueError("Trusted DNS servers are required.")

    dns_servers = [str(server).strip() for server in trusted_dns]

    server_addresses = ",".join(
        f'"{server}"' for server in dns_servers
    )

    command = [
        "powershell",
        "-Command",
        (
            f'Set-DnsClientServerAddress '
            f'-InterfaceAlias "{interface_alias}" '
            f'-ServerAddresses {server_addresses}'
        )
    ]

    return command


def clear_dns_cache():
    """
    Clear the Windows DNS resolver cache.
    """

    command = [
        "ipconfig",
        "/flushdns"
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        return {
            "success": True,
            "output": result.stdout.strip()
        }

    except subprocess.CalledProcessError as error:
        return {
            "success": False,
            "error": error.stderr.strip()
        }


def recover_dns(interface_alias, trusted_dns, dry_run=False):
    """
    Restore DNS configuration to the trusted baseline.

    When dry_run=True, the command is displayed but
    not executed.
    """

    command = build_recovery_command(
        interface_alias,
        trusted_dns
    )

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "command": command
        }

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        cache_result = clear_dns_cache()

        return {
            "success": True,
            "dry_run": False,
            "command": command,
            "output": result.stdout.strip(),
            "cache_cleared": cache_result["success"],
            "cache_output": cache_result.get("output", ""),
            "cache_error": cache_result.get("error", "")
        }

    except subprocess.CalledProcessError as error:
        return {
            "success": False,
            "dry_run": False,
            "command": command,
            "error": error.stderr.strip()
        }


if __name__ == "__main__":

    trusted_dns = [
        "8.8.8.8",
        "8.8.4.4"
    ]

    result = recover_dns(
        interface_alias="WiFi",
        trusted_dns=trusted_dns,
        dry_run=False
    )

    print("DNS Recovery Test")
    print("-----------------")
    print("Success:", result["success"])
    print("Dry run:", result["dry_run"])
    print("Command:")
    print(" ".join(result["command"]))