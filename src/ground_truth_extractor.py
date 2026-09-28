"""Deterministic Ground Truth extraction from human-verified raw spoken text (Agent 3).

Faithfully maps ALL explicitly spoken facts into the five fixed parameters.
Does not summarize away detail. Applies speaker self-corrections.
"""

from __future__ import annotations

import re
from typing import Any

from src.schema import MaintenanceExtraction

# Spoken numerals → digits (longer phrases first).
_NUMERAL_WORDS: tuple[tuple[str, str], ...] = (
    ("साढ़े", "7.5"),
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
    ("eleven", "11"),
    ("twelve", "12"),
    ("thirteen", "13"),
    ("fourteen", "14"),
    ("fifteen", "15"),
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
    ("half", "0.5"),
)

_NON_ASSET_KE_LIYE_PREFIXES = frozenset(
    {
        "replacement",
        "repair",
        "inspection",
        "maintenance",
        "plan",
    }
)

_APPROVAL_PATTERNS = (
    re.compile(r"\b(approval|permission|permit)\b", re.I),
    re.compile(r"\b(अनुमति|मंजूरी)\b", re.I),
    re.compile(r"\bapproval\s+required\b", re.I),
    re.compile(r"\bpermission\s+(chahiye|required|ke\s+bina)\b", re.I),
    re.compile(r"\b(ki\s+)?permission\s+(chahiye|required)\b", re.I),
    re.compile(r"permission\s+ke\s+bina", re.I),
    re.compile(r"approval\s+ke\s+bina", re.I),
)

_HINDI_DAYS = {
    "सोमवार": "Monday",
    "मंगलवार": "Tuesday",
    "बुधवार": "Wednesday",
    "गुरुवार": "Thursday",
    "शुक्रवार": "Friday",
    "शनिवार": "Saturday",
    "रविवार": "Sunday",
}

_ENGLISH_DAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)

_ROLE_SINGULAR = {
    "fitters": "fitter",
    "helpers": "helper",
    "electricians": "electrician",
    "engineers": "engineer",
    "technicians": "technician",
    "welders": "welder",
    "supervisors": "supervisor",
    "hydraulic technicians": "hydraulic technician",
    "mechanical fitters": "mechanical fitter",
    "mechanical engineers": "mechanical engineer",
}

_NUMERAL_WORD_SET = {w.lower() for w, _ in _NUMERAL_WORDS}


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _number_pattern() -> str:
    words = "|".join(re.escape(w) for w, _ in _NUMERAL_WORDS)
    return rf"(?:\d+(?:\.\d+)?|{words})"


def _parse_spoken_number(token: str) -> str | None:
    token = token.strip().lower()
    if re.fullmatch(r"\d+(\.\d+)?", token):
        return token
    for word, digit in _NUMERAL_WORDS:
        if token == word.lower() or token == word:
            return digit
    return None


def _format_hours_value(count: str) -> str:
    return f"{count} hour" if count == "1" else f"{count} hours"


def _role_label(raw: str, count: str) -> str:
    role = _normalize_whitespace(raw).lower()
    singular = _ROLE_SINGULAR.get(
        role,
        role[:-1] if role.endswith("s") and not role.endswith("ss") else role,
    )
    plurals = {
        "fitter": "fitters",
        "helper": "helpers",
        "electrician": "electricians",
        "engineer": "engineers",
        "technician": "technicians",
        "welder": "welders",
        "supervisor": "supervisors",
        "hydraulic technician": "hydraulic technicians",
        "mechanical fitter": "mechanical fitters",
        "mechanical engineer": "mechanical engineers",
    }
    if singular in plurals:
        return singular if count == "1" else plurals[singular]
    return role


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------


