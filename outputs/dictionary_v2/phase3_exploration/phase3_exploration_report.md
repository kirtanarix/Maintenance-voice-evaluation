# Dictionary v2 — Phase 3 exploration and implementation plan

Date: 2026-09-28

**Phase 3 implementation has NOT been performed.**

This report continues the completed Phase 1 ingestion and Phase 2 exploration. It proposes a conservative JSON/JSONL and Python layer for owner review. It does not approve relationships, allocate canonical IDs, regenerate either phase, or change the extraction/evaluation pipeline.

## 1. Findings and inspected files

The handover matches the actual artifact counts and source hashes. Phase 1 and Phase 2 remain the immutable evidence and proposal inputs. Demo data remains reference data in its own source group; it is not presumed synthetic. No cross-group physical identity is established by this review.

All eight artifacts were read during this inspection:

- `outputs/dictionary_v2/phase1/phase1_inventory.json`
- `outputs/dictionary_v2/phase1/phase1_records.jsonl` — every line parsed; record IDs, kinds, groups, industry evidence and per-source counts checked.
- `outputs/dictionary_v2/phase1/phase1_candidates.json`
- `outputs/dictionary_v2/phase1/phase1_report.md`
- `outputs/dictionary_v2/phase2_exploration/phase2_candidate_analysis.json`
- `outputs/dictionary_v2/phase2_exploration/phase2_rule_proposals.json`
- `outputs/dictionary_v2/phase2_exploration/phase2_high_risk_cases.json`
- `outputs/dictionary_v2/phase2_exploration/phase2_exploration_report.md`

All 46 inventoried files under `inputs/dictionary_v2/Live Company/` and `inputs/dictionary_v2/Demo Company/` were read as bytes for SHA-256 verification. Their exact names and hashes remain in the Phase 1 inventory. This check did not rerun source ingestion or independently certify every spreadsheet cell's interpretation.

Compatibility inspection covered `src/run_dictionary_v2_phase1.py`, especially ID generation, raw/derived observations, candidate scopes, industry evidence, validation and exclusive output creation. A search of the existing Python scripts found no Phase 2 generator and no other dictionary_v2 integration. Extraction/evaluation code requires no modification for the proposed layer. Python source files were included in the protected-file hash baseline.

Two temporary spreadsheet lock files were also present in Live Company during the preceding handover verification. They are not part of the 46 inventoried sources and must not become asset inputs or be deleted as part of this work. No required Phase 1 or Phase 2 artifact is missing. No Phase 3 exploration output existed before this report.

## 2. Verified Phase 1 counts

| Source group | Source files | Records |
|---|---:|---:|
| Live Company | 14 | 60,536 |
| Demo Company | 32 | 2,943 |
| Total | 46 | 63,479 |

| Record kind | Count |
|---|---:|
| asset | 42,050 |
| asset_metadata | 66 |
| identifier_mapping | 19,854 |
| workflow | 95 |
| personnel_or_status | 1 |
| guidance | 22 |
| footer_or_summary | 1 |
| unresolved | 1,390 |

There are 63,479 unique record IDs, with no duplicate IDs. Every per-source record count reconciles with the inventory. These are observations, including explicit blank and non-asset rows, not a physical-asset count.

| Candidate type | Groups |
|---|---:|
| possible_same_instance | 20,101 |
| possible_duplicate | 262 |
| conflicting_identifier | 553 |
| repeated_asset_name | 387 |
| possible_alias | 74 |
| repeated_identifier | 550 |
| Total | 21,927 |

Candidate groups can overlap in their observations. They are neither unique physical assets nor necessarily pairs.

## 3. Verified Phase 2 counts

| Proposed relationship | Confidence | Groups |
|---|---|---:|
| IDENTIFIER_MAPPING | high | 20,032 |
| DIFFERENT_ASSET_INSTANCES | high | 371 |
| SOURCE_VERSION_DUPLICATE | high | 262 |
| ALIAS_CANDIDATE | medium | 74 |
| SAME_ASSET_INSTANCE_CANDIDATE | medium | 119 |
| UNRESOLVED | low | 697 |
| UNRESOLVED | medium | 372 |
| Total | | 21,927 |

