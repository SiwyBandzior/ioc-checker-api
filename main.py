from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from abuseipdb import AbuseIPDBError, fetch_ip_report
from config import get_settings

app = FastAPI(title="IoC Checker API")

class IOCCheckRequest(BaseModel):
    ip_address: str

class IOCCHeckResult(BaseModel):
    ip_address: str
    country_code: str | None
    risk_score: int
    status: str

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ioc/check", response_model=IOCCheckRequest)
async def check_ip(payload: IOCCheckRequest):
    settings = get_settings()

    try:
        report = await fetch_ip_report(payload.ip_address)
    except AbuseIPDBError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    
    risk_score = report["abuseConfidenceScore"]
    status = "DANGEROUS" if risk_score > settings.risk_thereshold else "SAFE"

    return IOCCHeckResult(
        ip_address=payload.ip_address,
        country_code=report.get("countryCode"),
        risk_score=risk_score,
        status=status,
    )