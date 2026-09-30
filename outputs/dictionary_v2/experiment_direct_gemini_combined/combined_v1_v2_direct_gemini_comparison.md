# Five-pipeline comparison

| Pipeline | Overall | Assets | Quantities | Hours | Dates | Approval |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 78.8% | 86.0% | 46.0% | 72.0% | 98.0% | 92.0% |
| V1 | 83.6% | 92.0% | 42.0% | 96.0% | 98.0% | 90.0% |
| Full V2 | 83.6% | 88.0% | 46.0% | 96.0% | 98.0% | 90.0% |
| Compact V2 | 82.4% | 86.0% | 42.0% | 96.0% | 98.0% | 90.0% |
| Combined | 83.6% | 88.0% | 44.0% | 98.0% | 98.0% | 90.0% |

Combined vs Baseline: +4.80 percentage points

Combined vs V1: +0.00 percentage points

Combined vs Full V2: +0.00 percentage points

Combined vs Compact V2: +1.20 percentage points

Combined judgment counts:
```json
{
  "EXACT_MATCH": 121,
  "SEMANTIC_MATCH": 33,
  "PARTIAL_MATCH": 38,
  "MISSING": 1,
  "INCORRECT": 2,
  "HALLUCINATION": 0,
  "CORRECT_NULL": 55,
  "NOT_EVALUABLE": 0
}
```
