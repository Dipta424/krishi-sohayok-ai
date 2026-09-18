from fastapi import APIRouter, File, UploadFile

from services import vision_service

router = APIRouter()


@router.post("/detect")
async def detect(file: UploadFile = File(...)):
    content = await file.read()
    mime = file.content_type or "image/jpeg"
    return vision_service.detect_disease(content, mime)
