from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64
import binascii
import os
import logging

logging.basicConfig(level=logging.INFO)
 
app = FastAPI()
 
API_SECRET_KEY = "sk_test_123456789"  # Change to your secret key
SUPPORTED_LANGUAGES = {"Tamil", "English", "Hindi", "Malayalam", "Telugu"}
 
class VoiceDetectionRequest(BaseModel):
    language: str
    audioFormat: str
    audioBase64: str

@app.post("/api/voice-detection")
async def voice_detection(request: Request, payload: VoiceDetectionRequest):
    # API Key authentication
    api_key = request.headers.get("x-api-key")
    if api_key != API_SECRET_KEY:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid API key or malformed request"})
    # Language validation
    if payload.language not in SUPPORTED_LANGUAGES:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Unsupported language"})
    # Audio format validation
    if payload.audioFormat.lower() != "mp3":
        return JSONResponse(status_code=400, content={"status": "error", "message": "Audio format must be mp3"})
    # Decode base64 audio (be tolerant of data URLs, whitespace, and missing padding)
    b64 = payload.audioBase64
    if not isinstance(b64, str) or not b64.strip():
        return JSONResponse(status_code=400, content={"status": "error", "message": "No base64 audio provided"})

    # Strip data URL prefix if present
    if b64.startswith("data:"):
        try:
            b64 = b64.split(",", 1)[1]
        except Exception:
            logging.exception("Invalid data URL for audio")
            return JSONResponse(status_code=400, content={"status": "error", "message": "Malformed base64 audio: invalid data URL"})

    # Remove whitespace/newlines
    b64 = b64.strip().replace("\n", "").replace("\r", "")

    # Add padding if missing
    padding = len(b64) % 4
    if padding:
        b64 += "=" * (4 - padding)

    try:
        audio_bytes = base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError):
        logging.exception("Base64 decoding failed")
        return JSONResponse(status_code=400, content={"status": "error", "message": "Malformed base64 audio: invalid encoding"})
    except Exception:
        logging.exception("Unexpected error decoding base64 audio")
        return JSONResponse(status_code=400, content={"status": "error", "message": "Malformed base64 audio"})
    # Save audio temporarily (for feature extraction/model)
    temp_audio_path = "temp_audio.mp3"
    with open(temp_audio_path, "wb") as f:
        f.write(audio_bytes)
    # TODO: Extract features and run AI/Human classification model
    # Placeholder result
    classification = "AI_GENERATED"
    confidenceScore = 0.91
    explanation = "Unnatural pitch consistency and robotic speech patterns detected"
    # Remove temp file
    os.remove(temp_audio_path)
    return {
        "status": "success",
        "language": payload.language,
        "classification": classification,
        "confidenceScore": confidenceScore,
        "explanation": explanation
    }