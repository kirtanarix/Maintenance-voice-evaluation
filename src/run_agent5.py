"""Agent 5: speaker/dialect evaluation for the 9 new speaker recordings.

Isolated from Agent 4. Writes only under outputs/evaluation_speaker/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.config import PROJECT_ROOT
from src.speaker_evaluator import SPEAKER_ORDER, evaluate_speaker_subset
from src.speaker_report_generator import write_speaker_reports

DEFAULT_GT_PATH = PROJECT_ROOT / "outputs" / "ground_truth" / "ground_truth_final.json"
DEFAULT_SARVAM_PATH = (
    PROJECT_ROOT / "outputs" / "sarvam_gemini" / "sarvam_gemini_final.json"
)
DEFAULT_DIRECT_PATH = (
    PROJECT_ROOT / "outputs" / "direct_gemini" / "direct_gemini_final.json"
)
DEFAULT_SPEAKER_MAP = PROJECT_ROOT / "inputs" / "speaker_mapping.json"
DEFAULT_REPORT_PATH = (
    PROJECT_ROOT / "outputs" / "evaluation_speaker" / "evaluation_report.md"
)
DEFAULT_SUMMARY_PATH = (
    PROJECT_ROOT / "outputs" / "evaluation_speaker" / "evaluation_summary.json"
)

# Agent 4 outputs that must remain untouched.
AGENT4_REPORT = PROJECT_ROOT / "outputs" / "evaluation" / "evaluation_report.md"
AGENT4_SUMMARY = PROJECT_ROOT / "outputs" / "evaluation" / "evaluation_summary.json"


def load_json_object(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"{label} file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{label} must be a JSON object")
    return data


def load_speaker_mapping(path: Path) -> dict[str, list[str]]:
    raw = load_json_object(path, "Speaker mapping")
    mapping: dict[str, list[str]] = {}
    for speaker in SPEAKER_ORDER:
        if speaker not in raw:
            raise RuntimeError(f"Speaker mapping missing {speaker!r}")
        files = raw[speaker]
        if not isinstance(files, list) or not all(isinstance(x, str) for x in files):
            raise RuntimeError(f"Speaker {speaker!r} must map to a list of filename strings")
        mapping[speaker] = [x.strip() for x in files]
    extras = set(raw.keys()) - set(SPEAKER_ORDER)
    if extras:
        raise RuntimeError(f"Unexpected speakers in mapping: {sorted(extras)}")
    return mapping


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Agent 5: speaker/dialect evaluation for Sanjay, Mahesh, and Julfikar "
            "(9 recordings)."
        ),
    )
    parser.add_argument("--ground-truth", type=Path, default=DEFAULT_GT_PATH)
    parser.add_argument("--sarvam", type=Path, default=DEFAULT_SARVAM_PATH)
    parser.add_argument("--direct", type=Path, default=DEFAULT_DIRECT_PATH)
    parser.add_argument("--speaker-map", type=Path, default=DEFAULT_SPEAKER_MAP)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    agent4_hashes = {}
    for path in (AGENT4_REPORT, AGENT4_SUMMARY):
        if path.is_file():
            agent4_hashes[str(path)] = path.read_bytes()

    ground_truth = load_json_object(args.ground_truth.resolve(), "Ground Truth")
    sarvam = load_json_object(args.sarvam.resolve(), "Sarvam + Gemini")
    direct = load_json_object(args.direct.resolve(), "Direct Gemini")
    speaker_mapping = load_speaker_mapping(args.speaker_map.resolve())

    summary = evaluate_speaker_subset(
        ground_truth=ground_truth,
        sarvam=sarvam,
        direct=direct,
        speaker_mapping=speaker_mapping,
    )
    report_path = args.report.resolve()
    summary_path = args.summary.resolve()
    write_speaker_reports(summary, report_path, summary_path)

    for path_str, before in agent4_hashes.items():
        after = Path(path_str).read_bytes()
        if after != before:
            raise RuntimeError(f"Agent 4 output was modified unexpectedly: {path_str}")

    s = summary["overall"]["sarvam_gemini"]
    d = summary["overall"]["direct_gemini"]

    print("Agent 5 speaker/dialect evaluation complete")
    print(f"Recordings evaluated: {summary['total_recordings']}")
    for speaker in SPEAKER_ORDER:
        files = summary["speakers"][speaker]["filenames"]
        print(f"  {speaker}: {len(files)} ({', '.join(files)})")
    print(
        f"Sarvam + Gemini: {s['correct']}/{s['total']} = {s['accuracy_percent']}%"
    )
    print(
        f"Direct Gemini: {d['correct']}/{d['total']} = {d['accuracy_percent']}%"
    )
    print()
    for speaker in SPEAKER_ORDER:
        ss = summary["speakers"][speaker]["sarvam_gemini"]
        sd = summary["speakers"][speaker]["direct_gemini"]
        print(
            f"{speaker}: Sarvam {ss['correct']}/{ss['total']} ({ss['accuracy_percent']}%) | "
            f"Direct {sd['correct']}/{sd['total']} ({sd['accuracy_percent']}%)"
        )
    print()
    print(f"Markdown report: {report_path}")
    print(f"JSON summary: {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
