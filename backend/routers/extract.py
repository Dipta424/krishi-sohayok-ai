from fastapi import APIRouter
from pydantic import BaseModel

from services import llm_service

router = APIRouter()


class ExtractRequest(BaseModel):
    transcript: str


@router.post("/")
def extract(body: ExtractRequest):
    return llm_service.extract_info(body.transcript)
