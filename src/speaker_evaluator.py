"""Agent 5: speaker/dialect evaluation over a fixed 9-recording subset.

Reuses Agent 4 field comparers by import only — does not modify Agent 4 behavior.
Writes exclusively under outputs/evaluation_speaker/.
"""

from __future__ import annotations

from typing import Any

from src.evaluator import (
    COMPARERS,
    CORRECT_JUDGMENTS,
    PARAMETERS,
    accuracy_from_judgments,
    correct_count,
    count_judgments,
    display_value,
)
from src.normalizer import format_value

SPEAKER_ORDER = ("Sanjay", "Mahesh", "Julfikar")
PIPELINE_SARVAM = "sarvam_gemini"
PIPELINE_DIRECT = "direct_gemini"
PIPELINE_LABELS = {
    PIPELINE_SARVAM: "Sarvam + Gemini",
    PIPELINE_DIRECT: "Direct Gemini",
}


def _is_correct(judgment: str) -> bool:
    return judgment in CORRECT_JUDGMENTS


def _judgment_explanation(judgment: str, gt: Any, model: Any) -> str:
    if judgment in ("EXACT_MATCH", "SEMANTIC_MATCH", "CORRECT_NULL"):
        return "Counted as correct under semantic evaluation rules."
    if judgment == "PARTIAL_MATCH":
        return (
            "Partial overlap with Ground Truth; not counted as fully correct."
        )
    if judgment == "MISSING":
        return "Ground Truth contains a spoken fact that the model omitted."
    if judgment == "HALLUCINATION":
        return "Model produced a value not supported by Ground Truth."
    if judgment == "INCORRECT":
        return (
            f"Model value differs from Ground Truth "
            f"(GT={format_value(gt)}; model={format_value(model)})."
        )
    return f"Judgment={judgment}."


def compare_field(parameter: str, gt: Any, model: Any) -> str:
    comparer = COMPARERS[parameter]
    return comparer(gt, model)


