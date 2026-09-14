"""
DNS Recovery Module

Restores Windows DNS configuration to the trusted
DNS baseline using netsh.
"""

import subprocess


def build_recovery_commands(interface_alias, trusted_dns):
    """
    Build the netsh commands used to restore
    the trusted DNS servers.
    """

    if not interface_alias:
        raise ValueError("Interface alias is required.")

    if not trusted_dns:
        raise ValueError("Trusted DNS servers are required.")

    dns_servers = [str(server).strip() for server in trusted_dns]

    commands = []

    # Set the primary DNS server
    commands.append([
        "netsh",
        "interface",
        "ip",
        "set",
        "dns",
        f"name={interface_alias}",
        "static",
        dns_servers[0]
    ])

    # Add additional DNS servers
    for index, server in enumerate(dns_servers[1:], start=2):
        commands.append([
            "netsh",
            "interface",
            "ip",
            "add",
            "dns",
            f"name={interface_alias}",
            server,
            f"index={index}"
        ])

    return commands


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
            "error": error.stderr.strip(),
            "return_code": error.returncode
        }


def recover_dns(interface_alias, trusted_dns, dry_run=False):
    """
    Restore DNS configuration to the trusted baseline.

    When dry_run=True, the commands are displayed
    but not executed.
    """

    commands = build_recovery_commands(
        interface_alias,
        trusted_dns
    )

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "commands": commands
        }

    outputs = []

    try:
        for command in commands:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )

            outputs.append(result.stdout.strip())

        cache_result = clear_dns_cache()

        return {
            "success": True,
            "dry_run": False,
            "commands": commands,
            "output": "\n".join(outputs),
            "cache_cleared": cache_result["success"],
            "cache_output": cache_result.get("output", ""),
            "cache_error": cache_result.get("error", "")
        }

    except subprocess.CalledProcessError as error:
        return {
            "success": False,
            "dry_run": False,
            "commands": commands,
            "output": error.stdout.strip(),
            "error": error.stderr.strip(),
            "return_code": error.returncode
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

    print("\nCommands:")

    for command in result["commands"]:
        print(" ".join(command))

    print("\nOutput:")
    print(result.get("output", ""))

    print("\nError:")
    print(result.get("error", ""))

    print("\nCache cleared:")
    print(result.get("cache_cleared", "N/A"))

    print("\nReturn code:")
    print(result.get("return_code", "N/A"))