def _extract_assets(text: str) -> str | list[str] | None:
    assets: list[str] = []

    def add(candidate: str | None) -> None:
        if not candidate:
            return
        candidate = _normalize_whitespace(candidate)
        candidate = re.sub(
            r"\s+(का|की|के|से|में|को|for|needs|need)\s*$",
            "",
            candidate,
            flags=re.I,
        )
        if not candidate:
            return
        key = candidate.lower()
        if key in _NON_ASSET_KE_LIYE_PREFIXES:
            return
        if any(a.lower() == key for a in assets):
            return
        for existing in list(assets):
            if key in existing.lower() and key != existing.lower():
                return
            if existing.lower() in key and key != existing.lower():
                assets.remove(existing)
        assets.append(candidate)

    # "X के लिए" — skip purpose/manpower clauses.
    for match in re.finditer(r"([^।.!?,]+?)\s+के\s+लिए", text, re.I):
        candidate = _normalize_whitespace(match.group(1))
        candidate = re.split(r"[;:]", candidate)[-1].strip()
        if re.search(
            r"(fitter|engineer|technician|welder|electrician|helper|"
            r"फिटर|घंटे|hours?|\binspection\b)",
            candidate,
            re.I,
        ):
            continue
        first_token = candidate.lower().split()[0] if candidate.split() else ""
        if first_token in _NON_ASSET_KE_LIYE_PREFIXES or candidate.lower() in _NON_ASSET_KE_LIYE_PREFIXES:
            continue
        add(candidate)

    id_patterns = (
        r"(motor\s+of\s+conveyor\s+[A-Z]{1,3}-?\d+)",
        r"((?:Belt\s+)?conveyor\s+[A-Z]{1,3}-?\d+)",
        r"(conveyor\s+number\s+\w+)",
        r"(bucket\s+elevator\s+[A-Z]{1,3}-?\d+)",
        r"(Bucket\s+elevator\s+नंबर\s+\S+)",
        r"(cooling\s+water\s+pump\s+number\s+\w+)",
        r"(cooling\s+tower\s+fan)",
        r"(compressor\s+number\s+\w+)",
        r"(Compressor\s+नंबर\s+\S+)",
        r"(Raw\s+water\s+pump\s+नंबर\s+\S+)",
        r"(raw\s+water\s+pump\s+number\s+\w+)",
        r"(Packing\s+machine\s+number\s+\w+(?:\s+का\s+pneumatic\s+valve)?)",
        r"(clinker\s+cooler\s+fan)",
        r"(clinker\s+cooler\s+motor)",
        r"(raw\s+mill\s+feeder)",
        r"(Raw\s+mill\s+hydraulic\s+pump)",
        r"(Kiln\s+ID\s+fan)",
        r"(Kiln\s+inlet\s+fan)",
        r"(Kiln\s+auxiliary\s+drive)",
        r"(Kiln\s+burner)",
        r"(Kiln\s+main\s+drive)",
        r"(Cement\s+mill\s+separator)",
        r"(Cement\s+mill\s+gearbox)",
        r"(Cement\s+mill\s+की\s+chute\s+liner)",
        r"(Cement\s+mill\s+की\s+lubrication\s+line)",
        r"(Packing\s+plant\s+की\s+conveyor\s+[A-Z]{1,3}-?\d+(?:\s+का\s+motor)?)",
        r"(Packing\s+plant\s+के\s+screw\s+conveyor)",
        r"(Conveyor\s+CV-?\d+\s+के\s+tail\s+pulley)",
        r"(conveyor\s+[A-Z]{1,3}-?\d+(?:\s+का\s+motor)?)",
        r"(सीमेंट\s+मिल\s+नंबर\s+\S+\s+के\s+मोटर)",
        r"(क्लिंकर\s+बेल्ट\s+कन्वेयर)",
        r"(रॉ\s+मिल\s+के\s+फीडर)",
        r"(पैकिंग\s+मशीन\s+नंबर\s+\S+)",
        r"(gearbox\s+of\s+bucket\s+elevator\s+[A-Z]{1,3}-?\d+)",
        r"(छोटी\s+slurry\s+pump)",
        r"(Crusher\s+area\s+[^।.]{0,40}?slurry\s+pump)",
        r"(Crusher\s+की\s+discharge\s+chute)",
        r"(बड़ा\s+exhaust\s+fan)",
        r"(Workshop\s+के\s+पास\s+जो\s+बड़ा\s+exhaust\s+fan)",
        r"(hydraulic\s+cylinder\s+on\s+the\s+roller\s+press)",
        r"(bag\s+filter\s+fan)",
        r"(Raw\s+mill\s+fan)",
        r"(Packing\s+conveyor\s+[A-Z]{1,3}-?\d+)",
        r"(small\s+pump\s+near\s+the\s+clinker\s+cooler)",
        r"(handrail\s+near\s+the\s+kiln\s+platform)",
        r"(damaged\s+handrail\s+near\s+the\s+kiln\s+platform)",
        r"(Crusher\s+number\s+\w+)",
        r"(cement\s+mill\s+lubrication\s+system)",
        r"(Packing\s+plant\s+की\s+motor\s+starter\s+panel)",
        r"(Raw\s+mill\s+conveyor)",
        r"(kiln\s+hydraulic\s+system)",
        r"(Boiler\s+feed\s+pump)",
        r"(Cooling\s+tower\s+pump)",
        r"(Cement\s+mill\s+fan)",
        r"(Bucket\s+elevator\s+BE-?\d+\s+के\s+head\s+pulley)",
        r"(head\s+pulley\s+of\s+bucket\s+elevator\s+BE-?\d+)",
    )
    for pattern in id_patterns:
        for match in re.finditer(pattern, text, re.I):
            add(match.group(1))

    for match in re.finditer(
        r"((?:सीमेंट|Cement|रॉ|Raw|पैकिंग|Packing|Kiln|Belt|क्लिंकर|"
        r"Bucket|bucket|Crusher|Compressor|Workshop|Conveyor|Cooling|Boiler)[^।.?]{0,50}?)\s+"
        r"(?:का|की|के)\s+"
        r"(?:बेयरिंग|bearing|सील|seal|मोटर|motor|फीडर|feeder|guard|"
        r"filter|inspection|lubrication|chain|chute\s+liner|belt|"
        r"discharge\s+chute|pneumatic\s+valve|gearbox|"
        r"coupling|servicing|heater\s+wiring|gearbox\s+oil\s+change|"
        r"air\s+filter|maintenance|belt\s+replacement|belt\s+alignment)",
        text,
        re.I,
    ):
        add(match.group(1))

    # English "… on the <asset>" / "… of the <asset>"
    for match in re.finditer(
        r"(?:bearing|seal|coupling|guard|belt)\s+on\s+the\s+"
        r"((?:clinker\s+cooler\s+motor|[^.,।]{3,60}?motor))",
        text,
        re.I,
    ):
        add(match.group(1))
    for match in re.finditer(
        r"(?:servicing|preventive\s+servicing)\s+of\s+(?:the\s+)?"
        r"((?:raw\s+water\s+pump\s+number\s+\w+|[^.,।]{3,60}))",
        text,
        re.I,
    ):
        add(match.group(1))

    if not assets:
        return None
    if len(assets) == 1:
        return assets[0]
    return assets


# ---------------------------------------------------------------------------
# Quantities
# ---------------------------------------------------------------------------


