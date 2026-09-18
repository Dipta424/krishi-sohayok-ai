import os
import struct
import wave
from io import BytesIO

from config import ELEVENLABS_VOICE_ID, TTS_MOCK

FALLBACK_BANGLA = (
    "আপনার ফসলে ধান ব্লাস্টের লক্ষণ দেখা যাচ্ছে। "
    "স্থানীয় কৃষি কর্মকর্তার পরামর্শ নিন এবং ছত্রাকনাশক প্রয়োগের আগে নিরাপদ ব্যবহার নিশ্চিত করুন।"
)


def _generate_silent_wav(duration_sec: float = 2.0, sample_rate: int = 22050) -> bytes:
    n_frames = int(duration_sec * sample_rate)
    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack("<" + "h" * n_frames, *([0] * n_frames)))
    return buf.getvalue()


def synthesize_bangla(text: str) -> tuple[bytes | None, dict]:
    meta = {"fallback": False, "source": "elevenlabs"}
    use_text = text.strip() or FALLBACK_BANGLA

    if TTS_MOCK or not os.getenv("ELEVENLABS_API_KEY"):
        meta.update({"fallback": True, "source": "mock_wav_placeholder", "mock": True})
        return _generate_silent_wav(3.0), meta

    try:
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        audio = client.text_to_speech.convert(
            voice_id=ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
            text=use_text,
        )
        return b"".join(audio), meta
    except Exception as e:
        meta.update({"fallback": True, "source": "silent_wav_fallback", "error": str(e)})
        return _generate_silent_wav(2.0), meta
