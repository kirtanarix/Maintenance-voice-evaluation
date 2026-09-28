"""Safe, deterministic normalization for Agent 4 field comparison."""

from __future__ import annotations

import re
from typing import Any

# Longer phrases first so multi-word forms win over single tokens.
_NUMBER_WORDS: tuple[tuple[str, str], ...] = (
    ("one and a half", "1.5"),
    ("one-and-a-half", "1.5"),
    ("twenty one", "21"),
    ("twenty two", "22"),
    ("twenty three", "23"),
    ("twenty four", "24"),
    ("twenty five", "25"),
    ("half a kilo", "0.5 kg"),
    ("half kilo", "0.5 kg"),
    ("half a kg", "0.5 kg"),
    ("half kg", "0.5 kg"),
    ("a half", "0.5"),
    ("one half", "0.5"),
    ("ninety", "90"),
    ("half", "0.5"),
    ("zero", "0"),
    ("one", "1"),
    ("two", "2"),
    ("three", "3"),
    ("four", "4"),
    ("five", "5"),
    ("six", "6"),
    ("seven", "7"),
    ("eight", "8"),
    ("nine", "9"),
    ("ten", "10"),
    ("eleven", "11"),
    ("twelve", "12"),
    ("thirteen", "13"),
    ("fourteen", "14"),
    ("fifteen", "15"),
    ("sixteen", "16"),
    ("seventeen", "17"),
    ("eighteen", "18"),
    ("nineteen", "19"),
    ("twenty", "20"),
    # Hindi numerals commonly appearing in assets/dates
    ("साढ़े", "0.5plus"),  # handled specially with following number for clocks
    ("डेढ़", "1.5"),
    ("आधा", "0.5"),
    ("ग्यारह", "11"),
    ("बारह", "12"),
    ("एक", "1"),
    ("दो", "2"),
    ("तीन", "3"),
    ("चार", "4"),
    ("पांच", "5"),
    ("पाँच", "5"),
    ("छह", "6"),
    ("सात", "7"),
    ("आठ", "8"),
    ("नौ", "9"),
    ("दस", "10"),
)

_HINDI_DAYS = {
    "सोमवार": "monday",
    "मंगलवार": "tuesday",
    "बुधवार": "wednesday",
    "गुरुवार": "thursday",
    "शुक्रवार": "friday",
    "शनिवार": "saturday",
    "रविवार": "sunday",
}

# Bilingual equipment/common-word synonyms for asset comparison.
_SYNONYMS: tuple[tuple[str, str], ...] = (
    ("this afternoon", "today afternoon"),
    ("this evening", "today evening"),
    ("this morning", "today morning"),
    ("this night", "today night"),
    ("this shift", "today shift"),
    ("सीमेंट", "cement"),
    ("मिल", "mill"),
    ("मोटर", "motor"),
    ("कन्वेयर", "conveyor"),
    ("कॉन्वेयर", "conveyor"),
    ("बेल्ट", "belt"),
    ("फीडर", "feeder"),
    ("पंप", "pump"),
    ("बेयरिंग", "bearing"),
    ("फ़ैन", "fan"),
    ("फैन", "fan"),
    ("किलन", "kiln"),
    ("पैकिंग", "packing"),
    ("मशीन", "machine"),
    ("नंबर", "number"),
    ("रॉ", "raw"),
    ("क्लिंकर", "clinker"),
    ("गियरबॉक्स", "gearbox"),
    ("कपलिंग", "coupling"),
    ("स्लरी", "slurry"),
    ("बॉयलर", "boiler"),
    ("कल", "tomorrow"),
    ("आज", "today"),
    ("सुबह", "morning"),
    ("शाम", "evening"),
    ("दोपहर", "afternoon"),
    ("रात", "night"),
)

# ASCII punctuation only — Python \w does not keep Devanagari matras, so a
# Unicode "non-word" strip would shatter Hindi syllables.
_ASCII_PUNCT_RE = re.compile(r"[!\"#$&'()*+,;<=>?@\[\]^_`{|}~]+")
_WS_RE = re.compile(r"\s+")
_DECIMAL_TRAILING_ZERO_RE = re.compile(r"\b(\d+)\.0+\b")
_POSSESSIVE_RE = re.compile(r"\b(\w+)'s\b", re.I)
_HYPHENATED_HOUR_RE = re.compile(r"\b(\d+(?:\.\d+)?)-hours?\b", re.I)