def _extract_quantities(text: str) -> list[str] | None:
    num = _number_pattern()
    spans: list[tuple[int, int, str]] = []

    def add_at(start: int, end: int, item: str) -> None:
        item = _normalize_whitespace(item)
        if item:
            spans.append((start, end, item))

    for match in re.finditer(
        rf"\b({num})\s+(\d{{3,5}}(?:\s+C\d+)?(?:\s+spherical\s+roller)?)\s+(?:bearings?|बेयरिंग)",
        text,
        re.I,
    ):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        spec = _normalize_whitespace(match.group(2))
        label = "bearing" if count == "1" else "bearings"
        add_at(match.start(), match.end(), f"{count} {spec} {label}")

    split_bearing = re.search(
        rf"(?:Replace\s+)?({num})\s+bearings?\b.{{0,100}}?"
        rf"(?:bearings?\s+are|bearing\s+is|दोनों\s+bearing|bearing\s+number)\s+"
        rf"(\d{{3,5}}(?:\s*C\d+)?)",
        text,
        re.I | re.S,
    )
    if split_bearing:
        count = _parse_spoken_number(split_bearing.group(1)) or split_bearing.group(1)
        spec = _normalize_whitespace(split_bearing.group(2))
        add_at(split_bearing.start(), split_bearing.end(), f"{count} {spec} bearings")

    # "दोनों bearing 22218 हैं" with count from earlier "दो bearings"
    both_bearing = re.search(
        rf"({num})\s+bearings?.{{0,80}}?दोनों\s+bearing\s+(\d{{3,5}})",
        text,
        re.I | re.S,
    )
    if both_bearing:
        count = _parse_spoken_number(both_bearing.group(1)) or both_bearing.group(1)
        spec = both_bearing.group(2)
        add_at(both_bearing.start(), both_bearing.end(), f"{count} {spec} bearings")

    # Generic "दो bearings" / "Quantity दो" when no spec yet
    for match in re.finditer(rf"\b({num})\s+bearings?\b", text, re.I):
        # Skip if already covered by spec patterns nearby
        nearby = text[match.start() : min(len(text), match.end() + 40)]
        if re.search(r"\d{3,5}", nearby):
            continue
        # Skip false hits like "C3 bearing" where digits are part of a model code
        if match.start() > 0 and re.match(r"[A-Za-z]", text[match.start() - 1]):
            continue
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        label = "bearing" if count == "1" else "bearings"
        add_at(match.start(), match.end(), f"{count} {label}")

    for match in re.finditer(
        rf"({num})\s+(?:kilo|kg|kilogram|kilograms|किलो)(?:\s+of)?\s+(?:grease|ग्रीस)",
        text,
        re.I,
    ):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        add_at(match.start(), match.end(), f"{count} kg grease")

    for match in re.finditer(rf"({num})\s+(M\d+)\s+bolts?", text, re.I):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        add_at(match.start(), match.end(), f"{count} {match.group(2)} bolts")
    for match in re.finditer(rf"({num})\s+bolts?\b", text, re.I):
        if re.search(r"M\d+", text[max(0, match.start() - 8) : match.end()], re.I):
            continue
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        label = "bolt" if count == "1" else "bolts"
        add_at(match.start(), match.end(), f"{count} {label}")

    # Materials: liner plates, couplings, belts, pulley bearings, oils, kits
    for match in re.finditer(rf"({num})\s+liner\s+plates?", text, re.I):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        label = "liner plate" if count == "1" else "liner plates"
        add_at(match.start(), match.end(), f"{count} {label}")
    for match in re.finditer(rf"({num})\s+couplings?\b", text, re.I):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        label = "coupling" if count == "1" else "couplings"
        add_at(match.start(), match.end(), f"{count} {label}")
    for match in re.finditer(rf"({num})\s+belts?\b", text, re.I):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        label = "belt" if count == "1" else "belts"
        add_at(match.start(), match.end(), f"{count} {label}")
    for match in re.finditer(rf"({num})\s+pulley\s+bearings?", text, re.I):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        label = "pulley bearing" if count == "1" else "pulley bearings"
        add_at(match.start(), match.end(), f"{count} {label}")
    for match in re.finditer(
        rf"({num})\s+(?:लीटर|liters?|litres?)\s+compressor\s+oil",
        text,
        re.I,
    ):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        add_at(match.start(), match.end(), f"{count} liters compressor oil")
    for match in re.finditer(
        rf"({num})\s+(?:लीटर|liters?|litres?)\s+gear\s+oil",
        text,
        re.I,
    ):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        add_at(match.start(), match.end(), f"{count} liters gear oil")
    for match in re.finditer(rf"({num})\s+splice\s+kits?", text, re.I):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        label = "splice kit" if count == "1" else "splice kits"
        add_at(match.start(), match.end(), f"{count} {label}")

    for match in re.finditer(rf"({num})\s+seal\s+kits?", text, re.I):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        label = "seal kit" if count == "1" else "seal kits"
        add_at(match.start(), match.end(), f"{count} {label}")
    seal_qty = re.search(rf"seal\s+kit\s+quantity\s+is\s+({num})", text, re.I)
    if seal_qty:
        count = _parse_spoken_number(seal_qty.group(1)) or seal_qty.group(1)
        label = "seal kit" if count == "1" else "seal kits"
        add_at(seal_qty.start(), seal_qty.end(), f"{count} {label}")

    for match in re.finditer(rf"({num})\s+gaskets?", text, re.I):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        label = "gasket" if count == "1" else "gaskets"
        add_at(match.start(), match.end(), f"{count} {label}")

    for match in re.finditer(rf"({num})\s+(?:नए\s+|new\s+)?grease\s+nipples?", text, re.I):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        label = "grease nipple" if count == "1" else "grease nipples"
        add_at(match.start(), match.end(), f"{count} {label}")

    for match in re.finditer(
        rf"(?:air\s+filter\s+quantity\s+is\s+({num})|({num})\s+air\s+filters?)",
        text,
        re.I,
    ):
        raw = match.group(1) or match.group(2)
        count = _parse_spoken_number(raw) or raw
        label = "air filter" if count == "1" else "air filters"
        add_at(match.start(), match.end(), f"{count} {label}")

    if re.search(r"air\s+filter", text, re.I):
        for match in re.finditer(rf"({num})\s+filters?\b", text, re.I):
            if re.search(r"air\s+filter", text[max(0, match.start() - 10) : match.end()], re.I):
                continue
            count = _parse_spoken_number(match.group(1)) or match.group(1)
            label = "air filter" if count == "1" else "air filters"
            add_at(match.start(), match.end(), f"{count} {label}")
    else:
        for match in re.finditer(rf"({num})\s+filters?\b", text, re.I):
            count = _parse_spoken_number(match.group(1)) or match.group(1)
            label = "filter" if count == "1" else "filters"
            add_at(match.start(), match.end(), f"{count} {label}")

    role_re = (
        rf"({num})\s+"
        rf"((?:mechanical\s+|hydraulic\s+)?"
        rf"(?:fitters?|helpers?|electricians?|engineers?|technicians?|welders?|supervisors?)"
        rf"|फिटर|फिटर्स)"
    )
    for match in re.finditer(role_re, text, re.I):
        count = _parse_spoken_number(match.group(1)) or match.group(1)
        role_raw = match.group(2)
        if role_raw.startswith("फिटर"):
            role_raw = "fitter"
        label = _role_label(role_raw, count)
        add_at(match.start(), match.end(), f"{count} {label}")

    uncertainty_patterns = (
        (
            re.compile(
                r"(?:do\s+not\s+confirm\s+the\s+material[^.]*|"
                r"material[^.]*until\s+inspection[^.]*|"
                r"coupling\s+may\s+need\s+replacement,\s+but\s+do\s+not\s+confirm[^.]+)",
                re.I,
            ),
            "material not confirmed until inspection",
        ),
        (re.compile(r"Spare\s+अभी\s+confirm\s+नहीं\s+है", re.I), "spare not confirmed"),
        (
            re.compile(r"Spare\s+material\s+अभी\s+तय\s+नहीं\s+है", re.I),
            "spare material not confirmed",
        ),
        (
            re.compile(
                r"कौन\s+सा\s+valve\s+या\s+कौन\s+सा\s+material\s+चाहिए,\s*अभी\s+confirm\s+नहीं\s+है",
                re.I,
            ),
            "valve/material not confirmed",
        ),
        (re.compile(r"length\s+अभी\s+confirm\s+नहीं\s+है", re.I), "length not confirmed"),
        (
            re.compile(r"Tag\s+number\s+अभी\s+मेरे\s+पास\s+नहीं\s+है", re.I),
            "tag number not available",
        ),
        (
            re.compile(
                r"Chain\s+की\s+quantity\s+और\s+specification\s+अभी\s+confirm\s+नहीं\s+है",
                re.I,
            ),
            "chain quantity/specification not confirmed",
        ),
        (
            re.compile(
                r"Chain\s+replace\s+करनी\s+पड़ेगी\s+या\s+नहीं,\s*inspection\s+के\s+बाद",
                re.I,
            ),
            "chain replacement pending inspection",
        ),
        (
            re.compile(r"Material\s+will\s+be\s+confirmed\s+after\s+site\s+inspection", re.I),
            "material not confirmed until site inspection",
        ),
        (
            re.compile(
                r"required\s+material\s+will\s+be\s+decided\s+after\s+inspection",
                re.I,
            ),
            "material not confirmed until inspection",
        ),
        (
            re.compile(r"Equipment\s+tag\s+अभी\s+available\s+नहीं\s+है", re.I),
            "equipment tag not available",
        ),
        (
            re.compile(
                r"Bearing\s+का\s+size\s+और\s+quantity\s+अभी\s+पता\s+नहीं\s+है",
                re.I,
            ),
            "bearing size/quantity not known",
        ),
        (
            re.compile(
                r"Bearing\s+बदलना\s+है\s+या\s+balancing\s+करनी\s+है,\s*बाद\s+में\s+confirm",
                re.I,
            ),
            "bearing replacement or balancing pending confirmation",
        ),
        (
            re.compile(r"exact\s+time\s+अभी\s+confirm\s+नहीं\s+है", re.I),
            "exact time not confirmed",
        ),
        (
            re.compile(
                r"morning\s+या\s+afternoon\s+अभी\s+confirm\s+नहीं\s+है",
                re.I,
            ),
            "morning/afternoon not confirmed",
        ),
        (
            re.compile(
                r"seal\s+kit\s+and\s+oil\s+quantity\s+are\s+not\s+known\s+yet",
                re.I,
            ),
            "seal kit and oil quantity not known",
        ),
        (
            re.compile(r"Confirm\s+the\s+materials\s+after\s+inspection", re.I),
            "materials not confirmed until inspection",
        ),
        (
            re.compile(
                r"No\s+replacement\s+should\s+be\s+assumed\s+before\s+inspection",
                re.I,
            ),
            "no replacement assumed before inspection",
        ),
        (
            re.compile(
                r"do\s+not\s+have\s+the\s+equipment\s+tag\s+number|"
                r"I\s+do\s+not\s+have\s+the\s+equipment\s+tag",
                re.I,
            ),
            "equipment tag not available",
        ),
        (
            re.compile(
                r"Do\s+not\s+order\s+bearings\s+until\s+the\s+inspection\s+confirms",
                re.I,
            ),
            "do not order bearings until inspection confirms cause",
        ),
        (
            re.compile(r"Spare\s+material\s+अभी\s+confirm\s+नहीं\s+है", re.I),
            "spare material not confirmed",
        ),
        (
            re.compile(
                r"steel\s+material\s+will\s+be\s+measured\s+at\s+site|"
                r"final\s+quantity\s+is\s+confirmed",
                re.I,
            ),
            "steel material quantity not confirmed until site measurement",
        ),
        (
            re.compile(r"filter\s+change\s+नहीं\s+करना\s+है", re.I),
            "filter change not required",
        ),
        (
            re.compile(
                r"Leakage\s+का\s+source\s+मिलने\s+के\s+बाद\s+material\s+decide|"
                r"material\s+decide\s+करेंगे",
                re.I,
            ),
            "material not confirmed until leakage source found",
        ),
        (
            re.compile(r"अभी\s+gearbox\s+replace\s+नहीं\s+करना\s+है", re.I),
            "gearbox replacement not to be done yet",
        ),
        (
            re.compile(
                r"gearbox\s+replacement\s+assume\s+नहीं\s+करना\s+है",
                re.I,
            ),
            "gearbox replacement not to be assumed",
        ),
        (
            re.compile(
                r"Replace\s+the\s+mechanical\s+seal\s+if\s+inspection\s+confirms\s+wear",
                re.I,
            ),
            "mechanical seal replacement pending inspection confirmation",
        ),
        (
            re.compile(
                r"Repair\s+के\s+लिए\s+कितना\s+plate\s+material\s+चाहिए,\s*अभी\s+confirm\s+नहीं\s+है",
                re.I,
            ),
            "plate material not confirmed",
        ),
        (
            re.compile(
                r"Valve\s+replace\s+करना\s+है\s+या\s+नहीं,\s*inspection\s+के\s+बाद\s+decide",
                re.I,
            ),
            "valve replacement pending inspection",
        ),
        (
            re.compile(r"Material\s+अभी\s+required\s+नहीं\s+है", re.I),
            "material not required currently",
        ),
        (
            re.compile(
                r"required\s+spare\s+parts\s+are\s+not\s+known\s+yet",
                re.I,
            ),
            "spare parts not known yet",
        ),
        (
            re.compile(
                r"कोई\s+replacement\s+material\s+अभी\s+confirm\s+नहीं\s+है",
                re.I,
            ),
            "replacement material not confirmed",
        ),
        (
            re.compile(r"Exact\s+time\s+बाद\s+में\s+confirm\s+करेंगे", re.I),
            "exact time not confirmed yet",
        ),
        (
            re.compile(
                r"Spare\s+parts\s+site\s+inspection\s+के\s+बाद\s+confirm",
                re.I,
            ),
            "spare parts not confirmed until site inspection",
        ),
        (
            re.compile(r"bearing\s+number\s+अभी\s+confirm\s+नहीं\s+है", re.I),
            "bearing number not confirmed",
        ),
        (
            re.compile(
                r"Do\s+not\s+raise\s+a\s+motor\s+replacement\s+request\s+yet",
                re.I,
            ),
            "motor replacement not to be raised yet",
        ),
    )
    for pattern, note in uncertainty_patterns:
        match = pattern.search(text)
        if match:
            add_at(match.start(), match.end(), note)

    quantities = _apply_quantity_corrections(text, spans)
    # Cancelled filter change: drop filter quantities entirely.
    if re.search(r"filter\s+change\s+नहीं\s+करना\s+है", text, re.I):
        quantities = [
            q
            for q in (quantities or [])
            if "filter" not in q.lower() or "not required" in q.lower()
        ] or None
    return quantities or None


