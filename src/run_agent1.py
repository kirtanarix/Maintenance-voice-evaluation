"""Agent 1: discover audio files, run Sarvam STT → Gemini extraction, write sarvam_gemini_final.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from src.config import (
    AUDIO_DIR,
    AUDIO_EXTENSIONS,
    FINAL_JSON_PATH,
    OUTPUT_DIR,
    load_settings,
)
from src.extractor import extract_from_transcript
from src.gemini_client import GeminiClient
from src.sarvam_client import SarvamSTTClient


def discover_audio_files(audio_dir: Path) -> list[Path]:
    if not audio_dir.is_dir():
        return []
    files = [
        p
        for p in sorted(audio_dir.iterdir())
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
    ]
    return files


def load_existing_results(path: Path) -> dict[str, dict]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Existing sarvam_gemini_final.json is invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Existing sarvam_gemini_final.json must be a JSON object")
    return data


def save_results(path: Path, results: dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".json.tmp")
    temp_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(path)


class SarvamStepError(Exception):
    pass


class GeminiStepError(Exception):
    pass


def process_file(
    audio_path: Path,
    sarvam: SarvamSTTClient,
    gemini: GeminiClient,
) -> dict:
    try:
        transcript = sarvam.transcribe_file(audio_path)
    except Exception as exc:
        raise SarvamStepError(str(exc)) from exc
    try:
        extraction = extract_from_transcript(
            gemini,
            transcript,
            audio_filename=audio_path.name,
        )
    except Exception as exc:
        raise GeminiStepError(str(exc)) from exc
    return extraction.model_dump(mode="json")


def main() -> int:
    sarvam_key, gemini_key = load_settings()
    sarvam = SarvamSTTClient(sarvam_key)
    gemini = GeminiClient(gemini_key)

    audio_files = discover_audio_files(AUDIO_DIR)
    total = len(audio_files)
    if total == 0:
        print(f"No audio files found in {AUDIO_DIR}")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if not FINAL_JSON_PATH.is_file():
            save_results(FINAL_JSON_PATH, {})
        return 0

    results = load_existing_results(FINAL_JSON_PATH)
    success_count = 0
    fail_count = 0

    for index, audio_path in enumerate(audio_files, start=1):
        name = audio_path.name
        print(f"[{index}/{total}] {name}")
        try:
            payload = process_file(audio_path, sarvam, gemini)
            print("    Sarvam: success")
            print("    Gemini: success")
            results[name] = payload
            save_results(FINAL_JSON_PATH, results)
            success_count += 1
        except SarvamStepError as exc:
            print(f"    Sarvam: failed ({exc})")
            print("    Gemini: skipped")
            fail_count += 1
        except GeminiStepError as exc:
            print("    Sarvam: success")
            print(f"    Gemini: failed ({exc})")
            fail_count += 1
        except Exception as exc:
            print(f"    Sarvam: failed ({exc})")
            print("    Gemini: skipped")
            fail_count += 1

    print()
    print(f"Processed: {total}, successful: {success_count}, failed: {fail_count}")
    print(f"Output: {FINAL_JSON_PATH}")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