High-confidence proposals total 20,665. Unresolved proposals total 1,069. The automation-status totals are 20,859 `review_required`, 697 `do_not_automate`, and 371 `safe_to_automate`. These are different dimensions of the same candidate population, not additive populations. High confidence does not constitute owner approval.

All Phase 1 candidate IDs occur exactly once in Phase 2. Phase 2 source-record membership matches Phase 1 for every candidate. All candidate references and all five high-risk groups' record references resolve.

## 4. Contradictions, limitations and their proposed treatment

### Industry certainty

Phase 1 labels 2,376 observations as industry `confirmed` using filename evidence. Its implementation recognizes filename terms such as cement, dairy, refinery and printing. Another 58,409 observations have ambiguous filename context; 2,694 have unknown industry evidence. Phase 2 report section 10 and rule R13 reject filename-only asset industry assignment.

Preserve the Phase 1 annotation verbatim as a source-derived claim, including its original certainty. Separately record Phase 3 review status. Do not interpret Phase 1 `confirmed` as approval for canonical associations. Filename-only claims remain pending unless the owner approves sufficient supporting evidence. Lexical families such as HVAC/cooling and fire protection are not an approved industry taxonomy.

### Relationship confidence and approval

The 262 `SOURCE_VERSION_DUPLICATE` high-confidence labels are proposals; identical positional source rows do not by themselves establish export chronology, authoritative precedence or physical identity. Similarly, the 20,032 mappings are candidate groups, not 20,032 unique identifier pairs or instances. Phase 2 requires review for both categories. The handover's possible safe automation therefore requires a separately reviewed rule; it is not blanket approval to apply these proposals.

The 371 distinct-instance proposals may conservatively preserve separation, but even those labels must not automatically create physical instances for non-asset observations or turn incomplete evidence into an established identity claim.

### Evidence and reproducibility

All 13 rule proposals reuse the same two-record Cool Kit example. These examples do not individually substantiate each rule, particularly industry, alias, containment and conflict rules. Rule approval should cite relevant records and counterexamples.

No Phase 2 generating script was found. The existing output is hash-linked to Phase 1 and internally consistent, but its classification logic cannot be reproduced from an identified checked-in generator. Keep it as a versioned proposal input; do not recreate Phase 2 during Phase 3.

### Source parsing and triage

The Phase 1 report identifies a GSPL unterminated quoted CSV field and 161,064 populated cells without headers. Positional values are retained, but recovered interpretation is provisional. Other sources have duplicate headers, varying widths, explicit blank rows and merged cells. Phase 3 must not infer missing field semantics or forward-fill source values. Record kinds are conservative triage, not certification that every `asset` row denotes a distinct registered machine.

## 5. Existing IDs and exact reference contract

The Phase 1 helper generates an ID as a prefix plus the first 24 hexadecimal characters of a SHA-256 digest. The digest input is compact, sorted-key JSON of the supplied parts, with Unicode preserved and UTF-8 encoding.

- `source_id`: generated from the source-relative path and source-file SHA-256.
- `record_id`: generated from `source_id`, sheet/table name and original row number.
- `candidate_id`: generated from candidate type, evidence and sorted member record IDs.

Phase 2 reuses `candidate_id` and records members in `source_record_ids`; Phase 1 uses `record_ids`. Phase 3 must reference these exact existing strings, not recreate IDs from normalized text or row order in a new file.

Each Phase 3 decision should retain `candidate_ids` when applicable and explicit `source_record_ids`. Decisions originating from an individual observation or a high-risk case need not invent a Phase 1 candidate. Preserve the existing high-risk `case_id` in `high_risk_case_ids`. Candidate groups are evidence containers: any approved relationship must state its actual endpoints and must not automatically expand a group into all possible pairs.

For cell-level evidence, use `record_id` plus `column_index`. Duplicate header names make a header string alone insufficient. File, sheet, row, source group, original identifiers and raw values remain resolvable through the immutable record and inventory. Filename evidence should reference the source and identify its basis explicitly.

Bind every build to hashes of all eight Phase 1/2 artifacts and the source inventory. A changed source file produces a new source ID and consequently new record IDs; carrying decisions across a new ingestion requires explicit remapping review. Do not use row coordinates as persistent identity across revisions.

