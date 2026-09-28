# Dictionary v1.0 evaluation — 9 recordings

Ground truth: `outputs/ground_truth/ground_truth_final.json`; exact baseline subset selected in memory.

Unchanged Agent 4 field comparers and normalization; nine-recording grouping uses the existing speaker evaluator.
Accuracy = 100 × (EXACT_MATCH + SEMANTIC_MATCH + CORRECT_NULL) / all field judgments, rounded to two decimals. PARTIAL_MATCH receives no accuracy credit.

9 recordings × 5 fields = 45 comparisons per pipeline; no missing, unexpected or skipped recordings.

## Overall and parameter accuracy

| Pipeline | Correct / Total | Accuracy |
|---|---:|---:|
| Direct Gemini | 38/45 | 84.44% |
| Sarvam + Gemini | 31/45 | 68.89% |

| Parameter | Direct Gemini | Sarvam + Gemini |
|---|---:|---:|
| assets | 7/9 (77.78%) | 6/9 (66.67%) |
| quantities | 4/9 (44.44%) | 1/9 (11.11%) |
| hours | 9/9 (100.00%) | 8/9 (88.89%) |
| dates | 9/9 (100.00%) | 8/9 (88.89%) |
| approval_intent | 9/9 (100.00%) | 8/9 (88.89%) |

## Speaker accuracy

| Speaker | Pipeline | Recordings | Correct / Total | Accuracy |
|---|---|---:|---:|---:|
| Sanjay | Direct Gemini | 3 | 13/15 | 86.67% |
| Jigish (legacy mapping: Mahesh) | Direct Gemini | 3 | 13/15 | 86.67% |
| Julfikar | Direct Gemini | 3 | 12/15 | 80.00% |
| Sanjay | Sarvam + Gemini | 3 | 10/15 | 66.67% |
| Jigish (legacy mapping: Mahesh) | Sarvam + Gemini | 3 | 9/15 | 60.00% |
| Julfikar | Sarvam + Gemini | 3 | 12/15 | 80.00% |

## Direct Gemini — per-recording results

Non-correct fields: 7. Every field below includes its ground truth, model value and classification.

### sanjaybhai_voice_051.wav — Sanjay

```json
{
  "assets": {
    "ground_truth": "Kiln inlet fan",
    "model": "Kiln inlet fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 kg grease",
      "1 seal kit",
      "2 fitters",
      "1 helper"
    ],
    "model": [
      "two fitters",
      "one helper",
      "one seal kit",
      "2 kg grease"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "4 hours"
      }
    ],
    "model": [
      "4 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Monday morning 8:00",
    "model": "Monday at 8:00 AM",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": "Process team से shutdown confirmation लेना है",
    "model": "Shutdown confirmation required from process team",
    "judgment": "SEMANTIC_MATCH"
  }
}
```

### sanjaybhai_voice_052.wav — Sanjay

