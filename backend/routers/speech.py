from fastapi import APIRouter, File, UploadFile

from services import stt_service

router = APIRouter()


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename or "audio.webm"
    return stt_service.transcribe(content, filename)
