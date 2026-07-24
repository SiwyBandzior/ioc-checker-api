import ipaddress

SAFE = "SAFE"
DANGEROUS = "DANGEROUS"


def determine_status(risk_score: int, threshold: int) -> str:
    """Czysta funkcja: zamienia liczbowy wynik na werdykt SAFE/DANGEROUS."""
    return DANGEROUS if risk_score > threshold else SAFE


def validate_ip_address(value: str) -> str:
    """Sprawdza, czy tekst jest poprawnym adresem IPv4 lub IPv6."""
    try:
        ipaddress.ip_address(value)
    except ValueError as exc:
        raise ValueError(f"'{value}' nie jest poprawnym adresem IP") from exc
    return value
