# IoC Checker API

REST API for checking threat-intelligence indicators of compromise (IoCs), starting with IP reputation lookups via [AbuseIPDB](https://www.abuseipdb.com/). Built with Python and FastAPI.

> **Status: work in progress.** This is the backend of a larger IoC Checker web platform I am building step by step — see the [roadmap](#roadmap) below.

## Features

- IP reputation check against AbuseIPDB (abuse confidence score, total reports, country, ISP) **[SPRAWDŹ: dopasuj listę pól do tego, co faktycznie zwraca abuseipdb.py]**
- API keys and settings loaded from environment variables (`.env`) — no secrets in code
- Clean module split: `main.py` (API layer), `abuseipdb.py` (provider client), `config.py` (configuration)

## Tech stack

Python 3 · FastAPI · Uvicorn · python-dotenv **[SPRAWDŹ: wyrównaj z requirements.txt — dopisz np. requests/httpx, jeśli używasz]**

## Getting started

```bash
git clone https://github.com/SiwyBandzior/ioc-checker-api.git
cd ioc-checker-api
pip install -r requirements.txt
cp .env.example .env   # add your AbuseIPDB API key
uvicorn main:app --reload
```

Interactive API docs (Swagger UI): http://127.0.0.1:8000/docs

## Example

```
GET /check/ip/8.8.8.8
```

```json
{
  "ip": "8.8.8.8",
  "abuse_confidence_score": 0,
  "total_reports": 0,
  "country": "US"
}
```

**[SPRAWDŹ: podmień na prawdziwy endpoint z main.py i realną odpowiedź — wystarczy skopiować z /docs]**

## Roadmap

- [ ] React frontend (web UI)
- [ ] Automated tests: pytest (API) and Playwright (end-to-end)
- [ ] Additional intelligence sources (e.g. VirusTotal, URLhaus)
- [ ] Docker setup

## Background

This project grew out of my earlier CLI script (Threat-Intelligence-Automator-IoC-Checker) and is being rebuilt as a web service to practice API design, automated testing and full-stack development.

## Author

Kazimierz Nowak — [LinkedIn](https://www.linkedin.com/in/kazimierz-nowak-sec) · [GitHub](https://github.com/SiwyBandzior)