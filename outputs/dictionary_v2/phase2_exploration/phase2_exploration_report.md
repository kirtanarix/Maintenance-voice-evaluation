# Dictionary v2 — Phase 2 exploration report

## 1. Executive Summary
All 21,927 Phase 1 candidate relationships were analyzed without applying a merge, rename, canonical ID, or dictionary change. 20,032 mapping relationships and 371 distinct-instance decisions have high-confidence evidence, while 1,069 remain unresolved.

## 2. Phase 1 Input Statistics
Phase 1 inputs read: 46 source files; 60,536 Live Company records; 2,943 Demo Company records; 21,927 candidates. Source groups are retained independently.

## 3. Candidate Category Analysis
Candidate labels were treated as signals. Counts: possible_same_instance 20,101, possible_duplicate 262, conflicting_identifier 553, repeated_asset_name 387, possible_alias 74, repeated_identifier 550. Proposed results: ALIAS_CANDIDATE|medium: 74, DIFFERENT_ASSET_INSTANCES|high: 371, IDENTIFIER_MAPPING|high: 20,032, SAME_ASSET_INSTANCE_CANDIDATE|medium: 119, SOURCE_VERSION_DUPLICATE|high: 262, UNRESOLVED|low: 697, UNRESOLVED|medium: 372.

## 4. Live vs Demo Comparison
Live Company has 60,536 observations across 14 files; Demo Company has 2,943 observations across 32 files. Lexical family patterns occur in both contexts, but no source evidence directly establishes cross-context instance identity. Demo is preserved as reference observations, not treated as synthetic data.

## 5. Concept vs Variant vs Instance Analysis
Observed names can identify a concept-family lexical pattern, but only independent identifiers plus compatible source context can support an instance candidate. Different tags under the same name are classified `DIFFERENT_ASSET_INSTANCES`; descriptions, capacities, models, and type strings remain variant/specification evidence until a future reviewed representation is designed.

## 6. Alias Analysis
74 textual alias signals are `ALIAS_CANDIDATE` and review-required. Case, spacing, spelling, and punctuation are not semantic authority; no aliases were created.

## 7. Identifier Analysis
Exact identifiers associated with explicit mapping rows produce 20,032 high-confidence mapping proposals, never a record merge. 553 conflicting-identifier signals remain unresolved. Identifier punctuation and leading zeros are preserved exactly.

## 8. Manufacturer / Model Analysis
Manufacturer, model, and model-number observations retain their raw source values. Case-only and formatting similarities remain unsafe alias candidates. Internal codes, generated references, and placeholders are not reclassified as OEM models.

## 9. Component / Assembly Analysis
The source observations do not establish enough containment semantics to automate `COMPONENT_OF`, `PART_OF`, or `ASSEMBLY_OF`. Related words in descriptions are insufficient; parent and component observations remain distinct.

## 10. Cross-Industry Analysis
No industry taxonomy was created. Patterns observed in both source contexts are lexical only: HVAC / cooling (Live 20248, Demo 8); Motors / drives (Live 243, Demo 1); Material handling (Live 57, Demo 31); Vehicles (Live 36, Demo 4); Valves / piping (Live 179, Demo 0); Pumps (Live 22, Demo 55); Fire protection (Live 353, Demo 66). File labels alone are not used to assign industry to an asset.

## 11. High-Risk Cases
- **same_equipment_number_conflicting_description** — 1000117336 is repeated across materially different source observations. Evidence: 0.Adani Cement_Assets_Exported_23-Sep-2026.xlsx / Assets_Exported_23-Sep-2026 / row 211, 0.Adani Cement_Assets_Exported_23-Sep-2026.xlsx / Assets_Exported_23-Sep-2026 / row 1668. Which source observation, if any, is authoritative for equipment identity?
- **punctuation_sensitive_identifiers** — Hyphen variants such as SS--S-6 / SS-S-6 and 1208--W-2 / 1208-W-2 are unsafe to normalize. Evidence: 9Cool Kit_HVAC_0.2import-assets-New Format-CK-Live-Asset Tag & Cust Tag.xlsx / 0.2import-assets-New Format-CK- / row 3, 9Cool Kit_HVAC_0.2import-assets-New Format-CK-Live-Asset Tag & Cust Tag.xlsx / 0.2import-assets-New Format-CK- / row 253. Are punctuation changes data-entry variants or distinct identifiers?
- **conflicting_identifier_clusters** — Identifier conflict groups cannot be safely resolved. Evidence: Asset IMP Format_Havmor_New.csv / None / row 1182, Asset IMP Format_Havmor_New.csv / None / row 1238. What additional source evidence establishes the relationship?
- **alias_candidates** — Text normalization lacks semantic authority. Evidence: Asset IMP Format_Havmor_New.csv / None / row 379, Asset IMP Format_Havmor_New.csv / None / row 304. What additional source evidence establishes the relationship?
- **repeated_raw_names** — Names recur across potentially independent instances. Evidence: 0.2import-assets-New Format-KC-Phase 2-Final.csv / None / row 117, 0.2import-assets-New Format-KC-Phase 2-Final-Revised.csv / None / row 117. What additional source evidence establishes the relationship?

## 12. Proposed Cleanup Rules
13 proposals are documented in `phase2_rule_proposals.json`. They preserve observations, require review for relationship creation, and prohibit automated alias or component/assembly inference.

## 13. Automation vs Manual Review Boundaries
371 proposals are safe only because they preserve separation or treat placeholders as missing evidence. 20,859 require review; 697 are explicitly excluded from automation. No proposal creates a canonical asset.

## 14. Unresolved Questions
1,069 candidate relationships remain unresolved. Project-owner confirmation is needed for identifier scope (company/site/global), whether repeated exports are source versions, whether punctuation variants are equivalent, and whether location conflicts represent moves, multiple units, or source errors.

## 15. Recommended Phase 2 Implementation Plan
First retain immutable observations and provenance. Next implement only reviewed relationship links for explicit identifier mappings. Add manual adjudication for conflicts, aliases, variants, and parent/component claims. Do not canonicalize or delete records until those reviews establish a documented rule and validation set.

## Validation Summary
Phase 1 hashes unchanged after output generation: True. Source hashes unchanged: True. Every candidate record ID is valid: True. Candidate count reconciles: True. JSON artifacts were written only under this Phase 2 directory.
