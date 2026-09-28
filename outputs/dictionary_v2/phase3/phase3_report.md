# Dictionary v2 — Phase 3 report

## Purpose and scope

Phase 3 creates an evidence-supported reference layer without modifying or merging source observations. No extraction/evaluation or Gemini integration was changed.

## Inputs and outputs

Inputs: all four immutable Phase 1 artifacts, all four Phase 2 artifacts, and the Phase 3 exploration report. Source bytes were checked against the Phase 1 inventory. Manifest hashes identify the exact inputs and builder.

Outputs: review_decisions.jsonl, concepts.jsonl, variants.jsonl, instances.jsonl, industry_associations.jsonl, manifest.json, and this report. The only additional artifact is build_phase3.py, containing the builder, validator and regression tests.

## Counts

| Item | Count |
|---|---:|
| Source files | 46 |
| Source observations | 63,479 |
| Candidate relationships | 21,927 |
| Approved candidate relationships | 19,281 |
| Deferred candidate relationships | 2,646 |
| review_decisions.jsonl records | 85,411 |
| concepts.jsonl records | 9 |
| variants.jsonl records | 9 |
| instances.jsonl records | 477 |
| industry_associations.jsonl records | 0 |

Review decisions contain one decision per candidate, one disposition per source observation, and five deferred high-risk cases. Source-only dispositions are not additional candidate relationships and do not imply a requirement to manually classify every record.

| Relationship | Approved | Deferred |
|---|---:|---:|
| ALIAS_CANDIDATE | 0 | 74 |
| DIFFERENT_ASSET_INSTANCES | 31 | 340 |
| IDENTIFIER_MAPPING | 19,058 | 974 |
| SAME_ASSET_INSTANCE_CANDIDATE | 0 | 119 |
| SOURCE_VERSION_DUPLICATE | 192 | 70 |
| UNRESOLVED | 0 | 1,069 |

## Canonical evidence

Concepts require exact agreement between an item name and sheet title, corroborated by distinct registered tags in a source. Source categories alone are not promoted. Conflict/high-risk records are excluded. No case, spelling or punctuation aliases are created.

| Concept (exact source label) | Source registrations |
|---|---:|
| Safety Belt | 15 |
| Safety Shower | 9 |
| Fire Hose Pipe | 102 |
| First Aid Box | 39 |
| Emergency Door | 15 |
| Fire Hose Reel | 6 |
| Fire Extinguisher | 261 |
| Spill Control Kit | 24 |
| SCBA Set | 6 |

Variants retain exact values from the explicit extinguisher type/capacity field. Only unambiguous full capacity syntax is parsed; raw codes and units are retained, and unexplained suffixes remain uninterpreted. Formatting variants are not silently equated.

| Variant (exact source label) | Source registrations |
|---|---:|
| ABC 6Kg | 36 |
| CO2 22.5KG | 12 |
| ABC 6KG | 102 |
| ABC 6KG (M) | 6 |
| W/CO2 50 Ltr | 3 |
| CLEAN AGENT 2KG | 24 |
| CO2 4.5KG | 57 |
| CLEAN AGENT 5KG | 6 |
| M/FOAM 50Ltr | 15 |

Instances are source-scoped registered-asset representations, each supported by one observation. Their cross-observation identity is unresolved. Repeated exports can represent the same physical asset multiple times: the instance count is NOT a deduplicated physical-asset total. All instances reference an existing concept; a variant is optional.

Manufacturer and model source observations are retained separately. Canonical manufacturer/model remain null because source labels do not establish OEM identities. Company remains an observation rather than an invented company registry.

Industry associations: zero. Filename-only industry annotations remain verbatim in source dispositions, including Phase 1's certainty, without becoming canonical claims.

## Applied boundaries and preserved conflicts

Identifier mappings express the exact pair co-observed within each source row; they do not unify identifier scopes, source records or physical assets. Source-version proposals are approved only as identical full raw-cell content, without chronology or precedence. Separation approvals are restricted to one source snapshot, not revised exports.

All five high-risk cases remain deferred: Adani 1000117336; Cool Kit SS--S-6/SS-S-6 and 1208--W-2/1208-W-2; conflicting identifier clusters; textual aliases; repeated raw names. All conflicting_identifier candidate groups remain deferred. No component/assembly relationships or semantic aliases are created.

Phase 2 confidence is not authority: every approved relationship passed an independent raw-evidence rule. Source-version duplicates and mappings never trigger instance union. Deferred candidates keep all original member IDs.

## Validation

Validation: **PASS**. 21 embedded safety regression tests passed. All JSON/JSONL outputs were parsed and structurally validated. Two in-memory builds, with reversed record/candidate/proposal input order on the second run, produced byte-identical data artifacts and identical IDs. Saved files are validated again on disk.

Validated: input hashes and source counts; complete candidate coverage; every record's disposition; valid source/candidate/decision references; unique entity IDs; concept/variant/instance links; exact identifier namespaces, values and scopes; preserved raw manufacturer/model observations; all five high-risk cases deferred; no multi-observation instance merges; no unsupported industries or aliases.

The protected-file fingerprint covers 6,253 files outside this directory, including inputs, Phase 1/2, exploration, Python pipeline, audio and repository metadata. Before/after SHA-256 equality is required for a successful run. Original source files and Phase 1/2 artifacts were not modified.

## Limitations

This is deliberately a small canonical dictionary, not comprehensive semantic classification of all 42,050 asset observations. Unknowns and unsupported concepts remain source evidence. The GSPL malformed CSV row and unnamed cells remain unresolved; no ingestion repair was attempted. Phase 2's missing generator and repeated rule examples are not treated as authoritative semantic evidence. Temporary spreadsheet lock files are ignored as inputs but preserved.

No final flat dictionary or prompt export is generated. Broader concepts, semantic aliases, resolved physical identities and industries need stronger project evidence. No external services, database, embeddings, RAG or APIs are used.

## Reproduce and verify

From the project root:

```powershell
python -B -X utf8 outputs/dictionary_v2/phase3/build_phase3.py --verify
```

The builder refuses to overwrite any existing output. --verify is read-only: it rebuilds twice in memory, validates existing artifacts and compares bytes, including the manifest and report. Do not delete reviewed outputs merely to rerun the build.
