"""Agent 2: original audio → Gemini → five-parameter direct_gemini_final.json (no Sarvam)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from src.config import (
    AUDIO_DIR,
    AUDIO_EXTENSIONS,
    DIRECT_FINAL_JSON_PATH,
    DIRECT_OUTPUT_DIR,
    GEMINI_MODEL,
    load_gemini_settings,
)
from src.direct_extractor import extract_from_audio
from src.gemini_audio_client import GeminiAudioClient


def discover_audio_files(audio_dir: Path) -> list[Path]:
    if not audio_dir.is_dir():
        return []
    return [
        p
        for p in sorted(audio_dir.iterdir())
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
    ]


def load_existing_results(path: Path) -> dict[str, dict]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Existing direct_gemini_final.json is invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Existing direct_gemini_final.json must be a JSON object")
    return data


def save_results(path: Path, results: dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".json.tmp")
    temp_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(path)


def validate_record_payload(payload: dict) -> None:
    allowed = {"assets", "quantities", "hours", "dates", "approval_intent"}
    extra = set(payload.keys()) - allowed
    if extra:
        raise ValueError(f"Record contains disallowed keys: {sorted(extra)}")


def main() -> int:
    gemini_key = load_gemini_settings()
    gemini = GeminiAudioClient(gemini_key)

    audio_files = discover_audio_files(AUDIO_DIR)
    total = len(audio_files)
    if total == 0:
        print(f"No audio files found in {AUDIO_DIR}")
        DIRECT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if not DIRECT_FINAL_JSON_PATH.is_file():
            save_results(DIRECT_FINAL_JSON_PATH, {})
        return 0

    results = load_existing_results(DIRECT_FINAL_JSON_PATH)
    success_count = 0
    fail_count = 0

    print(f"Gemini model: {GEMINI_MODEL}")
    print(f"Direct audio pipeline (no Sarvam)")
    print()

    for index, audio_path in enumerate(audio_files, start=1):
        name = audio_path.name
        print(f"[{index}/{total}] {name}")
        try:
            extraction = extract_from_audio(gemini, audio_path)
            payload = extraction.model_dump(mode="json")
            validate_record_payload(payload)
            results[name] = payload
            save_results(DIRECT_FINAL_JSON_PATH, results)
            print("    Gemini (direct audio): success")
            success_count += 1
        except Exception as exc:
            print(f"    Gemini (direct audio): failed ({exc})")
            fail_count += 1

    print()
    print(f"Discovered: {total}, successful: {success_count}, failed: {fail_count}")
    print(f"Output: {DIRECT_FINAL_JSON_PATH}")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