# Words that must never be treated as equipment-ID prefixes (e.g. "at 10").
_EQUIP_PREFIX_BLOCKLIST = frozenset(
    {
        "at",
        "am",
        "pm",
        "to",
        "for",
        "of",
        "on",
        "in",
        "by",
        "or",
        "an",
        "no",
        "as",
        "is",
        "up",
        "do",
        "if",
        "we",
        "me",
        "my",
        "it",
        "vs",
    }
)
# Prefer hyphenated IDs and compact alnum forms; allow spaced "BC 15".
_EQUIP_ID_RE = re.compile(r"\b([a-z]{1,4})(?:-|[\s]+)(\d{1,4})\b", re.I)
_EQUIP_COMPACT_RE = re.compile(r"\b([a-z]{1,4})(\d{2,4})\b", re.I)

_FILLER_WORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "of",
        "and",
        "to",
        "for",
        "with",
        "in",
        "on",
        "at",
        "by",
        "from",
        "का",
        "की",
        "के",
        "में",
        "से",
        "को",
        "है",
        "हैं",
        "जो",
        "पर",
    }
)


def normalize_equipment_ids(text: str) -> str:
    """Normalize equipment IDs: BC-15 / BC 15 / bc15 → bc15."""

    def repl(match: re.Match[str]) -> str:
        prefix = match.group(1).lower()
        if prefix in _EQUIP_PREFIX_BLOCKLIST:
            return match.group(0)
        return f"{prefix}{match.group(2)}"

    text = _EQUIP_ID_RE.sub(repl, text)

    def compact(match: re.Match[str]) -> str:
        prefix = match.group(1).lower()
        if prefix in _EQUIP_PREFIX_BLOCKLIST:
            return match.group(0)
        return f"{prefix}{match.group(2)}"

    return _EQUIP_COMPACT_RE.sub(compact, text)


def normalize_time_tokens(text: str) -> str:
    """Normalize clock/time-of-day forms toward comparable tokens."""
    # "nine in the morning" / "9 in the morning" → "9 am"
    text = re.sub(
        r"\b(\d{1,2})\s+in\s+the\s+morning\b",
        r"\1 am",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"\b(\d{1,2})\s+in\s+the\s+(?:evening|afternoon)\b",
        r"\1 pm",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"\b(\d{1,2})\s+in\s+the\s+night\b",
        r"\1 pm",
        text,
        flags=re.I,
    )

    # Keep colon forms intact until rewritten.
    text = re.sub(r"\b(\d{1,2}):00\s*(a\.?m\.?|am)\b", r"\1 am", text, flags=re.I)
    text = re.sub(r"\b(\d{1,2}):00\s*(p\.?m\.?|pm)\b", r"\1 pm", text, flags=re.I)
    # Bare HH:00 → hour token (period may come from surrounding "morning")
    text = re.sub(r"\b(\d{1,2}):00\b", r"\1", text)
    text = re.sub(r"\b(\d{1,2})\.00\b", r"\1", text)
    text = re.sub(r"\b(\d{1,2}):(\d{2})\b", r"\1:\2", text)

    text = re.sub(r"\b(\d{1,2})\s*a\.?m\.?\b", r"\1 am", text, flags=re.I)
    text = re.sub(r"\b(\d{1,2})\s*p\.?m\.?\b", r"\1 pm", text, flags=re.I)
    # "morning 11" / "11 morning" already covered by schedule logic; keep am/pm
    text = re.sub(r"\bnoon\b", "12 pm", text, flags=re.I)
    text = re.sub(r"\bmidnight\b", "12 am", text, flags=re.I)
    return text


