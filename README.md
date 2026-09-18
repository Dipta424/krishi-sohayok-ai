# Krishi Sohayok — AI Agro-Advisory Platform (final prototype)

## Run the demo (no API keys required)

From this folder:

```bash
./run-demo.sh
```

Then open **http://localhost:8000** in your browser.

The app runs end-to-end with built-in fallbacks (STT, vision, LLM, TTS). Add keys in `backend/.env` (see `.env.example`) only when you want live AI during rehearsal.

---

## Overview

Krishi Sohayok helps Bangladesh smallholder farmers report crop symptoms by voice or text, detect disease from leaf photos, receive treatment guidance with live weather, check wholesale price fairness, and print a **Field Health Card** with optional Bengali audio.

## Features

- Voice/text intake (Bangla + English)
- AI crop disease detection from photos
- Combined agronomic treatment reasoning (symptoms + vision + Open-Meteo weather)
- Market price anomaly detection (local CSV + z-score)
- Bengali voice advisory + printable Field Health Card

## Architecture

| Layer | Choice |
|---|---|
| Frontend | React + Vite (served by FastAPI in demo mode) |
| Backend | FastAPI (Python 3.11+) |
| Database | SQLite via SQLAlchemy |
| STT | Groq `whisper-large-v3` → local Whisper → canned transcript |
| Vision | Gemini 2.5 Flash → Roboflow (optional) → cached diagnosis |
| Reasoning LLM | Gemini 2.5 Flash → Groq `llama-3.3-70b-versatile` → canned JSON |
| Weather | Open-Meteo |
| Market | Static BD wholesale CSV + z-score |
| TTS | ElevenLabs (`TTS_MOCK=true` default) → silent WAV fallback |

## Project layout

```
backend/          FastAPI app, services, SQLite, CSV data
frontend/         React UI (built to frontend/dist)
run-demo.sh       Single-command launcher
```

## Developer mode (hot reload UI)

```bash
# Terminal 1
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

Set `frontend/.env`: `VITE_API_URL=http://localhost:8000`

## Judge demo path

1. Type or record symptoms → transcript + JSON  
2. Upload leaf photo → diagnosis  
3. Treatment plan (auto, uses weather)  
4. Market check — e.g. rice at **30** BDT → undercut warning  
5. **Field Health Card** → print / save PDF  

## Tech credits

Groq Whisper, Google Gemini 2.5 Flash, ElevenLabs (optional), Open-Meteo, static market CSV.
