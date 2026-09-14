from scripts.dns_detection import (
    compare_dns_configuration,
    detect_dns_change,
    verify_dns_change
)


def test_matching_dns_configuration():
    """Matching DNS values should be considered normal."""

    trusted_dns = ["8.8.8.8", "8.8.4.4"]
    current_dns = ["8.8.8.8", "8.8.4.4"]

    assert compare_dns_configuration(current_dns, trusted_dns) is True
    assert detect_dns_change(current_dns, trusted_dns) == "NORMAL"


def test_different_dns_configuration():
    """Different DNS values should produce a discrepancy."""

    trusted_dns = ["8.8.8.8", "8.8.4.4"]
    current_dns = ["1.1.1.1", "8.8.4.4"]

    assert compare_dns_configuration(current_dns, trusted_dns) is False
    assert detect_dns_change(
        current_dns,
        trusted_dns
    ) == "DISCREPANCY_DETECTED"


def test_dns_change_is_verified():
    """A DNS mismatch should be confirmed as a change."""

    trusted_dns = ["8.8.8.8", "8.8.4.4"]
    current_dns = ["1.1.1.1", "8.8.4.4"]

    assert verify_dns_change(current_dns, trusted_dns) is True


def test_dns_order_does_not_create_false_detection():
    """
    The same DNS servers in a different order should
    still be considered a matching configuration.
    """

    trusted_dns = ["8.8.8.8", "8.8.4.4"]
    current_dns = ["8.8.4.4", "8.8.8.8"]

    assert compare_dns_configuration(current_dns, trusted_dns) is True
    assert detect_dns_change(current_dns, trusted_dns) == "NORMAL"