```json
{
  "assets": {
    "ground_truth": "raw water pump number three",
    "model": "raw water pump number 3",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 technician",
      "1 helper",
      "mechanical seal replacement pending inspection confirmation"
    ],
    "model": [
      "1 technician",
      "1 helper"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "3 hours"
      }
    ],
    "model": [
      "3 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Tuesday morning",
    "model": "Tuesday morning",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### sanjaybhai_voice_053.wav — Sanjay

```json
{
  "assets": {
    "ground_truth": "Crusher की discharge chute",
    "model": "crusher discharge chute",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 welder",
      "1 fitter",
      "plate material not confirmed"
    ],
    "model": [
      "1 welder",
      "1 fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "4 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "4 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "tomorrow afternoon",
    "model": [
      "tomorrow afternoon"
    ],
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### jigishbhai_voice_057.wav — Jigish (legacy mapping: Mahesh)

```json
{
  "assets": {
    "ground_truth": "Raw mill conveyor",
    "model": "raw mill conveyor",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 fitters",
      "material not required currently"
    ],
    "model": [
      "2 fitters"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "2 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "tomorrow morning",
    "model": "tomorrow morning",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### jigishbhai_voice_058.wav — Jigish (legacy mapping: Mahesh)

```json
{
  "assets": {
    "ground_truth": "clinker cooler motor",
    "model": "clinker cooler motor",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 6316 C3 bearing",
      "2 kg grease",
      "4 M18 bolts",
      "2 fitters"
    ],
    "model": [
      "1 6316 C3 bearing",
      "2 kg of grease",
      "4 M18 bolts",
      "2 fitters"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "4 hours"
      }
    ],
    "model": [
      "4 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Friday at 10 AM",
    "model": [
      "Friday at 10 AM"
    ],
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### jigishbhai_voice_059.wav — Jigish (legacy mapping: Mahesh)

```json
{
  "assets": {
    "ground_truth": "Cement mill gearbox",
    "model": "Cement mill gearbox",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 engineer",
      "1 fitter",
      "gearbox replacement not to be assumed"
    ],
    "model": [
      "1 engineer",
      "1 fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "3 hours"
      }
    ],
    "model": [
      "3 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "today night shift",
    "model": "today night shift",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### julfikar_voice_054.wav — Julfikar

```json
{
  "assets": {
    "ground_truth": "Conveyor CV-18 के tail pulley",
    "model": "conveyor structure tail pulley",
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "2 22216 bearings",
      "1 kg grease",
      "2 fitters"
    ],
    "model": [
      "2 22216 bearings",
      "1 kg grease",
      "2 fitters"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "3 hours"
      }
    ],
    "model": [
      "3 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Saturday morning 9:00",
    "model": [
      "Saturday morning at 9 AM"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### julfikar_voice_055.wav — Julfikar

```json
{
  "assets": {
    "ground_truth": "compressor number four",
    "model": "compressor number 4",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "6 M12 bolts",
      "1 coupling",
      "2 fitters"
    ],
    "model": [
      "1 coupling",
      "6 M12 bolts",
      "2 fitters"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "3 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "3 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "3 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "3 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### julfikar_voice_056.wav — Julfikar

```json
{
  "assets": {
    "ground_truth": "Packing machine number two का pneumatic valve",
    "model": [
      "packing machine number 2",
      "pneumatic valve"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 technician",
      "valve replacement pending inspection"
    ],
    "model": [
      "one technician"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "2 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "today evening",
    "model": "today evening",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```


## Sarvam + Gemini — per-recording results

Non-correct fields: 14. Every field below includes its ground truth, model value and classification.

### sanjaybhai_voice_051.wav — Sanjay

```json
{
  "assets": {
    "ground_truth": "Kiln inlet fan",
    "model": "kiln inlet fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 kg grease",
      "1 seal kit",
      "2 fitters",
      "1 helper"
    ],
    "model": [
      "Two filters",
      "a helper",
      "One seal kit",
      "two kilos of grease"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "4 hours"
      }
    ],
    "model": [
      "four hours"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Monday morning 8:00",
    "model": [
      "Monday at 8 AM"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": "Process team से shutdown confirmation लेना है",
    "model": "Need to get shutdown confirmation from the process team.",
    "judgment": "INCORRECT"
  }
}
```

### sanjaybhai_voice_052.wav — Sanjay

```json
{
  "assets": {
    "ground_truth": "raw water pump number three",
    "model": [
      "raw water pump number three"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 technician",
      "1 helper",
      "mechanical seal replacement pending inspection confirmation"
    ],
    "model": [
      "one technician",
      "one helper"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "3 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "three hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Tuesday morning",
    "model": [
      "Tuesday morning"
    ],
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### sanjaybhai_voice_053.wav — Sanjay

```json
{
  "assets": {
    "ground_truth": "Crusher की discharge chute",
    "model": "discharge tube of the cluster",
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "1 welder",
      "1 fitter",
      "plate material not confirmed"
    ],
    "model": [
      "one welder",
      "one filter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "4 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "about four hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "tomorrow afternoon",
    "model": [
      "tomorrow afternoon"
    ],
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### jigishbhai_voice_057.wav — Jigish (legacy mapping: Mahesh)

```json
{
  "assets": {
    "ground_truth": "Raw mill conveyor",
    "model": "raw mill conveyor",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 fitters",
      "material not required currently"
    ],
    "model": [
      "Two fitters"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "about two hours"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "tomorrow morning",
    "model": [
      "tomorrow morning"
    ],
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### jigishbhai_voice_058.wav — Jigish (legacy mapping: Mahesh)

```json
{
  "assets": {
    "ground_truth": "clinker cooler motor",
    "model": "Clicker collar motor",
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "1 6316 C3 bearing",
      "2 kg grease",
      "4 M18 bolts",
      "2 fitters"
    ],
    "model": [
      "16316 C3 bearing",
      "2 kilogram of grease",
      "4 M18 bolts",
      "fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "4 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "4 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Friday at 10 AM",
    "model": [
      "Friday at 10:00 AM"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### jigishbhai_voice_059.wav — Jigish (legacy mapping: Mahesh)

```json
{
  "assets": {
    "ground_truth": "Cement mill gearbox",
    "model": "cement mill gearbox",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 engineer",
      "1 fitter",
      "gearbox replacement not to be assumed"
    ],
    "model": [
      "an engineer",
      "a fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "3 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "3 hours"
      }
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "dates": {
    "ground_truth": "today night shift",
    "model": [
      "tonight in the night shift"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### julfikar_voice_054.wav — Julfikar

```json
{
  "assets": {
    "ground_truth": "Conveyor CV-18 के tail pulley",
    "model": [
      "tail pulley of the conveyor track"
    ],
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "2 22216 bearings",
      "1 kg grease",
      "2 fitters"
    ],
    "model": [
      "two 22216 bearings",
      "one kilo of grease",
      "two fitters"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "3 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "3 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Saturday morning 9:00",
    "model": [
      "9 AM on Saturday morning"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### julfikar_voice_055.wav — Julfikar

```json
{
  "assets": {
    "ground_truth": "compressor number four",
    "model": "compressor number four",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "6 M12 bolts",
      "1 coupling",
      "2 fitters"
    ],
    "model": [
      "One coupling",
      "6 M12 bolts"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "3 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "3 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "3 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "3 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### julfikar_voice_056.wav — Julfikar

```json
{
  "assets": {
    "ground_truth": "Packing machine number two का pneumatic valve",
    "model": [
      "packing machine number two"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 technician",
      "valve replacement pending inspection"
    ],
    "model": [
      "one technician"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "2 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "today evening",
    "model": [
      "this evening"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

## Limitations and comparison notes

- The legacy speaker mapping labels jigishbhai_* as Mahesh. Reports display this group as Jigish (legacy mapping: Mahesh); grouping and scoring are unchanged.
- The extraction intervention included the dictionary plus explicit source-only safeguards; Agent 1 used fresh Sarvam transcripts. These results measure observed changes, not an isolated dictionary-only causal effect.
- The dictionary declares that its vocabulary was informed by these 59 recordings. Results do not establish held-out generalization.
- Scoring uses the existing deterministic heuristic comparers, not a new human audio review. HALLUCINATION is an evaluator classification against ground truth.
- No extraction API calls, regeneration, dictionary-based scoring, or changes to evaluation/normalization were made.
