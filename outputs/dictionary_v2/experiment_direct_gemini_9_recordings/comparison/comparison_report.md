# Nine-recording evaluation

| Pipeline | Overall | Assets | Quantities | Hours | Dates | Approval intent |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 80.0% | 66.67% | 44.44% | 88.89% | 100.0% | 100.0% |
| dictionary_v1 | 84.44% | 77.78% | 44.44% | 100.0% | 100.0% | 100.0% |
| dictionary_v2 | 80.0% | 66.67% | 44.44% | 100.0% | 100.0% | 88.89% |
| combined_v1_v2 | 82.22% | 77.78% | 33.33% | 100.0% | 100.0% | 100.0% |

Counts:
- baseline: {"EXACT_MATCH": 23, "SEMANTIC_MATCH": 4, "PARTIAL_MATCH": 7, "MISSING": 0, "INCORRECT": 2, "HALLUCINATION": 0, "CORRECT_NULL": 9, "NOT_EVALUABLE": 0}
- dictionary_v1: {"EXACT_MATCH": 24, "SEMANTIC_MATCH": 5, "PARTIAL_MATCH": 6, "MISSING": 0, "INCORRECT": 1, "HALLUCINATION": 0, "CORRECT_NULL": 9, "NOT_EVALUABLE": 0}
- dictionary_v2: {"EXACT_MATCH": 24, "SEMANTIC_MATCH": 3, "PARTIAL_MATCH": 6, "MISSING": 1, "INCORRECT": 2, "HALLUCINATION": 0, "CORRECT_NULL": 9, "NOT_EVALUABLE": 0}
- combined_v1_v2: {"EXACT_MATCH": 24, "SEMANTIC_MATCH": 4, "PARTIAL_MATCH": 7, "MISSING": 0, "INCORRECT": 1, "HALLUCINATION": 0, "CORRECT_NULL": 9, "NOT_EVALUABLE": 0}
