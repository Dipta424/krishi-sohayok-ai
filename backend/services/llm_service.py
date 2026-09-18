import json
import os
import re

import requests
from google import genai
from groq import Groq

EXTRACT_SYSTEM_PROMPT = """You are an agricultural information extractor for Bangladesh.
Given a farmer's raw transcript (Bangla or English), output ONLY valid JSON, no prose, no markdown fences, matching exactly this schema:

{
  "crop_type": string,
  "planting_date": string or null,
  "symptoms": string,
  "location": string or null,
  "weather_condition": string or null,
  "farming_stage": string or null,
  "previous_treatment": string or null
}

If a field isn't mentioned, use null. Never invent details not present in the transcript."""

TREATMENT_SYSTEM_PROMPT = """You are an agronomic advisory engine for smallholder farmers in Bangladesh.
Given the farmer's structured symptoms, an image-based diagnosis, and current weather, produce JSON:

{
  "disease_explanation": string,
  "probable_cause": string,
  "organic_treatment": string,
  "chemical_treatment": string,
  "dosage": string,
  "safety_instructions": string,
  "pre_harvest_interval_days": number,
  "spraying_recommendation": string
}

Rules:
- If rain is forecast within 6 hours, spraying_recommendation must say to postpone.
- Always include a pre-harvest interval — never omit it.
- Keep chemical names and dosages realistic and conservative; when uncertain, recommend consulting the local
  Sub-Assistant Agriculture Officer (SAAO) rather than guessing a specific chemical."""

FALLBACK_EXTRACT = {
    "crop_type": "rice",
    "planting_date": None,
    "symptoms": "Brown spots on leaves, spreading over the past week",
    "location": "Bangladesh",
    "weather_condition": None,
    "farming_stage": "vegetative",
    "previous_treatment": None,
}

FALLBACK_TREATMENT = {
    "disease_explanation": "Leaf lesions consistent with fungal blast on rice — demo advisory.",
    "probable_cause": "High humidity and infected seed or residue.",
    "organic_treatment": "Neem oil spray (3%) every 7 days; remove heavily infected leaves.",
    "chemical_treatment": "Consult SAAO before applying fungicides; tricyclazole may be considered where approved.",
    "dosage": "Follow label and SAAO guidance — do not exceed registered rates.",
    "safety_instructions": "Wear mask, gloves, and long sleeves; keep children away during spraying.",
    "pre_harvest_interval_days": 21,
    "spraying_recommendation": "Spray in calm morning hours if no rain is expected within 6 hours.",
}


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _parse_json(text: str) -> dict:
    cleaned = _strip_json_fences(text)
    return json.loads(cleaned)


def _regex_extract_fallback(transcript: str) -> dict:
    lower = transcript.lower()
    crop = "rice"
    for keyword, name in [
        ("ধান", "rice"),
        ("rice", "rice"),
        ("potato", "potato"),
        ("আলু", "potato"),
        ("tomato", "tomato"),
        ("টমেটো", "tomato"),
    ]:
        if keyword in lower or keyword in transcript:
            crop = name
            break
    return {
        **FALLBACK_EXTRACT,
        "crop_type": crop,
        "symptoms": transcript[:500] if transcript else FALLBACK_EXTRACT["symptoms"],
    }


def _call_gemini_json(system_prompt: str, user_content: str) -> dict:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not set")
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{system_prompt}\n\nUser input:\n{user_content}",
    )
    return _parse_json(response.text)


def _call_groq_json(system_prompt: str, user_content: str) -> dict:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not set")
    client = Groq(api_key=key)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )
    return _parse_json(completion.choices[0].message.content)


def extract_info(transcript: str) -> dict:
    try:
        data = _call_gemini_json(EXTRACT_SYSTEM_PROMPT, transcript)
        return {**data, "source": "gemini", "fallback": False}
    except Exception as gemini_err:
        try:
            data = _call_groq_json(EXTRACT_SYSTEM_PROMPT, transcript)
            return {**data, "source": "groq", "fallback": True, "primary_error": str(gemini_err)}
        except Exception as groq_err:
            try:
                data = _regex_extract_fallback(transcript)
                return {
                    **data,
                    "source": "regex_fallback",
                    "fallback": True,
                    "primary_error": str(gemini_err),
                    "secondary_error": str(groq_err),
                }
            except Exception:
                return {
                    **FALLBACK_EXTRACT,
                    "source": "canned_extract_fallback",
                    "fallback": True,
                    "primary_error": str(gemini_err),
                    "secondary_error": str(groq_err),
                }


def recommend_treatment(payload: dict) -> dict:
    user_content = json.dumps(payload, ensure_ascii=False)
    try:
        data = _call_gemini_json(TREATMENT_SYSTEM_PROMPT, user_content)
        return {**data, "source": "gemini", "fallback": False}
    except Exception as gemini_err:
        try:
            data = _call_groq_json(TREATMENT_SYSTEM_PROMPT, user_content)
            return {**data, "source": "groq", "fallback": True, "primary_error": str(gemini_err)}
        except Exception:
            plan = {**FALLBACK_TREATMENT}
            weather = payload.get("weather") or {}
            if weather.get("rain_within_6h"):
                plan["spraying_recommendation"] = (
                    "Postpone spraying — rain forecast within 6 hours (cached demo advisory)."
                )
            return {
                **plan,
                "source": "canned_treatment_fallback",
                "fallback": True,
                "primary_error": str(gemini_err),
            }


def fetch_weather(lat: float = 23.8103, lon: float = 90.4125) -> dict:
    """Open-Meteo for Dhaka area default."""
    fallback = {
        "temperature_c": 28.0,
        "humidity_percent": 75,
        "precipitation_mm_next_6h": 0.0,
        "rain_within_6h": False,
        "description": "Partly cloudy (cached demo weather)",
        "fallback": True,
    }
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation",
            "hourly": "precipitation",
            "forecast_hours": 6,
            "timezone": "Asia/Dhaka",
        }
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        current = data.get("current", {})
        hourly = data.get("hourly", {})
        precip = hourly.get("precipitation", [])[:6]
        precip_sum = sum(p or 0 for p in precip)
        rain_within_6h = precip_sum > 0.5
        return {
            "temperature_c": current.get("temperature_2m", 28),
            "humidity_percent": current.get("relative_humidity_2m", 75),
            "precipitation_mm_next_6h": round(precip_sum, 2),
            "rain_within_6h": rain_within_6h,
            "description": "Live Open-Meteo forecast",
            "fallback": False,
        }
    except Exception as e:
        return {**fallback, "error": str(e)}
