import pytest

from ioc_service import DANGEROUS, SAFE, determine_status


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
