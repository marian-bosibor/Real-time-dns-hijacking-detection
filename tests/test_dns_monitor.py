import sys
from pathlib import Path

# Allow the test to import dns_monitor.py from the scripts directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))

from dns_monitor import get_dns_configuration


def test_get_dns_configuration_returns_data():
    """Verify that Windows DNS configuration can be collected."""

    dns_configuration = get_dns_configuration()

    assert isinstance(dns_configuration, list)
    assert len(dns_configuration) > 0


def test_dns_configuration_contains_required_fields():
    """Verify that each DNS entry contains the expected fields."""

    dns_configuration = get_dns_configuration()

    for interface in dns_configuration:
        assert "InterfaceAlias" in interface
        assert "InterfaceIndex" in interface
        assert "AddressFamily" in interface
        assert "ServerAddresses" in interface