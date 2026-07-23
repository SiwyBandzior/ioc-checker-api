SAFE = "SAFE"
DANGEROUS = "DANGEROUS"


def determine_status(risk_score: int, threshold: int) -> str:
    """Czysta funkcja: zamienia liczbowy wynik na werdykt SAFE/DANGEROUS."""
    return DANGEROUS if risk_score > threshold else SAFE