Future canonical IDs should be opaque, allocated once through approved decisions and independent of preferred labels, industry, sort position and normalized names. Rebuilding the same approved inputs must preserve those IDs. This report allocates none.

## 6. Proposed six-file Phase 3 structure

The requested six files are sufficient. No additional entity database, graph engine or separate manufacturer/model registry is necessary at this stage.

| File | Proposed content |
|---|---|
| `review_decisions.jsonl` | Pending, approved, rejected or deferred decisions; explicit relationship endpoints; source/candidate/high-risk references; reviewer or approved-rule reference; rationale; evidence; superseded-decision reference where needed. |
| `concepts.jsonl` | Approved general equipment meanings, stable IDs, preferred labels, reviewed aliases, supporting decision and record references. |
| `variants.jsonl` | Approved concept reference and meaningful type/configuration/capacity/duty/dimension specifications, including original values and units, with evidence and decision references. |
| `instances.jsonl` | Approved physical identities, optional concept/variant references, company/site observations, namespace-and-scope-qualified identifiers, separate manufacturer/model observations, and provenance. |
| `industry_associations.jsonl` | Many-to-many links with explicit subject type/ID, reviewed industry label, evidence basis, certainty, review status and decision references. |
| `manifest.json` | Schema and builder versions, immutable input hashes, approved rule definitions/version, artifact hashes/counts and validation results. |

The decision ledger also stores approved source-version and identifier-mapping links, so a seventh relationships file is unnecessary. Manufacturer and model remain separate evidenced fields, not synonyms or entity keys. Introduce separate registries only if a later approved use case needs them.

A decision entry should contain a proposed action independently of its review status. Confidence, approval and automation eligibility are separate fields. Human approval records who decided and why; rule-applied approval identifies the owner-approved rule/version and the evidence that passed it. Corrections supersede earlier decisions rather than erase their history. Multiple active contradictory approvals must fail validation.

An identifier value must retain its raw representation, namespace, explicit scope and source reference. Scope can be unresolved. Missing company/site must not imply global uniqueness. An identifier mapping can link identifiers observed together without assigning either observation to a canonical instance.

The architecture is not a mandatory linear chain. A concept may be supported without a known instance; an instance may have no approved variant; an observation may remain entirely unresolved. Concept reuse across industries does not establish physical identity across Live and Demo. Do not create industry-specific copies of the same approved concept. No CCTV-specific rule is warranted.

Only approved associations should populate the canonical industry view. Pending/uncertain industry proposals remain reviewable in the decision ledger; any approved association still retains the evidence's uncertainty and basis. Never automatically propagate an instance's context to all instances of its concept.

Keep all non-asset and unresolved observations accessible in Phase 1. A compact future Gemini reference export should select approved vocabulary and specifications with provenance, not copy raw administrative/personnel fields into prompts. That export and pipeline integration are later scope, not this implementation plan's initial deliverable.

## 7. Automation boundaries

| Operation | Proposed boundary |
|---|---|
| Hash/count/reference validation, proposal indexing and provenance preservation | Deterministic automation; no semantic approval. |
| Exact identifiers explicitly associated in a source row | May produce mapping proposals. Applying a relationship requires a reviewed rule or individual decision; no automatic instance union. |
| Identical source rows / apparent repeated exports | Preserve observations and propose a source relationship. Approve version semantics only with reviewed evidence. |
| Distinct-instance separation | Preserve separation by default. Apply a reviewed rule only within its documented scope and absent contradictory evidence. |
| Text/semantic aliases, manufacturer/model equivalence | No automatic approval without explicit evidence and an approved rule. |
| Conflicting or punctuation-normalized identifiers | No automatic equivalence, replacement or conflict winner. |
| Component/assembly links and industry classification | No inference from words, lexical overlap, category or filename alone. |
| Repeated names, common location, manufacturer or model | Never sufficient by themselves for instance identity. |

Do not perform transitive identity closure over candidate groups, identifier mappings or source-version links. Even approved instance-equivalence decisions must be checked against explicit separation decisions and unresolved conflicting evidence before a shared instance is materialized.

## 8. High-risk cases to retain

