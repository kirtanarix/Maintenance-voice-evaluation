"""Gemini extraction prompt and orchestration (transcript → five fields)."""

from __future__ import annotations

import json

from src.gemini_client import GeminiClient
from src.schema import MaintenanceExtraction

EXTRACTION_SYSTEM_INSTRUCTION = """You extract structured maintenance information from an English transcript produced by Sarvam speech-to-text (translate mode).

Rules:
- Use ONLY information explicitly supported by the transcript.
- Do NOT hallucinate, guess, infer, or normalize beyond what was spoken.
- Output JSON with EXACTLY these five keys and no others:
  assets, quantities, hours, dates, approval_intent

Field semantics:
- assets: equipment/machine/asset names explicitly mentioned. One string or a list if multiple. null if none.
- quantities: list of strings for explicitly spoken quantities (materials, manpower, bolts, grease, etc.). null if none.
- hours: list of entries for explicitly spoken time durations. Preserve work duration vs machine downtime as separate entries when both are spoken (e.g. use objects like {"kind":"work_duration","value":"..."} and {"kind":"machine_downtime","value":"..."} or plain strings that keep the distinction). null if none.
- dates: scheduling phrases as spoken (Saturday, tomorrow morning, Monday at 10 AM). Do not invent calendar dates. null if none.
- approval_intent: only explicit approval/permission requests. null if not explicitly mentioned. Do not treat informational statements as approval.

Always include all five keys. Use null (or empty list only when the schema expects a list and nothing was said — prefer null for absent list fields)."""


def extract_from_transcript(
    gemini: GeminiClient,
    transcript: str,
    *,
    audio_filename: str,
) -> MaintenanceExtraction:
    user_content = (
        f"Audio file: {audio_filename}\n\n"
        "Sarvam transcript (English):\n"
        f"{transcript}\n\n"
        "Return the five-field JSON extraction."
    )
    raw_json = gemini.generate_json(
        system_instruction=EXTRACTION_SYSTEM_INSTRUCTION,
        user_content=user_content,
    )
    data = json.loads(raw_json)
    return MaintenanceExtraction.model_validate(data)
