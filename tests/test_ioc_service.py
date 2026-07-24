import pytest

from ioc_service import DANGEROUS, SAFE, determine_status, validate_ip_address


@pytest.mark.parametrize(
    ("risk_score", "threshold", "expected"),
    [
        (0, 50, SAFE),
        (50, 50, SAFE),
        (51, 50, DANGEROUS),
        (100, 50, DANGEROUS),
        (30, 20, DANGEROUS),
        (30, 40, SAFE),
    ],
)
def test_determine_status(risk_score, threshold, expected):
    assert determine_status(risk_score, threshold) == expected


@pytest.mark.parametrize("value", ["8.8.8.8", "1.1.1.1", "::1", "2001:db8::1"])
def test_validate_ip_address_accepts_valid(value):
    assert validate_ip_address(value) == value


@pytest.mark.parametrize(
    "value",
    ["not-an-ip", "", "999.1.1.1", "8.8.8", "8.8.8.8.8", " 8.8.8.8"],
)
def test_validate_ip_address_rejects_invalid(value):
    with pytest.raises(ValueError):
        validate_ip_address(value)
