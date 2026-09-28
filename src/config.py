"""Environment variables and model configuration for Agent 1."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = PROJECT_ROOT / "audio"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "sarvam_gemini"
FINAL_JSON_PATH = OUTPUT_DIR / "sarvam_gemini_final.json"

DIRECT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "direct_gemini"
DIRECT_FINAL_JSON_PATH = DIRECT_OUTPUT_DIR / "direct_gemini_final.json"

SARVAM_MODEL = "saaras:v4"
# Sarvam translate mode: Indic speech → English before Gemini extraction.
SARVAM_MODE = "translate"
SARVAM_REST_MAX_SECONDS = 29.5

GEMINI_MODEL = "gemini-3.6-flash"

AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".webm"}


def load_settings() -> tuple[str, str]:
    """Load API keys from .env. Values are stripped; keys are never logged."""
    load_dotenv(PROJECT_ROOT / ".env")
    sarvam_key = (os.getenv("SARVAM_API_KEY") or "").strip()
    gemini_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not sarvam_key:
        raise RuntimeError("SARVAM_API_KEY is missing or empty in .env")
    if not gemini_key:
        raise RuntimeError("GEMINI_API_KEY is missing or empty in .env")
    return sarvam_key, gemini_key


def load_gemini_settings() -> str:
    """Load Gemini API key only (Agent 2 direct audio pipeline)."""
    load_dotenv(PROJECT_ROOT / ".env")
    gemini_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not gemini_key:
        raise RuntimeError("GEMINI_API_KEY is missing or empty in .env")
    return gemini_key


AUDIO_MIME_TYPES: dict[str, str] = {
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".flac": "audio/flac",
    ".ogg": "audio/ogg",
    ".aac": "audio/aac",
    ".webm": "audio/webm",
}


def mime_type_for_audio(path: Path) -> str:
    mime = AUDIO_MIME_TYPES.get(path.suffix.lower())
    if not mime:
        raise ValueError(f"Unsupported audio extension: {path.suffix}")
    return mime
