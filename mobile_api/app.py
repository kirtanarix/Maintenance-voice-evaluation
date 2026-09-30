"""Stateless multipart HTTP boundary; no experiment outputs are written."""
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from fastapi import FastAPI, File, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from starlette.exceptions import HTTPException

from mobile_api.service import ConfigurationError, transcribe
from src.config import AUDIO_EXTENSIONS
from src.schema import MaintenanceExtraction

MAX_AUDIO_BYTES = 20 * 1024 * 1024
app = FastAPI(title="Maintenance Voice API", version="1.0.0")


class SuccessResponse(BaseModel):
    success: Literal[True] = True
    data: MaintenanceExtraction


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: Literal[False] = False
    error: ErrorDetail


def error(status: int, code: str, message: str):
    return JSONResponse(status_code=status, content={
        "success": False, "error": {"code": code, "message": message}
    })


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return error(422, "INVALID_AUDIO", "Provide an audio file in the multipart field 'audio'.")


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return error(exc.status_code, "INVALID_REQUEST", "The request could not be processed.")


@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    return error(500, "INTERNAL_ERROR", "The request could not be completed.")


@app.post("/api/v1/transcribe", response_model=SuccessResponse,
          responses={s: {"model": ErrorResponse} for s in (400, 413, 415, 422, 500, 502, 503)})
def transcribe_audio(audio: UploadFile = File(...)):
    """Send an audio recording and receive the existing five-field extraction."""
    try:
        suffix = Path(audio.filename or "").suffix.lower()
        if suffix not in AUDIO_EXTENSIONS:
            return error(415, "UNSUPPORTED_AUDIO", "Use WAV, MP3, M4A, FLAC, OGG, AAC, or WEBM audio.")
        # Extension controls the existing client's MIME mapping. Mobile clients
        # may legitimately supply application/octet-stream, so do not reject it.
        with TemporaryDirectory(prefix="maintenance-audio-") as directory:
            path = Path(directory) / ("upload" + suffix)
            size = 0
            with path.open("wb") as destination:
                while chunk := audio.file.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_AUDIO_BYTES:
                        return error(413, "AUDIO_TOO_LARGE", "Audio must not exceed 20 MiB.")
                    destination.write(chunk)
            if not size:
                return error(400, "INVALID_AUDIO", "The audio file is empty.")
            try:
                result = MaintenanceExtraction.model_validate(transcribe(path))
            except ConfigurationError:
                return error(503, "SERVICE_UNAVAILABLE", "The extraction service is not configured.")
            except (ValidationError, ValueError):
                return error(502, "INVALID_MODEL_RESPONSE", "The extraction service returned an invalid response.")
            except Exception:
                return error(502, "EXTRACTION_FAILED", "The extraction service could not process the audio.")
            return SuccessResponse(data=result)
    finally:
        audio.file.close()
