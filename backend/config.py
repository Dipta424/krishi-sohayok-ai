import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./krishi.db")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
TTS_MOCK = os.getenv("TTS_MOCK", "true").lower() in ("1", "true", "yes")
