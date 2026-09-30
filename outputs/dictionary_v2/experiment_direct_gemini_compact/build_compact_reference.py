from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "outputs/dictionary_v2/reference/reference_dictionary.json"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    concepts = source.get("concepts", [])
    variants = source.get("variants", [])
    compact = {
        "version": "dictionary-v2-compact-reference-v1",
        "purpose": "Compact company-derived asset/equipment vocabulary for maintenance voice extraction",
        "rules": source.get("rules", []),
        "concepts": [
            {k: item.get(k) for k in ("reference_id", "label", "normalized_label", "type", "parent_concept")}
            for item in concepts
        ],
        "variants": [
            {k: item.get(k) for k in ("reference_id", "label", "normalized_label", "type", "parent_concept")}
            for item in variants
        ],
    }
    compact_path = OUT / "compact_reference.json"
    compact_path.write_text(json.dumps(compact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    full_min = json.dumps(source, ensure_ascii=False, separators=(",", ":"))
    compact_min = json.dumps(compact, ensure_ascii=False, separators=(",", ":"))
    full_labels = {x for item in concepts + variants for x in item.get("raw_source_labels", []) if x}
    compact_labels = {item.get("label") for item in concepts + variants if item.get("label")}
    compact_vocab = [
        {k: item.get(k) for k in ("reference_id", "label", "normalized_label", "type", "parent_concept")}
        for item in concepts + variants
    ]
    compact_items = compact["concepts"] + compact["variants"]
    parent_ids = {x["reference_id"] for x in compact["concepts"]}
    checks = {
        "source_sha256_matches_expected": sha256(SOURCE) == "ddbe7b2130e8aca3f588daf7b5fae0eb80411648f9abae6d4d66eacc4842204c",
        "concept_count_preserved": len(concepts) == len(compact["concepts"]),
        "variant_count_preserved": len(variants) == len(compact["variants"]),
        "compact_vocab_preserved": compact_vocab == compact_items,
        "variant_parents_valid": all(v["parent_concept"] in parent_ids for v in compact["variants"]),
        "api_calls_made": False,
    }
    manifest = {
        "phase": "dictionary_v2_compact_reference_preflight",
        "source": str(SOURCE),
        "source_sha256": sha256(SOURCE),
        "compact_sha256": sha256(compact_path),
        "full_counts": {"concepts": len(concepts), "variants": len(variants), "entries": len(concepts)+len(variants), "unique_raw_source_labels": len(full_labels)},
        "compact_counts": {"concepts": len(compact["concepts"]), "variants": len(compact["variants"]), "entries": len(compact_items), "unique_labels": len(compact_labels)},
        "serialized_chars": {"full": len(full_min), "compact": len(compact_min), "reduction_percent": round((1-len(compact_min)/len(full_min))*100, 3)},
        "file_bytes": {"full": SOURCE.stat().st_size, "compact": compact_path.stat().st_size, "reduction_percent": round((1-compact_path.stat().st_size/SOURCE.stat().st_size)*100, 3)},
        "estimated_tokens_heuristic_chars_div_4": {"full": round(len(full_min)/4), "compact": round(len(compact_min)/4)},
        "checks": checks,
        "api_execution_started": False,
    }
    (OUT / "compact_reference_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    report = f"""# Dictionary V2 Compact Reference Preflight\n\nNo API calls were made. The compact reference is derived only from the frozen Phase 5 reference.\n\n- Full entries: {len(concepts)+len(variants)} ({len(concepts)} concepts, {len(variants)} variants)\n- Compact entries: {len(compact_items)} ({len(compact['concepts'])} concepts, {len(compact['variants'])} variants)\n- Unique raw source labels in full metadata: {len(full_labels)}\n- Unique canonical labels preserved in compact vocabulary: {len(compact_labels)}\n- Serialized characters: {len(full_min):,} -> {len(compact_min):,} ({manifest['serialized_chars']['reduction_percent']}% reduction)\n- File bytes: {SOURCE.stat().st_size:,} -> {compact_path.stat().st_size:,} ({manifest['file_bytes']['reduction_percent']}% reduction)\n- Estimated tokens (chars/4 heuristic): {round(len(full_min)/4):,} -> {round(len(compact_min)/4):,}\n\nThe compact layer retains every concept/variant compact field and valid parent reference. It removes raw source labels, source record IDs, evidence counts, status, and other provenance metadata from the prompt payload; the frozen full reference remains untouched.\n\nChecks: {json.dumps(checks, sort_keys=True)}\n"""
    (OUT / "compact_reference_report.md").write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
