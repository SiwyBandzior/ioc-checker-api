from fastapi.testclient import TestClient

import main
from abuseipdb import AbuseIPDBError
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_check_ip_dangerous(monkeypatch):
    async def fake_fetch_ip_report(ip_address: str) -> dict:
        return {"abuseConfidenceScore": 87, "countryCode": "RU"}

    monkeypatch.setattr(main, "fetch_ip_report", fake_fetch_ip_report)

    response = client.post("/ioc/check", json={"ip_address": "1.2.3.4"})

    assert response.status_code == 200
    body = response.json()
    assert body["risk_score"] == 87
    assert body["status"] == "DANGEROUS"
    assert body["country_code"] == "RU"


def test_check_ip_safe(monkeypatch):
    async def fake_fetch_ip_report(ip_address: str) -> dict:
        return {"abuseConfidenceScore": 0, "countryCode": "US"}

    monkeypatch.setattr(main, "fetch_ip_report", fake_fetch_ip_report)

    response = client.post("/ioc/check", json={"ip_address": "8.8.8.8"})

    assert response.status_code == 200
    assert response.json()["status"] == "SAFE"


def test_check_ip_upstream_error_returns_502(monkeypatch):
    async def fake_fetch_ip_report(ip_address: str) -> dict:
        raise AbuseIPDBError("symulowany blad sieci")

    monkeypatch.setattr(main, "fetch_ip_report", fake_fetch_ip_report)

    response = client.post("/ioc/check", json={"ip_address": "1.2.3.4"})

    assert response.status_code == 502


def test_check_ip_rejects_missing_field():
    response = client.post("/ioc/check", json={})
    assert response.status_code == 422
