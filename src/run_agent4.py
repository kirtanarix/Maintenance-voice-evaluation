"""Agent 4: deterministic evaluation of Sarvam+Gemini and Direct Gemini vs Ground Truth."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.evaluator import evaluate
from src.report_generator import write_reports

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_GT_PATH = PROJECT_ROOT / "outputs" / "ground_truth" / "ground_truth_final.json"
DEFAULT_SARVAM_PATH = PROJECT_ROOT / "outputs" / "sarvam_gemini" / "sarvam_gemini_final.json"
DEFAULT_DIRECT_PATH = PROJECT_ROOT / "outputs" / "direct_gemini" / "direct_gemini_final.json"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "outputs" / "evaluation" / "evaluation_report.md"
DEFAULT_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "evaluation" / "evaluation_summary.json"

EXPECTED_PARAMETERS = (
    "assets",
    "quantities",
    "hours",
    "dates",
    "approval_intent",
)


def load_json_object(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"{label} file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{label} must be a JSON object keyed by audio filename")
    return data


def validate_parameters(data: dict, label: str) -> None:
    if not data:
        raise RuntimeError(f"{label} contains no recordings")
    for filename, record in data.items():
        if not isinstance(record, dict):
            raise RuntimeError(f"{label} record {filename!r} must be an object")
        missing = [p for p in EXPECTED_PARAMETERS if p not in record]
        if missing:
            raise RuntimeError(
                f"{label} record {filename!r} missing parameters: {', '.join(missing)}"
            )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Agent 4: compare Sarvam+Gemini and Direct Gemini extractions against Ground Truth."
        ),
    )
    parser.add_argument(
        "--ground-truth",
        type=Path,
        default=DEFAULT_GT_PATH,
        help=f"Ground Truth JSON (default: {DEFAULT_GT_PATH})",
    )
    parser.add_argument(
        "--sarvam",
        type=Path,
        default=DEFAULT_SARVAM_PATH,
        help=f"Sarvam + Gemini JSON (default: {DEFAULT_SARVAM_PATH})",
    )
    parser.add_argument(
        "--direct",
        type=Path,
        default=DEFAULT_DIRECT_PATH,
        help=f"Direct Gemini JSON (default: {DEFAULT_DIRECT_PATH})",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Markdown report path (default: {DEFAULT_REPORT_PATH})",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_SUMMARY_PATH,
        help=f"Optional JSON summary path (default: {DEFAULT_SUMMARY_PATH})",
    )
    parser.add_argument(
        "--no-summary-json",
        action="store_true",
        help="Skip writing evaluation_summary.json",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    gt_path = args.ground_truth.resolve()
    sarvam_path = args.sarvam.resolve()
    direct_path = args.direct.resolve()
    report_path = args.report.resolve()
    summary_path = None if args.no_summary_json else args.summary.resolve()

    # 1–5: validate inputs exist, parse, confirm GT records, match by filename, five params
    ground_truth = load_json_object(gt_path, "Ground Truth")
    sarvam = load_json_object(sarvam_path, "Sarvam + Gemini")
    direct = load_json_object(direct_path, "Direct Gemini")

    validate_parameters(ground_truth, "Ground Truth")
    validate_parameters(sarvam, "Sarvam + Gemini")
    validate_parameters(direct, "Direct Gemini")

    # 6–8: judgments, percentages, report
    result = evaluate(ground_truth, sarvam, direct)
    summary = write_reports(result, report_path, summary_path)

    s = summary["overall"]["sarvam_gemini"]
    d = summary["overall"]["direct_gemini"]

    print("Agent 4 evaluation complete")
    print(f"Recordings: {result.gt_count}")
    print(f"Sarvam + Gemini: {s['correct']}/{s['total']} = {s['accuracy_percent']}%")
    print(f"Direct Gemini: {d['correct']}/{d['total']} = {d['accuracy_percent']}%")
    print()
    print("Assets:")
    print(
        f"  Sarvam {summary['per_parameter']['assets']['sarvam_gemini']['correct']}/"
        f"{summary['per_parameter']['assets']['sarvam_gemini']['total']} "
        f"({summary['per_parameter']['assets']['sarvam_gemini']['accuracy_percent']}%) | "
        f"Direct {summary['per_parameter']['assets']['direct_gemini']['correct']}/"
        f"{summary['per_parameter']['assets']['direct_gemini']['total']} "
        f"({summary['per_parameter']['assets']['direct_gemini']['accuracy_percent']}%)"
    )
    print("Quantities:")
    print(
        f"  Sarvam {summary['per_parameter']['quantities']['sarvam_gemini']['correct']}/"
        f"{summary['per_parameter']['quantities']['sarvam_gemini']['total']} "
        f"({summary['per_parameter']['quantities']['sarvam_gemini']['accuracy_percent']}%) | "
        f"Direct {summary['per_parameter']['quantities']['direct_gemini']['correct']}/"
        f"{summary['per_parameter']['quantities']['direct_gemini']['total']} "
        f"({summary['per_parameter']['quantities']['direct_gemini']['accuracy_percent']}%)"
    )
    print("Hours:")
    print(
        f"  Sarvam {summary['per_parameter']['hours']['sarvam_gemini']['correct']}/"
        f"{summary['per_parameter']['hours']['sarvam_gemini']['total']} "
        f"({summary['per_parameter']['hours']['sarvam_gemini']['accuracy_percent']}%) | "
        f"Direct {summary['per_parameter']['hours']['direct_gemini']['correct']}/"
        f"{summary['per_parameter']['hours']['direct_gemini']['total']} "
        f"({summary['per_parameter']['hours']['direct_gemini']['accuracy_percent']}%)"
    )
    print("Dates:")
    print(
        f"  Sarvam {summary['per_parameter']['dates']['sarvam_gemini']['correct']}/"
        f"{summary['per_parameter']['dates']['sarvam_gemini']['total']} "
        f"({summary['per_parameter']['dates']['sarvam_gemini']['accuracy_percent']}%) | "
        f"Direct {summary['per_parameter']['dates']['direct_gemini']['correct']}/"
        f"{summary['per_parameter']['dates']['direct_gemini']['total']} "
        f"({summary['per_parameter']['dates']['direct_gemini']['accuracy_percent']}%)"
    )
    print("Approval:")
    print(
        f"  Sarvam {summary['per_parameter']['approval_intent']['sarvam_gemini']['correct']}/"
        f"{summary['per_parameter']['approval_intent']['sarvam_gemini']['total']} "
        f"({summary['per_parameter']['approval_intent']['sarvam_gemini']['accuracy_percent']}%) | "
        f"Direct {summary['per_parameter']['approval_intent']['direct_gemini']['correct']}/"
        f"{summary['per_parameter']['approval_intent']['direct_gemini']['total']} "
        f"({summary['per_parameter']['approval_intent']['direct_gemini']['accuracy_percent']}%)"
    )
    print()
    print(f"Overall: Sarvam {s['accuracy_percent']}% | Direct {d['accuracy_percent']}%")
    print(f"Markdown report: {report_path}")
    if summary_path is not None:
        print(f"JSON summary: {summary_path}")
    if result.missing_in_sarvam:
        print(f"Missing in Sarvam + Gemini: {', '.join(result.missing_in_sarvam)}")
    if result.missing_in_direct:
        print(f"Missing in Direct Gemini: {', '.join(result.missing_in_direct)}")
    if result.unexpected_in_sarvam:
        print(f"Unexpected in Sarvam + Gemini: {', '.join(result.unexpected_in_sarvam)}")
    if result.unexpected_in_direct:
        print(f"Unexpected in Direct Gemini: {', '.join(result.unexpected_in_direct)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
