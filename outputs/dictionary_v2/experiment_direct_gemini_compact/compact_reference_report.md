# Dictionary V2 Compact Reference Preflight

No API calls were made. The compact reference is derived only from the frozen Phase 5 reference.

- Full entries: 141 (124 concepts, 17 variants)
- Compact entries: 141 (124 concepts, 17 variants)
- Unique raw source labels in full metadata: 478
- Unique canonical labels preserved in compact vocabulary: 132
- Serialized characters: 906,470 -> 23,590 (97.398% reduction)
- File bytes: 1,179,553 -> 31,698 (97.313% reduction)
- Estimated tokens (chars/4 heuristic): 226,618 -> 5,898

The compact layer retains every concept/variant compact field and valid parent reference. It removes raw source labels, source record IDs, evidence counts, status, and other provenance metadata from the prompt payload; the frozen full reference remains untouched.

Checks: {"api_calls_made": false, "compact_vocab_preserved": true, "concept_count_preserved": true, "source_sha256_matches_expected": true, "variant_count_preserved": true, "variant_parents_valid": true}
