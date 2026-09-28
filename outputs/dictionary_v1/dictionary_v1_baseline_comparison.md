# Baseline versus dictionary v1.0

Baseline scores read from existing reports and exactly reproduced with current ground truth and unchanged evaluators. New scores verified against saved dictionary evaluation files.

| Dataset | Pipeline | Baseline | Dictionary v1 | Difference | Correct fields |
|---|---|---:|---:|---:|---:|
| 50 | Direct Gemini | 78.80% | 83.60% | +4.80 pp | 197 → 209 / 250 |
| 50 | Sarvam + Gemini | 64.80% | 70.00% | +5.20 pp | 162 → 175 / 250 |
| 9 | Direct Gemini | 77.78% | 84.44% | +6.67 pp | 35 → 38 / 45 |
| 9 | Sarvam + Gemini | 64.44% | 68.89% | +4.44 pp | 29 → 31 / 45 |

Differences use unrounded correct/total fractions, then round to two decimals. This avoids subtracting already-rounded percentages.

## 50 recordings — Direct Gemini

| Parameter | Baseline | Dictionary v1 | Difference | Correct fields |
|---|---:|---:|---:|---:|
| assets | 86.00% | 92.00% | +6.00 pp | 43 → 46 / 50 |
| quantities | 46.00% | 42.00% | -4.00 pp | 23 → 21 / 50 |
| hours | 72.00% | 96.00% | +24.00 pp | 36 → 48 / 50 |
| dates | 98.00% | 98.00% | +0.00 pp | 49 → 49 / 50 |
| approval_intent | 92.00% | 90.00% | -2.00 pp | 46 → 45 / 50 |

## 50 recordings — Sarvam + Gemini

| Parameter | Baseline | Dictionary v1 | Difference | Correct fields |
|---|---:|---:|---:|---:|
| assets | 62.00% | 62.00% | +0.00 pp | 31 → 31 / 50 |
| quantities | 32.00% | 36.00% | +4.00 pp | 16 → 18 / 50 |
| hours | 60.00% | 82.00% | +22.00 pp | 30 → 41 / 50 |
| dates | 80.00% | 80.00% | +0.00 pp | 40 → 40 / 50 |
| approval_intent | 90.00% | 90.00% | +0.00 pp | 45 → 45 / 50 |

## 9 recordings — Direct Gemini

| Parameter | Baseline | Dictionary v1 | Difference | Correct fields |
|---|---:|---:|---:|---:|
| assets | 66.67% | 77.78% | +11.11 pp | 6 → 7 / 9 |
| quantities | 44.44% | 44.44% | +0.00 pp | 4 → 4 / 9 |
| hours | 88.89% | 100.00% | +11.11 pp | 8 → 9 / 9 |
| dates | 100.00% | 100.00% | +0.00 pp | 9 → 9 / 9 |
| approval_intent | 88.89% | 100.00% | +11.11 pp | 8 → 9 / 9 |

## 9 recordings — Sarvam + Gemini

| Parameter | Baseline | Dictionary v1 | Difference | Correct fields |
|---|---:|---:|---:|---:|
| assets | 55.56% | 66.67% | +11.11 pp | 5 → 6 / 9 |
| quantities | 11.11% | 11.11% | +0.00 pp | 1 → 1 / 9 |
| hours | 66.67% | 88.89% | +22.22 pp | 6 → 8 / 9 |
| dates | 88.89% | 88.89% | +0.00 pp | 8 → 8 / 9 |
| approval_intent | 100.00% | 88.89% | -11.11 pp | 9 → 8 / 9 |

## Execution and methodology

Command: `.venv/bin/python -m src.run_dictionary_v1_evaluation`.

New wrapper: `src/run_dictionary_v1_evaluation.py`. Existing `src/evaluator.py`, `src/normalizer.py`, `src/report_generator.py:_build_summary`, and `src/speaker_evaluator.py:evaluate_speaker_subset` are reused unchanged. The wrapper only selects subsets, validates, and formats new reports.

Ground truth for both datasets: `outputs/ground_truth/ground_truth_final.json`, selecting original baseline IDs in memory. Baseline field-level judgments were reproduced exactly before scoring dictionary results.

Outputs: four files each under `outputs/dictionary_v1/evaluation_50/` and `outputs/dictionary_v1/evaluation_9/`: combined summary, detailed Markdown report, Direct Gemini evaluation JSON and Sarvam + Gemini evaluation JSON.

All requested 50/50/9/9 records were evaluated with five fields each. No missing, unexpected or silently skipped recordings; input and result schemas checked. No evaluation exceptions occurred.

## Anomalies and interpretation limits

- The legacy speaker mapping labels jigishbhai_* as Mahesh. Reports display this group as Jigish (legacy mapping: Mahesh); grouping and scoring are unchanged.
- The extraction intervention included the dictionary plus explicit source-only safeguards; Agent 1 used fresh Sarvam transcripts. These results measure observed changes, not an isolated dictionary-only causal effect.
- The dictionary declares that its vocabulary was informed by these 59 recordings. Results do not establish held-out generalization.
- Scoring uses the existing deterministic heuristic comparers, not a new human audio review. HALLUCINATION is an evaluator classification against ground truth.
- No extraction API calls, regeneration, dictionary-based scoring, or changes to evaluation/normalization were made.

Integrity check: all 402 protected pre-existing files match their SHA-256 snapshots. Baseline evaluations, ground truth, dictionary, all extraction artifacts, and existing evaluation/normalization code were untouched. No extraction agents were rerun.
