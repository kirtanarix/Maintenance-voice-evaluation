"""Markdown and JSON report generation for Agent 4 evaluation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.evaluator import (
    MODEL_DIRECT,
    MODEL_SARVAM,
    PARAMETERS,
    EvaluationResult,
    accuracy_from_judgments,
    attribute_errors,
    collect_model_judgments,
    collect_parameter_judgments,
    correct_count,
    count_judgments,
    display_value,
)

EVALUATION_VERSION = "semantic-v2"

PARAM_LABELS = {
    "assets": "Assets",
    "quantities": "Quantities",
    "hours": "Hours",
    "dates": "Dates",
    "approval_intent": "Approval intent",
}


def _pct(value: float) -> str:
    if value == int(value):
        return f"{int(value)}%"
    return f"{value:.2f}".rstrip("0").rstrip(".") + "%"


def _frac(correct: int, total: int) -> str:
    pct = 0.0 if total == 0 else round(100.0 * correct / total, 2)
    return f"{correct} / {total} = {_pct(pct)}"


def _build_summary(result: EvaluationResult) -> dict[str, Any]:
    sarvam_j = collect_model_judgments(result, MODEL_SARVAM)
    direct_j = collect_model_judgments(result, MODEL_DIRECT)
    sarvam_counts = count_judgments(sarvam_j)
    direct_counts = count_judgments(direct_j)
    attribution = attribute_errors(result)

    per_param: dict[str, dict[str, Any]] = {}
    for param in PARAMETERS:
        s_j = collect_parameter_judgments(result, MODEL_SARVAM, param)
        d_j = collect_parameter_judgments(result, MODEL_DIRECT, param)
        s_c, s_t = correct_count(s_j)
        d_c, d_t = correct_count(d_j)
        per_param[param] = {
            "sarvam_gemini": {
                "correct": s_c,
                "partial": s_j.count("PARTIAL_MATCH"),
                "incorrect": s_j.count("INCORRECT"),
                "missing": s_j.count("MISSING"),
                "hallucination": s_j.count("HALLUCINATION"),
                "total": s_t,
                "accuracy_percent": accuracy_from_judgments(s_j),
                "counts": count_judgments(s_j),
            },
            "direct_gemini": {
                "correct": d_c,
                "partial": d_j.count("PARTIAL_MATCH"),
                "incorrect": d_j.count("INCORRECT"),
                "missing": d_j.count("MISSING"),
                "hallucination": d_j.count("HALLUCINATION"),
                "total": d_t,
                "accuracy_percent": accuracy_from_judgments(d_j),
                "counts": count_judgments(d_j),
            },
        }

    s_c, s_t = correct_count(sarvam_j)
    d_c, d_t = correct_count(direct_j)

    return {
        "evaluation_version": EVALUATION_VERSION,
        "methodology": {
            "correct_judgments": [
                "EXACT_MATCH",
                "SEMANTIC_MATCH",
                "CORRECT_NULL",
            ],
            "partial_match_policy": (
                "PARTIAL_MATCH does not count toward overall/parameter accuracy "
                "numerator. It is reported separately. Component overlap may be "
                "partial, but conflicting quantities (e.g. 1 vs 2 fitters) are INCORRECT."
            ),
            "normalization": [
                "number words → digits",
                "equipment IDs: BC-15 / BC15 → bc15",
                "unit aliases: kg/kilogram, hour/hours, liter/litre",
                "time forms: 10:00 / 10 AM",
                "Hindi↔English day names and common asset synonyms",
                "possessives and punctuation stripped",
            ],
            "hours_kinds": [
                "work_duration",
                "inspection_duration",
                "machine_downtime",
            ],
            "error_attribution_heuristic": (
                "Without stored Sarvam transcripts: Sarvam wrong + Direct correct → "
                "likely_stt_error; Sarvam correct + Direct wrong → direct_extraction_error; "
                "both wrong → both_pipelines_error."
            ),
        },
        "dataset": {
            "ground_truth_recordings": result.gt_count,
            "sarvam_gemini_recordings": result.sarvam_count,
            "direct_gemini_recordings": result.direct_count,
            "parameters_per_recording": len(PARAMETERS),
            "total_comparisons": len(sarvam_j) + len(direct_j),
            "comparisons_per_model": len(sarvam_j),
        },
        "missing_recordings": {
            "sarvam_gemini": result.missing_in_sarvam,
            "direct_gemini": result.missing_in_direct,
        },
        "unexpected_recordings": {
            "sarvam_gemini": result.unexpected_in_sarvam,
            "direct_gemini": result.unexpected_in_direct,
        },
        "overall": {
            "sarvam_gemini": {
                "correct": s_c,
                "partial": sarvam_counts.get("PARTIAL_MATCH", 0),
                "incorrect": sarvam_counts.get("INCORRECT", 0),
                "missing": sarvam_counts.get("MISSING", 0),
                "hallucination": sarvam_counts.get("HALLUCINATION", 0),
                "total": s_t,
                "accuracy_percent": accuracy_from_judgments(sarvam_j),
                "counts": sarvam_counts,
            },
            "direct_gemini": {
                "correct": d_c,
                "partial": direct_counts.get("PARTIAL_MATCH", 0),
                "incorrect": direct_counts.get("INCORRECT", 0),
                "missing": direct_counts.get("MISSING", 0),
                "hallucination": direct_counts.get("HALLUCINATION", 0),
                "total": d_t,
                "accuracy_percent": accuracy_from_judgments(direct_j),
                "counts": direct_counts,
            },
        },
        "per_parameter": per_param,
        # Backward-compatible flat percents
        "per_parameter_accuracy_percent": {
            param: {
                "sarvam_gemini": per_param[param]["sarvam_gemini"]["accuracy_percent"],
                "direct_gemini": per_param[param]["direct_gemini"]["accuracy_percent"],
            }
            for param in PARAMETERS
        },
        "error_attribution": attribution,
        "recordings": [
            {
                "filename": rec.filename,
                "sarvam_gemini": {
                    f.parameter: {
                        "ground_truth": f.ground_truth,
                        "model": f.model_value,
                        "judgment": f.judgment,
                    }
                    for f in rec.sarvam_fields
                },
                "direct_gemini": {
                    f.parameter: {
                        "ground_truth": f.ground_truth,
                        "model": f.model_value,
                        "judgment": f.judgment,
                    }
                    for f in rec.direct_fields
                },
            }
            for rec in result.recordings
        ],
    }


def _error_analysis_section(result: EvaluationResult) -> list[str]:
    lines: list[str] = ["## 7. Error Analysis", ""]

    for param in PARAMETERS:
        label = PARAM_LABELS[param]
        lines.append(f"### {label}")
        lines.append("")
        findings: list[str] = []
        for rec in result.recordings:
            for model_name, fields in (
                ("Sarvam + Gemini", rec.sarvam_fields),
                ("Direct Gemini", rec.direct_fields),
            ):
                for f in fields:
                    if f.parameter != param:
                        continue
                    if f.judgment in ("EXACT_MATCH", "SEMANTIC_MATCH", "CORRECT_NULL"):
                        continue
                    findings.append(
                        f"- `{rec.filename}` / {model_name}: **{f.judgment}** — "
                        f"Ground Truth `{display_value(f.ground_truth)}` vs "
                        f"model `{display_value(f.model_value)}`."
                    )
        if findings:
            lines.extend(findings[:40])
            if len(findings) > 40:
                lines.append(f"- … and {len(findings) - 40} more.")
        else:
            lines.append("No errors observed for this parameter on the supplied recordings.")
        lines.append("")
    return lines


def _representative_examples(result: EvaluationResult) -> list[str]:
    lines = ["## 8. Representative Examples", ""]
    shown = 0
    for rec in result.recordings:
        for fields, label in (
            (rec.sarvam_fields, "Sarvam + Gemini"),
            (rec.direct_fields, "Direct Gemini"),
        ):
            for f in fields:
                if f.judgment == "SEMANTIC_MATCH" and shown < 8:
                    lines.append(
                        f"- Semantic match (`{rec.filename}` / {label} / {f.parameter}): "
                        f"GT `{display_value(f.ground_truth)}` ≈ model "
                        f"`{display_value(f.model_value)}`."
                    )
                    shown += 1
    if shown == 0:
        lines.append("No SEMANTIC_MATCH examples found.")
    lines.append("")
    shown_p = 0
    for rec in result.recordings:
        for fields, label in (
            (rec.sarvam_fields, "Sarvam + Gemini"),
            (rec.direct_fields, "Direct Gemini"),
        ):
            for f in fields:
                if f.judgment == "PARTIAL_MATCH" and shown_p < 6:
                    lines.append(
                        f"- Partial (`{rec.filename}` / {label} / {f.parameter}): "
                        f"GT `{display_value(f.ground_truth)}` vs model "
                        f"`{display_value(f.model_value)}`."
                    )
                    shown_p += 1
    lines.append("")
    return lines


def _attribution_section(summary: dict[str, Any]) -> list[str]:
    attr = summary["error_attribution"]["counts"]
    lines = [
        "## 9. STT vs Extraction Error Attribution",
        "",
        "Transcripts are not stored in Agent 1 outputs, so attribution is heuristic:",
        "",
        "- **likely_stt_error**: Sarvam+Gemini incorrect on a parameter while Direct Gemini is correct "
        "(Direct recovered the fact from audio; Sarvam path likely lost it in STT or STT→extract).",
        "- **direct_extraction_error**: Direct Gemini incorrect while Sarvam+Gemini is correct.",
        "- **both_pipelines_error**: both pipelines incorrect on the same parameter.",
        "",
        "| Attribution | Count |",
        "|---|---:|",
        f"| likely_stt_error | {attr['likely_stt_error']} |",
        f"| direct_extraction_error | {attr['direct_extraction_error']} |",
        f"| both_pipelines_error | {attr['both_pipelines_error']} |",
        f"| both_correct | {attr['both_correct']} |",
        "",
    ]
    return lines


def _model_comparison_narrative(summary: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    s_acc = summary["overall"]["sarvam_gemini"]["accuracy_percent"]
    d_acc = summary["overall"]["direct_gemini"]["accuracy_percent"]
    s_c = summary["overall"]["sarvam_gemini"]["correct"]
    s_t = summary["overall"]["sarvam_gemini"]["total"]
    d_c = summary["overall"]["direct_gemini"]["correct"]
    d_t = summary["overall"]["direct_gemini"]["total"]
    lines.append(
        f"On this dataset, Direct Gemini achieved {_pct(d_acc)} ({d_c}/{d_t}) compared with "
        f"{_pct(s_acc)} ({s_c}/{s_t}) for Sarvam + Gemini."
    )
    lines.append("")
    lines.append(
        "These results are limited to the supplied recordings and should not be read as a "
        "universal claim that either pipeline is better in general."
    )
    lines.append("")
    return lines


def generate_markdown(result: EvaluationResult, summary: dict[str, Any]) -> str:
    s = summary["overall"]["sarvam_gemini"]
    d = summary["overall"]["direct_gemini"]
    sc = s["counts"]
    dc = d["counts"]
    ds = summary["dataset"]

    lines: list[str] = [
        "# Maintenance Voice Model Evaluation",
        "",
        "## 1. Evaluation Overview",
        "",
        f"- Evaluation version: **{summary['evaluation_version']}**",
        "- Pipelines compared against human-verified Ground Truth:",
        "  1. Sarvam STT → Gemini extraction",
        "  2. Direct Gemini audio extraction",
        "- Parameters: assets, quantities, hours, dates, approval_intent",
        "",
        "## 2. Dataset Size",
        "",
        f"- Ground Truth recording count: **{ds['ground_truth_recordings']}**",
        f"- Sarvam + Gemini recording count: **{ds['sarvam_gemini_recordings']}**",
        f"- Direct Gemini recording count: **{ds['direct_gemini_recordings']}**",
        f"- Parameters per recording: **{ds['parameters_per_recording']}**",
        f"- Comparisons per model: **{ds['comparisons_per_model']}**",
        f"- Total comparisons (both models): **{ds['total_comparisons']}**",
        "",
    ]

    if result.missing_in_sarvam or result.missing_in_direct:
        lines.append("### Missing model recordings")
        lines.append("")
        if result.missing_in_sarvam:
            lines.append(
                "- Absent from Sarvam + Gemini: "
                + ", ".join(f"`{x}`" for x in result.missing_in_sarvam)
            )
        if result.missing_in_direct:
            lines.append(
                "- Absent from Direct Gemini: "
                + ", ".join(f"`{x}`" for x in result.missing_in_direct)
            )
        lines.append("")

    if result.unexpected_in_sarvam or result.unexpected_in_direct:
        lines.append("### Unexpected model recordings")
        lines.append("")
        if result.unexpected_in_sarvam:
            lines.append(
                "- Unexpected in Sarvam + Gemini: "
                + ", ".join(f"`{x}`" for x in result.unexpected_in_sarvam)
            )
        if result.unexpected_in_direct:
            lines.append(
                "- Unexpected in Direct Gemini: "
                + ", ".join(f"`{x}`" for x in result.unexpected_in_direct)
            )
        lines.append("")

    lines.extend(
        [
            "## 3. Evaluation Methodology",
            "",
            "Judgments per parameter:",
            "",
            "- **EXACT_MATCH** / **SEMANTIC_MATCH** / **CORRECT_NULL** → count as correct",
            "- **PARTIAL_MATCH** → incomplete overlap; **not** counted in accuracy numerator",
            "- **MISSING** / **INCORRECT** / **HALLUCINATION** → not correct",
            "",
            "Hours kinds are compared separately when specified "
            "(`work_duration`, `inspection_duration`, `machine_downtime`). "
            "Same numeric duration with a different kind is PARTIAL_MATCH, not full credit.",
            "",
            "Quantity order does not matter. Conflicting numeric values for the same item "
            "are INCORRECT (e.g. 1 fitter vs 2 fitters).",
            "",
            "## 4. Semantic Normalization Rules",
            "",
        ]
    )
    for rule in summary["methodology"]["normalization"]:
        lines.append(f"- {rule}")
    lines.extend(
        [
            "",
            "## 5. Overall Accuracy",
            "",
            "| Metric | Sarvam + Gemini | Direct Gemini |",
            "|---|---:|---:|",
            f"| Overall accuracy | {_frac(s['correct'], s['total'])} | {_frac(d['correct'], d['total'])} |",
            f"| Exact matches | {sc['EXACT_MATCH']} | {dc['EXACT_MATCH']} |",
            f"| Semantic matches | {sc['SEMANTIC_MATCH']} | {dc['SEMANTIC_MATCH']} |",
            f"| Correct nulls | {sc['CORRECT_NULL']} | {dc['CORRECT_NULL']} |",
            f"| Partial matches | {sc['PARTIAL_MATCH']} | {dc['PARTIAL_MATCH']} |",
            f"| Missing | {sc['MISSING']} | {dc['MISSING']} |",
            f"| Incorrect | {sc['INCORRECT']} | {dc['INCORRECT']} |",
            f"| Hallucinations | {sc['HALLUCINATION']} | {dc['HALLUCINATION']} |",
            "",
            "## 6. Parameter-wise Accuracy",
            "",
            "| Parameter | Sarvam + Gemini | Direct Gemini |",
            "|---|---:|---:|",
        ]
    )

    for param in PARAMETERS:
        label = PARAM_LABELS[param]
        sp = summary["per_parameter"][param]["sarvam_gemini"]
        dp = summary["per_parameter"][param]["direct_gemini"]
        lines.append(
            f"| {label} | {_frac(sp['correct'], sp['total'])} | {_frac(dp['correct'], dp['total'])} |"
        )

    lines.extend(["", "## Detailed Recording Results", ""])

    for rec in result.recordings:
        gt = rec.ground_truth or {}
        lines.append(f"### {rec.filename}")
        lines.append("")
        lines.append("| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |")
        lines.append("|---|---|---|---|")
        for param in PARAMETERS:
            gt_v = display_value(gt.get(param))
            s_field = next(f for f in rec.sarvam_fields if f.parameter == param)
            d_field = next(f for f in rec.direct_fields if f.parameter == param)
            lines.append(
                f"| {param} | {gt_v} | {display_value(s_field.model_value)} | "
                f"{display_value(d_field.model_value)} |"
            )
        lines.append("")
        lines.append("| Parameter | Sarvam judgment | Direct Gemini judgment |")
        lines.append("|---|---|---|")
        for param in PARAMETERS:
            s_field = next(f for f in rec.sarvam_fields if f.parameter == param)
            d_field = next(f for f in rec.direct_fields if f.parameter == param)
            lines.append(f"| {param} | {s_field.judgment} | {d_field.judgment} |")
        lines.append("")

    lines.extend(_error_analysis_section(result))
    lines.extend(_representative_examples(result))
    lines.extend(_attribution_section(summary))

    lines.extend(
        [
            "## 10. Dataset Limitations",
            "",
            "This evaluation measures only the supplied recordings against the human-verified "
            "Ground Truth. Partial matches are visible in counts but excluded from accuracy "
            "numerators. Error attribution is heuristic because Sarvam transcripts are not "
            "persisted in `outputs/sarvam_gemini/sarvam_gemini_final.json`.",
            "",
            "## 11. Final Factual Comparison",
            "",
        ]
    )
    lines.extend(_model_comparison_narrative(summary))
    return "\n".join(lines)


def write_reports(
    result: EvaluationResult,
    markdown_path: Path,
    summary_path: Path | None = None,
) -> dict[str, Any]:
    summary = _build_summary(result)
    markdown = generate_markdown(result, summary)

    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown, encoding="utf-8")

    if summary_path is not None:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return summary
