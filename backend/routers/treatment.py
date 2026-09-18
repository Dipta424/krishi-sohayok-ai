from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import AdvisorySession
from services import llm_service

router = APIRouter()


class TreatmentRequest(BaseModel):
    extracted: dict
    diagnosis: dict
    lat: float | None = 23.8103
    lon: float | None = 90.4125
    transcript: str | None = None


@router.get("/weather")
def weather(lat: float = 23.8103, lon: float = 90.4125):
    return llm_service.fetch_weather(lat, lon)


@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db)):
    rows = db.query(AdvisorySession).order_by(AdvisorySession.created_at.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "disease_name": r.disease_name,
            "severity": r.severity,
        }
        for r in rows
    ]


@router.post("/")
def treatment(body: TreatmentRequest, db: Session = Depends(get_db)):
    weather = llm_service.fetch_weather(body.lat or 23.8103, body.lon or 90.4125)
    payload = {
        "extracted": body.extracted,
        "diagnosis": body.diagnosis,
        "weather": weather,
    }
    plan = llm_service.recommend_treatment(payload)

    session = AdvisorySession(
        transcript=body.transcript,
        extracted_json=body.extracted,
        disease_name=body.diagnosis.get("disease_name"),
        severity=body.diagnosis.get("severity"),
        treatment_plan=plan,
        market_analysis=None,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {"session_id": session.id, "weather": weather, "treatment_plan": plan}
