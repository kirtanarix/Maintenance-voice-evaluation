# Compact Dictionary V2 Direct Gemini Evaluation

Scored with unchanged `src/evaluator.py` and existing ground truth.

Overall accuracy: 82.4%

- assets: 86.0%
- quantities: 42.0%
- hours: 96.0%
- dates: 98.0%
- approval_intent: 90.0%

Judgment counts:
```json
{
  "EXACT_MATCH": 118,
  "SEMANTIC_MATCH": 33,
  "PARTIAL_MATCH": 39,
  "MISSING": 2,
  "INCORRECT": 3,
  "HALLUCINATION": 0,
  "CORRECT_NULL": 55,
  "NOT_EVALUABLE": 0
}
```
