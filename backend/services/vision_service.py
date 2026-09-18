import base64
import json
import os
import re

import requests
from google import genai

VISION_PROMPT = """You are a crop pathology assistant for Bangladeshi agriculture.
Analyze this leaf/crop image. Respond ONLY with JSON:
{
  "disease_name": string,
  "possible_pathogen": string,
  "severity": "mild" | "moderate" | "severe" | "critical",
  "affected_area_percent": number,
  "confidence": number
}"""


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _parse_json(text: str) -> dict:
    return json.loads(_strip_json_fences(text))


def _fallback_diagnosis(error: str | None = None):
    return {
        "disease_name": "Rice Blast (Pyricularia oryzae) — cached demo result",
        "possible_pathogen": "Pyricularia oryzae",
        "severity": "moderate",
        "affected_area_percent": 22,
        "confidence": 0.0,
        "fallback": True,
        "error": error,
    }


def _roboflow_fallback(image_bytes: bytes) -> dict:
    key = os.getenv("ROBOFLOW_API_KEY")
    if not key:
        raise ValueError("ROBOFLOW_API_KEY not set")
    # Public crop disease model placeholder endpoint pattern
    url = "https://detect.roboflow.com/crop-disease/1"
    r = requests.post(
        url,
        params={"api_key": key},
        files={"file": ("leaf.jpg", image_bytes, "image/jpeg")},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    predictions = data.get("predictions") or []
    if not predictions:
        raise ValueError("No Roboflow predictions")
    top = max(predictions, key=lambda p: p.get("confidence", 0))
    conf = float(top.get("confidence", 0))
    return {
        "disease_name": top.get("class", "Unknown disease"),
        "possible_pathogen": "See Roboflow model label",
        "severity": "moderate" if conf > 0.5 else "mild",
        "affected_area_percent": min(95, int(conf * 100)),
        "confidence": round(conf, 2),
        "fallback": True,
        "source": "roboflow",
    }


def detect_disease(image_bytes: bytes, mime_type: str) -> dict:
    try:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY not set")
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64.b64encode(image_bytes).decode(),
                    }
                },
                VISION_PROMPT,
            ],
        )
        result = _parse_json(response.text)
        return {**result, "fallback": False, "source": "gemini"}
    except Exception as e:
        try:
            return _roboflow_fallback(image_bytes)
        except Exception:
            return _fallback_diagnosis(error=str(e))