def _apply_quantity_corrections(
    text: str,
    spans: list[tuple[int, int, str]],
) -> list[str]:
    correction_points = [
        m.start()
        for m in re.finditer(r"(?:नहीं|नही)\s*,?|correction\s*,?", text, re.I)
    ]
    if not correction_points:
        return _dedupe_keep_order([item for _, _, item in spans])

    keep_flags = [True] * len(spans)
    for corr_pos in correction_points:
        after_roles: set[str] = set()
        for start, _end, item in spans:
            if start >= corr_pos:
                role = _quantity_role_key(item)
                if role:
                    after_roles.add(role)
        if not after_roles:
            continue
        for i, (start, _end, item) in enumerate(spans):
            if start < corr_pos:
                role = _quantity_role_key(item)
                if role and role in after_roles:
                    keep_flags[i] = False

    kept = [item for keep, (*_, item) in zip(keep_flags, spans) if keep]
    return _dedupe_keep_order(kept)


def _quantity_role_key(item: str) -> str | None:
    lower = item.lower()
    if "pulley bearing" in lower or "pulley bearings" in lower:
        return "pulley bearing"
    if "liner plate" in lower:
        return "liner plate"
    if "coupling" in lower:
        return "coupling"
    if "belt" in lower and "conveyor" not in lower:
        return "belt"
    if "gear oil" in lower:
        return "gear oil"
    if "compressor oil" in lower:
        return "compressor oil"
    if "electrician" in lower:
        return "electrician"
    if "mechanical engineer" in lower:
        return "mechanical engineer"
    if "engineer" in lower:
        return "engineer"
    if "mechanical fitter" in lower:
        return "mechanical fitter"
    if "fitter" in lower:
        return "fitter"
    if "helper" in lower:
        return "helper"
    if "hydraulic technician" in lower:
        return "hydraulic technician"
    if "technician" in lower:
        return "technician"
    if "welder" in lower:
        return "welder"
    if "supervisor" in lower:
        return "supervisor"
    if "bearing" in lower:
        return "bearing"
    if "grease nipple" in lower:
        return "grease nipple"
    if "grease" in lower:
        return "grease"
    if "bolt" in lower:
        return "bolt"
    if "seal kit" in lower:
        return "seal kit"
    if "splice kit" in lower:
        return "splice kit"
    if "gasket" in lower:
        return "gasket"
    if "air filter" in lower:
        return "air filter"
    if "filter" in lower:
        return "filter"
    return None


