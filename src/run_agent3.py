"""Agent 3: human-verified raw text → Ground Truth JSON (no external APIs)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.config import PROJECT_ROOT
from src.ground_truth_extractor import extract_ground_truth

DEFAULT_INPUT_PATH = PROJECT_ROOT / "inputs" / "ground_truth_input.json"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "ground_truth" / "ground_truth_final.json"


def load_input_records(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise RuntimeError(f"Input file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in input file: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Input file must be a JSON object mapping filename → raw text")
    records: dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(key, str) or not key.strip():
            raise RuntimeError("Each input key must be a non-empty audio filename string")
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"Raw text for {key!r} must be a non-empty string")
        records[key.strip()] = value.strip()
    return records


def load_existing_results(path: Path) -> dict[str, dict]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Existing output JSON is invalid: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Output file must be a JSON object")
    return data


def save_results(path: Path, results: dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".json.tmp")
    temp_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Ground Truth JSON from human-verified raw spoken text.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help=f"Input JSON (default: {DEFAULT_INPUT_PATH})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output JSON (default: {DEFAULT_OUTPUT_PATH})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_path = args.input.resolve()
    output_path = args.output.resolve()

    records = load_input_records(input_path)
    results = load_existing_results(output_path)

    for filename, raw_text in records.items():
        extraction = extract_ground_truth(raw_text)
        results[filename] = extraction.model_dump(mode="json")

    save_results(output_path, results)

    print(f"Ground Truth records updated: {len(records)}")
    print(f"Total records in output: {len(results)}")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
