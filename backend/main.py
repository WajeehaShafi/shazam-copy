import os
import tempfile
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment

from match import match_clip

app = FastAPI()

# Allow the frontend (running on a different port/origin) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # fine for local dev; restrict later if needed
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIDENCE_THRESHOLD = 50  # tweak based on testing


@app.post("/match")
async def match_audio(file: UploadFile = File(...)):
    # Save the uploaded chunk to a temp file first (raw bytes from browser)
    temp_id = uuid.uuid4().hex
    raw_path = os.path.join(tempfile.gettempdir(), f"{temp_id}_raw")
    wav_path = os.path.join(tempfile.gettempdir(), f"{temp_id}.wav")

    with open(raw_path, "wb") as f:
        f.write(await file.read())

    try:
        # Convert whatever format the browser sent (webm/ogg) into wav
        audio = AudioSegment.from_file(raw_path)
        audio.export(wav_path, format="wav")

        # Run it through our existing matching pipeline
        result = match_clip(wav_path)

        if result is None:
            return {"match": False, "message": "No match found"}

        confident = result["score"] >= CONFIDENCE_THRESHOLD

        return {
            "match": confident,
            "title": result["title"],
            "artist": result["artist"],
            "score": result["score"],
        }

    finally:
        # Clean up temp files regardless of success/failure
        for p in (raw_path, wav_path):
            if os.path.exists(p):
                os.remove(p)


@app.get("/")
async def root():
    return {"status": "Shazam clone backend running"}