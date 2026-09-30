# Baseline / V1 / Full V2 / Compact V2 Direct Gemini Comparison

| Pipeline | Overall | Assets | Quantities | Hours | Dates | Approval intent |
|---|---:|---:|---:|---:|---:|---:|
| Baseline Direct Gemini | 78.8% | 86.0% | 46.0% | 72.0% | 98.0% | 92.0% |
| Direct Gemini + Dictionary V1 | 83.6% | 92.0% | 42.0% | 96.0% | 98.0% | 90.0% |
| Direct Gemini + full Dictionary V2 | 83.6% | 88.0% | 46.0% | 96.0% | 98.0% | 90.0% |
| Direct Gemini + Compact Dictionary V2 | 82.4% | 86.0% | 42.0% | 96.0% | 98.0% | 90.0% |

## Judgment counts

### Baseline Direct Gemini

```json
{
  "EXACT_MATCH": 112,
  "SEMANTIC_MATCH": 30,
  "PARTIAL_MATCH": 49,
  "MISSING": 0,
  "INCORRECT": 4,
  "HALLUCINATION": 0,
  "CORRECT_NULL": 55,
  "NOT_EVALUABLE": 0
}
```

### Direct Gemini + Dictionary V1

```json
{
  "EXACT_MATCH": 119,
  "SEMANTIC_MATCH": 35,
  "PARTIAL_MATCH": 40,
  "MISSING": 1,
  "INCORRECT": 0,
  "HALLUCINATION": 0,
  "CORRECT_NULL": 55,
  "NOT_EVALUABLE": 0
}
```

### Direct Gemini + full Dictionary V2

```json
{
  "EXACT_MATCH": 120,
  "SEMANTIC_MATCH": 34,
  "PARTIAL_MATCH": 37,
  "MISSING": 2,
  "INCORRECT": 2,
  "HALLUCINATION": 0,
  "CORRECT_NULL": 55,
  "NOT_EVALUABLE": 0
}
```

### Direct Gemini + Compact Dictionary V2

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

## Overall changes

- Compact V2 → full V2: +1.20 percentage points
- Compact V2 → V1: +1.20 percentage points
- Compact V2 → baseline: -3.60 percentage points

## Recording-level asset changes versus full V2

- voice_006.wav: full V2="Packing plant conveyor BC-09 motor"; compact V2="Packing plant conveyor BC-9 motor"
- voice_008.wav: full V2=["Packing machine number 3", "pneumatic valve"]; compact V2=["Packing machine number 3", "pneumatic valve"]
- voice_034.wav: full V2=["bag filter fan", "motor", "coupling", "bearing"]; compact V2="bag filter fan"
- voice_037.wav: full V2=["small pump", "clinker cooler"]; compact V2="small pump near the clinker cooler"

## Compact/full behavior checks

- PC-09 → BC-09 substitution: inspect predictions for the literal identifiers; no automatic semantic reinterpretation was applied.
- Unsupported component additions and composite splitting were evaluated using the unchanged evaluator and prediction comparison.
- Quantity/specification behavior is reflected in the quantities accuracy and judgment counts above.

The conclusion is based on the completed 50-recording evaluation; prompt size alone is not treated as evidence of improvement.
