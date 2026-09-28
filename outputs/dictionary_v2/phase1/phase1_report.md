# Asset Reference — Phase 1 Report

Phase 1 does not perform canonical asset merging.

Validation: **PASS**. Ingestion coverage: **46/46 files parsed**.
Unsupported/failed files remain inventoried with zero ingested records; validation PASS covers supported-source preservation, not full-format coverage.

## 1. Files discovered

| Group | Filename | Format | Status | Records |
|---|---|---|---|---:|
| Live Company | 0.Adani Cement_Assets_Exported_23-Sep-2026.xlsx | xlsx | parsed | 1675 |
| Live Company | 1Max Cemenve Live_Cement_Industry_Asset List_tableExport.xls | html_table | parsed | 353 |
| Live Company | 2.1BALCO_Asset_Import.xlsx | xlsx | parsed | 25 |
| Live Company | 2.2GSPL_Gas&mix_custom-asset-report-2026-09-25.csv | csv | parsed | 17897 |
| Live Company | 3.1Swama_Garbage Collect_SMC_List of Vehicle-.xlsx | xlsx | parsed | 63 |
| Live Company | 3Zydus_Fire Safety_AssetMaster_Sysma_onboarding ZTL-16-June-2025.xlsx | xlsx | parsed | 247 |
| Live Company | 3Zydus_Fire Safety_AssetMaster_Sysma_onboarding ZTL-2nd Mail.xlsx | xlsx | parsed | 247 |
| Live Company | 3Zydus_Fire Safety_AssetMaster_Sysma_onboarding ZTL.xlsx | xlsx | parsed | 247 |
| Live Company | 7Harsah Engineering_0.2import-assets-New Format-Harsha Maintenance-2.csv | csv | parsed | 3 |
| Live Company | 7Harsah Engineering_0.2import-assets-New Format-Harsha Maintenance.csv | csv | parsed | 66 |
| Live Company | 7Harsah Engineering_0.2import-assets-New Format-Harsha PM.csv | csv | parsed | 3 |
| Live Company | 8GSEC-Equipment_Master.xlsx | xlsx | parsed | 2 |
| Live Company | 9Cool Kit_HVAC_0.2import-assets-New Format-CK-Live-Asset Tag & Cust Tag.xlsx | xlsx | parsed | 19854 |
| Live Company | 9Cool Kit_HVAC_0.2import-assets-New Format-CK-Live.xlsx | xlsx | parsed | 19854 |
| Demo Company | 0.2import-assets-New Format-AJT.csv | csv | parsed | 5 |
| Demo Company | 0.2import-assets-New Format-Auto ID Phase 2.1 (PI).csv | csv | parsed | 5 |
| Demo Company | 0.2import-assets-New Format-BOI-Test.csv | csv | parsed | 1 |
| Demo Company | 0.2import-assets-New Format-Centena Group 2.1 (PI).csv | csv | parsed | 5 |
| Demo Company | 0.2import-assets-New Format-GGWPL-50-36=14 Addition FE.csv | csv | parsed | 14 |
| Demo Company | 0.2import-assets-New Format-GGWPL-Process.csv | csv | parsed | 2 |
| Demo Company | 0.2import-assets-New Format-GGWPL.csv | csv | parsed | 376 |
| Demo Company | 0.2import-assets-New Format-KC-Phase 2-Final-Revised.csv | csv | parsed | 141 |
| Demo Company | 0.2import-assets-New Format-KC-Phase 2-Final.csv | csv | parsed | 141 |
| Demo Company | 0.2import-assets-New Format-KCJPL.csv | csv | parsed | 114 |
| Demo Company | 0.2import-assets-New Format-LI_New Phase-07-Mar-2024.csv | csv | parsed | 49 |
| Demo Company | 0.2import-assets-New Format-RJI-New.csv | csv | parsed | 1 |
| Demo Company | 0.2import-assets-New Format-RJI-old updated.csv | csv | parsed | 5 |
| Demo Company | 0.2import-assets-New Format-SAI.csv | csv | parsed | 8 |
| Demo Company | 0.2import-assets-New Format-Syskode.csv | csv | parsed | 40 |
| Demo Company | 0.2import-assets-New Format-Sysma New Phase-04-Mar-2024.csv | csv | parsed | 99 |
| Demo Company | 0.2import-assets-New Format-TS.csv | csv | parsed | 40 |
| Demo Company | 0.2import-assets-New Format-Wow RFID.csv | csv | parsed | 12 |
| Demo Company | 0Asset IMP Format_Vidya Dairy.csv | csv | parsed | 327 |
| Demo Company | 0Asset IMP_Format Paradip Port.csv | csv | parsed | 22 |
| Demo Company | 0Asset IMP_Format-CT-4-Final.csv | csv | parsed | 10 |
| Demo Company | 0Asset IMP_Format-MI.csv | csv | parsed | 5 |
| Demo Company | 0Asset IMP_Format-YG.csv | csv | parsed | 5 |
| Demo Company | Asset Format-07-Feb-2024.xlsx | xlsx | parsed | 3 |
| Demo Company | Asset IMP Format_Brigade Tower.csv | csv | parsed | 26 |
| Demo Company | Asset IMP Format_Chiripal Group-06-Feb-2023.csv | csv | parsed | 11 |
| Demo Company | Asset IMP Format_Havmor_New.csv | csv | parsed | 1260 |
| Demo Company | Asset IMP Format_MBMC.csv | csv | parsed | 72 |
| Demo Company | Asset IMP Format_Refinery-9-Mar-2023.csv | csv | parsed | 5 |
| Demo Company | Asset IMP_Captain Fresh_CF-HSR Layout-16-Feb-2023.csv | csv | parsed | 40 |
| Demo Company | Asset IMP_Rani Sati Printing.csv | csv | parsed | 16 |
| Demo Company | ICD Sabarmati.xlsx | xlsx | parsed | 83 |

