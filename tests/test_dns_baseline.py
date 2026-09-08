import sys
from pathlib import Path

# Allow the test to import modules from the scripts directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))

from dns_baseline import create_baseline, compare_with_baseline


def test_create_valid_baseline():
    """Verify that a valid trusted DNS baseline can be created."""

    baseline = create_baseline(
        "WiFi",
        ["8.8.8.8", "8.8.4.4"]
    )

    assert baseline["interface_alias"] == "WiFi"
    assert baseline["dns_servers"] == ["8.8.8.8", "8.8.4.4"]


def test_matching_dns_configuration():
    """Verify that matching DNS settings are recognized."""

    result = compare_with_baseline(
        ["8.8.8.8", "8.8.4.4"],
        ["8.8.8.8", "8.8.4.4"]
    )

    assert result is True


def test_non_matching_dns_configuration():
    """Verify that different DNS settings are identified."""

    result = compare_with_baseline(
        ["10.10.10.10"],
        ["8.8.8.8", "8.8.4.4"]
    )

    assert result is False


def test_invalid_dns_server_is_rejected():
    """Verify that invalid IP addresses cannot become trusted DNS."""

    try:
        create_baseline(
            "WiFi",
            ["not-a-valid-ip"]
        )
        assert False
    except ValueError:
        assert True