import subprocess
import json


def get_dns_configuration():
    """
    Collect the current DNS configuration from Windows.

    Returns:
        list: DNS configuration for all network interfaces.
    """

    command = [
        "powershell.exe",
        "-NoProfile",
        "-Command",
        (
            "Get-DnsClientServerAddress | "
            "Select-Object InterfaceAlias, InterfaceIndex, AddressFamily, ServerAddresses | "
            "ConvertTo-Json -Compress"
        )
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout.strip()

        if not output:
            return []

        data = json.loads(output)

        # PowerShell returns a dictionary instead of a list
        # when there is only one result.
        if isinstance(data, dict):
            data = [data]

        return data

    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"Failed to retrieve Windows DNS configuration: {error}"
        ) from error

    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Windows returned DNS information in an unexpected format."
        ) from error


if __name__ == "__main__":
    dns_configuration = get_dns_configuration()

    print("Current Windows DNS Configuration")
    print("=" * 40)

    for interface in dns_configuration:
        print(f"Interface: {interface.get('InterfaceAlias')}")
        print(f"Index: {interface.get('InterfaceIndex')}")
        print(f"Address Family: {interface.get('AddressFamily')}")
        print(f"DNS Servers: {interface.get('ServerAddresses')}")
        print("-" * 40)