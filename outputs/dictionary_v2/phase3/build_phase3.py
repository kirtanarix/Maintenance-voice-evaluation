"""Standalone Phase 3 builder/validator; Python standard library, no pipeline imports.

Run with python -B -X utf8 outputs/dictionary_v2/phase3/build_phase3.py
Use --verify to rebuild in memory and compare all saved outputs. Existing outputs
are never overwritten. Both modes check protected files and run regression tests.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "outputs/dictionary_v2"
VERSION = "phase3-v1"
SCHEMA = "dictionary_v2.phase3.1"
FILES = ("review_decisions.jsonl", "concepts.jsonl", "variants.jsonl",
         "instances.jsonl", "industry_associations.jsonl", "manifest.json",
         "phase3_report.md")
PHASE1 = ("phase1_inventory.json", "phase1_records.jsonl",
          "phase1_candidates.json", "phase1_report.md")
PHASE2 = ("phase2_candidate_analysis.json", "phase2_rule_proposals.json",
          "phase2_high_risk_cases.json", "phase2_exploration_report.md")
MISSING = {"", "na", "n/a", "n.a.", "not available", "not applicable", "nil",
           "nill", "none", "-", "--na--", "default manufacturer", "default fabrication"}
SPEC_HEADER = "TYPE AND CAPACITY OF FIRE EXTINGUISHER"
RULES = {
    "MAPPING": "Exactly two clean observations: one asset and one identifier_mapping; exactly one asset_tag and customer_tag in each, both exact pairs equal. Approve only co-observation of the pair within each row, never cross-source identity or scope equivalence.",
    "SEPARATION": "Clean asset observations in one source snapshot, same explicit company, distinct asset tags, no shared identifier literal across any namespace. Preserve registration separation; never apply across revised exports.",
    "SOURCE_COPY": "Clean observations from multiple sources in one source group have identical full raw cells. Approve identical source-observation content only; chronology, precedence and physical identity remain unknown.",
    "CONCEPT": "An asset's single exact name equals its sheet title, corroborated by at least two distinct asset tags in a source. No category promotion, label normalization, aliasing, industry mapping or unexplained suffix interpretation. Conflict/high-risk/parse-issue observations excluded.",
    "VARIANT": "Retain the exact non-placeholder value of an explicit TYPE AND CAPACITY OF FIRE EXTINGUISHER field only on the exact Fire Extinguisher concept. Parse only full unambiguous numeric-capacity/unit syntax; preserve other specifications as raw text.",
    "INSTANCE": "One clean tagged source registration per instance, with an evidenced concept; exact source-scoped tag ID. No source observations are combined. Cross-observation identity remains unresolved even if exports repeat.",
    "DEFER": "All other candidate proposals, all conflicting_identifier candidates and all five high-risk cases remain deferred. No automatic aliases, components, OEM model equivalence or industries.",
    "DISPOSITION": "Every Phase 1 record receives exactly one disposition, either represented by canonical entries or retained only as immutable source evidence. This does not require manual classification of every source-only row.",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable(prefix, *parts):
    return prefix + "_" + hashlib.sha256(packed(parts).encode("utf-8")).hexdigest()[:24]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def protected_fingerprint():
    """Hash every project file outside Phase 3, including pipeline, audio and git."""
    h, count = hashlib.sha256(), 0
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and not path.is_relative_to(HERE):
            # This ordering/encoding also permits an independent before/after audit.
            item = [path.relative_to(ROOT).as_posix(), sha(path)]
            h.update(json.dumps(item, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
            count += 1
    return {"files": count, "sha256": h.hexdigest()}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def useful(value):
    return value is not None and str(value).strip().casefold() not in MISSING


def observations(record, field):
    return record["derived"][field]


def values(record, field):
    return tuple(x["value_raw"] for x in observations(record, field))


def identifiers(record, namespace=None):
    return [x for x in observations(record, "identifiers")
            if useful(x["value_raw"]) and (namespace is None or x["namespace"] == namespace)]


def pair(record):
    tags, customers = identifiers(record, "asset_tag"), identifiers(record, "customer_tag")
    if len(tags) == len(customers) == 1:
        return tags[0]["value_raw"], customers[0]["value_raw"]
    return None


def source_evidence(record, columns=()):
    return {"record_id": record["record_id"], "source_id": record["source_id"],
            "source_group": record["source_group"], "filename": record["filename"],
            "sheet": record["sheet"], "row_number": record["row_number"],
            "column_indices": sorted(set(columns))}


def identifier_evidence(record, item):
    return {"record_id": record["record_id"], "column_index": item["column_index"],
            "namespace": item["namespace"], "value_raw": item["value_raw"],
            "header_raw": record["cells"][item["column_index"]]["header_raw"],
            "scope": {"source_group": record["source_group"], "source_id": record["source_id"],
                      "company_values_raw": list(values(record, "company_observations")),
                      "global_uniqueness": False}}


def load_inputs():
    hashes1 = {name: sha(BASE / "phase1" / name) for name in PHASE1}
    hashes2 = {name: sha(BASE / "phase2_exploration" / name) for name in PHASE2}
    inventory = read_json(BASE / "phase1/phase1_inventory.json")
    payload = read_json(BASE / "phase1/phase1_candidates.json")
    analysis = read_json(BASE / "phase2_exploration/phase2_candidate_analysis.json")
    rules = read_json(BASE / "phase2_exploration/phase2_rule_proposals.json")
    risks = read_json(BASE / "phase2_exploration/phase2_high_risk_cases.json")
    require(hashes1 == analysis["input_phase1_sha256"], "Phase 1 differs from Phase 2 pinned inputs")
    for filename in (BASE / "phase1/phase1_report.md",
                     BASE / "phase2_exploration/phase2_exploration_report.md",
                     BASE / "phase3_exploration/phase3_exploration_report.md"):
        filename.read_text(encoding="utf-8")
    source_root = ROOT / "inputs/dictionary_v2"
    sources = {s["source_id"]: s for s in inventory["sources"]}
    require(len(sources) == len(inventory["sources"]), "Duplicate source IDs")
    for source in sources.values():
        require(sha(source_root / source["relative_path"]) == source["sha256"], "Source file hash changed")
    known = {s["relative_path"] for s in sources.values()}
    extras = sorted(p.relative_to(source_root).as_posix() for p in source_root.rglob("*")
                    if p.is_file() and p.relative_to(source_root).as_posix() not in known)
    require(all(Path(p).name.startswith(".~lock.") and p.endswith("#") for p in extras),
            "Uninventoried source input; ingestion scope requires review")
    records, counts = {}, Counter()
    with (BASE / "phase1/phase1_records.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            raw = json.loads(line)
            rid = raw["record_id"]
            require(rid not in records and raw["source_id"] in sources, "Invalid record identity")
            require(raw["source_group"] == sources[raw["source_id"]]["company_source_group"], "Source group mismatch")
            # Keep only relevant raw cells in memory. The immutable source JSONL remains authoritative.
            cols = {x["column_index"] for group in raw["derived"].values() if isinstance(group, list)
                    for x in group if isinstance(x, dict) and "column_index" in x}
            cols.update(c["column_index"] for c in raw["raw_cells"] if c["header_raw"] == SPEC_HEADER)
            compact = {k: raw[k] for k in ("record_id", "source_id", "source_group", "filename", "sheet",
                                           "row_number", "record_kind", "derived")}
            compact["cells"] = {c["column_index"]: c for c in raw["raw_cells"] if c["column_index"] in cols}
            compact["raw_signature"] = stable("raw", raw["raw_cells"])
            compact["parse_issue"] = raw.get("parse_issue")
            for group in raw["derived"].values():
                if isinstance(group, list):
                    for obs in group:
                        if "column_index" in obs:
                            require(compact["cells"][obs["column_index"]]["value_raw"] == obs["value_raw"],
                                    "Derived value does not match raw cell")
            records[rid] = compact
            counts[raw["source_id"]] += 1
    require(all(counts[sid] == s["record_count"] for sid, s in sources.items()), "Source counts mismatch")
    candidates = {c["candidate_id"]: c for c in payload["candidates"]}
    proposals = {c["candidate_id"]: c for c in analysis["candidates"]}
    require(len(candidates) == len(payload["candidates"]) == payload["candidate_count"], "Candidate count mismatch")
    require(len(proposals) == len(analysis["candidates"]) == analysis["candidate_count"], "Proposal count mismatch")
    require(candidates.keys() == proposals.keys(), "Phase 2 candidate coverage mismatch")
    for cid, c in candidates.items():
        require(len(c["record_ids"]) >= 2 and len(set(c["record_ids"])) == len(c["record_ids"])
                and set(c["record_ids"]) <= records.keys(), "Invalid candidate members")
        require(set(c["record_ids"]) == set(proposals[cid]["source_record_ids"])
                and c["candidate_type"] == proposals[cid]["candidate_type"], "Proposal membership mismatch")
        require(c["status"] == "needs_review", "Unexpected Phase 1 applied decision")
    require(len(risks["cases"]) == risks["case_count"] == 5, "Expected five high-risk cases")
    require(len({c["case_id"] for c in risks["cases"]}) == 5, "Duplicate high-risk IDs")
    require(all(set(c["source_record_ids"]) <= records.keys() for c in risks["cases"]), "Bad risk reference")
    require(len(rules["rules"]) == rules["rule_count"], "Rule count mismatch")
    blocked = set().union(*(set(c["record_ids"]) for c in candidates.values()
                            if c["candidate_type"] == "conflicting_identifier"),
                          *(set(c["source_record_ids"]) for c in risks["cases"]))
    blocked.update(rid for rid, r in records.items() if r["parse_issue"])
    # Detect conflicting same-namespace values in a single row as well.
    for rid, record in records.items():
        by_ns = defaultdict(set)
        for item in identifiers(record):
            by_ns[item["namespace"]].add(packed(item["value_raw"]))
        if any(len(v) > 1 for v in by_ns.values()):
            blocked.add(rid)
    scoped_tags = defaultdict(set)
    for rid, record in records.items():
        for item in identifiers(record, "asset_tag"):
            scoped_tags[(record["source_id"], packed(item["value_raw"]))].add(rid)
    for members in scoped_tags.values():
        if len(members) > 1:
            blocked.update(members)
    return {"records": records, "candidates": candidates, "proposals": proposals,
            "risks": risks["cases"], "blocked": blocked, "inventory": inventory,
            "hashes1": hashes1, "hashes2": hashes2, "ignored_lock_files": extras,
            "exploration_hash": sha(BASE / "phase3_exploration/phase3_exploration_report.md")}


def relationship_rule(candidate, proposal, members, blocked):
    if any(r["record_id"] in blocked or r.get("parse_issue") for r in members):
        return None, "Conflict, high-risk or parse-issue observation: retain unresolved."
    if candidate["candidate_type"] == "conflicting_identifier":
        return None, "Conflicting identifier remains unresolved."
    if proposal["confidence"] != "high":
        return None, "No evidence-backed rule authorizes this alias, identity or unresolved proposal."
    relation = proposal["proposed_relationship"]
    if len({r["source_group"] for r in members}) != 1:
        return None, "Cross-group relationship is not established."
    if relation == "IDENTIFIER_MAPPING":
        if len(members) == 2 and sorted(r["record_kind"] for r in members) == ["asset", "identifier_mapping"]:
            pairs = [pair(r) for r in members]
            if pairs[0] is not None and pairs[0] == pairs[1]:
                return "MAPPING", "The same exact asset-tag/customer-tag pair is explicitly co-observed in each row; no record identity is asserted."
        return None, "A shared identifier alone does not validate an unambiguous explicit mapping pair."
    if relation == "SOURCE_VERSION_DUPLICATE":
        if len({r["source_id"] for r in members}) > 1 and len({r["raw_signature"] for r in members}) == 1:
            return "SOURCE_COPY", "Full raw cell content is identical across sources; version order and physical identity remain unknown."
        return None, "Full raw content does not establish a cross-source identical-observation relationship."
    if relation == "DIFFERENT_ASSET_INSTANCES":
        if (all(r["record_kind"] == "asset" for r in members)
                and len({r["source_id"] for r in members}) == 1
                and all(values(r, "company_observations") for r in members)
                and len({values(r, "company_observations") for r in members}) == 1
                and all(len(identifiers(r, "asset_tag")) == 1 for r in members)):
            literals = [set(packed(x["value_raw"]) for x in identifiers(r)) for r in members]
            if sum(map(len, literals)) == len(set().union(*literals)):
                return "SEPARATION", "Separate tagged registrations in one source snapshot; preserve separation without claiming cross-export physical distinctness."
        return None, "Different tags across revisions, shared identifiers or incomplete scope do not establish distinct instances."
    return None, "No automatic rule for this proposal."


def make_decision(kind, key, relation, status, ids, reason, rule, confidence="high", candidate=None):
    return {"decision_id": stable("decision", VERSION, kind, key), "decision_kind": kind,
            "source_candidate_id": candidate, "relationship_type": relation, "status": status,
            "confidence": confidence, "source_record_ids": sorted(ids), "target_record_ids": [],
            "reason": reason, "evidence": [], "rule_id": rule, "rule_version": VERSION,
            "approval_basis": "user-authorized evidence rule; not manual record review" if status == "approved" else None}


def specification(record):
    cells = [c for c in record["cells"].values() if c["header_raw"] == SPEC_HEADER and useful(c["value_raw"])]
    return cells[0] if len(cells) == 1 else None


def attributes(label):
    # No fuzzy parsing, suffix removal, code expansion, unit conversion or aliasing.
    match = re.fullmatch(r"([A-Z][A-Z0-9 /]*) ([0-9]+(?:\.[0-9]+)?)\s*(KG|Kg|Ltr)", label)
    if match:
        return {"type_code_raw": match[1], "capacity": {"value_raw": match[2], "unit_raw": match[3]}}
    return {"specification_raw": label}


def canonical_entries(data):
    records, blocked = data["records"], data["blocked"]
    cohorts = defaultdict(list)
    for rid, record in records.items():
        if rid in blocked or record["record_kind"] != "asset" or len(identifiers(record, "asset_tag")) != 1:
            continue
        names = values(record, "asset_name_candidates")
        if (len(names) == 1 and names[0] == record["sheet"] and isinstance(names[0], str)
                and re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*", names[0])):
            cohorts[names[0]].append(rid)
    concepts, variants, instances, refs = [], {}, [], {}
    for label, rids in sorted(cohorts.items()):
        by_source = defaultdict(set)
        for rid in rids:
            r = records[rid]
            by_source[r["source_id"]].add(packed(identifiers(r, "asset_tag")[0]["value_raw"]))
        if not any(len(tags) >= 2 for tags in by_source.values()):
            continue
        cid = stable("concept", "exact-source-equipment-name", label)
        concepts.append({"concept_id": cid, "preferred_name": label, "aliases": [],
                         "source_record_ids": sorted(rids), "status": "approved", "rule_id": "CONCEPT",
                         "decision_ids": sorted(stable("decision", VERSION, "source_disposition", rid) for rid in rids)})
        for rid in sorted(rids):
            record = records[rid]
            did = stable("decision", VERSION, "source_disposition", rid)
            spec = specification(record) if label == "Fire Extinguisher" else None
            vid = None
            if spec:
                raw_label = str(spec["value_raw"])
                vid = stable("variant", cid, "exact-source-specification", raw_label)
                if vid not in variants:
                    variants[vid] = {"variant_id": vid, "concept_id": cid, "label": raw_label,
                                     "attributes": attributes(raw_label), "source_record_ids": [],
                                     "decision_ids": [], "status": "approved", "rule_id": "VARIANT"}
                variants[vid]["source_record_ids"].append(rid)
                variants[vid]["decision_ids"].append(did)
            tag = identifiers(record, "asset_tag")[0]
            # Source-scoped registrations intentionally do not deduplicate snapshots.
            iid = stable("instance", record["source_group"], record["source_id"], "asset_tag", tag["value_raw"])
            instance = {"instance_id": iid, "concept_id": cid, "variant_id": vid,
                        "company_id": None, "company_observations": list(observations(record, "company_observations")),
                        "manufacturer": None, "model": None,
                        "manufacturer_observations": list(observations(record, "manufacturer_observations")),
                        "model_observations": list(observations(record, "model_observations")),
                        "identifiers": [identifier_evidence(record, x) for x in identifiers(record)],
                        "locations": list(observations(record, "location_observations")),
                        "source_record_ids": [rid], "decision_ids": [did],
                        "resolution_status": "unresolved", "registration_status": "source_evidenced",
                        "identity_scope": "single_source_registration; cross-observation identity unresolved",
                        "rule_id": "INSTANCE"}
            instances.append(instance)
            refs[rid] = {"concept_id": cid, "variant_id": vid, "instance_id": iid}
    # Repeated tags inside a source must never generate colliding instance IDs.
    duplicates = {key for key, n in Counter(x["instance_id"] for x in instances).items() if n > 1}
    require(not duplicates, "Duplicate scoped registration key requires unresolved handling")
    for variant in variants.values():
        variant["source_record_ids"].sort()
        variant["decision_ids"].sort()
    return concepts, list(variants.values()), instances, refs


def build(data):
    records = data["records"]
    concepts, variants, instances, refs = canonical_entries(data)
    decisions = []
    for cid, candidate in sorted(data["candidates"].items()):
        proposal = data["proposals"][cid]
        ids = sorted(candidate["record_ids"])
        members = [records[rid] for rid in ids]
        rule, reason = relationship_rule(candidate, proposal, members, data["blocked"])
        d = make_decision("candidate_relationship", cid, proposal["proposed_relationship"],
                          "approved" if rule else "deferred", ids, reason, rule or "DEFER",
                          proposal["confidence"], cid)
        d["phase2_automation_status"] = proposal["automation_status"]
        d["evidence"] = [source_evidence(r, [x["column_index"] for x in identifiers(r)]) for r in members]
        d["relationship_semantics"] = {"asset_merge": False, "physical_identity_asserted": False,
                                       "version_precedence": None}
        if rule == "MAPPING":
            d["identifier_pairs"] = [{"record_id": r["record_id"], "association_scope": "within_this_observation",
                                       "identifiers": [identifier_evidence(r, x) for x in identifiers(r)
                                                       if x["namespace"] in {"asset_tag", "customer_tag"}]} for r in members]
        if rule == "SOURCE_COPY":
            d["evidence_basis"] = "full_raw_cells_equal; no chronology established"
        decisions.append(d)
    for case in sorted(data["risks"], key=lambda x: x["case_id"]):
        d = make_decision("high_risk_case", case["case_id"], "UNRESOLVED", "deferred",
                          case["source_record_ids"], case["problem"], "DEFER", "low")
        d["high_risk_case_id"] = case["case_id"]
        d["open_question"] = case["open_question"]
        d["evidence"] = [source_evidence(records[rid]) for rid in sorted(case["source_record_ids"])]
        decisions.append(d)
    for rid, record in sorted(records.items()):
        represented = rid in refs
        reason = ("Exact name/sheet and registered-tag evidence supports the concept and one source registration; physical identity across observations is unresolved."
                  if represented else "Retained in immutable Phase 1 only; no canonical identity or meaning is asserted by the current evidence rules.")
        if rid in data["blocked"]:
            reason = "Conflict, high-risk or parse issue retained unresolved; no canonical materialization."
        d = make_decision("source_disposition", rid, "SOURCE_OBSERVATION", "approved" if represented else "deferred",
                          [rid], reason, "DISPOSITION", "high" if represented else "low")
        d["disposition"] = "represented_source_registration" if represented else "source_evidence_only"
        d["record_kind"] = record["record_kind"]
        d["canonical_references"] = refs.get(rid, {})
        d["source_industry_evidence"] = record["derived"]["industry_evidence"]
        columns = [x["column_index"] for x in observations(record, "asset_name_candidates")]
        columns += [x["column_index"] for x in identifiers(record)]
        spec = specification(record)
        if represented and spec:
            columns.append(spec["column_index"])
        d["evidence"] = [source_evidence(record, columns)]
        decisions.append(d)
    return {"review_decisions.jsonl": sorted(decisions, key=lambda x: x["decision_id"]),
            "concepts.jsonl": sorted(concepts, key=lambda x: x["concept_id"]),
            "variants.jsonl": sorted(variants, key=lambda x: x["variant_id"]),
            "instances.jsonl": sorted(instances, key=lambda x: x["instance_id"]),
            "industry_associations.jsonl": []}


def validate(data, output):
    records = data["records"]
    decisions = output["review_decisions.jsonl"]
    all_decision_ids = {d["decision_id"] for d in decisions}
    maps = {}
    for filename, key in (("review_decisions.jsonl", "decision_id"), ("concepts.jsonl", "concept_id"),
                          ("variants.jsonl", "variant_id"), ("instances.jsonl", "instance_id"),
                          ("industry_associations.jsonl", "association_id")):
        rows = output[filename]
        maps[key] = {r[key]: r for r in rows}
        require(len(maps[key]) == len(rows), "Duplicate " + key)
        for row in rows:
            require(set(row["source_record_ids"]) <= records.keys(), "Invalid source reference")
            require(set(row.get("decision_ids", [])) <= all_decision_ids, "Invalid decision reference")
    decision_ids = maps["decision_id"].keys()
    candidate_rows = [d for d in decisions if d["decision_kind"] == "candidate_relationship"]
    require(Counter(d["source_candidate_id"] for d in candidate_rows) == Counter({cid: 1 for cid in data["candidates"]}),
            "Incomplete candidate disposition")
    for d in decisions:
        require(d["status"] in {"approved", "rejected", "deferred"} and d["rule_version"] == VERSION, "Bad decision status/version")
        require(set(d["target_record_ids"]) <= records.keys(), "Invalid target record")
        for ev in d["evidence"]:
            require(ev["record_id"] in d["source_record_ids"], "Evidence outside decision")
            r = records[ev["record_id"]]
            require(ev == source_evidence(r, ev["column_indices"]), "Incorrect evidence coordinates")
            require(set(ev["column_indices"]) <= r["cells"].keys(), "Invalid evidence columns")
    for d in candidate_rows:
        c = data["candidates"][d["source_candidate_id"]]
        p = data["proposals"][d["source_candidate_id"]]
        require(set(d["source_record_ids"]) == set(c["record_ids"]), "Candidate members changed")
        members = [records[rid] for rid in sorted(c["record_ids"])]
        rule, _ = relationship_rule(c, p, members, data["blocked"])
        require(d["status"] == ("approved" if rule else "deferred") and d["rule_id"] == (rule or "DEFER"), "Unsupported approval")
        require(d["relationship_type"] == p["proposed_relationship"], "Relationship changed")
        require(d["relationship_semantics"] == {"asset_merge": False, "physical_identity_asserted": False,
                                                "version_precedence": None}, "Unauthorized identity assertion")
        if rule == "MAPPING":
            expected = [{"record_id": r["record_id"], "association_scope": "within_this_observation",
                         "identifiers": [identifier_evidence(r, x) for x in identifiers(r)
                                         if x["namespace"] in {"asset_tag", "customer_tag"}]} for r in members]
            require(d["identifier_pairs"] == expected, "Mapping namespace/value/scope changed")
    dispositions = [d for d in decisions if d["decision_kind"] == "source_disposition"]
    require(Counter(rid for d in dispositions for rid in d["source_record_ids"]) == Counter({rid: 1 for rid in records}),
            "Source record missing or duplicated in disposition ledger")
    for d in dispositions:
        require(len(d["source_record_ids"]) == 1, "Disposition combines observations")
        rid = d["source_record_ids"][0]
        require(d["source_industry_evidence"] == records[rid]["derived"]["industry_evidence"], "Industry evidence changed")
        for key, value in d["canonical_references"].items():
            require(value is None or value in maps[key], "Invalid canonical reference")
            if value is not None:
                require(rid in maps[key][value]["source_record_ids"], "Canonical provenance mismatch")
    risk_rows = [d for d in decisions if d["decision_kind"] == "high_risk_case"]
    require(Counter(d["high_risk_case_id"] for d in risk_rows) == Counter({r["case_id"]: 1 for r in data["risks"]}), "Risk case lost")
    for case in data["risks"]:
        d = next(d for d in risk_rows if d["high_risk_case_id"] == case["case_id"])
        require(d["status"] == "deferred" and set(d["source_record_ids"]) == set(case["source_record_ids"]), "Risk silently resolved")
    require(len(decisions) == len(candidate_rows) + len(dispositions) + len(risk_rows), "Unexpected decision type")
    for concept in output["concepts.jsonl"]:
        require(concept["aliases"] == [], "Unapproved alias")
        for rid in concept["source_record_ids"]:
            r = records[rid]
            require(values(r, "asset_name_candidates") == (concept["preferred_name"],)
                    and r["sheet"] == concept["preferred_name"] and rid not in data["blocked"], "Unsupported concept")
    for variant in output["variants.jsonl"]:
        require(variant["concept_id"] in maps["concept_id"], "Invalid variant concept")
        require(variant["attributes"] == attributes(variant["label"]), "Guessed specification attributes")
        for rid in variant["source_record_ids"]:
            spec = specification(records[rid])
            require(spec is not None and spec["value_raw"] == variant["label"], "Specification differs from evidence")
    represented = set()
    for instance in output["instances.jsonl"]:
        require(instance["concept_id"] in maps["concept_id"], "Invalid instance concept")
        if instance["variant_id"] is not None:
            require(instance["variant_id"] in maps["variant_id"] and
                    maps["variant_id"][instance["variant_id"]]["concept_id"] == instance["concept_id"], "Invalid instance variant")
        require(len(instance["source_record_ids"]) == 1, "Source observations merged into instance")
        rid = instance["source_record_ids"][0]
        require(rid not in represented and rid not in data["blocked"], "Duplicate or risky registration")
        represented.add(rid)
        r = records[rid]
        require(instance["identifiers"] == [identifier_evidence(r, x) for x in identifiers(r)], "Identifier namespace/value/scope altered")
        require(instance["manufacturer"] is None and instance["model"] is None, "OEM identity guessed")
        for dst, src in (("manufacturer_observations", "manufacturer_observations"),
                         ("model_observations", "model_observations"), ("company_observations", "company_observations"),
                         ("locations", "location_observations")):
            require(instance[dst] == observations(r, src), "Raw observation changed")
        require(instance["resolution_status"] == "unresolved", "Cross-observation identity resolved without authority")
    require(represented == {d["source_record_ids"][0] for d in dispositions if d["canonical_references"]}, "Disposition coverage mismatch")
    require(output["industry_associations.jsonl"] == [], "No sufficient industry evidence rule approved")
    return {"status": "PASS", "source_references": True, "candidate_and_decision_references": True,
            "unique_entity_ids": True, "concept_variant_instance_links": True,
            "identifier_namespaces_values_and_scopes_preserved": True,
            "all_records_have_dispositions": True, "all_five_high_risk_cases_deferred": True,
            "no_instance_merges": True, "no_unsupported_aliases_or_industries": True}


def encode_jsonl(rows):
    return ("".join(packed(row) + "\n" for row in rows)).encode("utf-8")


def regression_tests():
    """Exercise safety boundaries with synthetic records, never project files."""
    def row(rid, kind="asset", source="source-one", tag="TAG-01", customer="SS--S-6"):
        items = [{"namespace": "asset_tag", "value_raw": tag, "column_index": 1},
                 {"namespace": "customer_tag", "value_raw": customer, "column_index": 2}]
        return {"record_id": rid, "record_kind": kind, "source_id": source, "source_group": "Live Company",
                "raw_signature": "same", "parse_issue": None,
                "derived": {"identifiers": items, "company_observations": [{"value_raw": "Company"}]}}
    c = {"candidate_type": "possible_same_instance"}
    proposal = {"confidence": "high", "proposed_relationship": "IDENTIFIER_MAPPING"}
    left, right = row("left"), row("right", "identifier_mapping", "source-two")
    tests = []
    def check(name, condition):
        require(condition, "Regression failed: " + name)
        tests.append(name)
    check("explicit_pair", relationship_rule(c, proposal, [left, right], set())[0] == "MAPPING")
    for variant in ("SS-S-6", "SS--S-06", "ss--s-6"):
        changed = row("right", "identifier_mapping", "source-two", customer=variant)
        check("exact_identifier_" + variant, relationship_rule(c, proposal, [left, changed], set())[0] is None)
    check("blocked_mapping", relationship_rule(c, proposal, [left, right], {"left"})[0] is None)
    cross = copy.deepcopy(right); cross["source_group"] = "Demo Company"
    check("cross_group_mapping", relationship_rule(c, proposal, [left, cross], set())[0] is None)
    duplicate = copy.deepcopy(right); duplicate["derived"]["identifiers"].append(copy.deepcopy(duplicate["derived"]["identifiers"][0]))
    check("ambiguous_pair", relationship_rule(c, proposal, [left, duplicate], set())[0] is None)
    check("mapping_placeholder", pair(row("placeholder", tag="N/A")) is None)
    sep = {"confidence": "high", "proposed_relationship": "DIFFERENT_ASSET_INSTANCES"}
    second = row("second", tag="TAG-02", customer="SS-S-7")
    check("separate_snapshot", relationship_rule(c, sep, [left, second], set())[0] == "SEPARATION")
    second["source_id"] = "revision"
    check("revision_not_distinct", relationship_rule(c, sep, [left, second], set())[0] is None)
    second["source_id"] = left["source_id"]; second["derived"]["identifiers"][1]["value_raw"] = "TAG-01"
    check("cross_namespace_collision", relationship_rule(c, sep, [left, second], set())[0] is None)
    version = {"confidence": "high", "proposed_relationship": "SOURCE_VERSION_DUPLICATE"}
    check("identical_source_content", relationship_rule(c, version, [left, right], set())[0] == "SOURCE_COPY")
    changed = copy.deepcopy(right); changed["raw_signature"] = "changed"
    check("content_difference", relationship_rule(c, version, [left, changed], set())[0] is None)
    for relation in ("ALIAS_CANDIDATE", "SAME_ASSET_INSTANCE_CANDIDATE", "UNRESOLVED", "COMPONENT_OF"):
        check("defer_" + relation, relationship_rule(c, {"confidence": "high", "proposed_relationship": relation}, [left, right], set())[0] is None)
    check("suffix_not_interpreted", attributes("ABC 6KG (M)") == {"specification_raw": "ABC 6KG (M)"})
    check("capacity_preserved", attributes("CO2 4.5KG")["capacity"] == {"value_raw": "4.5", "unit_raw": "KG"})
    check("punctuation_ids_distinct", stable("instance", "SS--S-6") != stable("instance", "SS-S-6"))
    check("capacity_ids_distinct", stable("variant", "ABC 6KG") != stable("variant", "ABC 9KG"))
    return tests


def report(data, output, validation, tests, protected):
    candidates = [d for d in output["review_decisions.jsonl"] if d["decision_kind"] == "candidate_relationship"]
    counts = Counter((d["relationship_type"], d["status"]) for d in candidates)
    approved = sum(d["status"] == "approved" for d in candidates)
    rows = ["# Dictionary v2 — Phase 3 report", "", "## Purpose and scope", "",
            "Phase 3 creates an evidence-supported reference layer without modifying or merging source observations. No extraction/evaluation or Gemini integration was changed.", "",
            "## Inputs and outputs", "",
            "Inputs: all four immutable Phase 1 artifacts, all four Phase 2 artifacts, and the Phase 3 exploration report. Source bytes were checked against the Phase 1 inventory. Manifest hashes identify the exact inputs and builder.", "",
            "Outputs: review_decisions.jsonl, concepts.jsonl, variants.jsonl, instances.jsonl, industry_associations.jsonl, manifest.json, and this report. The only additional artifact is build_phase3.py, containing the builder, validator and regression tests.", "",
            "## Counts", "", "| Item | Count |", "|---|---:|",
            f"| Source files | {len(data['inventory']['sources']):,} |",
            f"| Source observations | {len(data['records']):,} |",
            f"| Candidate relationships | {len(candidates):,} |",
            f"| Approved candidate relationships | {approved:,} |",
            f"| Deferred candidate relationships | {len(candidates)-approved:,} |"]
    for filename, records in output.items():
        rows.append(f"| {filename} records | {len(records):,} |")
    rows += ["", "Review decisions contain one decision per candidate, one disposition per source observation, and five deferred high-risk cases. Source-only dispositions are not additional candidate relationships and do not imply a requirement to manually classify every record.", "",
             "| Relationship | Approved | Deferred |", "|---|---:|---:|"]
    for relation in sorted({d["relationship_type"] for d in candidates}):
        rows.append(f"| {relation} | {counts[relation, 'approved']:,} | {counts[relation, 'deferred']:,} |")
    rows += ["", "## Canonical evidence", "",
             "Concepts require exact agreement between an item name and sheet title, corroborated by distinct registered tags in a source. Source categories alone are not promoted. Conflict/high-risk records are excluded. No case, spelling or punctuation aliases are created.", "",
             "| Concept (exact source label) | Source registrations |", "|---|---:|"]
    rows += [f"| {c['preferred_name']} | {len(c['source_record_ids']):,} |" for c in output["concepts.jsonl"]]
    rows += ["", "Variants retain exact values from the explicit extinguisher type/capacity field. Only unambiguous full capacity syntax is parsed; raw codes and units are retained, and unexplained suffixes remain uninterpreted. Formatting variants are not silently equated.", "",
             "| Variant (exact source label) | Source registrations |", "|---|---:|"]
    rows += [f"| {v['label']} | {len(v['source_record_ids']):,} |" for v in output["variants.jsonl"]]
    rows += ["", "Instances are source-scoped registered-asset representations, each supported by one observation. Their cross-observation identity is unresolved. Repeated exports can represent the same physical asset multiple times: the instance count is NOT a deduplicated physical-asset total. All instances reference an existing concept; a variant is optional.", "",
             "Manufacturer and model source observations are retained separately. Canonical manufacturer/model remain null because source labels do not establish OEM identities. Company remains an observation rather than an invented company registry.", "",
             "Industry associations: zero. Filename-only industry annotations remain verbatim in source dispositions, including Phase 1's certainty, without becoming canonical claims.", "",
             "## Applied boundaries and preserved conflicts", "",
             "Identifier mappings express the exact pair co-observed within each source row; they do not unify identifier scopes, source records or physical assets. Source-version proposals are approved only as identical full raw-cell content, without chronology or precedence. Separation approvals are restricted to one source snapshot, not revised exports.", "",
             "All five high-risk cases remain deferred: Adani 1000117336; Cool Kit SS--S-6/SS-S-6 and 1208--W-2/1208-W-2; conflicting identifier clusters; textual aliases; repeated raw names. All conflicting_identifier candidate groups remain deferred. No component/assembly relationships or semantic aliases are created.", "",
             "Phase 2 confidence is not authority: every approved relationship passed an independent raw-evidence rule. Source-version duplicates and mappings never trigger instance union. Deferred candidates keep all original member IDs.", "",
             "## Validation", "",
             f"Validation: **{validation['status']}**. {len(tests)} embedded safety regression tests passed. All JSON/JSONL outputs were parsed and structurally validated. Two in-memory builds, with reversed record/candidate/proposal input order on the second run, produced byte-identical data artifacts and identical IDs. Saved files are validated again on disk.", "",
             "Validated: input hashes and source counts; complete candidate coverage; every record's disposition; valid source/candidate/decision references; unique entity IDs; concept/variant/instance links; exact identifier namespaces, values and scopes; preserved raw manufacturer/model observations; all five high-risk cases deferred; no multi-observation instance merges; no unsupported industries or aliases.", "",
             f"The protected-file fingerprint covers {protected['files']:,} files outside this directory, including inputs, Phase 1/2, exploration, Python pipeline, audio and repository metadata. Before/after SHA-256 equality is required for a successful run. Original source files and Phase 1/2 artifacts were not modified.", "",
             "## Limitations", "",
             "This is deliberately a small canonical dictionary, not comprehensive semantic classification of all 42,050 asset observations. Unknowns and unsupported concepts remain source evidence. The GSPL malformed CSV row and unnamed cells remain unresolved; no ingestion repair was attempted. Phase 2's missing generator and repeated rule examples are not treated as authoritative semantic evidence. Temporary spreadsheet lock files are ignored as inputs but preserved.", "",
             "No final flat dictionary or prompt export is generated. Broader concepts, semantic aliases, resolved physical identities and industries need stronger project evidence. No external services, database, embeddings, RAG or APIs are used.", "",
             "## Reproduce and verify", "", "From the project root:", "", "```powershell",
             "python -B -X utf8 outputs/dictionary_v2/phase3/build_phase3.py --verify", "```", "",
             "The builder refuses to overwrite any existing output. --verify is read-only: it rebuilds twice in memory, validates existing artifacts and compares bytes, including the manifest and report. Do not delete reviewed outputs merely to rerun the build.", ""]
    return "\n".join(rows).encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Read-only rerun and byte comparison")
    args = parser.parse_args()
    require(HERE == ROOT / "outputs/dictionary_v2/phase3", "Builder must stay in the authorized output directory")
    if not args.verify:
        require(not any((HERE / name).exists() for name in FILES), "Outputs already exist; use --verify")
    before = protected_fingerprint()
    print("Protected baseline captured; loading immutable inputs.", flush=True)
    data = load_inputs()
    tests = regression_tests()
    first = build(data)
    validation = validate(data, first)
    encoded = {name: encode_jsonl(rows) for name, rows in first.items()}
    print("First build validated; checking deterministic rerun with reversed input order.", flush=True)
    reordered = dict(data)
    for key in ("records", "candidates", "proposals"):
        reordered[key] = dict(reversed(list(data[key].items())))
    reordered["risks"] = list(reversed(data["risks"]))
    second = build(reordered)
    validate(data, second)
    require(encoded == {name: encode_jsonl(rows) for name, rows in second.items()}, "Nondeterministic data output")
    validation.update({"json_jsonl_valid": True, "deterministic_reordered_rerun": True,
                       "protected_files_unchanged": True, "source_hashes_match_phase1": True,
                       "phase1_hashes_match_phase2": True, "regression_tests_passed": tests})
    encoded["phase3_report.md"] = report(data, first, validation, tests, before)
    candidate_rows = [d for d in first["review_decisions.jsonl"] if d["decision_kind"] == "candidate_relationship"]
    manifest = {"schema_version": SCHEMA, "phase_version": "Phase 3", "rule_version": VERSION,
                "phase1_input_sha256": data["hashes1"], "phase2_input_sha256": data["hashes2"],
                "phase3_exploration_sha256": data["exploration_hash"], "builder_sha256": sha(Path(__file__)),
                "source_file_counts": dict(Counter(s["company_source_group"] for s in data["inventory"]["sources"])),
                "source_record_counts": dict(Counter(r["record_kind"] for r in data["records"].values())),
                "source_group_record_counts": dict(Counter(r["source_group"] for r in data["records"].values())),
                "source_record_count": len(data["records"]), "candidate_count": len(data["candidates"]),
                "candidate_decisions": dict(Counter(d["status"] for d in candidate_rows)),
                "output_record_counts": {name: len(rows) for name, rows in first.items()},
                "output_sha256": {name: hashlib.sha256(content).hexdigest() for name, content in encoded.items()},
                "protected_project_fingerprint": before, "ignored_source_lock_files": data["ignored_lock_files"],
                "rules": RULES, "validation": validation,
                "timestamp_policy": "Omitted so identical inputs produce byte-identical results",
                "identity_policy": "Exact source labels/specifications; source-scoped tags; no physical instance merges"}
    encoded["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    require(before == protected_fingerprint(), "Protected files changed during build")
    if args.verify:
        for name, content in encoded.items():
            require((HERE / name).read_bytes() == content, "Saved artifact differs from deterministic build: " + name)
    else:
        for name, content in encoded.items():
            with (HERE / name).open("xb") as stream:
                stream.write(content)
    disk = {}
    for name in first:
        with (HERE / name).open(encoding="utf-8") as stream:
            disk[name] = [json.loads(line) for line in stream]
    validate(data, disk)
    require(read_json(HERE / "manifest.json") == manifest, "Manifest round-trip mismatch")
    require(before == protected_fingerprint(), "Protected files changed during output verification")
    require({p.name for p in HERE.iterdir()} == set(FILES) | {Path(__file__).name}, "Unexpected extra artifact")
    print(json.dumps({"status": "PASS", "mode": "verify" if args.verify else "build",
                      "output_record_counts": manifest["output_record_counts"],
                      "candidate_decisions": manifest["candidate_decisions"],
                      "regression_tests": len(tests), "protected_files": before["files"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