# ---------------------------------------------------------------------------
# Hours
# ---------------------------------------------------------------------------


def _hour_kind(local_window: str, full_match_text: str) -> str:
    # Prefer markers immediately around this duration.
    if re.search(r"(बंद|downtime|shutdown|remain\s+stopped|stopped\s+for|बंद\s+चाहिए|बंद\s+रहेगी|shut\s+down)", full_match_text, re.I):
        if not re.search(r"(काम|job|work|inspection|maintenance\s+activity\s+will\s+take)", full_match_text, re.I):
            return "machine_downtime"
    if re.search(
        r"(का\s+काम|पूरा\s+काम|काम\s+में|complete\s+job|job\s+will\s+take|घंटे\s+का\s+है|"
        r"घंटे\s+लगेंगे|घंटे\s+लगेगा)",
        full_match_text,
        re.I,
    ) and not re.search(r"(बंद|downtime|stopped)", full_match_text, re.I):
        return "work_duration"
    if re.search(
        r"(बंद|downtime|shutdown|remain\s+stopped|stopped\s+for)",
        local_window,
        re.I,
    ) and not re.search(r"(का\s+काम|काम\s+में|complete\s+job|पूरा\s+काम)", local_window, re.I):
        return "machine_downtime"
    if re.search(
        r"(का\s+inspection|inspections?\s+रखो|के\s+inspection|inspect\s+it\s+for|"
        r"hour(?:s)?\s+inspection|घंटे\s+inspection|-hour\s+inspection|"
        r"पहले\s+.+\s+inspection)",
        local_window,
        re.I,
    ):
        return "inspection_duration"
    if re.search(
        r"(का\s+inspection|के\s+inspection|inspect\s+it\s+for|inspection\s+रखो|"
        r"-hour\s+inspection|घंटे\s+inspection)",
        full_match_text,
        re.I,
    ):
        return "inspection_duration"
    return "work_duration"


