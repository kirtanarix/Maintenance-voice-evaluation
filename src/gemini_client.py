"""Gemini API client for structured extraction."""

from __future__ import annotations

from google import genai
from google.genai import types

from src.config import GEMINI_MODEL


class GeminiClient:
    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = GEMINI_MODEL

    @property
    def model_name(self) -> str:
        return self._model

    def generate_json(
        self,
        *,
        system_instruction: str,
        user_content: str,
    ) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.0,
            ),
        )
        text = (response.text or "").strip()
        if not text:
            raise ValueError("Gemini returned empty JSON")
        return text
