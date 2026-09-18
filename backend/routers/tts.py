from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel

from services import tts_service

router = APIRouter()


class TtsRequest(BaseModel):
    text: str


@router.post("/")
def synthesize(body: TtsRequest):
    audio, meta = tts_service.synthesize_bangla(body.text)
    if audio is None:
        return {"audio": None, **meta}
    return Response(
        content=audio,
        media_type="audio/mpeg" if meta.get("source") == "elevenlabs" and not meta.get("mock") else "audio/wav",
        headers={"X-TTS-Source": meta.get("source", "unknown"), "X-TTS-Fallback": str(meta.get("fallback", False))},
    )