def evaluate_speaker_subset(
    *,
    ground_truth: dict[str, Any],
    sarvam: dict[str, Any],
    direct: dict[str, Any],
    speaker_mapping: dict[str, list[str]],
) -> dict[str, Any]:
    """Evaluate only the mapped speaker recordings against shared Ground Truth."""
    speakers_out: dict[str, Any] = {}
    all_sarvam: list[str] = []
    all_direct: list[str] = []
    all_sarvam_by_param: dict[str, list[str]] = {p: [] for p in PARAMETERS}
    all_direct_by_param: dict[str, list[str]] = {p: [] for p in PARAMETERS}
    recordings_detail: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    evaluated_files: list[str] = []

    for speaker in SPEAKER_ORDER:
        if speaker not in speaker_mapping:
            raise RuntimeError(f"Speaker mapping missing required speaker: {speaker}")
        filenames = list(speaker_mapping[speaker])
        if len(filenames) != 3:
            raise RuntimeError(
                f"Speaker {speaker!r} must have exactly 3 recordings, found {len(filenames)}"
            )

        speaker_sarvam: list[str] = []
        speaker_direct: list[str] = []
        speaker_sarvam_by_param: dict[str, list[str]] = {p: [] for p in PARAMETERS}
        speaker_direct_by_param: dict[str, list[str]] = {p: [] for p in PARAMETERS}
        speaker_recordings: list[dict[str, Any]] = []

        for filename in filenames:
            if filename not in ground_truth:
                raise RuntimeError(f"Ground Truth missing recording: {filename}")
            if filename not in sarvam:
                raise RuntimeError(f"Sarvam + Gemini missing recording: {filename}")
            if filename not in direct:
                raise RuntimeError(f"Direct Gemini missing recording: {filename}")

            gt_rec = ground_truth[filename]
            s_rec = sarvam[filename]
            d_rec = direct[filename]
            evaluated_files.append(filename)

            field_rows: dict[str, Any] = {}
            for param in PARAMETERS:
                if param not in gt_rec:
                    raise RuntimeError(f"Ground Truth {filename!r} missing {param}")
                gt_val = gt_rec[param]
                s_val = s_rec.get(param)
                d_val = d_rec.get(param)
                s_j = compare_field(param, gt_val, s_val)
                d_j = compare_field(param, gt_val, d_val)

                speaker_sarvam.append(s_j)
                speaker_direct.append(d_j)
                all_sarvam.append(s_j)
                all_direct.append(d_j)
                speaker_sarvam_by_param[param].append(s_j)
                speaker_direct_by_param[param].append(d_j)
                all_sarvam_by_param[param].append(s_j)
                all_direct_by_param[param].append(d_j)

                field_rows[param] = {
                    "ground_truth": gt_val,
                    "sarvam_gemini": {"value": s_val, "judgment": s_j},
                    "direct_gemini": {"value": d_val, "judgment": d_j},
                }

                for pipeline_key, judgment, model_val in (
                    (PIPELINE_SARVAM, s_j, s_val),
                    (PIPELINE_DIRECT, d_j, d_val),
                ):
                    if not _is_correct(judgment):
                        errors.append(
                            {
                                "speaker": speaker,
                                "filename": filename,
                                "pipeline": PIPELINE_LABELS[pipeline_key],
                                "pipeline_key": pipeline_key,
                                "parameter": param,
                                "ground_truth": gt_val,
                                "model_output": model_val,
                                "classification": judgment,
                                "explanation": _judgment_explanation(
                                    judgment, gt_val, model_val
                                ),
                            }
                        )

            rec_detail = {
                "speaker": speaker,
                "filename": filename,
                "parameters": field_rows,
            }
            speaker_recordings.append(rec_detail)
            recordings_detail.append(rec_detail)

        speakers_out[speaker] = {
            "recordings": len(filenames),
            "filenames": filenames,
            "sarvam_gemini": _pipeline_stats(
                speaker_sarvam, speaker_sarvam_by_param
            ),
            "direct_gemini": _pipeline_stats(
                speaker_direct, speaker_direct_by_param
            ),
            "recordings_detail": speaker_recordings,
        }

    if len(evaluated_files) != 9:
        raise RuntimeError(f"Expected 9 recordings, evaluated {len(evaluated_files)}")
    if len(set(evaluated_files)) != 9:
        raise RuntimeError("Duplicate filenames in speaker mapping")
    if len(all_sarvam) != 45 or len(all_direct) != 45:
        raise RuntimeError(
            f"Expected 45 comparisons per pipeline; "
            f"got sarvam={len(all_sarvam)} direct={len(all_direct)}"
        )

    return {
        "evaluation_type": "speaker_dialect",
        "evaluation_version": "speaker-v1",
        "total_recordings": 9,
        "parameters": list(PARAMETERS),
        "comparisons_per_pipeline": 45,
        "speaker_mapping_note": (
            "Speaker labels follow inputs/speaker_mapping.json. "
            "The Mahesh group uses jigishbhai_* filenames as listed in that mapping; "
            "identity is not inferred from transcript text."
        ),
        "evaluated_filenames": evaluated_files,
        "speakers": speakers_out,
        "overall": {
            "sarvam_gemini": _pipeline_stats(all_sarvam, all_sarvam_by_param),
            "direct_gemini": _pipeline_stats(all_direct, all_direct_by_param),
        },
        "errors": errors,
        "recordings": recordings_detail,
        "methodology": {
            "correct_judgments": sorted(CORRECT_JUDGMENTS),
            "partial_match_policy": (
                "PARTIAL_MATCH is reported but excluded from accuracy numerators."
            ),
            "same_ground_truth": True,
            "reuses_agent4_comparers": True,
            "agent4_outputs_untouched": True,
        },
    }


def _pipeline_stats(
    judgments: list[str],
    by_param: dict[str, list[str]],
) -> dict[str, Any]:
    correct, total = correct_count(judgments)
    per_param: dict[str, Any] = {}
    for param in PARAMETERS:
        c, t = correct_count(by_param[param])
        per_param[param] = {
            "correct": c,
            "total": t,
            "accuracy_percent": accuracy_from_judgments(by_param[param]),
            "counts": count_judgments(by_param[param]),
        }
    return {
        "correct": correct,
        "total": total,
        "accuracy_percent": accuracy_from_judgments(judgments),
        "counts": count_judgments(judgments),
        "per_parameter": per_param,
    }


def frac_label(correct: int, total: int, pct: float) -> str:
    if pct == int(pct):
        pct_s = f"{int(pct)}%"
    else:
        pct_s = f"{pct:.2f}".rstrip("0").rstrip(".") + "%"
    return f"{correct}/{total} ({pct_s})"
