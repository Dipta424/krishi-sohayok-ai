from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String

from database import Base


class AdvisorySession(Base):
    __tablename__ = "advisory_sessions"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    transcript = Column(String)
    extracted_json = Column(JSON)
    disease_name = Column(String)
    severity = Column(String)
    treatment_plan = Column(JSON)
    market_analysis = Column(JSON)
