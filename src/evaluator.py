"""Deterministic field-level comparison of model outputs against Ground Truth."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from src.normalizer import (
    approval_as_text,
    assets_as_list,
    dates_as_list,
    format_value,
    hours_as_list,
    is_null,
    normalize_text,
    quantities_as_list,
)

PARAMETERS: tuple[str, ...] = (
    "assets",
    "quantities",
    "hours",
    "dates",
    "approval_intent",
)

JUDGMENTS: tuple[str, ...] = (
    "EXACT_MATCH",
    "SEMANTIC_MATCH",
    "PARTIAL_MATCH",
    "MISSING",
    "INCORRECT",
    "HALLUCINATION",
    "CORRECT_NULL",
    "NOT_EVALUABLE",
)

CORRECT_JUDGMENTS = frozenset({"EXACT_MATCH", "SEMANTIC_MATCH", "CORRECT_NULL"})

MODEL_SARVAM = "sarvam_gemini"
MODEL_DIRECT = "direct_gemini"

_TOKEN_RE = re.compile(r"[a-z0-9./%-]+", re.I)


@dataclass
class FieldResult:
    parameter: str
    ground_truth: Any
    model_value: Any
    judgment: str


@dataclass
class RecordingResult:
    filename: str
    ground_truth: dict[str, Any] | None
    sarvam: dict[str, Any] | None
    direct: dict[str, Any] | None
    sarvam_fields: list[FieldResult] = field(default_factory=list)
    direct_fields: list[FieldResult] = field(default_factory=list)


@dataclass
class EvaluationResult:
    recordings: list[RecordingResult]
    missing_in_sarvam: list[str]
    missing_in_direct: list[str]
    unexpected_in_sarvam: list[str]
    unexpected_in_direct: list[str]
    gt_count: int
    sarvam_count: int
    direct_count: int


def _tokens(text: str) -> set[str]:
    raw = _TOKEN_RE.findall(normalize_text(text))
    out: set[str] = set()
    for t in raw:
        out.add(t)
        # Light plural stemming so fitters≈fitter, bearings≈bearing
        if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
            out.add(t[:-1])
        elif len(t) > 2:
            out.add(t + "s")
    return out


def _exact_norm_equal(a: str, b: str) -> bool:
    return normalize_text(a) == normalize_text(b)


def _semantic_strings_equal(a: str, b: str) -> bool:
    na, nb = normalize_text(a), normalize_text(b)
    if na == nb:
        return True
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return False
    if ta == tb:
        return True
    # Asset-style containment after synonym/ID normalization:
    # "bc15 conveyor" vs "belt conveyor bc15" should match when core IDs/nouns align.
    if ta.issubset(tb) or tb.issubset(ta):
        # Reject if conflicting equipment IDs (e.g. bc15 vs bc16)
        id_a = {t for t in ta if re.fullmatch(r"[a-z]{1,3}\d{1,3}", t)}
        id_b = {t for t in tb if re.fullmatch(r"[a-z]{1,3}\d{1,3}", t)}
        if id_a and id_b and id_a != id_b:
            return False
        return True
    return False


def _string_containment_ratio(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    return inter / max(len(ta), len(tb))


def compare_assets(gt: Any, model: Any) -> str:
    gt_list = assets_as_list(gt)
    model_list = assets_as_list(model)

    if gt_list is None and model_list is None:
        return "CORRECT_NULL"
    if gt_list is None and model_list is not None:
        return "HALLUCINATION"
    if gt_list is not None and model_list is None:
        return "MISSING"

    assert gt_list is not None and model_list is not None

    gt_norms = [normalize_text(x) for x in gt_list]
    model_norms = [normalize_text(x) for x in model_list]

    if gt_norms == model_norms:
        # Exact after safe normalization only (case/whitespace/punct)
        raw_equal = (
            [x.strip().lower() for x in gt_list]
            == [x.strip().lower() for x in model_list]
        )
        return "EXACT_MATCH" if raw_equal or gt_norms == model_norms else "SEMANTIC_MATCH"

    # Pairwise: all GT assets have a semantic match and vice versa
    matched_gt = set()
    matched_model = set()
    exact_pairs = 0
    semantic_pairs = 0
    incorrect_pairs = 0

    for i, g in enumerate(gt_list):
        best_j = -1
        best_score = -1.0
        for j, m in enumerate(model_list):
            if j in matched_model:
                continue
            if _exact_norm_equal(g, m) or _semantic_strings_equal(g, m):
                score = 1.0
            else:
                score = _string_containment_ratio(g, m)
            if score > best_score:
                best_score = score
                best_j = j
        if best_j >= 0 and best_score >= 1.0:
            matched_gt.add(i)
            matched_model.add(best_j)
            if _exact_norm_equal(g, model_list[best_j]) and g.strip().lower() == model_list[best_j].strip().lower():
                exact_pairs += 1
            elif _exact_norm_equal(g, model_list[best_j]) or _semantic_strings_equal(g, model_list[best_j]):
                # Same after normalization → treat as exact/semantic at field level later
                if normalize_text(g) == normalize_text(model_list[best_j]):
                    exact_pairs += 1
                else:
                    semantic_pairs += 1
            else:
                semantic_pairs += 1
        elif best_j >= 0 and best_score >= 0.5:
            # Partial lexical overlap but not identity (e.g. Kiln vs Kiran share tokens)
            # Conflicting asset identity → INCORRECT when core nouns differ
            g_tok, m_tok = _tokens(g), _tokens(model_list[best_j])
            if g_tok != m_tok and not g_tok.issubset(m_tok) and not m_tok.issubset(g_tok):
                incorrect_pairs += 1
                matched_gt.add(i)
                matched_model.add(best_j)
            else:
                matched_gt.add(i)
                matched_model.add(best_j)
                semantic_pairs += 1

    unmatched_gt = len(gt_list) - len(matched_gt)
    unmatched_model = len(model_list) - len(matched_model)

    if incorrect_pairs and unmatched_gt == 0 and unmatched_model == 0 and exact_pairs + semantic_pairs == 0:
        return "INCORRECT"
    if incorrect_pairs and (exact_pairs + semantic_pairs) == 0:
        return "INCORRECT"
    if incorrect_pairs:
        return "PARTIAL_MATCH"
    if unmatched_gt and unmatched_model == 0 and (exact_pairs + semantic_pairs) > 0:
        return "PARTIAL_MATCH"
    if unmatched_model and unmatched_gt == 0 and (exact_pairs + semantic_pairs) > 0:
        # Extra assets not in GT
        return "PARTIAL_MATCH" if (exact_pairs + semantic_pairs) else "HALLUCINATION"
    if unmatched_gt and unmatched_model:
        return "PARTIAL_MATCH" if (exact_pairs + semantic_pairs) else "INCORRECT"
    if exact_pairs == len(gt_list) and unmatched_model == 0:
        return "EXACT_MATCH"
    if (exact_pairs + semantic_pairs) == len(gt_list) and unmatched_model == 0:
        return "SEMANTIC_MATCH"
    if (exact_pairs + semantic_pairs) == 0 and unmatched_model > 0:
        return "INCORRECT"
    return "PARTIAL_MATCH"


def _quantity_core_tokens(text: str) -> set[str]:
    """Tokens that identify a quantity item (numbers, units, specs, nouns)."""
    return _tokens(text)


def _quantities_match(a: str, b: str) -> tuple[str | None, float]:
    """Return (judgment_for_pair, score). judgment None if no usable match."""
    if a.strip() == b.strip():
        return "EXACT_MATCH", 1.0
    if a.strip().lower() == b.strip().lower():
        return "EXACT_MATCH", 1.0
    if normalize_text(a) == normalize_text(b):
        return "SEMANTIC_MATCH", 1.0

    ta, tb = _quantity_core_tokens(a), _quantity_core_tokens(b)
    if not ta or not tb:
        return None, 0.0

    nums_a = {t for t in ta if re.fullmatch(r"\d+(\.\d+)?", t)}
    nums_b = {t for t in tb if re.fullmatch(r"\d+(\.\d+)?", t)}
    content_a = ta - nums_a
    content_b = tb - nums_b

    # Pure number on one side cannot identify an item (e.g. "one" ≠ "1 air filter").
    if not content_a or not content_b:
        if content_a == content_b and nums_a and nums_b and nums_a == nums_b:
            return "SEMANTIC_MATCH", 0.9
        return None, 0.0

    if nums_a and nums_b and nums_a != nums_b and not nums_a.issubset(nums_b) and not nums_b.issubset(nums_a):
        non_num_overlap = content_a & content_b
        if non_num_overlap:
            return "INCORRECT", 0.4
        return None, 0.0

    # Require content-token identity overlap, not mere numeric subset.
    content_overlap = content_a & content_b
    if not content_overlap:
        return None, 0.0

    if content_a == content_b and (not nums_a or not nums_b or nums_a == nums_b):
        return "SEMANTIC_MATCH", 1.0
    if content_a.issubset(content_b) or content_b.issubset(content_a):
        if nums_a and nums_b and nums_a != nums_b:
            return "INCORRECT", 0.4
        # Partial item wording (e.g. "2 bearings" vs "2 6318 C3 bearings")
        ratio = len(content_overlap) / max(len(content_a), len(content_b))
        if ratio >= 0.85 and (not nums_a or not nums_b or nums_a == nums_b):
            return "SEMANTIC_MATCH", ratio
        if ratio >= 0.5 and (not nums_a or not nums_b or nums_a == nums_b):
            return "PARTIAL_MATCH", ratio
        return None, ratio

    inter = ta & tb
    ratio = len(inter) / max(len(ta), len(tb))
    if ratio >= 0.85 and (not nums_a or not nums_b or nums_a == nums_b):
        return "SEMANTIC_MATCH", ratio
    if ratio >= 0.5 and (not nums_a or not nums_b or nums_a == nums_b):
        return "PARTIAL_MATCH", ratio
    return None, ratio


def compare_quantities(gt: Any, model: Any) -> str:
    gt_list = quantities_as_list(gt)
    model_list = quantities_as_list(model)

    if gt_list is None and model_list is None:
        return "CORRECT_NULL"
    if gt_list is None and model_list is not None:
        return "HALLUCINATION"
    if gt_list is not None and model_list is None:
        return "MISSING"

    assert gt_list is not None and model_list is not None

    # Greedy best-match pairing
    used_model: set[int] = set()
    judgments: list[str] = []
    for g in gt_list:
        best_j = -1
        best_kind: str | None = None
        best_score = -1.0
        for j, m in enumerate(model_list):
            if j in used_model:
                continue
            kind, score = _quantities_match(g, m)
            if kind and score > best_score:
                best_score = score
                best_j = j
                best_kind = kind
        if best_j >= 0 and best_kind:
            used_model.add(best_j)
            judgments.append(best_kind)
        else:
            judgments.append("MISSING")

    extra = len(model_list) - len(used_model)
    if extra > 0:
        # Unmatched model quantities
        for j, m in enumerate(model_list):
            if j not in used_model:
                # If GT had nothing overlapping, treat as hallucination extras
                judgments.append("HALLUCINATION")

    if all(j == "EXACT_MATCH" for j in judgments) and extra == 0:
        return "EXACT_MATCH"
    if all(j in ("EXACT_MATCH", "SEMANTIC_MATCH") for j in judgments) and extra == 0:
        return "SEMANTIC_MATCH"
    if all(j == "MISSING" for j in judgments[: len(gt_list)]) and extra == 0:
        return "MISSING"
    if any(j == "INCORRECT" for j in judgments) and not any(
        j in ("EXACT_MATCH", "SEMANTIC_MATCH", "PARTIAL_MATCH") for j in judgments
    ):
        return "INCORRECT"
    if any(j == "HALLUCINATION" for j in judgments) and not any(
        j in ("EXACT_MATCH", "SEMANTIC_MATCH") for j in judgments[: len(gt_list)]
    ):
        if all(j in ("HALLUCINATION", "MISSING") for j in judgments):
            return "HALLUCINATION"
    if any(j in ("MISSING", "INCORRECT", "PARTIAL_MATCH", "HALLUCINATION") for j in judgments):
        if any(j in ("EXACT_MATCH", "SEMANTIC_MATCH", "PARTIAL_MATCH") for j in judgments):
            return "PARTIAL_MATCH"
        if any(j == "INCORRECT" for j in judgments):
            return "INCORRECT"
        if any(j == "MISSING" for j in judgments):
            return "MISSING"
    return "PARTIAL_MATCH"


def _hour_value_equal(a: str, b: str) -> str | None:
    if a.strip() == b.strip():
        return "EXACT_MATCH"
    if a.strip().lower() == b.strip().lower():
        return "EXACT_MATCH"
    if normalize_text(a) == normalize_text(b):
        return "SEMANTIC_MATCH"
    if _semantic_strings_equal(a, b):
        return "SEMANTIC_MATCH"
    ta, tb = _tokens(a), _tokens(b)
    if ta and tb and ta == tb:
        return "SEMANTIC_MATCH"
    nums_a = {t for t in ta if re.fullmatch(r"\d+(\.\d+)?", t)}
    nums_b = {t for t in tb if re.fullmatch(r"\d+(\.\d+)?", t)}
    if nums_a and nums_b and nums_a != nums_b:
        return "INCORRECT"
    if ta & tb:
        return "PARTIAL_MATCH"
    return None


def compare_hours(gt: Any, model: Any) -> str:
    gt_list = hours_as_list(gt)
    model_list = hours_as_list(model)

    if gt_list is None and model_list is None:
        return "CORRECT_NULL"
    if gt_list is None and model_list is not None:
        return "HALLUCINATION"
    if gt_list is not None and model_list is None:
        return "MISSING"

    assert gt_list is not None and model_list is not None

    used_model: set[int] = set()
    pair_judgments: list[str] = []

    for g in gt_list:
        best_j = -1
        best_kind: str | None = None
        wrong_kind_j = -1
        for j, m in enumerate(model_list):
            if j in used_model:
                continue
            g_kind = g["kind"]
            m_kind = m["kind"]
            kind_ok = (
                g_kind == m_kind
                or g_kind == "unspecified"
                or m_kind == "unspecified"
            )
            vj = _hour_value_equal(g["value"], m["value"])
            if vj is None:
                continue
            if not kind_ok:
                # Same numeric duration, different semantic kind → not full credit
                if wrong_kind_j < 0 and vj in ("EXACT_MATCH", "SEMANTIC_MATCH"):
                    wrong_kind_j = j
                continue
            rank = {"EXACT_MATCH": 3, "SEMANTIC_MATCH": 2, "PARTIAL_MATCH": 1, "INCORRECT": 0}
            if best_kind is None or rank.get(vj, -1) > rank.get(best_kind, -1):
                best_kind = vj
                best_j = j
        if best_j >= 0 and best_kind:
            used_model.add(best_j)
            pair_judgments.append(best_kind)
        elif wrong_kind_j >= 0:
            used_model.add(wrong_kind_j)
            pair_judgments.append("PARTIAL_MATCH")
        else:
            pair_judgments.append("MISSING")

    extra = len(model_list) - len(used_model)
    if extra:
        # Remaining model hours: wrong-kind or hallucinated
        for j, m in enumerate(model_list):
            if j in used_model:
                continue
            # If any GT has same value but different kind → do not equate; count as extra/incorrect concept
            conflict = False
            for g in gt_list:
                if g["kind"] != m["kind"] and _hour_value_equal(g["value"], m["value"]) in (
                    "EXACT_MATCH",
                    "SEMANTIC_MATCH",
                ):
                    conflict = True
                    break
                if g["kind"] != m["kind"] and normalize_text(g["value"]) != normalize_text(m["value"]):
                    # unrelated extra hour concept
                    pass
            pair_judgments.append("INCORRECT" if conflict else "HALLUCINATION")

    if all(j == "EXACT_MATCH" for j in pair_judgments) and extra == 0:
        return "EXACT_MATCH"
    if all(j in ("EXACT_MATCH", "SEMANTIC_MATCH") for j in pair_judgments) and extra == 0:
        return "SEMANTIC_MATCH"
    if any(j == "MISSING" for j in pair_judgments) and any(
        j in ("EXACT_MATCH", "SEMANTIC_MATCH") for j in pair_judgments
    ):
        return "PARTIAL_MATCH"
    if any(j in ("MISSING", "INCORRECT", "HALLUCINATION", "PARTIAL_MATCH") for j in pair_judgments):
        if any(j in ("EXACT_MATCH", "SEMANTIC_MATCH", "PARTIAL_MATCH") for j in pair_judgments):
            return "PARTIAL_MATCH"
        if all(j == "MISSING" for j in pair_judgments[: len(gt_list)]):
            return "MISSING"
        if any(j == "INCORRECT" for j in pair_judgments):
            return "INCORRECT"
        if any(j == "HALLUCINATION" for j in pair_judgments):
            return "HALLUCINATION"
    return "PARTIAL_MATCH"


_DAY_NAMES = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    "tomorrow",
    "today",
)

_PERIOD_TOKENS = frozenset({"morning", "evening", "afternoon", "night", "shift"})
_NOTE_HINTS = frozenset(
    {
        "exact",
        "time",
        "process",
        "team",
        "provided",
        "provide",
        "batayegi",
        "bataegi",
        "confirm",
        "maintenance",
        "supervisor",
        "will",
    }
)


def _hour_numbers(tokens: set[str]) -> set[str]:
    hours: set[str] = set()
    for t in tokens:
        if re.fullmatch(r"\d{1,2}", t):
            n = int(t)
            # Ignore 0 from stray ":00" fragments; keep 1–23 clock hours.
            if 1 <= n <= 23:
                hours.add(str(n))
        m = re.fullmatch(r"(\d{1,2}):(\d{2})", t)
        if m:
            hours.add(str(int(m.group(1))))
    return hours


def _date_key_parts(text: str) -> tuple[set[str], set[str], set[str]]:
    """Return (day tokens, period/hour schedule tokens, note tokens)."""
    norm = normalize_text(text)
    toks = set(_TOKEN_RE.findall(norm))
    days = {d for d in _DAY_NAMES if d in toks}
    periods = toks & _PERIOD_TOKENS
    hours = _hour_numbers(toks)
    # AM/PM imply period buckets without forcing mismatch vs morning/afternoon labels
    if "am" in toks:
        periods.add("morning")
    if "pm" in toks:
        # afternoon/evening both acceptable for pm; mark generic pm
        periods.add("afternoon")
    schedule = periods | {f"h{h}" for h in hours}
    notes = toks & _NOTE_HINTS
    return days, schedule, notes


def _schedules_compatible(gt_sched: set[str], model_sched: set[str]) -> bool:
    if gt_sched == model_sched:
        return True
    # Same clock hour with morning vs am-derived morning
    gt_hours = {t for t in gt_sched if t.startswith("h")}
    model_hours = {t for t in model_sched if t.startswith("h")}
    gt_periods = gt_sched - gt_hours
    model_periods = model_sched - model_hours
    if gt_hours and model_hours and gt_hours != model_hours:
        return False
    if gt_hours == model_hours:
        if not gt_periods or not model_periods:
            return True
        if gt_periods & model_periods:
            return True
        # morning vs empty when hour present is OK
        return False
    if not gt_hours and not model_hours:
        return bool(gt_periods & model_periods) or gt_periods == model_periods
    return False


def compare_dates(gt: Any, model: Any) -> str:
    gt_list = dates_as_list(gt)
    model_list = dates_as_list(model)

    if gt_list is None and model_list is None:
        return "CORRECT_NULL"
    if gt_list is None and model_list is not None:
        return "HALLUCINATION"
    if gt_list is not None and model_list is None:
        return "MISSING"

    assert gt_list is not None and model_list is not None

    gt_joined = " ".join(gt_list)
    model_joined = " ".join(model_list)

    if gt_joined.strip() == model_joined.strip():
        return "EXACT_MATCH"
    if gt_joined.strip().lower() == model_joined.strip().lower():
        return "EXACT_MATCH"
    if normalize_text(gt_joined) == normalize_text(model_joined):
        return "SEMANTIC_MATCH"

    gt_days, gt_sched, gt_notes = _date_key_parts(gt_joined)
    model_days, model_sched, model_notes = _date_key_parts(model_joined)

    if not gt_days and not model_days and not gt_sched and not model_sched:
        if _semantic_strings_equal(gt_joined, model_joined):
            return "SEMANTIC_MATCH"
        return "INCORRECT"

    days_ok = gt_days == model_days or (gt_days & model_days and not (gt_days - model_days) and not (model_days - gt_days))
    if not days_ok:
        if gt_days and model_days and not (gt_days & model_days):
            return "INCORRECT"
        if gt_days != model_days:
            return "PARTIAL_MATCH"

    sched_ok = _schedules_compatible(gt_sched, model_sched)
    gt_has_time = bool({t for t in gt_sched if t.startswith("h")} or (gt_sched & _PERIOD_TOKENS))
    model_has_time = bool({t for t in model_sched if t.startswith("h")} or (model_sched & _PERIOD_TOKENS))

    # Lost explicit time-of-day / clock while day matches
    if days_ok and gt_has_time and not model_has_time:
        return "PARTIAL_MATCH"
    if days_ok and not sched_ok:
        return "PARTIAL_MATCH"

    # Explicit process-team / exact-time note omitted
    gt_has_note = bool(gt_notes & {"exact", "process", "team", "provided", "confirm", "maintenance"})
    model_has_note = bool(model_notes & {"exact", "process", "team", "provided", "confirm", "maintenance"})
    if days_ok and sched_ok and gt_has_note and not model_has_note:
        return "PARTIAL_MATCH"
    if days_ok and sched_ok:
        return "SEMANTIC_MATCH"
    return "PARTIAL_MATCH"


_APPROVAL_HINTS = re.compile(
    r"\b(approv|permission|permit|मंजूरी|अनुमति)\w*\b",
    re.I,
)


def compare_approval(gt: Any, model: Any) -> str:
    gt_text = approval_as_text(gt)
    model_text = approval_as_text(model)

    if gt_text is None and model_text is None:
        return "CORRECT_NULL"
    if gt_text is None and model_text is not None:
        # Model invents approval when GT has none
        return "HALLUCINATION"
    if gt_text is not None and model_text is None:
        return "MISSING"

    assert gt_text is not None and model_text is not None

    if gt_text == model_text:
        return "EXACT_MATCH"
    if gt_text.lower() == model_text.lower():
        return "EXACT_MATCH"
    if normalize_text(gt_text) == normalize_text(model_text):
        return "SEMANTIC_MATCH"
    if _semantic_strings_equal(gt_text, model_text):
        return "SEMANTIC_MATCH"

    gt_has = bool(_APPROVAL_HINTS.search(gt_text))
    model_has = bool(_APPROVAL_HINTS.search(model_text))
    if gt_has and model_has:
        ratio = _string_containment_ratio(gt_text, model_text)
        if ratio >= 0.5:
            return "PARTIAL_MATCH" if ratio < 0.85 else "SEMANTIC_MATCH"
        return "INCORRECT"
    if not gt_has and model_has:
        return "HALLUCINATION"
    if gt_has and not model_has:
        return "INCORRECT"
    return "INCORRECT"


COMPARERS = {
    "assets": compare_assets,
    "quantities": compare_quantities,
    "hours": compare_hours,
    "dates": compare_dates,
    "approval_intent": compare_approval,
}


def _validate_record(record: dict[str, Any], filename: str, source: str) -> None:
    missing = [p for p in PARAMETERS if p not in record]
    if missing:
        raise RuntimeError(
            f"{source} record {filename!r} missing parameters: {', '.join(missing)}"
        )


def compare_record_fields(
    gt_record: dict[str, Any] | None,
    model_record: dict[str, Any] | None,
    *,
    model_absent: bool = False,
) -> list[FieldResult]:
    results: list[FieldResult] = []
    for param in PARAMETERS:
        gt_val = None if gt_record is None else gt_record.get(param)
        if model_absent or model_record is None:
            results.append(
                FieldResult(
                    parameter=param,
                    ground_truth=gt_val,
                    model_value=None,
                    judgment="MISSING",
                )
            )
            continue
        model_val = model_record.get(param)
        judgment = COMPARERS[param](gt_val, model_val)
        results.append(
            FieldResult(
                parameter=param,
                ground_truth=gt_val,
                model_value=model_val,
                judgment=judgment,
            )
        )
    return results


def evaluate(
    ground_truth: dict[str, Any],
    sarvam: dict[str, Any],
    direct: dict[str, Any],
) -> EvaluationResult:
    if not isinstance(ground_truth, dict):
        raise RuntimeError("Ground Truth JSON must be an object keyed by filename")
    if not isinstance(sarvam, dict):
        raise RuntimeError("Sarvam + Gemini JSON must be an object keyed by filename")
    if not isinstance(direct, dict):
        raise RuntimeError("Direct Gemini JSON must be an object keyed by filename")

    gt_keys = set(ground_truth.keys())
    sarvam_keys = set(sarvam.keys())
    direct_keys = set(direct.keys())

    missing_in_sarvam = sorted(gt_keys - sarvam_keys)
    missing_in_direct = sorted(gt_keys - direct_keys)
    unexpected_in_sarvam = sorted(sarvam_keys - gt_keys)
    unexpected_in_direct = sorted(direct_keys - gt_keys)

    recordings: list[RecordingResult] = []
    for filename in sorted(gt_keys):
        gt_rec = ground_truth[filename]
        if not isinstance(gt_rec, dict):
            raise RuntimeError(f"Ground Truth record {filename!r} must be an object")
        _validate_record(gt_rec, filename, "Ground Truth")

        sarvam_rec = sarvam.get(filename)
        direct_rec = direct.get(filename)

        if sarvam_rec is not None:
            if not isinstance(sarvam_rec, dict):
                raise RuntimeError(f"Sarvam record {filename!r} must be an object")
            _validate_record(sarvam_rec, filename, "Sarvam + Gemini")
        if direct_rec is not None:
            if not isinstance(direct_rec, dict):
                raise RuntimeError(f"Direct Gemini record {filename!r} must be an object")
            _validate_record(direct_rec, filename, "Direct Gemini")

        rec = RecordingResult(
            filename=filename,
            ground_truth=gt_rec,
            sarvam=sarvam_rec if isinstance(sarvam_rec, dict) else None,
            direct=direct_rec if isinstance(direct_rec, dict) else None,
            sarvam_fields=compare_record_fields(
                gt_rec,
                sarvam_rec if isinstance(sarvam_rec, dict) else None,
                model_absent=filename in missing_in_sarvam,
            ),
            direct_fields=compare_record_fields(
                gt_rec,
                direct_rec if isinstance(direct_rec, dict) else None,
                model_absent=filename in missing_in_direct,
            ),
        )
        recordings.append(rec)

    return EvaluationResult(
        recordings=recordings,
        missing_in_sarvam=missing_in_sarvam,
        missing_in_direct=missing_in_direct,
        unexpected_in_sarvam=unexpected_in_sarvam,
        unexpected_in_direct=unexpected_in_direct,
        gt_count=len(gt_keys),
        sarvam_count=len(sarvam_keys),
        direct_count=len(direct_keys),
    )


def accuracy_from_judgments(judgments: list[str]) -> float:
    if not judgments:
        return 0.0
    correct = sum(1 for j in judgments if j in CORRECT_JUDGMENTS)
    return round(100.0 * correct / len(judgments), 2)


def count_judgments(judgments: list[str]) -> dict[str, int]:
    counts = {j: 0 for j in JUDGMENTS}
    for j in judgments:
        counts[j] = counts.get(j, 0) + 1
    return counts


def collect_model_judgments(result: EvaluationResult, model: str) -> list[str]:
    out: list[str] = []
    for rec in result.recordings:
        fields = rec.sarvam_fields if model == MODEL_SARVAM else rec.direct_fields
        out.extend(f.judgment for f in fields)
    return out


def collect_parameter_judgments(
    result: EvaluationResult, model: str, parameter: str
) -> list[str]:
    out: list[str] = []
    for rec in result.recordings:
        fields = rec.sarvam_fields if model == MODEL_SARVAM else rec.direct_fields
        for f in fields:
            if f.parameter == parameter:
                out.append(f.judgment)
    return out


def display_value(value: Any) -> str:
    return format_value(value)


CORRECT_SET = CORRECT_JUDGMENTS


def attribute_errors(result: EvaluationResult) -> dict[str, Any]:
    """Heuristic STT vs extraction attribution without stored transcripts.

    Rule (documented in report):
    - Sarvam wrong, Direct correct → likely_stt_error (Direct recovered from audio)
    - Sarvam correct, Direct wrong → direct_extraction_error
    - Both wrong → both_pipelines_error
    - Both correct → none
    """
    counts = {
        "likely_stt_error": 0,
        "direct_extraction_error": 0,
        "both_pipelines_error": 0,
        "both_correct": 0,
    }
    examples: list[dict[str, str]] = []
    for rec in result.recordings:
        for s_field, d_field in zip(rec.sarvam_fields, rec.direct_fields):
            s_ok = s_field.judgment in CORRECT_JUDGMENTS
            d_ok = d_field.judgment in CORRECT_JUDGMENTS
            if s_ok and d_ok:
                counts["both_correct"] += 1
                continue
            if (not s_ok) and d_ok:
                counts["likely_stt_error"] += 1
                if len(examples) < 25:
                    examples.append(
                        {
                            "filename": rec.filename,
                            "parameter": s_field.parameter,
                            "attribution": "likely_stt_error",
                            "sarvam_judgment": s_field.judgment,
                            "direct_judgment": d_field.judgment,
                        }
                    )
            elif s_ok and (not d_ok):
                counts["direct_extraction_error"] += 1
                if len(examples) < 25:
                    examples.append(
                        {
                            "filename": rec.filename,
                            "parameter": s_field.parameter,
                            "attribution": "direct_extraction_error",
                            "sarvam_judgment": s_field.judgment,
                            "direct_judgment": d_field.judgment,
                        }
                    )
            else:
                counts["both_pipelines_error"] += 1
                if len(examples) < 25:
                    examples.append(
                        {
                            "filename": rec.filename,
                            "parameter": s_field.parameter,
                            "attribution": "both_pipelines_error",
                            "sarvam_judgment": s_field.judgment,
                            "direct_judgment": d_field.judgment,
                        }
                    )
    return {"counts": counts, "examples": examples}


def correct_count(judgments: list[str]) -> tuple[int, int]:
    """Return (correct, total) where correct = EXACT/SEMANTIC/CORRECT_NULL."""
    total = len(judgments)
    correct = sum(1 for j in judgments if j in CORRECT_JUDGMENTS)
    return correct, total
