import main
from abuseipdb import AbuseIPDBError


def fake_report(score: int, country: str):
    async def _fake(ip_address: str) -> dict:
        return {"abuseConfidenceScore": score, "countryCode": country}

    return _fake


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_check_ip_dangerous(client, monkeypatch):
    monkeypatch.setattr(main, "fetch_ip_report", fake_report(87, "RU"))

    response = client.post("/ioc/check", json={"ip_address": "1.2.3.4"})

    assert response.status_code == 200
    body = response.json()
    assert body["risk_score"] == 87
    assert body["status"] == "DANGEROUS"
    assert body["country_code"] == "RU"
    assert body["id"] == 1


def test_check_ip_safe(client, monkeypatch):
    monkeypatch.setattr(main, "fetch_ip_report", fake_report(0, "US"))

    response = client.post("/ioc/check", json={"ip_address": "8.8.8.8"})

    assert response.status_code == 200
    assert response.json()["status"] == "SAFE"


def test_check_ip_upstream_error_returns_502(client, monkeypatch):
    async def failing_fetch(ip_address: str) -> dict:
        raise AbuseIPDBError("symulowany blad sieci")

    monkeypatch.setattr(main, "fetch_ip_report", failing_fetch)

    response = client.post("/ioc/check", json={"ip_address": "1.2.3.4"})

    assert response.status_code == 502


def test_check_ip_rejects_missing_field(client):
    response = client.post("/ioc/check", json={})
    assert response.status_code == 422


def test_history_is_empty_at_start(client):
    response = client.get("/ioc/history")
    assert response.status_code == 200
    assert response.json() == []


def test_history_returns_saved_scans(client, monkeypatch):
    monkeypatch.setattr(main, "fetch_ip_report", fake_report(75, "CN"))
    client.post("/ioc/check", json={"ip_address": "5.6.7.8"})

    monkeypatch.setattr(main, "fetch_ip_report", fake_report(0, "PL"))
    client.post("/ioc/check", json={"ip_address": "9.9.9.9"})

    response = client.get("/ioc/history")

    assert response.status_code == 200
    history = response.json()
    assert len(history) == 2
    assert {entry["ip_address"] for entry in history} == {"5.6.7.8", "9.9.9.9"}


def test_history_respects_limit(client, monkeypatch):
    monkeypatch.setattr(main, "fetch_ip_report", fake_report(10, "DE"))
    for ip in ("1.1.1.1", "2.2.2.2", "3.3.3.3"):
        client.post("/ioc/check", json={"ip_address": ip})

    response = client.get("/ioc/history?limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_failed_scan_is_not_saved(client, monkeypatch):
    async def failing_fetch(ip_address: str) -> dict:
        raise AbuseIPDBError("symulowany blad sieci")

    monkeypatch.setattr(main, "fetch_ip_report", failing_fetch)
    client.post("/ioc/check", json={"ip_address": "1.2.3.4"})

    response = client.get("/ioc/history")

    assert response.json() == []


def test_check_ip_rejects_invalid_format(client):
    response = client.post("/ioc/check", json={"ip_address": "not-an-ip"})
    assert response.status_code == 422


def test_invalid_ip_does_not_call_abuseipdb(client, monkeypatch):
    called = False

    async def spy_fetch(ip_address: str) -> dict:
        nonlocal called
        called = True
        return {"abuseConfidenceScore": 0, "countryCode": "PL"}

    monkeypatch.setattr(main, "fetch_ip_report", spy_fetch)

    client.post("/ioc/check", json={"ip_address": "999.999.999.999"})

    assert called is False


def test_scanned_at_is_utc_aware(client, monkeypatch):
    monkeypatch.setattr(main, "fetch_ip_report", fake_report(10, "PL"))

    response = client.post("/ioc/check", json={"ip_address": "1.2.3.4"})

    assert response.json()["scanned_at"].endswith("+00:00")
