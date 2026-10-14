
import pytest

from scripts.dns_recovery import build_recovery_commands


def test_build_recovery_commands():
    commands = build_recovery_commands(
        "WiFi",
        ["8.8.8.8", "8.8.4.4"]
    )

    # The first command sets the primary DNS server.
    assert commands[0] == [
        "netsh",
        "interface",
        "ip",
        "set",
        "dns",
        "name=WiFi",
        "static",
        "8.8.8.8"
    ]

    # The second command adds the secondary DNS server.
    assert commands[1] == [
        "netsh",
        "interface",
        "ip",
        "add",
        "dns",
        "name=WiFi",
        "8.8.4.4",
        "index=2"
    ]


def test_build_recovery_commands_rejects_missing_interface():
    with pytest.raises(ValueError):
        build_recovery_commands(
            "",
            ["8.8.8.8", "8.8.4.4"]
        )
        assert len(commands) == 2

def test_build_recovery_commands_rejects_missing_dns():
    with pytest.raises(ValueError):
        build_recovery_commands(
            "WiFi",
            []
        )

    
