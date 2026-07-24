# IoC Checker API

![Tests](https://github.com/SiwyBandzior/ioc-checker-api/actions/workflows/tests.yml/badge.svg)

REST API do sprawdzania reputacji adresów IP w bazie AbuseIPDB, z zapisem
historii skanów i pełnym pakietem testów automatycznych.

Projekt powstał jako przebudowa mojego wcześniejszego skryptu
[Threat-Intelligence-Automator](https://github.com/SiwyBandzior/Threat-Intelligence-Automator-IoC-Checker)
z jednoplikowego narzędzia CLI do aplikacji o strukturze produkcyjnej.

## Co się zmieniło względem pierwotnego skryptu

| Skrypt pierwotny | Ten projekt |
|---|---|
| Klucz API wpisany w kodzie źródłowym | Zmienne środowiskowe (`.env`), plik poza repozytorium |
| Jedna pętla proceduralna, brak funkcji | Podział na warstwy: klient HTTP / logika / API |
| Brak obsługi nieoczekiwanych odpowiedzi | Własny wyjątek `AbuseIPDBError`, mapowany na HTTP 502 |
| Wynik drukowany na konsolę | Zapis do bazy, historia dostępna przez `GET /ioc/history` |
| Brak walidacji wejścia | Walidacja formatu IP przed wywołaniem zewnętrznego API |
| Brak testów | 28 testów: jednostkowe + API, z mockowaniem |
| Uruchamiane ręcznie | GitHub Actions przy każdym pushu |

## Stack

- **Python 3.12**, **FastAPI**, **Uvicorn**
- **SQLAlchemy 2.0** (async) + **aiosqlite**
- **httpx** — asynchroniczny klient HTTP
- **pytest** + `monkeypatch` — testy jednostkowe i API
- **GitHub Actions** — CI

## Struktura

```
main.py           # endpointy HTTP, modele request/response
config.py         # konfiguracja i sekrety ze zmiennych środowiskowych
abuseipdb.py      # klient zewnętrznego API (izolowany, mockowalny)
ioc_service.py    # logika biznesowa (czyste funkcje)
database.py       # silnik bazy, sesje, zależność get_db
models.py         # model ORM: tabela ioc_scans
tests/            # testy jednostkowe i API
```

Klient HTTP jest celowo oddzielony od logiki biznesowej — dzięki temu
logikę można testować bez sieci, a warstwę API bez zużywania limitu
zapytań AbuseIPDB.

## Uruchomienie

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # i wpisz swój klucz AbuseIPDB

uvicorn main:app --reload
```

Dokumentacja interaktywna: http://localhost:8000/docs

## Endpointy

| Metoda | Ścieżka | Opis |
|---|---|---|
| `GET` | `/health` | Status aplikacji |
| `POST` | `/ioc/check` | Sprawdza pojedyncze IP i zapisuje wynik |
| `GET` | `/ioc/history?limit=50` | Historia skanów, od najnowszych |

Przykład:

```bash
curl -X POST http://localhost:8000/ioc/check \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "8.8.8.8"}'
```

```json
{
  "id": 1,
  "ip_address": "8.8.8.8",
  "country_code": "US",
  "risk_score": 0,
  "status": "SAFE",
  "scanned_at": "2026-07-24T15:15:37.995435+00:00"
}
```

## Testy

```bash
pytest -v
```

Testy są rozdzielone na dwa poziomy:

- **Jednostkowe** (`test_ioc_service.py`) — czyste funkcje w izolacji:
  klasyfikacja ryzyka i walidacja formatu IP. Bez sieci, bez bazy,
  z testami wartości brzegowych (np. wynik dokładnie równy progowi).
- **API** (`test_api.py`) — pełny stos FastAPI z zamockowanym AbuseIPDB.
  Każdy test dostaje świeżą bazę testową przez fixture.

Testowane są nie tylko ścieżki poprawne, ale też:
awaria zewnętrznego API → 502, brak wymaganego pola → 422,
nieudany skan nie trafia do bazy, a niepoprawne IP nie powoduje
wywołania zewnętrznego API (test typu *spy* chroniący limit zapytań).

Testy nie odpytują prawdziwego AbuseIPDB — reputacja adresów zmienia się
w czasie, więc testy zależne od żywych danych dawałyby fałszywe wyniki.

## Dalsze kroki

- [ ] Migracja `httpx` → `httpx2`
- [ ] Endpoint zbiorczy (`POST /ioc/check/bulk`)
- [ ] Frontend w React: formularz i tabela historii
- [ ] Testy E2E (Playwright)
- [ ] Docker Compose