## 2. Files successfully parsed

46

## 3. Files that failed or are unsupported

None.

## 4. Sheets discovered

Workbook sheets: 97. Empty sheets are included in the inventory.
CSV uses sheet=null; HTML tables retain separate numbered table names.

## 5. Total source records

63479

Headers are retained as positional inventory cells. Every explicit row after the header and every preamble row becomes one record, including explicit blank rows. Missing XML row numbers are inventoried as gaps, not invented records. Counts therefore differ from nonempty-only exploration counts.

## 6. Records by source group

- Live Company: 60536 records, 14 files.
- Demo Company: 2943 records, 32 files.

## 7. Records by record_kind

| Kind | Live Company | Demo Company | Total |
|---|---:|---:|---:|
| asset | 39966 | 2084 | 42050 |
| asset_metadata | 66 | 0 | 66 |
| identifier_mapping | 19854 | 0 | 19854 |
| workflow | 6 | 89 | 95 |
| personnel_or_status | 1 | 0 | 1 |
| guidance | 18 | 4 | 22 |
| footer_or_summary | 1 | 0 | 1 |
| unresolved | 624 | 766 | 1390 |

## 8. Candidate duplicate/alias counts

21927 unresolved candidate groups; group counts are not pair counts or a duplicate-asset count.
- conflicting_identifier: 553
- possible_alias: 74
- possible_duplicate: 262
- possible_same_instance: 20101
- repeated_asset_name: 387
- repeated_identifier: 550

Case, whitespace and punctuation comparisons apply to derived lexical observations only. Identifiers are compared exactly. Placeholder values do not generate identifier candidates. No spelling correction, fuzzy alias resolution, company equivalence or instance merging is performed.

## 9. Identifier conflicts

553 candidate groups with an exact scoped identifier but different name/model/location evidence.
Same identifiers may denote legitimate revisions, metadata links or collisions; every candidate remains needs_review.

- candidate_006ad54b139c9498679e7d9b: serial_number, 3 observations. See candidate JSON for identifiers and record references.
- candidate_00b6911a362a6b88759bd04a: customer_tag, 2 observations. See candidate JSON for identifiers and record references.
- candidate_0112a12cbb9f91325d5d223d: serial_number, 2 observations. See candidate JSON for identifiers and record references.
- candidate_017cfb00b4d8bb4eeca275ef: serial_number, 2 observations. See candidate JSON for identifiers and record references.
- candidate_01b46e9d1e826837e4b34c57: serial_number, 2 observations. See candidate JSON for identifiers and record references.
- candidate_028ff0e743882bb2068f6e44: serial_number, 2 observations. See candidate JSON for identifiers and record references.
- candidate_04178d5264b37f6ecde8a7fd: customer_tag, 2 observations. See candidate JSON for identifiers and record references.
- candidate_043f8278cb191e4d7282e756: serial_number, 2 observations. See candidate JSON for identifiers and record references.
- candidate_045197c0fe0529585abd0986: customer_tag, 2 observations. See candidate JSON for identifiers and record references.
- candidate_04573e6afdc39744360ca58c: customer_tag, 2 observations. See candidate JSON for identifiers and record references.
- candidate_045f2b23c2515edd6289171a: serial_number, 2 observations. See candidate JSON for identifiers and record references.
- candidate_047d982e26593c1207853cdb: serial_number, 2 observations. See candidate JSON for identifiers and record references.

## 10. Industry evidence counts

- Live Company: {"ambiguous":58409,"confirmed":2028,"unknown":99}
- Demo Company: {"confirmed":348,"unknown":2595}

Confirmed means explicit source labeling, not independently verified sector membership. HVAC/fire-safety/service context is retained as ambiguous with industry=null. No generic/cross-industry parent is created.

## 11. Unresolved records

- Live Company: 624. Reasons and source coordinates are on each JSONL record.
- Demo Company: 766. Reasons and source coordinates are on each JSONL record.

## 12. Important warnings