| Existing case ID | Case | Referenced observations | Required treatment |
|---|---|---:|---|
| `high_risk_001` | Adani equipment number 1000117336 with conflicting descriptions | 2 | Obtain authoritative equipment evidence; do not select a winner. |
| `high_risk_002` | Cool Kit punctuation-sensitive identifiers | 28 | Preserve SS--S-6 / SS-S-6 and 1208--W-2 / 1208-W-2 exactly; require explicit equivalence evidence. |
| `high_risk_003` | Conflicting identifier clusters | 3 | Review scope, source history and contradictory attributes. |
| `high_risk_004` | Text-only alias candidates | 2 | Require semantic authority beyond text similarity. |
| `high_risk_005` | Repeated raw names | 2 | Preserve independent observations; do not infer shared identity. |

These are the five existing example groups, not an exhaustive replacement for all 1,069 unresolved candidate groups or 1,390 unresolved source observations. Component/assembly claims also remain unapproved unless independently evidenced. Deferred cases must remain visible even when they produce no canonical output.

## 9. Owner decisions still needed

1. Approve this six-file schema and the separation of proposal confidence from review approval.
2. Define identifier scope, including company/site/source-system boundaries and handling missing context. Tags do not prove identity globally.
3. Identify who can approve rules or individual decisions, and supply rule-specific evidence and counterexamples before batch application.
4. Confirm source-version relationships and any authoritative precedence; filenames and identical rows alone do not establish chronology.
5. Approve concept naming, alias evidence and variant boundaries, including meaningful capacities, duty, configuration and units. Do not normalize away those distinctions.
6. Approve industry labels and acceptable evidence. Filename-only Phase 1 annotations must not silently become canonical associations.
7. Resolve or explicitly defer high-risk cases. Their resolution is not a prerequisite for an empty, validated framework, but it is required before applying affected identity decisions.
8. Confirm the treatment of Phase 2 as an immutable proposal input despite the missing generator; provide that script if available, without regenerating artifacts in this task.

## 10. Implementation sequence after approval

1. Add an isolated Python builder/validator with no extraction/evaluation dependencies or network calls. Pin input hashes and refuse existing output directories.
2. Validate schemas and references; establish the decision ledger with proposals still pending. Link all existing high-risk cases and retain unresolved coverage.
3. Encode only owner-approved rules with explicit scope and evidence predicates. Review other decisions individually; high confidence never substitutes for approval.
4. Materialize concepts, variants, instances and industry associations only from effective approved decisions. Empty canonical artifacts are valid when no decisions are approved.
5. Run meaningful tests for scope collisions, punctuation/leading-zero preservation, variant distinctions, repeated names, conflicting approvals, high-risk deferral, source-version links, missing references and Live/Demo separation.
6. Verify deterministic output from identical pinned inputs and decisions, unique IDs, complete provenance, valid references, unchanged protected inputs, and no relationship-induced loss of source observations. Use an explicit ordering and keep volatile build metadata out of deterministic content comparisons.
7. Deliver the new artifacts and validation summary for review. A later Gemini dictionary view remains a separately approved step.

This approach keeps implementation small: one builder, one validator or validation module, and the six data artifacts. No database, embeddings, RAG, API or cloud service is proposed.

## 11. Validation performed and limitations

- SHA-256 comparison passed for all 46 source files against the Phase 1 inventory.
- SHA-256 comparison passed for all four Phase 1 artifacts against the Phase 2 recorded input hashes.
- All 63,479 JSONL records parsed; record IDs are unique; record-kind, group and per-source counts reconcile.
- All 21,927 candidate IDs are unique and covered exactly once in Phase 2; member record sets match and references resolve.
- All reported Phase 2 relationship/confidence counts reconcile; five high-risk groups and 13 rule proposals are present.
- All five high-risk groups' source-record references resolve.
- Protected sources, Phase 1/2 artifacts and Python source files were hashed before report creation; final unchanged-file verification is recorded below.

No ingestion, extraction or evaluation program was executed. No source-cell reparse, independent semantic certification or reconstruction of Phase 2 logic was attempted. Structural consistency does not resolve data conflicts or prove physical identity.

Final protected-file verification: all 79 protected files matched the pre-write SHA-256 baseline, with zero missing or changed files. The exploration directory contains only this report. The implementation directory `outputs/dictionary_v2/phase3/` does not exist.

**Phase 3 implementation has NOT been performed.** Only this exploration report is authorized for creation in this task. Implementation remains subject to owner approval.
