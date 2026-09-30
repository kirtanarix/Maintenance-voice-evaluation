"""Dictionary v2 Phase 4: deterministic evidence-only coverage proposals.

Python standard library only. Run with -B to avoid bytecode files.
Default: validate two independent in-memory runs, then exclusively create outputs.
--verify: run twice again and compare all five saved artifacts byte-for-byte.
No Phase 1/2/3 builder is imported or executed. No semantic API is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "outputs/dictionary_v2"
VERSION = "phase4-coverage-v1"
OUTPUTS = ("phase4_concept_candidates.jsonl", "phase4_variant_candidates.jsonl",
           "phase4_review_queue.jsonl", "phase4_coverage_analysis.json", "phase4_coverage_report.md")
PROTECTED = ("inputs", "src", "outputs/dictionary_v2/phase1",
             "outputs/dictionary_v2/phase2_exploration", "outputs/dictionary_v2/phase3",
             "outputs/dictionary_v2/phase3_exploration")
MISSING = {"", "na", "n/a", "n.a.", "none", "nil", "nill", "not available", "not applicable", "-"}
CLASS_HEADERS = {"category", "asset type", "type of vehicle"}
CODE_HEADERS = {"object type"}
SPEC_HEADERS = {"type and capacity of fire extinguisher", "capacity", "size/dimension",
                "size/dimens.", "capacity of pump (m3/hr)"}
NAME_FIELDS = ("asset_name_candidates",)
REGISTRATION_NAMESPACES = ("asset_tag", "equipment_number", "equipment_code", "vehicle_registration", "technical_id")
RULES = {
    "existing_coverage": "Keep Phase 3 membership. Additional semantic matches require an exact asset-name label or the exact existing label followed by a fully parsed specification/type suffix. No fuzzy matches; new links are assessments, not Phase 3 changes.",
    "new_concept": "Propose an exact source label only when an explicit category/type field is corroborated by that exact phrase in asset names, or an exact sheet/name agreement exists; at least two distinct registrations must occur in one source snapshot. Repeated exports alone cannot meet this threshold.",
    "raw_names": "Repeated names alone are review signals, not approved concepts, aliases or physical identities.",
    "granularity": "A proposed category family may ultimately be a type/variant of a broader concept; this is always reviewed. Labels overlapping existing concepts are review-only rather than proposed duplicates.",
    "variants": "Only existing Phase 3 concepts can be variant parents. Use an explicit specification field or a complete exact-name suffix with a numeric capacity and unit or an explicit parenthesized Type marker. Never strip unexplained suffixes or infer specifications from identifiers, manufacturers or models.",
    "coverage": "Partition all Phase 1 IDs into existing assessed coverage, incremental proposed-concept coverage, or not covered. Conflicting/high-risk/parse-issue records outside the frozen baseline are held out. Non-asset observations remain source evidence, not missing equipment concepts.",
    "safety": "Every candidate is review-required. No alias, industry, component relationship, instance ID, merge or canonical concept is created. Raw values and Live/Demo provenance stay separate.",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable(kind, *parts):
    return "phase4_" + kind + "_" + hashlib.sha256(packed((VERSION, *parts)).encode("utf-8")).hexdigest()[:24]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot():
    paths = [p for sub in PROTECTED for p in (ROOT / sub).rglob("*") if p.is_file()]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def lines(path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def useful(value):
    return value is not None and str(value).strip().casefold() not in MISSING


def header(cell):
    # Header recognition only; no source value or identifier normalization.
    return str(cell["header_raw"]).strip().casefold()


def safe_label(label):
    return isinstance(label, str) and 3 <= len(label) <= 80 and bool(re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*", label))


def phrase(label, text):
    # Exact case and whitespace. A partial word/identifier match is not evidence.
    return bool(re.search(r"(?<![A-Za-z0-9])" + re.escape(label) + r"(?![A-Za-z0-9])", text))


def names(record):
    return record["derived"]["asset_name_candidates"]


def registration(record):
    for ns in REGISTRATION_NAMESPACES:
        vals = {packed(x["value_raw"]) for x in record["derived"]["identifiers"]
                if x["namespace"] == ns and useful(x["value_raw"])}
        if len(vals) == 1:
            return ns, next(iter(vals))
        if len(vals) > 1:
            return None
    return None


def independent_support(records, ids):
    groups = defaultdict(set)
    for rid in sorted(set(ids)):
        r = records[rid]
        reg = registration(r)
        if reg:
            groups[r["source_id"]].add(reg)
    return {sid: len(keys) for sid, keys in sorted(groups.items())}


def coordinate(record, column=None):
    result = {"record_id": record["record_id"], "source_id": record["source_id"],
              "source_group": record["source_group"], "filename": record["filename"],
              "sheet": record["sheet"], "row_number": record["row_number"]}
    if column is not None:
        cell = record["cells"][column]
        result.update({"column_index": column, "header_raw": cell["header_raw"], "value_raw": cell["value_raw"]})
    return result


def evidence_summary(data, ids):
    ids = sorted(set(ids))
    rs = data["records"]
    raw_names = Counter(str(n["value_raw"]) for rid in ids for n in names(rs[rid]))
    samples = []
    for rid in ids[:5]:
        r = rs[rid]
        example = coordinate(r)
        example["asset_name_fields"] = [coordinate(r, n["column_index"]) for n in names(r)]
        samples.append(example)
    return {"observation_count": len(ids),
            "counts_by_source_group": dict(sorted(Counter(rs[r]["source_group"] for r in ids).items())),
            "distinct_registrations_by_source": independent_support(rs, ids),
            "raw_name_count": len(raw_names),
            "raw_name_examples": [{"value_raw": name, "observations": count}
                                  for name, count in sorted(raw_names.items(), key=lambda x: (-x[1], x[0]))[:8]],
            "examples": samples,
            "identity_warning": "Registration keys are source-scoped evidence, not unique physical-asset counts."}


def files_for(data, ids):
    sources = data["sources"]
    return sorted({sources[data["records"][rid]["source_id"]]["relative_path"] for rid in ids})


def groups_for(data, ids):
    return sorted({data["records"][rid]["source_group"] for rid in ids})


def specification_suffix(concept_label, raw_name):
    if not isinstance(raw_name, str) or not raw_name.startswith(concept_label + " "):
        return None
    suffix = raw_name[len(concept_label) + 1:]
    match = re.fullmatch(r"([A-Za-z][A-Za-z0-9 /]*?)[ -]([0-9]+(?:\.[0-9]+)?) ?(KG|Kg|kg|LTR|Ltr|L|mm|MM)", suffix)
    if match:
        return suffix, {"type_code_raw": match[1], "capacity": {"value_raw": match[2], "unit_raw": match[3]}}
    match = re.fullmatch(r"\(([A-Za-z][A-Za-z0-9 ]*) Type\)", suffix)
    if match:
        return suffix, {"type_code_raw": match[1], "marker_raw": "Type"}
    return None


def load_inputs():
    inventory = load_json(BASE / "phase1/phase1_inventory.json")
    sources = {s["source_id"]: s for s in inventory["sources"]}
    p1 = load_json(BASE / "phase1/phase1_candidates.json")
    p2 = load_json(BASE / "phase2_exploration/phase2_candidate_analysis.json")
    risk = load_json(BASE / "phase2_exploration/phase2_high_risk_cases.json")
    rules = load_json(BASE / "phase2_exploration/phase2_rule_proposals.json")
    manifest = load_json(BASE / "phase3/manifest.json")
    input_hashes = {p.relative_to(ROOT).as_posix(): sha(p)
                    for folder in ("phase1", "phase2_exploration", "phase3")
                    for p in sorted((BASE / folder).iterdir()) if p.is_file()}
    for name, digest in p2["input_phase1_sha256"].items():
        require(sha(BASE / "phase1" / name) == digest, "Phase 1 input differs from Phase 2 manifest")
    for key, folder in (("phase1_input_sha256", "phase1"), ("phase2_input_sha256", "phase2_exploration")):
        for name, digest in manifest[key].items():
            require(sha(BASE / folder / name) == digest, "Phase 3 pinned input mismatch")
    for name, digest in manifest["output_sha256"].items():
        require(sha(BASE / "phase3" / name) == digest, "Phase 3 artifact differs from its manifest")
    require(sha(BASE / "phase3/build_phase3.py") == manifest["builder_sha256"], "Phase 3 builder changed")
    for path in (BASE / "phase1/phase1_report.md", BASE / "phase2_exploration/phase2_exploration_report.md",
                 BASE / "phase3/phase3_report.md", BASE / "phase3/build_phase3.py"):
        path.read_text(encoding="utf-8")
    for source in sources.values():
        require(sha(ROOT / "inputs/dictionary_v2" / source["relative_path"]) == source["sha256"], "Source file changed")
    records, source_counts = {}, Counter()
    for raw in lines(BASE / "phase1/phase1_records.jsonl"):
        rid = raw["record_id"]
        require(rid not in records and raw["source_id"] in sources, "Invalid Phase 1 record")
        keep = {x["column_index"] for field in raw["derived"].values() if isinstance(field, list)
                for x in field if isinstance(x, dict) and "column_index" in x}
        keep.update(c["column_index"] for c in raw["raw_cells"]
                    if header(c) in CLASS_HEADERS | CODE_HEADERS | SPEC_HEADERS)
        r = {key: raw[key] for key in ("record_id", "source_id", "source_group", "filename", "sheet",
                                       "row_number", "record_kind", "classification_reason", "derived")}
        r["cells"] = {c["column_index"]: c for c in raw["raw_cells"] if c["column_index"] in keep}
        r["parse_issue"] = raw.get("parse_issue")
        for field in raw["derived"].values():
            if isinstance(field, list):
                for obs in field:
                    if "column_index" in obs:
                        require(r["cells"][obs["column_index"]]["value_raw"] == obs["value_raw"], "Derived/raw mismatch")
        records[rid] = r
        source_counts[r["source_id"]] += 1
    require(all(source_counts[sid] == s["record_count"] for sid, s in sources.items()), "Source counts differ")
    candidates = {c["candidate_id"]: c for c in p1["candidates"]}
    proposals = {c["candidate_id"]: c for c in p2["candidates"]}
    require(len(candidates) == len(p1["candidates"]) == p1["candidate_count"], "Candidate IDs/count invalid")
    require(len(proposals) == len(p2["candidates"]) == p2["candidate_count"] and proposals.keys() == candidates.keys(), "Phase 2 coverage differs")
    for cid, c in candidates.items():
        require(set(c["record_ids"]) <= records.keys() and set(c["record_ids"]) == set(proposals[cid]["source_record_ids"]), "Bad candidate references")
    concepts = {c["concept_id"]: c for c in lines(BASE / "phase3/concepts.jsonl")}
    variants = {v["variant_id"]: v for v in lines(BASE / "phase3/variants.jsonl")}
    instances = list(lines(BASE / "phase3/instances.jsonl"))
    industries = list(lines(BASE / "phase3/industry_associations.jsonl"))
    require(len(concepts) == manifest["output_record_counts"]["concepts.jsonl"], "Concept count differs")
    require(len(variants) == manifest["output_record_counts"]["variants.jsonl"], "Variant count differs")
    require(len(instances) == manifest["output_record_counts"]["instances.jsonl"], "Instance count differs")
    require(len(industries) == manifest["output_record_counts"]["industry_associations.jsonl"], "Industry count differs")
    for obj in [*concepts.values(), *variants.values(), *instances]:
        require(set(obj["source_record_ids"]) <= records.keys(), "Invalid Phase 3 source reference")
        if "concept_id" in obj:
            require(obj["concept_id"] in concepts, "Invalid Phase 3 concept reference")
    deferred, decisions_seen, dispositions, candidate_decisions, risk_decisions = [], set(), Counter(), {}, {}
    ledger_count = 0
    for d in lines(BASE / "phase3/review_decisions.jsonl"):
        require(d["decision_id"] not in decisions_seen and set(d["source_record_ids"]) <= records.keys(), "Invalid Phase 3 decision")
        decisions_seen.add(d["decision_id"])
        ledger_count += 1
        if d["decision_kind"] == "source_disposition":
            dispositions.update(d["source_record_ids"])
        elif d["decision_kind"] == "candidate_relationship":
            cid = d["source_candidate_id"]
            require(cid in candidates and cid not in candidate_decisions, "Invalid Phase 3 candidate decision")
            require(set(d["source_record_ids"]) == set(candidates[cid]["record_ids"]), "Phase 3 membership changed")
            candidate_decisions[cid] = d["status"]
            if d["status"] == "deferred":
                deferred.append({key: d[key] for key in ("decision_id", "source_candidate_id", "relationship_type",
                                                        "source_record_ids", "reason", "status")})
        elif d["decision_kind"] == "high_risk_case":
            risk_decisions[d["high_risk_case_id"]] = d
    require(dispositions == Counter({rid: 1 for rid in records}), "Incomplete source dispositions")
    require(ledger_count == manifest["output_record_counts"]["review_decisions.jsonl"], "Ledger count differs")
    require(candidate_decisions.keys() == candidates.keys(), "Incomplete Phase 3 candidate decisions")
    require(len(risk["cases"]) == risk["case_count"] == len(risk_decisions) == 5, "Expected five high-risk cases")
    for case in risk["cases"]:
        require(case["case_id"] in risk_decisions and risk_decisions[case["case_id"]]["status"] == "deferred", "Risk not unresolved")
        require(set(case["source_record_ids"]) == set(risk_decisions[case["case_id"]]["source_record_ids"]), "Risk members differ")
    require(len(rules["rules"]) == rules["rule_count"], "Phase 2 rules invalid")
    blocked = set().union(*(set(c["record_ids"]) for c in candidates.values() if c["candidate_type"] == "conflicting_identifier"),
                          *(set(c["source_record_ids"]) for c in risk["cases"]))
    blocked.update(rid for rid, r in records.items() if r["parse_issue"])
    return {"records": records, "sources": sources, "concepts": concepts, "variants": variants,
            "candidates": candidates, "blocked": blocked, "risk_cases": risk["cases"], "deferred": deferred,
            "input_hashes": input_hashes, "manifest": manifest, "decision_ids": decisions_seen}


def concept_signals(data):
    """Exact structured labels; no token clustering or manufactured parent names."""
    groups = defaultdict(lambda: {"all": set(), "support": {}, "roles": set()})
    repeated_names = defaultdict(set)
    existing = {c["preferred_name"] for c in data["concepts"].values()}
    for rid, r in data["records"].items():
        if r["record_kind"] != "asset" or r["parse_issue"]:
            continue
        ns = names(r)
        for n in ns:
            if useful(n["value_raw"]):
                repeated_names[str(n["value_raw"])].add(rid)
        for cell in r["cells"].values():
            role = header(cell)
            if role not in CLASS_HEADERS | CODE_HEADERS or not useful(cell["value_raw"]):
                continue
            label = str(cell["value_raw"])
            if label in existing:
                continue
            group = groups[label]
            group["all"].add(rid)
            group["roles"].add(role)
            matching = [n["column_index"] for n in ns if phrase(label, str(n["value_raw"]))]
            if role in CLASS_HEADERS and matching:
                group["support"][rid] = {"basis": "explicit_classification_and_exact_name_phrase",
                                        "classification_columns": [cell["column_index"]], "name_columns": matching}
        if r["sheet"] not in existing:
            exact = [n["column_index"] for n in ns if n["value_raw"] == r["sheet"]]
            if exact:
                label = str(r["sheet"])
                groups[label]["all"].add(rid)
                groups[label]["roles"].add("sheet")
                groups[label]["support"][rid] = {"basis": "exact_sheet_and_asset_name",
                                                  "classification_columns": [], "name_columns": exact}
    for label, ids in sorted(repeated_names.items()):
        if label not in existing and label not in groups and len(ids) >= 2 and safe_label(label):
            groups[label]["all"].update(ids)
            groups[label]["roles"].add("repeated_name_only")
    output = []
    for label, group in sorted(groups.items()):
        ids = sorted(group["all"])
        # Single isolated category values are retained through uncovered-record review instead.
        if len(ids) < 2:
            continue
        support = sorted(group["support"])
        independence = independent_support(data["records"], support)
        overlaps = sorted(c["concept_id"] for c in data["concepts"].values()
                          if phrase(label, c["preferred_name"]) or phrase(c["preferred_name"], label))
        if not safe_label(label) or group["roles"] <= CODE_HEADERS:
            status, confidence = "rejected_as_concept", "low"
            reason = "Unexplained code, suffix, numeric value, combined label or classification-code field; do not manufacture an equipment concept by stripping text."
        elif overlaps:
            status, confidence = "needs_review", "medium"
            reason = "Exact text overlaps an existing concept label; evidence does not authorize a new duplicate concept or an alias."
        elif support and max(independence.values(), default=0) >= 2:
            status, confidence = "proposed", "high"
            reason = "Exact source classification/name or sheet/name corroboration across multiple source-scoped registrations supports a reviewable family proposal, not a canonical entry."
        else:
            status, confidence = "needs_review", "low"
            reason = "Category-only, repeated-name-only or repeated-export evidence lacks corroborated independent registrations; semantic granularity remains unresolved."
        supporting = support if status == "proposed" else ids
        cid = stable("concept_candidate", label, supporting, sorted(group["roles"]))
        evidence = evidence_summary(data, supporting)
        evidence["classification_roles"] = sorted(group["roles"])
        evidence["field_support"] = [{"record_id": rid, **group["support"][rid]} for rid in support if rid in supporting]
        evidence["same_category_but_uncorroborated_record_count"] = len(group["all"] - set(support))
        output.append({"candidate_id": cid, "proposed_label": label, "status": status, "confidence": confidence,
                       "reason": reason, "supporting_record_ids": supporting,
                       "supporting_source_files": files_for(data, supporting), "source_groups": groups_for(data, supporting),
                       "evidence_summary": evidence,
                       "relationship_to_existing_concept": {"status": "possible_overlap_review_only" if overlaps else "not_established",
                                                            "concept_ids": overlaps},
                       "review_required": True, "canonicalization_performed": False, "aliases_created": [],
                       "coverage_eligible_record_ids": [rid for rid in supporting if rid not in data["blocked"]] if status == "proposed" else [],
                       "held_for_conflict_review_record_ids": sorted(set(supporting) & data["blocked"]),
                       "granularity_status": "family_vs_type_or_variant_requires_review"})
    return sorted(output, key=lambda c: c["candidate_id"]), repeated_names


def existing_and_variants(data):
    matched = {cid: set(c["source_record_ids"]) for cid, c in data["concepts"].items()}
    direct = {cid: set() for cid in matched}
    parsed = {cid: set() for cid in matched}
    suggestions = defaultdict(list)
    unsupported = defaultdict(set)
    old_variants = {(v["concept_id"], v["label"]) for v in data["variants"].values()}
    for rid, r in data["records"].items():
        if r["record_kind"] != "asset" or r["parse_issue"]:
            continue
        for cid, concept in data["concepts"].items():
            label = concept["preferred_name"]
            name_exact = False
            for n in names(r):
                raw = n["value_raw"]
                if raw == label:
                    name_exact = True
                    direct[cid].add(rid)
                    if rid not in data["blocked"]:
                        matched[cid].add(rid)
                suffix = specification_suffix(label, raw)
                if suffix:
                    parsed[cid].add(rid)
                    if rid not in data["blocked"]:
                        matched[cid].add(rid)
                    if (cid, suffix[0]) not in old_variants:
                        suggestions[(cid, suffix[0])].append({"record_id": rid, "column_index": n["column_index"],
                                                            "basis": "complete_name_specification_suffix",
                                                            "attributes": suffix[1]})
                elif isinstance(raw, str) and raw != label and raw.startswith(label):
                    unsupported[cid].add(rid)
            if name_exact:
                for cell in r["cells"].values():
                    if header(cell) in SPEC_HEADERS and useful(cell["value_raw"]):
                        raw = str(cell["value_raw"])
                        if (cid, raw) not in old_variants:
                            suggestions[(cid, raw)].append({"record_id": rid, "column_index": cell["column_index"],
                                                           "basis": "explicit_specification_field", "attributes": {"specification_raw": raw}})
    proposals = []
    for (cid, label), evidence in sorted(suggestions.items()):
        evidence = sorted(evidence, key=lambda e: (e["record_id"], e["column_index"], e["basis"]))
        ids = sorted({e["record_id"] for e in evidence})
        fields = sorted({data["records"][e["record_id"]]["cells"][e["column_index"]]["header_raw"] for e in evidence})
        proposed = {"candidate_id": stable("variant_candidate", cid, label, ids), "concept_reference": cid,
                    "proposed_variant": label, "status": "proposed", "confidence": "medium",
                    "source_field": fields, "supporting_record_ids": ids,
                    "supporting_source_files": files_for(data, ids), "source_groups": groups_for(data, ids),
                    "evidence_summary": {**evidence_summary(data, ids), "specification_evidence": evidence},
                    "reason": "Explicit source specification or complete type/capacity suffix under an existing exact concept label; raw spelling and units remain unchanged.",
                    "review_required": True, "aliases_created": [],
                    "held_for_conflict_review_record_ids": sorted(set(ids) & data["blocked"])}
        proposals.append(proposed)
    return matched, direct, parsed, sorted(proposals, key=lambda p: p["candidate_id"]), unsupported


def queue_item(data, kind, key, ids, reason, references=None):
    ids = sorted(set(ids))
    require(ids, "Review item must have source evidence")
    return {"review_id": stable("review", kind, key, ids), "review_type": kind,
            "status": "unresolved", "review_required": True,
            "reason_automation_must_not_decide": reason, "supporting_record_ids": ids,
            "supporting_source_files": files_for(data, ids), "source_groups": groups_for(data, ids),
            "references": references or {}, "evidence_summary": evidence_summary(data, ids),
            "asset_merge": False, "aliases_created": [], "industry_associations_created": []}


def build(data):
    records, concepts = data["records"], data["concepts"]
    concept_candidates, repeated_names = concept_signals(data)
    existing, direct, parsed, variant_candidates, unsupported_specs = existing_and_variants(data)
    baseline = set().union(*(set(c["source_record_ids"]) for c in concepts.values()))
    existing_ids = set().union(*existing.values())
    proposed_union = set().union(*(set(c["coverage_eligible_record_ids"]) for c in concept_candidates))
    proposed_ids = proposed_union - existing_ids
    unresolved_ids = records.keys() - existing_ids - proposed_ids
    queue = []
    for c in concept_candidates:
        queue.append(queue_item(data, "concept_proposal_review" if c["status"] == "proposed" else "unsafe_or_ambiguous_concept",
                                c["candidate_id"], c["supporting_record_ids"], c["reason"] + " Review equipment-family versus variant granularity before any promotion.",
                                {"concept_candidate_id": c["candidate_id"]}))
    for v in variant_candidates:
        queue.append(queue_item(data, "variant_proposal_review", v["candidate_id"], v["supporting_record_ids"],
                                "Review specification interpretation and possible overlap with existing variants; different raw labels are not approved aliases.",
                                {"variant_candidate_id": v["candidate_id"], "concept_id": v["concept_reference"]}))
    for d in sorted(data["deferred"], key=lambda d: d["decision_id"]):
        queue.append(queue_item(data, "inherited_deferred_relationship", d["decision_id"], d["source_record_ids"],
                                "Inherited Phase 3 deferral; coverage analysis cannot decide physical identity or semantic equivalence. " + d["reason"],
                                {"phase3_decision_id": d["decision_id"], "phase1_candidate_id": d["source_candidate_id"],
                                 "relationship_type": d["relationship_type"]}))
    for case in sorted(data["risk_cases"], key=lambda c: c["case_id"]):
        queue.append(queue_item(data, "preserved_high_risk_case", case["case_id"], case["source_record_ids"],
                                case["why_unsafe_to_merge"], {"high_risk_case_id": case["case_id"], "case_type": case["case_type"]}))
    for cid, ids in sorted(unsupported_specs.items()):
        if ids:
            queue.append(queue_item(data, "unparsed_specification_or_registration_suffix", cid, ids,
                                    "A name begins with an existing concept but the remaining text is not a fully evidenced specification. Numbers may be instance labels; suffixes must not be guessed or stripped.",
                                    {"concept_id": cid}))
    # Case/format similarities are review signals only, never semantic equivalence.
    variant_groups = defaultdict(list)
    for v in data["variants"].values():
        variant_groups[(v["concept_id"], v["label"].casefold())].append(v)
    for key, vs in sorted(variant_groups.items()):
        if len(vs) > 1:
            queue.append(queue_item(data, "existing_variant_format_overlap", list(key),
                                    set().union(*(set(v["source_record_ids"]) for v in vs)),
                                    "Existing variants differ in formatting/case. This is an audit signal only; no variant or alias is consolidated.",
                                    {"concept_id": key[0], "phase3_variant_ids": sorted(v["variant_id"] for v in vs)}))
    # A shared phrase is insufficient to decide concept-vs-variant or part/assembly.
    proposed = [c for c in concept_candidates if c["status"] == "proposed"]
    variant_observation_ids = set().union(*(set(v["supporting_record_ids"]) for v in variant_candidates)) if variant_candidates else set()
    for i, left in enumerate(proposed):
        for right in proposed[i + 1:]:
            if phrase(left["proposed_label"], right["proposed_label"]) or phrase(right["proposed_label"], left["proposed_label"]):
                queue.append(queue_item(data, "concept_vs_variant_boundary", sorted([left["candidate_id"], right["candidate_id"]]),
                                        set(left["supporting_record_ids"]) | set(right["supporting_record_ids"]),
                                        "Separately corroborated source labels overlap lexically. Neither a subtype/variant relationship nor synonymy follows from the shared words; do not collapse distinct equipment families.",
                                        {"concept_candidate_ids": sorted([left["candidate_id"], right["candidate_id"]])}))
    # Keep outstanding observations reviewable in compact source/category/kind groups.
    unresolved_groups = defaultdict(set)
    semantic_flags = defaultdict(set)
    role_counts = Counter()
    industry_counts = Counter()
    for rid, r in records.items():
        if rid in unresolved_ids:
            cats = tuple(sorted(str(c["value_raw"]) for c in r["cells"].values()
                                if header(c) in CLASS_HEADERS and useful(c["value_raw"])))
            unresolved_groups[(r["source_id"], r["record_kind"], cats,
                               "conflict_or_high_risk" if rid in data["blocked"] else "no_qualified_family")].add(rid)
        for field in ("manufacturer_observations", "model_observations"):
            if r["derived"][field]:
                role_counts[field] += 1
                # Aggregate by source, not one task per manufacturer/model spelling.
                semantic_flags[("manufacturer_model_roles", r["source_id"])].add(rid)
        ie = r["derived"]["industry_evidence"]
        basis = "filename" if any("filename" in e for e in ie["evidence"]) else "other_or_none"
        industry_counts[(ie["status"], basis)] += 1
        if ie["evidence"]:
            semantic_flags[("industry_evidence_not_taxonomy", r["source_id"])].add(rid)
        if any(re.search(r"\b(?:assembly|component|part of|consists of)\b", str(n["value_raw"]), re.I) for n in names(r)):
            semantic_flags[("component_assembly_unproven", r["source_id"])].add(rid)
    for key, ids in sorted(unresolved_groups.items()):
        kind = "uncovered_asset_family" if key[1] == "asset" else "retained_source_only_observations"
        queue.append(queue_item(data, kind, [key[0], key[1], list(key[2]), key[3]], ids,
                                "No qualified coverage rule applies, or conflict evidence requires a hold. Raw observations remain intact. Non-asset rows are outside equipment vocabulary scope and need not be converted into concepts.",
                                {"record_kind": key[1], "source_categories_raw": list(key[2]), "coverage_hold_reason": key[3]}))
    flag_reasons = {
        "manufacturer_model_roles": "Manufacturer/model observations have separate source roles. Internal codes and generated model labels must not become concepts or variants; OEM meaning remains unverified.",
        "industry_evidence_not_taxonomy": "Preserve source industry annotations and their original certainty. Filename labels and lexical family words do not establish canonical industries.",
        "component_assembly_unproven": "Related words in names do not establish containment, component identity or assembly structure. No COMPONENT_OF/PART_OF/ASSEMBLY_OF relationship is proposed.",
    }
    for key, ids in sorted(semantic_flags.items()):
        item = queue_item(data, key[0], list(key), ids, flag_reasons[key[0]])
        item["evidence_summary"]["field_roles"] = {
            "manufacturer_model_roles": ["manufacturer_observations", "model_observations"],
            "industry_evidence_not_taxonomy": ["industry_evidence"],
            "component_assembly_unproven": ["asset_name_candidates"],
        }[key[0]]
        queue.append(item)
    # Repeated names with source-specific identifiers can refer to separate registrations.
    repeated_summaries = []
    for label, ids in sorted(repeated_names.items()):
        reg_counts = independent_support(records, ids)
        if len(ids) >= 2 and max(reg_counts.values(), default=0) >= 2:
            repeated_summaries.append({"raw_name": label, "record_ids": sorted(ids),
                                       "source_groups": groups_for(data, ids), "distinct_registrations_by_source": reg_counts})
    by_concept = []
    for cid, c in sorted(concepts.items()):
        baseline_ids = set(c["source_record_ids"])
        exact_baseline = all(any(n["value_raw"] == c["preferred_name"] for n in names(records[rid])) for rid in baseline_ids)
        by_concept.append({"concept_id": cid, "preferred_name": c["preferred_name"],
                           "phase3_record_count": len(baseline_ids), "assessed_existing_coverage_count": len(existing[cid]),
                           "additional_assessed_coverage_count": len(existing[cid] - baseline_ids),
                           "exact_name_observation_count_including_holds": len(direct[cid]),
                           "parsed_specification_name_count_including_holds": len(parsed[cid]),
                           "source_record_ids": sorted(existing[cid]),
                           "baseline_source_files": files_for(data, baseline_ids),
                           "baseline_exact_name_evidence_valid": exact_baseline,
                           "baseline_distinct_registrations_by_source": independent_support(records, baseline_ids),
                           "assessment": "Source-supported within a narrow template; not proof of full dictionary coverage or independent physical assets.",
                           "counts_by_source_group": dict(sorted(Counter(records[r]["source_group"] for r in existing[cid]).items()))})
    by_group = {}
    for group in sorted({r["source_group"] for r in records.values()}):
        ids = {rid for rid, r in records.items() if r["source_group"] == group}
        by_group[group] = {"total_observations": len(ids), "phase3_baseline": len(ids & baseline),
                           "existing_concept_coverage": len(ids & existing_ids),
                           "proposed_concept_coverage": len(ids & proposed_ids),
                           "unresolved_or_source_only": len(ids & unresolved_ids)}
    analysis = {
        "schema_version": "dictionary_v2.phase4_coverage.1", "rule_version": VERSION,
        "scope": "coverage assessment and reviewable proposals only; not a final dictionary",
        "input_sha256": data["input_hashes"], "builder_sha256": sha(Path(__file__)), "rules": RULES,
        "phase3_baseline": {"concepts": len(concepts), "variants": len(data["variants"]),
                            "represented_observations": len(baseline), "counts": data["manifest"]["output_record_counts"]},
        "total_phase1_observations": len(records), "phase1_record_kinds": dict(sorted(Counter(r["record_kind"] for r in records.values()).items())),
        "total_phase1_asset_observations": sum(r["record_kind"] == "asset" for r in records.values()),
        "observations_represented_by_existing_concepts": len(existing_ids),
        "observations_with_proposed_concept_coverage": len(proposed_ids),
        "observations_still_unresolved": len(unresolved_ids),
        "asset_observations_with_existing_concept_coverage": sum(records[r]["record_kind"] == "asset" for r in existing_ids),
        "asset_observations_with_proposed_concept_coverage": sum(records[r]["record_kind"] == "asset" for r in proposed_ids),
        "asset_observations_not_covered": sum(records[r]["record_kind"] == "asset" for r in unresolved_ids),
        "coverage_definition": "Unique observation IDs, not physical assets. Existing includes baseline plus explicitly assessed exact-name/specification matches. Proposed excludes existing coverage and is conditional on review. Unresolved includes source-only non-asset records; it is not the Phase 1 unresolved record-kind count.",
        "coverage_record_ids": {"existing": sorted(existing_ids), "proposed_incremental": sorted(proposed_ids),
                                "unresolved_or_source_only": sorted(unresolved_ids)},
        "unresolved_breakdown_by_record_kind": dict(sorted(Counter(records[r]["record_kind"] for r in unresolved_ids).items())),
        "conflict_or_high_risk_records_held_outside_baseline": len(data["blocked"] - baseline),
        "counts_by_concept": by_concept, "counts_by_source_group": by_group,
        "candidate_counts": {"concept_candidates_total": len(concept_candidates),
                             "proposed_new_concepts": sum(c["status"] == "proposed" for c in concept_candidates),
                             "review_only_concepts": sum(c["status"] == "needs_review" for c in concept_candidates),
                             "rejected_as_concepts": sum(c["status"] == "rejected_as_concept" for c in concept_candidates),
                             "proposed_new_variants": len(variant_candidates), "review_queue_items": len(queue)},
        "proposed_variant_observation_ids": sorted(variant_observation_ids),
        "observations_with_proposed_variant_coverage": len(variant_observation_ids),
        "asset_observations_with_proposed_variant_coverage": sum(records[r]["record_kind"] == "asset" for r in variant_observation_ids),
        "confidence_counts": {"concept_candidates": dict(sorted(Counter(c["confidence"] for c in concept_candidates).items())),
                              "variant_candidates": dict(sorted(Counter(v["confidence"] for v in variant_candidates).items()))},
        "review_counts_by_type": dict(sorted(Counter(q["review_type"] for q in queue).items())),
        "role_separation_observation_counts": dict(sorted(role_counts.items())),
        "industry_evidence_counts": [{"source_certainty": k[0], "basis": k[1], "observations": n}
                                     for k, n in sorted(industry_counts.items())],
        "repeated_names_with_distinct_source_registrations": repeated_summaries,
        "high_risk_cases": [{"case_id": c["case_id"], "status": "unresolved", "record_ids": sorted(c["source_record_ids"])}
                            for c in sorted(data["risk_cases"], key=lambda c: c["case_id"])],
        "effects": {"physical_asset_merges": 0, "canonical_ids_created": 0, "aliases_created": 0,
                    "industry_associations_created": 0, "phase3_entries_changed": 0},
    }
    return {"concepts": concept_candidates, "variants": variant_candidates,
            "queue": sorted(queue, key=lambda q: q["review_id"]), "analysis": analysis}


def validate(data, result):
    records, concepts = data["records"], data["concepts"]
    candidates = {c["candidate_id"]: c for c in result["concepts"]}
    variants = {v["candidate_id"]: v for v in result["variants"]}
    require(len(candidates) == len(result["concepts"]) and len(variants) == len(result["variants"]), "Duplicate proposal ID")
    require(len({q["review_id"] for q in result["queue"]}) == len(result["queue"]), "Duplicate review ID")
    for obj in [*result["concepts"], *result["variants"], *result["queue"]]:
        ids = obj["supporting_record_ids"]
        require(ids and ids == sorted(set(ids)) and set(ids) <= records.keys(), "Missing/invalid proposal evidence")
        require(obj["review_required"] is True and obj["aliases_created"] == [], "Unapproved automatic alias/action")
        require(obj["supporting_source_files"] == files_for(data, ids) and obj["source_groups"] == groups_for(data, ids), "Source provenance differs")
        ev = obj["evidence_summary"]
        require(ev["observation_count"] == len(ids), "Evidence count mismatch")
        for example in ev["examples"]:
            rid = example["record_id"]
            require(rid in ids, "Example outside supporting records")
            require({k: example[k] for k in coordinate(records[rid])} == coordinate(records[rid]), "Bad coordinates")
            require(example["asset_name_fields"] == [coordinate(records[rid], n["column_index"]) for n in names(records[rid])], "Raw example changed")
    for c in result["concepts"]:
        require(c["status"] in {"proposed", "needs_review", "rejected_as_concept"}, "Invalid concept status")
        require(set(c["relationship_to_existing_concept"]["concept_ids"]) <= concepts.keys(), "Bad existing concept reference")
        require(c["canonicalization_performed"] is False, "Canonicalization is forbidden")
        require(set(c["coverage_eligible_record_ids"]) <= set(c["supporting_record_ids"]) - data["blocked"], "Risk hold bypassed")
        if c["status"] == "proposed":
            require(safe_label(c["proposed_label"]) and not c["relationship_to_existing_concept"]["concept_ids"], "Unsafe duplicate family proposal")
            field_support = {e["record_id"]: e for e in c["evidence_summary"]["field_support"]}
            require(set(field_support) == set(c["supporting_record_ids"]), "Category-only proposal lacks field support")
            require(max(independent_support(records, c["supporting_record_ids"]).values(), default=0) >= 2, "Repeated exports mistaken for independent support")
            for rid, support in field_support.items():
                r = records[rid]
                require(r["record_kind"] == "asset" and not r["parse_issue"], "Non-asset concept evidence")
                if support["basis"] == "exact_sheet_and_asset_name":
                    require(r["sheet"] == c["proposed_label"] and all(r["cells"][i]["value_raw"] == c["proposed_label"] for i in support["name_columns"]), "Invalid sheet/name support")
                else:
                    require(support["classification_columns"] and support["name_columns"], "Missing independent field roles")
                    require(all(header(r["cells"][i]) in CLASS_HEADERS and r["cells"][i]["value_raw"] == c["proposed_label"]
                                for i in support["classification_columns"]), "Invalid classification evidence")
                    require(all(phrase(c["proposed_label"], str(r["cells"][i]["value_raw"])) for i in support["name_columns"]), "Missing exact name corroboration")
        else:
            require(c["coverage_eligible_record_ids"] == [], "Review-only candidate counted as covered")
    old = {(v["concept_id"], v["label"]) for v in data["variants"].values()}
    for v in result["variants"]:
        require(v["concept_reference"] in concepts and v["status"] == "proposed", "Variant has nonexistent parent")
        require((v["concept_reference"], v["proposed_variant"]) not in old, "Existing variant proposed as new")
        evidence = v["evidence_summary"]["specification_evidence"]
        require({e["record_id"] for e in evidence} == set(v["supporting_record_ids"]), "Missing variant evidence")
        for e in evidence:
            r = records[e["record_id"]]
            cell = r["cells"][e["column_index"]]
            label = concepts[v["concept_reference"]]["preferred_name"]
            if e["basis"] == "explicit_specification_field":
                require(header(cell) in SPEC_HEADERS and str(cell["value_raw"]) == v["proposed_variant"]
                        and any(n["value_raw"] == label for n in names(r)), "Manufacturer/model/code used as variant")
            else:
                parsed = specification_suffix(label, cell["value_raw"])
                require(parsed is not None and parsed[0] == v["proposed_variant"] and parsed[1] == e["attributes"], "Unexplained specification suffix")
    inherited = []
    risk = []
    for q in result["queue"]:
        require(q["status"] == "unresolved" and q["asset_merge"] is False and q["industry_associations_created"] == [], "Review item silently applied")
        require(q["reason_automation_must_not_decide"], "Missing review reason")
        refs = q["references"]
        if "concept_candidate_id" in refs:
            require(refs["concept_candidate_id"] in candidates, "Unknown concept candidate")
        require(set(refs.get("concept_candidate_ids", [])) <= candidates.keys(), "Unknown boundary candidate")
        if "variant_candidate_id" in refs:
            require(refs["variant_candidate_id"] in variants, "Unknown variant candidate")
        if "concept_id" in refs:
            require(refs["concept_id"] in concepts, "Unknown concept")
        require(set(refs.get("phase3_variant_ids", [])) <= data["variants"].keys(), "Unknown existing variant")
        if "phase3_decision_id" in refs:
            require(refs["phase3_decision_id"] in data["decision_ids"], "Unknown inherited decision")
        if "phase1_candidate_id" in refs:
            require(refs["phase1_candidate_id"] in data["candidates"], "Unknown inherited candidate")
        if q["review_type"] == "inherited_deferred_relationship":
            inherited.append(refs["phase3_decision_id"])
        if q["review_type"] == "preserved_high_risk_case":
            risk.append(refs["high_risk_case_id"])
            original = next(c for c in data["risk_cases"] if c["case_id"] == refs["high_risk_case_id"])
            require(set(original["source_record_ids"]) == set(q["supporting_record_ids"]), "High-risk evidence lost")
    require(Counter(inherited) == Counter(d["decision_id"] for d in data["deferred"]), "Inherited deferral lost")
    require(Counter(risk) == Counter(c["case_id"] for c in data["risk_cases"]), "High-risk case lost")
    a = result["analysis"]
    coverage = a["coverage_record_ids"]
    parts = [set(coverage[k]) for k in ("existing", "proposed_incremental", "unresolved_or_source_only")]
    require(sum(map(len, parts)) == len(set().union(*parts)) == len(records) and set().union(*parts) == records.keys(), "Coverage is not a disjoint complete partition")
    for key, part in zip(("observations_represented_by_existing_concepts", "observations_with_proposed_concept_coverage", "observations_still_unresolved"), parts):
        require(a[key] == len(part), "Coverage count mismatch")
    asset_parts = [sum(records[r]["record_kind"] == "asset" for r in part) for part in parts]
    require(a["asset_observations_with_existing_concept_coverage"] == asset_parts[0]
            and a["asset_observations_with_proposed_concept_coverage"] == asset_parts[1]
            and a["asset_observations_not_covered"] == asset_parts[2]
            and sum(asset_parts) == a["total_phase1_asset_observations"], "Asset coverage count mismatch")
    variant_ids = set(a["proposed_variant_observation_ids"])
    require(variant_ids <= records.keys() and a["proposed_variant_observation_ids"] == sorted(variant_ids), "Invalid proposed variant coverage")
    require(a["observations_with_proposed_variant_coverage"] == len(variant_ids), "Variant coverage count mismatch")
    require(a["asset_observations_with_proposed_variant_coverage"] == sum(records[r]["record_kind"] == "asset" for r in variant_ids), "Asset variant coverage mismatch")
    baseline = set().union(*(set(c["source_record_ids"]) for c in concepts.values()))
    require(baseline <= parts[0] and not ((parts[0] | parts[1]) - baseline) & data["blocked"], "Coverage silently resolves a conflict")
    for row in a["counts_by_concept"]:
        require(row["concept_id"] in concepts and set(row["source_record_ids"]) <= parts[0], "Invalid per-concept coverage")
    for group, counts in a["counts_by_source_group"].items():
        ids = {rid for rid, r in records.items() if r["source_group"] == group}
        require(counts["total_observations"] == len(ids) and counts["existing_concept_coverage"] == len(ids & parts[0])
                and counts["proposed_concept_coverage"] == len(ids & parts[1]) and counts["unresolved_or_source_only"] == len(ids & parts[2]), "Source-group counts differ")
    require(a["effects"] == {"physical_asset_merges": 0, "canonical_ids_created": 0, "aliases_created": 0,
                             "industry_associations_created": 0, "phase3_entries_changed": 0}, "Forbidden effect")
    return {"status": "PASS", "record_references_valid": True, "existing_concept_and_variant_parent_references_valid": True,
            "all_proposals_have_field_evidence": True, "coverage_partition_reconciles": True,
            "live_demo_provenance_preserved": True, "high_risk_cases_unresolved": 5,
            "inherited_deferred_relationships_preserved": len(inherited), "no_merges_aliases_or_industries_created": True}


def tests():
    passed = []
    def check(name, condition):
        require(condition, "Regression failed: " + name)
        passed.append(name)
    check("exact_phrase", phrase("Valve", "Ball Valve 2IN"))
    check("no_partial_word", not phrase("Valve", "ValveCode"))
    check("no_case_alias", not phrase("Valve", "VALVE"))
    check("do_not_strip_category_suffix", not safe_label("Valve-KC"))
    check("no_identifier_concept", not safe_label("CK-0001"))
    check("no_code_concept", not safe_label("PM101004"))
    check("no_combined_concept_guess", not safe_label("Motor / Pump"))
    parsed = specification_suffix("Fire Extinguisher", "Fire Extinguisher Co2-4.5 KG")
    check("complete_capacity_suffix", parsed == ("Co2-4.5 KG", {"type_code_raw": "Co2", "capacity": {"value_raw": "4.5", "unit_raw": "KG"}}))
    check("no_registration_variant", specification_suffix("Fire Extinguisher", "Fire Extinguisher-ABC-101") is None)
    check("no_unknown_suffix", specification_suffix("Fire Extinguisher", "Fire Extinguisher ABC-6 KG-ST") is None)
    check("no_model_variant", specification_suffix("Pump", "Pump MODEL-123") is None)
    check("explicit_type_marker", specification_suffix("Fire Extinguisher", "Fire Extinguisher (ABC Type)")[1] == {"type_code_raw": "ABC", "marker_raw": "Type"})
    check("no_type_suffix_stripping", specification_suffix("Fire Extinguisher", "Fire Extinguisher (ABC Type) - WRFID") is None)
    fake = {"a": {"source_id": "one", "derived": {"identifiers": [{"namespace": "asset_tag", "value_raw": "A-01"}]}},
            "b": {"source_id": "two", "derived": {"identifiers": [{"namespace": "asset_tag", "value_raw": "A-01"}]}}}
    check("exports_not_independent", max(independent_support(fake, fake).values()) == 1)
    fake["b"]["source_id"] = "one"
    check("repeated_same_tag_not_independent", max(independent_support(fake, fake).values()) == 1)
    fake["b"]["derived"]["identifiers"][0]["value_raw"] = "A--01"
    check("punctuation_stays_distinct", independent_support(fake, fake) == {"one": 2})
    check("stable_ids", stable("test", "Valve", ["a", "b"]) == stable("test", "Valve", ["a", "b"]))
    return passed


def make_report(data, result):
    a = result["analysis"]
    counts = a["candidate_counts"]
    proposed = sorted((c for c in result["concepts"] if c["status"] == "proposed"),
                      key=lambda c: (-len(c["coverage_eligible_record_ids"]), c["proposed_label"]))
    rows = ["# Dictionary v2 — Phase 4 coverage and semantic expansion", "",
            "## Summary", "",
            "This phase produces coverage assessments and evidence-backed proposals only. It does not create a final dictionary, canonical concepts, aliases, industry associations or physical-asset merges. Every proposal requires review.", "",
            f"Analyzed all {len(data['records']):,} Phase 1 observations against {len(data['concepts'])} existing concepts and {len(data['variants'])} existing variants. The Phase 3 baseline represents {a['phase3_baseline']['represented_observations']:,} observations, not unique physical assets.", "",
            "| Measure | Count |", "|---|---:|",
            f"| Phase 1 asset observations | {a['total_phase1_asset_observations']:,} |",
            f"| Existing-concept assessed coverage | {a['observations_represented_by_existing_concepts']:,} |",
            f"| Incremental proposed-concept coverage | {a['observations_with_proposed_concept_coverage']:,} |",
            f"| Asset observations with existing-concept coverage | {a['asset_observations_with_existing_concept_coverage']:,} |",
            f"| Asset observations with proposed-concept coverage | {a['asset_observations_with_proposed_concept_coverage']:,} |",
            f"| Asset observations not covered | {a['asset_observations_not_covered']:,} |",
            f"| Observations with proposed variant coverage | {a['observations_with_proposed_variant_coverage']:,} |",
            f"| Asset observations with proposed variant coverage | {a['asset_observations_with_proposed_variant_coverage']:,} |",
            f"| Not covered / unresolved / source-only | {a['observations_still_unresolved']:,} |",
            f"| Proposed new concepts | {counts['proposed_new_concepts']:,} |",
            f"| Proposed new variants of existing concepts | {counts['proposed_new_variants']:,} |",
            f"| Review-only concept signals | {counts['review_only_concepts']:,} |",
            f"| Rejected-as-concept signals | {counts['rejected_as_concepts']:,} |",
            f"| Review queue items | {counts['review_queue_items']:,} |", "",
            "## Coverage definitions and baseline", "",
            a["coverage_definition"], "",
            "The three coverage counts form a disjoint partition of all observations. A record supporting several proposals is counted once. Proposed coverage is conditional and is not an approved dictionary match. Conflict/high-risk observations remain held outside newly assessed coverage even if their words support a family proposal. Manufacturer/model roles never generate concepts.", "",
            "| Existing concept | Phase 3 membership | Assessed coverage | Additional assessment |", "|---|---:|---:|---:|"]
    for c in a["counts_by_concept"]:
        rows.append(f"| {c['preferred_name']} | {c['phase3_record_count']} | {c['assessed_existing_coverage_count']} | {c['additional_assessed_coverage_count']} |")
    rows += ["", "All baseline concepts retain exact source-name evidence. Their definitions were selected through a narrow sheet/name template, so their small number is not evidence of complete vocabulary coverage. Repeated exports repeat support observations and do not establish independent physical identities. No existing concept was deleted, renamed or widened in Phase 3.", "",
             "| Source group | Total | Existing assessed | Proposed incremental | Unresolved/source-only |", "|---|---:|---:|---:|---:|"]
    for group, c in a["counts_by_source_group"].items():
        rows.append(f"| {group} | {c['total_observations']:,} | {c['existing_concept_coverage']:,} | {c['proposed_concept_coverage']:,} | {c['unresolved_or_source_only']:,} |")
    rows += ["", "Live and Demo evidence is retained separately in every proposal and source-group count. A shared family label is not a cross-group physical relationship; Demo is not treated as synthetic.", "",
             "## Proposed new concepts", "",
             "Proposals require an explicit classification field corroborated by the same exact phrase in asset names, or exact sheet/name agreement, plus multiple distinct registrations within a source. Categories alone and description keywords alone are insufficient. Labels below are raw source labels, not an automatically approved taxonomy. Source-held counts do not establish unique physical assets.", "",
             "| Source label | Supporting observations | Eligible for coverage before overlap removal | Confidence |", "|---|---:|---:|---|"]
    for c in proposed:
        rows.append(f"| {c['proposed_label']} | {len(c['supporting_record_ids']):,} | {len(c['coverage_eligible_record_ids']):,} | {c['confidence']} |")
    rows += ["", "Each candidate includes all supporting record IDs, exact source files, source groups and field-column evidence. Names with different tags can support a family without becoming aliases. A specific source type may ultimately be a variant under a broader evidenced family; Phase 4 does not decide that taxonomy automatically.", "",
             "## Proposed new variants", "",
             "Every variant parent is an existing Phase 3 concept. Only explicit specification fields or complete type/capacity suffixes are used. Manufacturer, model, asset tag, customer tag, equipment number and source-system ID are excluded. Unit spellings and type codes are retained verbatim. Unexplained suffixes remain in review.", "",
             "| Existing concept | Proposed raw specification | Supporting observations |", "|---|---|---:|"]
    for v in result["variants"]:
        rows.append(f"| {data['concepts'][v['concept_reference']]['preferred_name']} | {v['proposed_variant']} | {len(v['supporting_record_ids'])} |")
    rows += ["", "Existing format differences such as ABC 6KG versus ABC 6Kg remain unmerged and appear as review signals. A raw suffix containing an unexplained code is not converted into attributes. Specifications of newly proposed concepts wait until a parent concept exists; no dangling variant parent is introduced.", "",
             "## Unsafe candidates and unresolved cases", "",
             "Codes, identifiers, combined labels and unexplained source suffixes are rejected as automatic concepts without deleting their evidence. Category-only signals and repeated names without independent corroboration remain review-only. Examples below are signals, not approved meanings.", "",
             "| Source label | Status | Supporting observations |", "|---|---|---:|"]
    unsafe = sorted((c for c in result["concepts"] if c["status"] != "proposed"), key=lambda c: (-len(c["supporting_record_ids"]), c["proposed_label"]))
    rows += [f"| {c['proposed_label'].replace('|', '/')} | {c['status']} | {len(c['supporting_record_ids']):,} |" for c in unsafe[:20]]
    rows += ["", "The complete candidate and review files retain all signals, not only these examples. Shared terms do not prove that a motor, a pump and an assembly are the same concept, nor that one contains another. Source fields and functional evidence are required before assigning concept/variant or component boundaries.", "",
             "Uncovered observations by Phase 1 record kind:", "", "| Kind | Count |", "|---|---:|"]
    rows += [f"| {kind} | {count:,} |" for kind, count in a["unresolved_breakdown_by_record_kind"].items()]
    rows += ["", "Identifier mappings, workflow, guidance, metadata and blank/unresolved rows remain source evidence. Their absence from concept coverage is not automatically a dictionary defect. The Phase 1 unresolved-kind count is distinct from the larger uncovered/source-only total above.", "",
             f"The review queue preserves all {len(data['deferred']):,} deferred Phase 3 candidate relationships. Queue items overlap in source evidence and are not counts of unique unresolved records. Complete coverage membership lists are stored in the analysis JSON.", "",
             "## High-risk, role and industry boundaries", "",
             "All five cases remain unresolved: Adani equipment number 1000117336; Cool Kit punctuation-sensitive identifiers; conflicting identifier clusters; text-only aliases; repeated raw names across potentially independent records. Each retains its original case ID and member IDs in the queue. No source evidence is discarded and no physical identity is inferred.", "",
             "Manufacturer and model observations remain separate field roles, including generated/internal labels. Component/assembly wording creates review flags only. Filename-derived industry certainty is preserved as source annotation, never promoted into an association. No special rule exists for CCTV or any example equipment family.", "",
             "## Validation and determinism", "",
             "Validation: **PASS**. All source/candidate/concept/variant-parent references resolve; every proposal has actual source evidence; coverage counts reconcile without double counting; all five high-risk cases and every inherited deferral remain unresolved. No merges, aliases, industry associations or physical canonical IDs were created.", "",
             f"{len(a['validation_statistics']['regression_tests'])} boundary tests passed. Two complete runs with reversed input traversal produced byte-identical versions of all five outputs, including this report and the analysis JSON. Timestamp fields are omitted. Saved outputs are parsed and validated again. The --verify command performs another independent read-only rerun and byte comparison.", "",
             "Source SHA-256 values match the Phase 1 inventory. Phase 1/2 hashes match Phase 2/3 manifests; Phase 3 outputs and builder match the Phase 3 manifest. A before/after per-file snapshot covers all inputs, Phase 1/2/3, exploration and pipeline source files. No existing protected artifact was modified. Git metadata is not semantic input and is not included in this phase's deterministic output fingerprint.", "",
             "## Files and reproduction", "",
             "Created only phase4_concept_candidates.jsonl, phase4_variant_candidates.jsonl, phase4_review_queue.jsonl, phase4_coverage_analysis.json, phase4_coverage_report.md and the standalone standard-library build_phase4.py in this directory.", "",
             "```powershell", "python -B -X utf8 outputs/dictionary_v2/phase4_coverage/build_phase4.py --verify", "```", "",
             "The builder creates outputs once; --refresh is available only for a targeted rebuild of the existing Phase 4 outputs after a builder fix, while --verify is read-only. It does not import or run the earlier builders and does not install packages or use APIs, embeddings or LLM semantic decisions. These proposals do not constitute a completed final dictionary.", ""]
    return "\n".join(rows).encode("utf-8")


def serialize(data, result, test_results):
    validation = validate(data, result)
    validation.update({"regression_tests": test_results, "protected_files_unchanged": True,
                       "source_and_phase_manifest_hashes_valid": True, "deterministic_second_run": True,
                       "json_jsonl_valid": True})
    result["analysis"]["validation_statistics"] = validation
    out = {}
    for name, key in ((OUTPUTS[0], "concepts"), (OUTPUTS[1], "variants"), (OUTPUTS[2], "queue")):
        out[name] = "".join(packed(x) + "\n" for x in result[key]).encode("utf-8")
    out[OUTPUTS[3]] = (json.dumps(result["analysis"], ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    out[OUTPUTS[4]] = make_report(data, result)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--refresh", action="store_true", help="Rebuild only the existing Phase 4 outputs after a builder fix")
    args = parser.parse_args()
    require(HERE == ROOT / "outputs/dictionary_v2/phase4_coverage", "Output location must remain Phase 4-specific")
    if not args.verify and not args.refresh:
        require(not any((HERE / name).exists() for name in OUTPUTS), "Existing output; use --verify")
    before = snapshot()
    print("Protected per-file baseline captured. Reading Phase 1/2/3 without running their builders.", flush=True)
    data = load_inputs()
    test_results = tests()
    first = build(data)
    bytes_first = serialize(data, first, test_results)
    print("First analysis validated. Running again with reversed input traversal.", flush=True)
    reversed_data = dict(data)
    for name in ("records", "sources", "concepts", "variants", "candidates"):
        reversed_data[name] = dict(reversed(list(data[name].items())))
    for name in ("deferred", "risk_cases"):
        reversed_data[name] = list(reversed(data[name]))
    second = build(reversed_data)
    bytes_second = serialize(reversed_data, second, test_results)
    require(bytes_first == bytes_second, "Second run is not byte-identical")
    require(before == snapshot(), "Protected file changed during analysis")
    if args.verify:
        for name, content in bytes_first.items():
            require((HERE / name).read_bytes() == content, "Saved output differs: " + name)
    else:
        for name, content in bytes_first.items():
            with (HERE / name).open("wb") as stream:
                stream.write(content)
    saved = {"concepts": list(lines(HERE / OUTPUTS[0])), "variants": list(lines(HERE / OUTPUTS[1])),
             "queue": list(lines(HERE / OUTPUTS[2])), "analysis": load_json(HERE / OUTPUTS[3])}
    validate(data, saved)
    require(before == snapshot(), "Protected file changed during output validation")
    require({p.name for p in HERE.iterdir()} == set(OUTPUTS) | {Path(__file__).name}, "Unexpected Phase 4 artifact")
    print(json.dumps({"status": "PASS", "mode": "verify" if args.verify else "build",
                      "existing_concepts_analyzed": len(data["concepts"]),
                      **first["analysis"]["candidate_counts"],
                      "existing_coverage": first["analysis"]["observations_represented_by_existing_concepts"],
                      "proposed_coverage": first["analysis"]["observations_with_proposed_concept_coverage"],
                      "unresolved_or_source_only": first["analysis"]["observations_still_unresolved"],
                      "protected_files_unchanged": len(before), "regression_tests": len(test_results),
                      "second_run_byte_identical": True}, indent=2), flush=True)


if __name__ == "__main__":
    main()