- 0.Adani Cement_Assets_Exported_23-Sep-2026.xlsx: Assets_Exported_23-Sep-2026: duplicate headers retained: ['sap equipment no.', 'criticality']
- 0.Adani Cement_Assets_Exported_23-Sep-2026.xlsx: Assets_Exported_23-Sep-2026: nonuniform row widths {'118': 1, '115': 1674, '106': 1}
- 2.2GSPL_Gas&mix_custom-asset-report-2026-09-25.csv: Unterminated quoted CSV field at EOF, logical row 17898; recovered fields are provisional
- 2.2GSPL_Gas&mix_custom-asset-report-2026-09-25.csv: 161064 populated cells have no header; retained positionally without guessed semantics
- 2.2GSPL_Gas&mix_custom-asset-report-2026-09-25.csv: None: duplicate headers retained: ['address', 'city', 'state', 'country', 'zip']
- 2.2GSPL_Gas&mix_custom-asset-report-2026-09-25.csv: None: nonuniform row widths {'47': 2, '58': 17896}
- 3.1Swama_Garbage Collect_SMC_List of Vehicle-.xlsx: Sheet1: 8 explicit blank rows retained as unresolved
- 3Zydus_Fire Safety_AssetMaster_Sysma_onboarding ZTL-16-June-2025.xlsx: Fire Extinguisher: nonuniform row widths {'23': 1, '24': 1, '22': 100, '5': 2}
- 3Zydus_Fire Safety_AssetMaster_Sysma_onboarding ZTL-16-June-2025.xlsx: Fire Ball: nonuniform row widths {'22': 10, '7': 2}
- 3Zydus_Fire Safety_AssetMaster_Sysma_onboarding ZTL-16-June-2025.xlsx: Fire Hose Box: nonuniform row widths {'21': 15, '5': 2}
- 3Zydus_Fire Safety_AssetMaster_Sysma_onboarding ZTL-2nd Mail.xlsx: Fire Extinguisher: nonuniform row widths {'23': 1, '24': 1, '22': 100, '5': 2}
- 3Zydus_Fire Safety_AssetMaster_Sysma_onboarding ZTL-2nd Mail.xlsx: Fire Ball: nonuniform row widths {'22': 10, '7': 2}
- 3Zydus_Fire Safety_AssetMaster_Sysma_onboarding ZTL-2nd Mail.xlsx: Fire Hose Box: nonuniform row widths {'21': 15, '5': 2}
- 3Zydus_Fire Safety_AssetMaster_Sysma_onboarding ZTL.xlsx: Fire Extinguisher: nonuniform row widths {'23': 1, '24': 1, '22': 100, '5': 2}
- 3Zydus_Fire Safety_AssetMaster_Sysma_onboarding ZTL.xlsx: Fire Ball: nonuniform row widths {'22': 10, '7': 2}
- 3Zydus_Fire Safety_AssetMaster_Sysma_onboarding ZTL.xlsx: Fire Hose Box: nonuniform row widths {'21': 15, '5': 2}
- 8GSEC-Equipment_Master.xlsx: Sheet1: duplicate headers retained: ['description', 'customer', 'vendor']
- Asset Format-07-Feb-2024.xlsx: 1 populated cells have no header; retained positionally without guessed semantics
- Asset Format-07-Feb-2024.xlsx: 0.2import-assets-New Format: nonuniform row widths {'19': 1, '20': 1, '5': 2}
- ICD Sabarmati.xlsx: Sheet1: nonuniform row widths {'8': 1, '7': 83}
- ICD Sabarmati.xlsx: Sheet1: 1 merged ranges retained without propagating values
- Original identifiers, manufacturer/model spellings, company names and repeated records remain unchanged.
- XLSX numbers are exact XML numeric strings tagged number; date serials retain style indexes and workbook date system. Formulas retain formula attributes/cached values and are never calculated. Shared/merged cells are not forward-filled.
- Raw records retain administrative/personnel fields and any source credentials. Report summaries do not reproduce them; do not feed this full registry to extraction prompts indiscriminately.
- Asset classification is conservative rule-based triage, not certification of a physical asset or final canonical identity.

## 13. Coverage validation

- PASS: all_discovered_files_in_inventory
- PASS: source_bytes_unchanged
- PASS: every_parsed_row_exactly_once
- PASS: per_source_counts_reconcile
- PASS: raw_values_headers_positions_and_unnamed_cells_preserved
- PASS: every_record_has_valid_kind
- PASS: groups_preserved
- PASS: all_candidates_unresolved_and_referentially_valid
- PASS: candidate_ids_unique
- PASS: no_canonical_merge
- PASS: source_hashes_still_unchanged_after_validation

## Reproduce

`python3 -B src/run_dictionary_v2_phase1.py`

Requires Python 3.10+ standard library only. Existing output directories are refused; use --output-dir with a new review directory for a subsequent run. Source files and existing extraction/evaluation/dictionary code are not written.
