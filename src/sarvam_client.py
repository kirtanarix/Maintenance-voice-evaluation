"""Sarvam Speech-to-Text (Saaras v4) client (mode from config, e.g. translate → English)."""

from __future__ import annotations

import json
import shutil
import tempfile
import wave
from pathlib import Path

from sarvamai import SarvamAI

from src.config import SARVAM_MODE, SARVAM_MODEL, SARVAM_REST_MAX_SECONDS


def _audio_duration_seconds(path: Path) -> float | None:
    suffix = path.suffix.lower()
    if suffix == ".wav":
        try:
            with wave.open(str(path), "rb") as wf:
                rate = wf.getframerate()
                if rate <= 0:
                    return None
                return wf.getnframes() / float(rate)
        except wave.Error:
            return None
    return None


def _extract_transcript_from_batch_json(payload: dict) -> str:
    for key in ("transcript", "text", "transcription"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    if isinstance(payload.get("results"), list):
        parts: list[str] = []
        for item in payload["results"]:
            if isinstance(item, dict):
                for key in ("transcript", "text"):
                    part = item.get(key)
                    if isinstance(part, str) and part.strip():
                        parts.append(part.strip())
        if parts:
            return " ".join(parts)
    raise ValueError("Batch STT output did not contain a transcript")


class SarvamSTTClient:
    def __init__(self, api_key: str) -> None:
        self._client = SarvamAI(api_subscription_key=api_key)

    def transcribe_file(self, audio_path: Path) -> str:
        duration = _audio_duration_seconds(audio_path)
        if duration is not None and duration <= SARVAM_REST_MAX_SECONDS:
            return self._transcribe_rest(audio_path)
        if duration is not None and duration > SARVAM_REST_MAX_SECONDS:
            return self._transcribe_batch(audio_path)
        try:
            return self._transcribe_rest(audio_path)
        except Exception:
            return self._transcribe_batch(audio_path)

    def _transcribe_rest(self, audio_path: Path) -> str:
        with audio_path.open("rb") as audio_file:
            response = self._client.speech_to_text.transcribe(
                file=audio_file,
                model=SARVAM_MODEL,
                mode=SARVAM_MODE,
            )
        transcript = (response.transcript or "").strip()
        if not transcript:
            raise ValueError("Sarvam REST returned an empty transcript")
        return transcript

    def _transcribe_batch(self, audio_path: Path) -> str:
        job = self._client.speech_to_text_job.create_job(
            model=SARVAM_MODEL,
            mode=SARVAM_MODE,
        )
        if not job.upload_files([str(audio_path)]):
            raise RuntimeError("Sarvam batch upload failed")
        job.start()
        status = job.wait_until_complete(poll_interval=5, timeout=1800)
        if not job.is_successful():
            raise RuntimeError(
                f"Sarvam batch job failed (state={status.job_state})"
            )

        temp_dir = Path(tempfile.mkdtemp(prefix="sarvam_stt_"))
        try:
            job.download_outputs(str(temp_dir))
            output_json = temp_dir / f"{audio_path.name}.json"
            if not output_json.is_file():
                raise FileNotFoundError(
                    f"Expected batch output at {output_json.name}"
                )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            return _extract_transcript_from_batch_json(payload)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
