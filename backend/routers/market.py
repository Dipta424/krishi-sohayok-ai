from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import AdvisorySession
from services import market_service

router = APIRouter()


class MarketRequest(BaseModel):
    crop: str
    farmer_price: float
    session_id: int | None = None


@router.post("/analyze")
def analyze(body: MarketRequest, db: Session = Depends(get_db)):
    result = market_service.analyze_price(body.crop, body.farmer_price)
    if body.session_id:
        session = db.get(AdvisorySession, body.session_id)
        if session:
            session.market_analysis = result
            db.commit()
    return result