def normalize_text(value: str) -> str:
    """Lowercase, trim, collapse whitespace, map numbers/units/IDs/synonyms."""
    text = value.strip().lower()
    text = _POSSESSIVE_RE.sub(r"\1", text)
    text = _WS_RE.sub(" ", text)

    # Hindi/English phrase synonyms BEFORE any punctuation work so Devanagari
    # matras are not lost (Python \w does not retain them).
    for src, dst in sorted(_SYNONYMS, key=lambda x: -len(x[0])):
        text = text.replace(src.lower(), dst)
    for hindi, english in _HINDI_DAYS.items():
        text = text.replace(hindi, english)

    text = _HYPHENATED_HOUR_RE.sub(r"\1 hours", text)
    text = re.sub(r"\b(\d+(?:\.\d+)?)-hour\b", r"\1 hours", text, flags=re.I)

    for word, digit in _NUMBER_WORDS:
        if word == "साढ़े":
            continue
        text = re.sub(rf"\b{re.escape(word)}\b", digit, text)

    text = re.sub(r"साढ़े\s+(\d+(?:\.\d+)?)", lambda m: str(float(m.group(1)) + 0.5), text)

    # Time forms while colon / a.m. punctuation still present.
    text = normalize_time_tokens(text)

    # Strip ASCII punctuation only (preserve Unicode script text).
    text = _ASCII_PUNCT_RE.sub(" ", text)
    # Parenthetical Hindi notes often use () already stripped; collapse leftover dashes
    # used as separators but keep hyphenated equipment via prior ID pass after.
    text = text.replace("(", " ").replace(")", " ")
    text = _WS_RE.sub(" ", text).strip()

    text = _DECIMAL_TRAILING_ZERO_RE.sub(r"\1", text)
    text = re.sub(r"\bkilograms?\b", "kg", text)
    text = re.sub(r"\bkilos?\b", "kg", text)
    text = re.sub(r"\bhrs?\b", "hours", text)
    text = re.sub(r"\bhour\b", "hours", text)
    text = re.sub(r"\bminutes?\b", "minutes", text)
    text = re.sub(r"\bliters?\b", "liters", text)
    text = re.sub(r"\blitres?\b", "liters", text)
    text = re.sub(r"\bलीटर\b", "liters", text)

    text = normalize_equipment_ids(text)

    tokens = [t for t in text.split() if t not in _FILLER_WORDS]
    text = " ".join(tokens)
    text = _WS_RE.sub(" ", text).strip()
    return text


def is_null(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    return False


def format_value(value: Any) -> str:
    """Human-readable display for report cells."""
    if value is None:
        return "null"
    if isinstance(value, str):
        return value if value.strip() else "null"
    if isinstance(value, list):
        if not value:
            return "null"
        parts: list[str] = []
        for item in value:
            if isinstance(item, dict):
                kind = item.get("kind", "")
                val = item.get("value", "")
                parts.append(f"{kind}: {val}" if kind else str(val))
            else:
                parts.append(str(item))
        return "; ".join(parts)
    if isinstance(value, dict):
        kind = value.get("kind", "")
        val = value.get("value", "")
        return f"{kind}: {val}" if kind else str(value)
    return str(value)


def assets_as_list(value: Any) -> list[str] | None:
    if is_null(value):
        return None
    if isinstance(value, str):
        return [value.strip()] if value.strip() else None
    if isinstance(value, list):
        items = [str(x).strip() for x in value if str(x).strip()]
        return items or None
    return [str(value).strip()]


def quantities_as_list(value: Any) -> list[str] | None:
    if is_null(value):
        return None
    if isinstance(value, str):
        return [value.strip()] if value.strip() else None
    if isinstance(value, list):
        items = [str(x).strip() for x in value if not is_null(x)]
        return items or None
    return [str(value).strip()]


def hours_as_list(value: Any) -> list[dict[str, str]] | None:
    """Normalize hours to list of {kind, value} dicts."""
    if is_null(value):
        return None
    items: list[dict[str, str]] = []
    raw = value if isinstance(value, list) else [value]
    for item in raw:
        if is_null(item):
            continue
        if isinstance(item, dict):
            kind = str(item.get("kind") or "").strip().lower()
            val = str(item.get("value") or "").strip()
            if not val and "duration" in item:
                val = str(item["duration"]).strip()
            items.append({"kind": kind or "unspecified", "value": val})
        else:
            items.append({"kind": "unspecified", "value": str(item).strip()})
    return items or None


def dates_as_list(value: Any) -> list[str] | None:
    if is_null(value):
        return None
    if isinstance(value, str):
        return [value.strip()] if value.strip() else None
    if isinstance(value, list):
        items = [str(x).strip() for x in value if not is_null(x)]
        return items or None
    return [str(value).strip()]


def approval_as_text(value: Any) -> str | None:
    if is_null(value):
        return None
    if isinstance(value, str):
        return value.strip() or None
    return str(value).strip() or None
