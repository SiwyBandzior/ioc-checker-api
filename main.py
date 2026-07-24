import datetime as dt
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, field_serializer, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from abuseipdb import AbuseIPDBError, fetch_ip_report
from config import get_settings
from database import engine, get_db, init_db
from ioc_service import determine_status, validate_ip_address
from models import IOCScan


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(title="IoC Checker API", lifespan=lifespan)


class IOCCheckRequest(BaseModel):
    ip_address: str

    @field_validator("ip_address")
    @classmethod
    def check_ip_format(cls, value: str) -> str:
        return validate_ip_address(value)


class IOCCheckResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ip_address: str
    country_code: str | None
    risk_score: int
    status: str
    scanned_at: dt.datetime

    @field_serializer("scanned_at")
    def serialize_scanned_at(self, value: dt.datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=dt.timezone.utc)
        return value.isoformat()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ioc/check", response_model=IOCCheckResult)
async def check_ip(payload: IOCCheckRequest, db: AsyncSession = Depends(get_db)):
    settings = get_settings()

    try:
        report = await fetch_ip_report(payload.ip_address)
    except AbuseIPDBError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    risk_score = report["abuseConfidenceScore"]

    scan = IOCScan(
        ip_address=payload.ip_address,
        country_code=report.get("countryCode"),
        risk_score=risk_score,
        status=determine_status(risk_score, settings.risk_threshold),
    )

    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    return scan


@app.get("/ioc/history", response_model=list[IOCCheckResult])
async def get_history(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IOCScan).order_by(IOCScan.scanned_at.desc()).limit(limit))
    return result.scalars().all()
