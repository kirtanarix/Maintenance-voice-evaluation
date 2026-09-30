# Baseline vs Dictionary V1 vs Dictionary V2 â€” Direct Gemini

| Pipeline | Overall accuracy | Assets | Quantities | Hours | Dates | Approval intent |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 78.8% | 86.0% | 46.0% | 72.0% | 98.0% | 92.0% |
| Dictionary V1 | 83.6% | 92.0% | 42.0% | 96.0% | 98.0% | 90.0% |
| Dictionary V2 | 83.6% | 88.0% | 46.0% | 96.0% | 98.0% | 90.0% |

| Change | Overall percentage points |
|---|---:|
| V1 â†’ V2 | +0.00 |
| Baseline â†’ V2 | +4.80 |

Counts (V2): {"EXACT_MATCH": 120, "SEMANTIC_MATCH": 34, "PARTIAL_MATCH": 37, "MISSING": 2, "INCORRECT": 2, "HALLUCINATION": 0, "CORRECT_NULL": 55, "NOT_EVALUABLE": 0}

V2 evaluation uses the unchanged evaluator and ground truth; no baseline or Dictionary V1 rerun was performed.
