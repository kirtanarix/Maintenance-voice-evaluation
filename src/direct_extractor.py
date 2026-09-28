"""Direct audio → Gemini extraction (no Sarvam)."""

from __future__ import annotations

from pathlib import Path

from src.gemini_audio_client import GeminiAudioClient
from src.schema import MaintenanceExtraction

DIRECT_EXTRACTION_SYSTEM_INSTRUCTION = """You are a maintenance voice extraction system.

The user message includes the original maintenance voice recording as audio. That audio is the ONLY authoritative source.

Processing steps (internal — do not output a transcript):
1. Listen to the full recording. It may be Hindi, Hinglish, English, or mixed, including technical terms, equipment IDs, numbers, and self-corrections.
2. Derive an English understanding of what was actually spoken.
3. From that understanding, extract exactly five maintenance parameters into JSON.

Output rules:
- Return JSON with EXACTLY these five keys and no others: assets, quantities, hours, dates, approval_intent
- Do NOT include transcript, english_transcript, language, model, confidence, notes, or any sixth field.
- Use ONLY information explicitly supported by the audio. Do NOT hallucinate, guess, or infer unstated facts.
- When the speaker corrects themselves (e.g. "three fitters... no, two fitters and one helper"), use the corrected final values only.
- Preserve technical terms and IDs as spoken (e.g. 6205 C3, M60, BC-12, BE-07).
- If something was not spoken, use null (prefer null over empty lists for absent list fields).

Field semantics:
- assets: equipment/machine/asset explicitly mentioned. String or list if multiple. null if none. Preserve ambiguity; do not invent names.
- quantities: list of strings for explicitly spoken quantities (materials, manpower, specs). null if none.
- hours: list of entries for explicitly spoken durations. Keep work duration and machine downtime separate when both are spoken (e.g. {"kind":"work_duration","value":"6 hours"} and {"kind":"machine_downtime","value":"2 hours"}, or distinct plain strings). Do not collapse one into the other. null if none.
- dates: scheduling phrases as spoken (Saturday, tomorrow, Monday at 10 AM). Do not invent calendar dates. If another team will provide exact time, state that inside this field. null if none.
- approval_intent: ONLY explicit approval/permission requests. null if not explicitly mentioned. Mentioning a team for scheduling or information is NOT approval.

Always include all five keys."""

DIRECT_USER_PROMPT = (
    "Listen to the attached maintenance voice recording. "
    "Internally interpret the spoken content in English, then return the five-field JSON extraction only."
)


def extract_from_audio(
    gemini: GeminiAudioClient,
    audio_path: Path,
) -> MaintenanceExtraction:
    return gemini.extract_from_audio_file(
        audio_path,
        system_instruction=DIRECT_EXTRACTION_SYSTEM_INSTRUCTION,
        user_prompt=DIRECT_USER_PROMPT,
    )
