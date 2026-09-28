"""Markdown + JSON report writer for Agent 5 (speaker/dialect evaluation)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.evaluator import PARAMETERS, display_value
from src.speaker_evaluator import SPEAKER_ORDER, frac_label

PARAM_LABELS = {
    "assets": "Assets",
    "quantities": "Quantities",
    "hours": "Hours",
    "dates": "Dates",
    "approval_intent": "Approval",
}


def _cell(stats: dict[str, Any], param: str | None = None) -> str:
    if param is None:
        return frac_label(stats["correct"], stats["total"], stats["accuracy_percent"])
    p = stats["per_parameter"][param]
    return frac_label(p["correct"], p["total"], p["accuracy_percent"])


def generate_markdown(summary: dict[str, Any]) -> str:
    overall_s = summary["overall"]["sarvam_gemini"]
    overall_d = summary["overall"]["direct_gemini"]
    lines: list[str] = [
        "# Speaker/Dialect Evaluation",
        "",
        "## 1. Objective",
        "",
        "This evaluation tests whether model performance varies across individual "
        "speakers on a fixed set of maintenance voice recordings. It is separate "
        "from the full-dataset Agent 4 evaluation and does not replace it.",
        "",
        "## 2. Dataset",
        "",
        "- 3 recordings from Sanjay",
        "- 3 recordings from Mahesh",
        "- 3 recordings from Julfikar",
        "- 9 recordings total",
        "- 5 parameters per recording (assets, quantities, hours, dates, approval_intent)",
        "- 45 field comparisons per pipeline",
        "",
        f"Speaker identity is taken from `inputs/speaker_mapping.json`. "
        f"{summary['speaker_mapping_note']}",
        "",
        "Evaluated filenames:",
        "",
    ]
    for speaker in SPEAKER_ORDER:
        files = ", ".join(f"`{f}`" for f in summary["speakers"][speaker]["filenames"])
        lines.append(f"- **{speaker}**: {files}")
    lines.extend(
        [
            "",
            "## 3. Speaker-wise Results",
            "",
            "| Speaker | Pipeline | Assets | Quantities | Hours | Dates | Approval | Overall |",
            "|---------|----------|--------|------------|-------|-------|----------|---------|",
        ]
    )
    for speaker in SPEAKER_ORDER:
        for pipe_key, pipe_label in (
            ("sarvam_gemini", "Sarvam + Gemini"),
            ("direct_gemini", "Direct Gemini"),
        ):
            st = summary["speakers"][speaker][pipe_key]
            lines.append(
                "| {speaker} | {pipe} | {a} | {q} | {h} | {d} | {ap} | {o} |".format(
                    speaker=speaker,
                    pipe=pipe_label,
                    a=_cell(st, "assets"),
                    q=_cell(st, "quantities"),
                    h=_cell(st, "hours"),
                    d=_cell(st, "dates"),
                    ap=_cell(st, "approval_intent"),
                    o=_cell(st),
                )
            )

    lines.extend(
        [
            "",
            "## 4. Pipeline Comparison",
            "",
            "Nine-recording aggregate (this speaker evaluation only):",
            "",
            f"- Sarvam + Gemini: **{overall_s['correct']} / {overall_s['total']} = "
            f"{overall_s['accuracy_percent']}%**",
            f"- Direct Gemini: **{overall_d['correct']} / {overall_d['total']} = "
            f"{overall_d['accuracy_percent']}%**",
            "",
            f"On this 9-recording speaker evaluation, Direct Gemini achieved "
            f"{overall_d['accuracy_percent']}% ({overall_d['correct']}/{overall_d['total']}) "
            f"compared with {overall_s['accuracy_percent']}% "
            f"({overall_s['correct']}/{overall_s['total']}) for Sarvam + Gemini.",
            "",
            "These figures apply only to this 9-recording subset and do not replace "
            "the existing full-dataset Agent 4 results.",
            "",
            "## 5. Speaker/Dialect Comparison",
            "",
        ]
    )

    speaker_rows = []
    for speaker in SPEAKER_ORDER:
        s_acc = summary["speakers"][speaker]["sarvam_gemini"]["accuracy_percent"]
        d_acc = summary["speakers"][speaker]["direct_gemini"]["accuracy_percent"]
        speaker_rows.append((speaker, s_acc, d_acc))
        lines.append(
            f"- **{speaker}**: Sarvam + Gemini {s_acc}%; Direct Gemini {d_acc}%."
        )

    s_vals = [r[1] for r in speaker_rows]
    d_vals = [r[2] for r in speaker_rows]
    lines.append("")
    if max(s_vals) - min(s_vals) > 0 or max(d_vals) - min(d_vals) > 0:
        lines.append("Performance varied across the three speakers.")
        lines.append("")
        lines.append(
            f"- Sarvam + Gemini speaker range: {min(s_vals)}% to {max(s_vals)}% "
            f"(spread {round(max(s_vals) - min(s_vals), 2)} percentage points)."
        )
        lines.append(
            f"- Direct Gemini speaker range: {min(d_vals)}% to {max(d_vals)}% "
            f"(spread {round(max(d_vals) - min(d_vals), 2)} percentage points)."
        )
    else:
        lines.append(
            "On this subset, overall accuracy did not differ across the three speakers."
        )
    lines.extend(
        [
            "",
            "No dialect label is assigned beyond the named speakers in the mapping file.",
            "",
            "## 6. Parameter-wise Comparison",
            "",
            "| Parameter | Sarvam + Gemini | Direct Gemini |",
            "|---|---:|---:|",
        ]
    )
    for param in PARAMETERS:
        sp = overall_s["per_parameter"][param]
        dp = overall_d["per_parameter"][param]
        lines.append(
            f"| {PARAM_LABELS[param]} | "
            f"{frac_label(sp['correct'], sp['total'], sp['accuracy_percent'])} | "
            f"{frac_label(dp['correct'], dp['total'], dp['accuracy_percent'])} |"
        )

    lines.extend(["", "## 7. Detailed Errors", ""])
    errors = summary.get("errors") or []
    if not errors:
        lines.append(
            "No incorrect or partial comparisons were observed on this 9-recording set."
        )
    else:
        lines.append(
            f"{len(errors)} non-correct field comparisons "
            "(PARTIAL_MATCH, MISSING, INCORRECT, HALLUCINATION, etc.):"
        )
        lines.append("")
        for i, err in enumerate(errors, start=1):
            lines.extend(
                [
                    f"### Error {i}",
                    "",
                    f"- Speaker: **{err['speaker']}**",
                    f"- Audio: `{err['filename']}`",
                    f"- Pipeline: {err['pipeline']}",
                    f"- Parameter: `{err['parameter']}`",
                    f"- Ground Truth: `{display_value(err['ground_truth'])}`",
                    f"- Model output: `{display_value(err['model_output'])}`",
                    f"- Classification: **{err['classification']}**",
                    f"- Explanation: {err['explanation']}",
                    "",
                ]
            )

    lines.extend(
        [
            "## 8. Limitations",
            "",
            "- Only 9 recordings were evaluated.",
            "- Only 3 speakers were represented.",
            "- Only 3 recordings per speaker were used.",
            "- Results measure this specific dataset only.",
            "- Results should not be generalized to all speakers or dialects.",
            "- This report does not modify or replace Agent 4 full-dataset evaluation outputs.",
            "",
        ]
    )
    return "\n".join(lines)


def write_speaker_reports(
    summary: dict[str, Any],
    markdown_path: Path,
    summary_path: Path,
) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(generate_markdown(summary), encoding="utf-8")
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
