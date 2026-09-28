"""Gemini API client for direct audio → structured extraction."""

from __future__ import annotations

from pathlib import Path

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from src.config import GEMINI_MODEL, mime_type_for_audio
from src.schema import MaintenanceExtraction


class GeminiAudioClient:
    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = GEMINI_MODEL

    @property
    def model_name(self) -> str:
        return self._model

    def extract_from_audio_file(
        self,
        audio_path: Path,
        *,
        system_instruction: str,
        user_prompt: str,
    ) -> MaintenanceExtraction:
        mime_type = mime_type_for_audio(audio_path)
        audio_bytes = audio_path.read_bytes()
        if not audio_bytes:
            raise ValueError(f"Audio file is empty: {audio_path.name}")

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(
                                data=audio_bytes,
                                mime_type=mime_type,
                            ),
                            types.Part.from_text(text=user_prompt),
                        ],
                    )
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )
        except genai_errors.ClientError as exc:
            raise RuntimeError(
                f"Gemini API error for model {self._model!r}: {exc}"
            ) from exc
        except genai_errors.ServerError as exc:
            raise RuntimeError(
                f"Gemini server error for model {self._model!r}: {exc}"
            ) from exc

        text = (response.text or "").strip()
        if not text:
            raise ValueError("Gemini returned empty JSON for audio extraction")
        return MaintenanceExtraction.model_validate_json(text)
