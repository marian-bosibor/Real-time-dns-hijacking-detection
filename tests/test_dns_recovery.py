from scripts.dns_recovery import build_recovery_command


def test_build_recovery_command():
    command = build_recovery_command(
        "WiFi",
        ["8.8.8.8", "8.8.4.4"]
    )

    assert command[0] == "powershell"
    assert "-Command" in command
    assert "WiFi" in command[-1]
    assert "8.8.8.8" in command[-1]
    assert "8.8.4.4" in command[-1]


def test_build_recovery_command_rejects_missing_interface():
    try:
        build_recovery_command(
            "",
            ["8.8.8.8", "8.8.4.4"]
        )
        assert False
    except ValueError:
        assert True


def test_build_recovery_command_rejects_missing_dns():
    try:
        build_recovery_command(
            "WiFi",
            []
        )
        assert False
    except ValueError:
        assert True