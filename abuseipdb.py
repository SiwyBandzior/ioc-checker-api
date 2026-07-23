import httpx
from config import get_settings

class AbuseIPDBError(Exception):
    """Wlasny wyjatek: cos poszlo nie tak w rozmowie z AbuseIPDB."""

async def fetch_ip_report(ip_address: str) -> dict:
    settings = get_settings()

    headers = {"Accept": "application/json", "Key": settings.abuseipdb_api_key}
    params = {
        "ipAddress": ip_address,
        "maxAgeInDays": str(settings.abuseipdb_max_age_days),
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                settings.abuseipdb_base_url, headers=headers, params=params
            )
        except httpx.RequestError as exc:
            raise AbuseIPDBError(f"Błąd sieci przy sprawdzaniu {ip_address}: {exc}") from exc
        
    if response.status_code != 200:
        raise AbuseIPDBError(
            f"AbuseIPDB zwróciło status {response.status_code} dla {ip_address}"
        )
    
    try:
        return response.json()["data"]
    except (KeyError, ValueError) as exc:
        raise AbuseIPDBError(f"Nieoczekiwana odpowiedź dla {ip_address}") from exc