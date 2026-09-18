from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import Base, engine
from routers import extract, market, speech, treatment, tts, vision

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Krishi Sohayok API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(speech.router, prefix="/api/speech", tags=["speech"])
app.include_router(extract.router, prefix="/api/extract", tags=["extract"])
app.include_router(vision.router, prefix="/api/vision", tags=["vision"])
app.include_router(treatment.router, prefix="/api/treatment", tags=["treatment"])
app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(tts.router, prefix="/api/tts", tags=["tts"])


@app.get("/health")
def health():
    return {"status": "ok"}


if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