def _extract_hours(text: str) -> list[str | dict[str, Any]] | None:
    num = _number_pattern()
    entries: list[tuple[int, int, dict[str, Any]]] = []
    patterns = (
        re.compile(rf"({num})\s+घंटे", re.I),
        re.compile(rf"({num})\s+hours?\b", re.I),
        re.compile(rf"({num})-hour\b", re.I),
        re.compile(r"\bninety\s+minutes?\b", re.I),
        re.compile(rf"({num})\s+minutes?\b", re.I),
    )

    for pattern in patterns:
        for match in pattern.finditer(text):
            if re.search(r"ninety", match.group(0), re.I):
                count = "1.5"
                value = "1.5 hours"
            elif "minute" in match.group(0).lower():
                mins = _parse_spoken_number(match.group(1)) or match.group(1)
                try:
                    hours_val = float(mins) / 60.0
                    count = str(int(hours_val)) if hours_val.is_integer() else str(hours_val)
                except ValueError:
                    count = mins
                value = _format_hours_value(count) if count != mins else f"{mins} minutes"
            else:
                count = _parse_spoken_number(match.group(1)) or match.group(1)
                value = _format_hours_value(count)
            left = text[max(0, match.start() - 50) : match.start()]
            right = text[match.end() : match.end() + 40]
            clause_break = max(
                left.rfind("और"),
                left.rfind("but"),
                left.rfind("लेकिन"),
                left.rfind(","),
                left.rfind("।"),
                left.rfind("."),
            )
            if clause_break >= 0:
                left = left[clause_break + 1 :]
            local = left + match.group(0) + right
            tight = text[max(0, match.start() - 25) : match.end() + 25]
            kind = _hour_kind(local, tight)
            if re.search(r"के\s+inspection", text[match.end() : match.end() + 30], re.I):
                kind = "inspection_duration"
            if re.search(r"-hour\s+inspection|घंटे\s+inspection|पहले\s+.{0,10}inspection", local, re.I):
                kind = "inspection_duration"
            if (
                kind == "work_duration"
                and re.search(r"\binspect(?:\s|ion\b)", text[max(0, match.start() - 100) : match.start()], re.I)
                and not re.search(r"(काम|job\s+will|complete\s+job|पूरा\s+काम|maintenance\s+job)", tight, re.I)
            ):
                kind = "inspection_duration"
            if re.search(r"(बंद\s+चाहिए|बंद\s+रहेगी|बंद\s+रखनी|stopped\s+for|needs\s+to\s+be\s+stopped|shut\s+down\s+for|must\s+be\s+shut\s+down)", tight, re.I):
                kind = "machine_downtime"
            if re.search(r"(पूरा\s+काम|का\s+काम\s+है|complete\s+maintenance\s+job|job\s+will\s+take)", tight, re.I) and not re.search(
                r"(बंद|stopped)", tight, re.I
            ):
                kind = "work_duration"
            entries.append((match.start(), match.end(), {"kind": kind, "value": value}))

    entries = _apply_hour_corrections(text, entries)
    if not entries:
        return None

    out: list[str | dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for _s, _e, entry in entries:
        key = (entry["kind"], entry["value"])
        if key in seen:
            continue
        seen.add(key)
        out.append(entry)
    return out


def _apply_hour_corrections(
    text: str,
    entries: list[tuple[int, int, dict[str, Any]]],
) -> list[tuple[int, int, dict[str, Any]]]:
    corr = re.search(
        rf"({_number_pattern()})\s+(?:घंटे|hours?)\s*(?:नहीं|नही)[^.।]*?"
        rf"({_number_pattern()})\s+(?:घंटे|hours?|होगा)",
        text,
        re.I,
    )
    if not corr:
        corr = re.search(
            rf"(?:Duration\s+)?({_number_pattern()})\s+(?:घंटे|hours?)\s*(?:नहीं|नही)\s*,?\s*"
            rf"(?:लगभग\s+)?({_number_pattern()})\s+(?:घंटे|hours?|होगा)",
            text,
            re.I,
        )
    if not corr:
        return entries

    rejected = _parse_spoken_number(corr.group(1)) or corr.group(1)
    final = _parse_spoken_number(corr.group(2)) or corr.group(2)
    corr_start = corr.start()

    kept: list[tuple[int, int, dict[str, Any]]] = []
    for start, end, entry in entries:
        count = entry["value"].split()[0]
        if count == rejected and start <= corr_start + 10:
            continue
        if count == final or start >= corr_start:
            kept.append((start, end, entry))
        elif count != rejected:
            kept.append((start, end, entry))
    final_value = _format_hours_value(final)
    if not any(e["value"] == final_value for *_rest, e in kept):
        kept.append((corr.end(), corr.end(), {"kind": "work_duration", "value": final_value}))
    kept = [t for t in kept if t[2]["value"] != _format_hours_value(rejected)]
    return kept


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------


def _extract_dates(text: str) -> str | list[str] | None:
    parts: list[str] = []

    def add(phrase: str) -> None:
        phrase = _normalize_whitespace(phrase)
        if phrase and phrase not in parts:
            parts.append(phrase)

    process_note = None
    process_match = re.search(
        r"(?:exact\s+time\s+(?:process\s+team|maintenance\s+(?:supervisor|team))\s+"
        r"(?:बताएगी|बताएगा|confirm\s+करेगी|batayegi|will\s+provide|will\s+tell|will\s+confirm)"
        r"|exact\s+time\s+will\s+be\s+provided\s+by\s+the\s+process\s+team)",
        text,
        re.I,
    )
    if process_match:
        process_note = _normalize_whitespace(process_match.group(0)).rstrip("।.!,;")

    # "today at four PM"
    today_clock = re.search(
        rf"\btoday\s+at\s+({_number_pattern()})\s*(AM|PM|am|pm)\b",
        text,
        re.I,
    )
    if today_clock:
        n = _parse_spoken_number(today_clock.group(1)) or today_clock.group(1)
        add(f"today at {n} {today_clock.group(2).upper()}")

    if re.search(r"\btomorrow\s+morning\b", text, re.I):
        add("tomorrow morning")

    if re.search(r"आज\s+की\s+second\s+shift", text, re.I):
        add("today second shift")
    if re.search(r"\bnight\s+shift\b", text, re.I):
        if re.search(r"\bआज\b.*\bnight\s+shift\b|\btoday\b.*\bnight\s+shift\b", text, re.I):
            add("today night shift")
        else:
            add("night shift")
    if re.search(r"Exact\s+time\s+बाद\s+में\s+confirm", text, re.I):
        # attach later after day is known
        pass

    for day in _ENGLISH_DAYS:
        # "Monday को सुबह आठ बजे"
        hindi_clock = re.search(
            rf"\b{day}\b\s*को\s*(?:(सुबह|शाम|दोपहर)\s*)?"
            rf"(?:(?!साढ़े)({_number_pattern()})\s*बजे)?",
            text,
            re.I,
        )
        if hindi_clock and (hindi_clock.group(1) or hindi_clock.group(2)):
            bits = [day.capitalize()]
            period_map = {
                "सुबह": "morning",
                "शाम": "evening",
                "दोपहर": "afternoon",
            }
            if hindi_clock.group(1):
                bits.append(period_map[hindi_clock.group(1)])
            if hindi_clock.group(2):
                bits.append(f"{_parse_spoken_number(hindi_clock.group(2)) or hindi_clock.group(2)}:00")
            add(" ".join(bits))
            continue

        for match in re.finditer(
            rf"\b{day}\b(?:\s+(?:morning|afternoon|evening|night))?"
            rf"(?:"
            rf"\s+at\s+{_number_pattern()}(?:\s*(?:AM|PM|am|pm))?"
            rf"(?:\s+in\s+the\s+morning|\s+in\s+the\s+evening)?"
            rf"|"
            rf"\s+{_number_pattern()}\s*बजे"
            rf")?",
            text,
            re.I,
        ):
            tokens = match.group(0).split()
            tokens[0] = tokens[0].capitalize()
            rebuilt: list[str] = []
            i = 0
            while i < len(tokens):
                tok = tokens[i]
                if tok == "बजे":
                    i += 1
                    continue
                parsed = _parse_spoken_number(tok)
                if parsed and tok.lower() in _NUMERAL_WORD_SET:
                    # "Saturday morning nine बजे" → Saturday morning 9:00
                    if i + 1 < len(tokens) and tokens[i + 1] == "बजे":
                        rebuilt.append(f"{parsed}:00")
                    elif i > 0 and rebuilt and rebuilt[-1].lower() in {
                        "morning",
                        "afternoon",
                        "evening",
                        "night",
                    }:
                        rebuilt.append(f"{parsed}:00")
                    else:
                        rebuilt.append(parsed)
                else:
                    rebuilt.append(tok)
                i += 1
            add(" ".join(rebuilt))

    for hindi_day, english_day in _HINDI_DAYS.items():
        if hindi_day not in text:
            continue
        # Prefer "साढ़े नौ बजे" (9:30) before generic clock parsing.
        half = re.search(
            rf"{re.escape(hindi_day)}\s*(?:को\s*)?(सुबह|शाम|दोपहर)?\s*"
            rf"साढ़े\s+({_number_pattern()})\s*बजे",
            text,
            re.I,
        )
        if half:
            bits = [english_day]
            period = half.group(1)
            clock = half.group(2)
            period_map = {
                "सुबह": "morning",
                "शाम": "evening",
                "दोपहर": "afternoon",
            }
            if period:
                bits.append(period_map.get(period, period))
            hour = _parse_spoken_number(clock) or clock
            bits.append(f"{hour}:30")
            add(" ".join(bits))
            continue
        m = re.search(
            rf"{re.escape(hindi_day)}\s*(?:को\s*)?"
            rf"(?:(सुबह|शाम|दोपहर|afternoon|evening|morning)\s*)?"
            rf"(?:(?!साढ़े)({_number_pattern()})\s*बजे)?",
            text,
            re.I,
        )
        if not m:
            add(english_day)
            continue
        bits = [english_day]
        period = m.group(1)
        clock = m.group(2)
        period_map = {
            "सुबह": "morning",
            "शाम": "evening",
            "दोपहर": "afternoon",
            "afternoon": "afternoon",
            "evening": "evening",
            "morning": "morning",
        }
        if period:
            bits.append(period_map.get(period, period))
        if clock and clock != "साढ़े":
            bits.append(f"{_parse_spoken_number(clock) or clock}:00")
        add(" ".join(bits))

    # आज रात आठ बजे
    night = re.search(
        rf"\bआज\s+रात\s+({_number_pattern()})\s*बजे",
        text,
        re.I,
    )
    if night:
        n = _parse_spoken_number(night.group(1)) or night.group(1)
        add(f"today night {n}:00")

    relative_patterns = (
        (
            re.compile(
                rf"\bकल\b\s*((?:सुबह|शाम|दोपहर|evening|morning|afternoon)\s*)?"
                rf"(?:({_number_pattern()})\s*बजे)?"
            ),
            "tomorrow",
        ),
        (
            re.compile(
                rf"\bआज\b\s*(?:की\s*)?((?:सुबह|शाम|दोपहर|रात|shift|afternoon|evening|morning)\s*)?"
                rf"(?:({_number_pattern()})\s*बजे)?"
            ),
            "today",
        ),
        (re.compile(r"परसों"), "day after tomorrow"),
    )
    period_map = {
        "सुबह": "morning",
        "शाम": "evening",
        "दोपहर": "afternoon",
        "रात": "night",
        "shift": "shift",
        "afternoon": "afternoon",
        "evening": "evening",
        "morning": "morning",
    }
    for pattern, label in relative_patterns:
        m = pattern.search(text)
        if not m:
            continue
        if label == "day after tomorrow":
            add(label)
            continue
        # Prefer the more specific "today night X:00" already captured.
        if label == "today" and any(p.startswith("today night") for p in parts):
            continue
        if label == "today" and any("night shift" in p for p in parts):
            continue
        if label == "today" and any("second shift" in p for p in parts):
            continue
        if label == "tomorrow" and any(p.startswith("tomorrow morning") for p in parts):
            continue
        bits = [label]
        if m.lastindex and m.lastindex >= 1 and m.group(1):
            bits.append(period_map.get(m.group(1).strip(), m.group(1).strip()))
        if m.lastindex and m.lastindex >= 2 and m.group(2):
            bits.append(f"{_parse_spoken_number(m.group(2)) or m.group(2)}:00")
        if label == "today" and re.search(r"आज\s+afternoon", text, re.I):
            add("today afternoon")
            continue
        if label == "today" and re.search(r"आज\s+की\s+shift", text, re.I):
            add("today shift")
            continue
        if label == "today" and re.search(r"आज\s+शाम", text, re.I):
            add("today evening")
            continue
        if label == "today" and re.search(r"आज\s+दोपहर", text, re.I):
            add(" ".join(bits) if len(bits) > 1 else "today afternoon")
            continue
        if label == "tomorrow" and re.search(r"कल\s+evening", text, re.I):
            add("tomorrow evening")
            continue
        if label == "tomorrow" and re.search(r"कल\s+morning", text, re.I):
            add("tomorrow morning")
            continue
        add(" ".join(bits))

    if re.search(r"\bcurrent\s+shift\b", text, re.I):
        add("current shift")

    if parts and re.search(r"exact\s+time\s+अभी\s+confirm\s+नहीं\s+है", text, re.I):
        if "exact time" not in parts[0].lower():
            parts[0] = f"{parts[0]} (exact time not confirmed)"
    if parts and re.search(r"Exact\s+time\s+बाद\s+में\s+confirm", text, re.I):
        if "exact time" not in parts[0].lower():
            parts[0] = f"{parts[0]} (exact time later confirm)"
    if parts and re.search(r"morning\s+या\s+afternoon\s+अभी\s+confirm\s+नहीं\s+है", text, re.I):
        if "morning/afternoon" not in parts[0].lower():
            parts[0] = f"{parts[0]} (morning/afternoon not confirmed)"

    if process_note and parts:
        if "exact time" not in parts[0].lower():
            parts[0] = f"{parts[0]} ({process_note})"
        return parts[0] if len(parts) == 1 else parts
    if process_note and not parts:
        return process_note
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    return parts


# ---------------------------------------------------------------------------
# Approval
# ---------------------------------------------------------------------------


def _extract_approval_intent(text: str) -> str | None:
    explicit = re.search(
        r"((?:काम\s+शुरू\s+करने\s+से\s+पहले\s+)?"
        r"(?:process\s+team\s+की\s+approval\s+और\s+safety\s+permit\s+दोनों\s+चाहिए|"
        r"safety\s+permit\s+और\s+process\s+team\s+की\s+approval\s+जरूरी\s+है|"
        r"utilities\s+team\s+की\s+approval\s+जरूरी\s+है)"
        r"(?:।\s*Approval\s+(?:मिलने\s+के\s+बाद\s+ही|के\s+बिना)\s+(?:काम|job)\s+शुरू[^.।]*)?)",
        text,
        re.I,
    )
    if explicit:
        return _normalize_whitespace(explicit.group(1)).rstrip("।.!,;")

    shutdown_confirm = re.search(
        r"(Process\s+team\s+से\s+shutdown\s+confirmation\s+लेना\s+है)",
        text,
        re.I,
    )
    if shutdown_confirm:
        return _normalize_whitespace(shutdown_confirm.group(1)).rstrip("।.!,;")

    hot_work = re.search(
        r"((?:A\s+)?hot\s+work\s+permit\s+and\s+process\s+team\s+approval\s+"
        r"are\s+required\s+before\s+starting\s+the\s+job)",
        text,
        re.I,
    )
    if hot_work:
        return _normalize_whitespace(hot_work.group(1)).rstrip("।.!,;")

    height = re.search(
        r"((?:A\s+)?work-at-height\s+permit\s+is\s+required\s+before\s+starting)",
        text,
        re.I,
    )
    if height:
        return _normalize_whitespace(height.group(1)).rstrip("।.!,;")

    no_approval = re.search(
        r"(No\s+approval\s+is\s+required(?:\s+for\s+the\s+inspection)?)",
        text,
        re.I,
    )
    if no_approval:
        return _normalize_whitespace(no_approval.group(1)).rstrip("।.!,;")

    for pattern in _APPROVAL_PATTERNS:
        match = pattern.search(text)
        if match:
            start = match.start()
            end = match.end()
            left = max(text.rfind("।", 0, start), text.rfind(".", 0, start))
            start = left + 1 if left >= 0 else max(0, start - 40)
            rights = [i for i in (text.find("।", end), text.find(".", end)) if i >= 0]
            end = min(rights) + 1 if rights else min(len(text), end + 80)
            snippet = _normalize_whitespace(text[start:end]).rstrip("।.!,;")
            if re.search(r"exact\s+time|batayegi|बताएगी|बताएगा|confirm\s+करेगी", snippet, re.I):
                if not re.search(
                    r"(permission|approval|permit|अनुमति|मंजूरी|जरूरी|hot\s+work|work-at-height)",
                    snippet,
                    re.I,
                ):
                    continue
            return snippet
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_ground_truth(raw_text: str) -> MaintenanceExtraction:
    """Parse human-verified raw spoken text into the five-field Ground Truth."""
    text = _normalize_whitespace(raw_text)
    return MaintenanceExtraction(
        assets=_extract_assets(text),
        quantities=_extract_quantities(text),
        hours=_extract_hours(text),
        dates=_extract_dates(text),
        approval_intent=_extract_approval_intent(text),
    )
