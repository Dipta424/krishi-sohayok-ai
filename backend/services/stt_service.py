import os
import tempfile

from groq import Groq

FALLBACK_TRANSCRIPT = (
    "আমার ধানক্ষেতে পাতায় বাদামি দাগ দেখা যাচ্ছে, গত সপ্তাহ থেকে ছড়াচ্ছে।"
    " (cached demo transcript — STT unavailable)"
)

_whisper_model = None


def _get_groq_client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not set")
    return Groq(api_key=key)


def transcribe(audio_file_bytes: bytes, filename: str) -> dict:
    try:
        client = _get_groq_client()
        with tempfile.NamedTemporaryFile(suffix=filename, delete=False) as tmp:
            tmp.write(audio_file_bytes)
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            audio_data = f.read()
        result = client.audio.transcriptions.create(
            file=(filename, audio_data),
            model="whisper-large-v3",
            language=None,
        )
        return {"text": result.text, "source": "groq", "fallback": False}
    except Exception as e:
        return _local_whisper_fallback(audio_file_bytes, filename, error=str(e))


def _local_whisper_fallback(audio_bytes, filename, error):
    try:
        global _whisper_model
        import whisper

        if _whisper_model is None:
            _whisper_model = whisper.load_model("medium")
        with tempfile.NamedTemporaryFile(suffix=filename, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        result = _whisper_model.transcribe(tmp_path)
        return {
            "text": result["text"],
            "source": "local_whisper_fallback",
            "primary_error": error,
            "fallback": True,
        }
    except Exception as local_err:
        return {
            "text": FALLBACK_TRANSCRIPT,
            "source": "canned_stt_fallback",
            "primary_error": error,
            "secondary_error": str(local_err),
            "fallback": True,
        }
