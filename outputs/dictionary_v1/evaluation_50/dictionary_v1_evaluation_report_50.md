# Dictionary v1.0 evaluation — 50 recordings

Ground truth: `outputs/ground_truth/ground_truth_final.json`; exact baseline subset selected in memory.

Unchanged Agent 4 field comparers and normalization; nine-recording grouping uses the existing speaker evaluator.
Accuracy = 100 × (EXACT_MATCH + SEMANTIC_MATCH + CORRECT_NULL) / all field judgments, rounded to two decimals. PARTIAL_MATCH receives no accuracy credit.

50 recordings × 5 fields = 250 comparisons per pipeline; no missing, unexpected or skipped recordings.

## Overall and parameter accuracy

| Pipeline | Correct / Total | Accuracy |
|---|---:|---:|
| Direct Gemini | 209/250 | 83.60% |
| Sarvam + Gemini | 175/250 | 70.00% |

| Parameter | Direct Gemini | Sarvam + Gemini |
|---|---:|---:|
| assets | 46/50 (92.00%) | 31/50 (62.00%) |
| quantities | 21/50 (42.00%) | 18/50 (36.00%) |
| hours | 48/50 (96.00%) | 41/50 (82.00%) |
| dates | 49/50 (98.00%) | 40/50 (80.00%) |
| approval_intent | 45/50 (90.00%) | 45/50 (90.00%) |

## Direct Gemini — per-recording results

Non-correct fields: 41. Every field below includes its ground truth, model value and classification.

### voice001.wav

```json
{
  "assets": {
    "ground_truth": "Kiln auxiliary drive",
    "model": "Kiln auxiliary drive",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 6205 C3 bearings",
      "0.5 kg grease",
      "8 M60 bolts",
      "2 fitters"
    ],
    "model": [
      "two 6205 C3 bearings",
      "half kg grease",
      "eight M16 bolts",
      "two fitters"
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
      "4 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Saturday (exact time process team बताएगी)",
    "model": "Saturday (exact time to be confirmed by process team)",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_002.wav

```json
{
  "assets": {
    "ground_truth": "सीमेंट मिल नंबर एक के मोटर",
    "model": "cement mill number 1 motor",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 6312 C3 bearings",
      "0.5 kg grease",
      "2 fitters"
    ],
    "model": [
      "2 fitters",
      "two 6312 C3 bearings",
      "half kilo grease"
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
      "3 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "tomorrow morning 10:00",
    "model": "tomorrow at 10 AM",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_003.wav

```json
{
  "assets": {
    "ground_truth": "Belt conveyor BC-15",
    "model": [
      "belt conveyor BC-15"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 mechanical fitter",
      "1 engineer"
    ],
    "model": [
      "1 mechanical fitter",
      "1 engineer"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "2 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "today afternoon",
    "model": "today afternoon",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_004.wav

```json
{
  "assets": {
    "ground_truth": "cooling water pump number six",
    "model": "cooling water pump number 6",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 fitters",
      "material not confirmed until inspection"
    ],
    "model": [
      "two fitters"
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

### voice_005.wav

```json
{
  "assets": {
    "ground_truth": "रॉ मिल के फीडर",
    "model": [
      "raw mill feeder"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 seal kit",
      "4 gaskets",
      "1 mechanical fitter",
      "1 helper"
    ],
    "model": [
      "1 mechanical fitter",
      "1 helper",
      "1 seal kit",
      "4 gaskets"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "2 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "1 hour"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "2 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "1 hour"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Friday morning 11:00",
    "model": [
      "Friday at 11 AM"
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

### voice_006.wav

```json
{
  "assets": {
    "ground_truth": "Packing plant की conveyor PC-09 का motor",
    "model": "Conveyor PC-09 motor",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "1 fitter",
      "spare not confirmed"
    ],
    "model": [
      "1 electrician",
      "1 fitter"
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
    "ground_truth": "tomorrow evening",
    "model": "tomorrow evening",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_007.wav

```json
{
  "assets": {
    "ground_truth": "gearbox of bucket elevator BE-11",
    "model": [
      "bucket elevator BE-11 gearbox"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 mechanical engineer",
      "1 fitter"
    ],
    "model": [
      "1 mechanical engineer",
      "1 fitter"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "2 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Wednesday at nine in the morning",
    "model": [
      "Wednesday at 9 in the morning"
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

### voice_008.wav

```json
{
  "assets": {
    "ground_truth": "पैकिंग मशीन नंबर तीन",
    "model": [
      "packing machine number 3"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 technician",
      "valve/material not confirmed"
    ],
    "model": [
      "1 technician"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "1.5 hours"
      }
    ],
    "model": [
      "1.5 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "today shift",
    "model": "today's shift",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_009.wav

```json
{
  "assets": {
    "ground_truth": "Kiln ID fan",
    "model": "Kiln ID fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "4 22220 spherical roller bearings",
      "2 kg grease",
      "3 fitters"
    ],
    "model": [
      "4 22220 spherical roller bearings",
      "2 kg grease",
      "3 fitters"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "6 hours"
      }
    ],
    "model": [
      "6 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Saturday (exact time process team बताएगी)",
    "model": "Saturday (exact time to be provided by process team)",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_010.wav

```json
{
  "assets": {
    "ground_truth": "raw mill feeder",
    "model": "raw mill feeder",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 seal kit",
      "6 gaskets",
      "2 fitters",
      "1 helper"
    ],
    "model": [
      "2 fitters",
      "1 helper",
      "1 seal kit",
      "6 gaskets"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "5 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "2 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "5 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "2 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Thursday afternoon",
    "model": "Thursday afternoon",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_011.wav

```json
{
  "assets": {
    "ground_truth": "क्लिंकर बेल्ट कन्वेयर",
    "model": "clinker belt conveyor",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 welder",
      "1 fitter"
    ],
    "model": [
      "1 welder",
      "1 fitter"
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
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  },
  "approval_intent": {
    "ground_truth": "काम शुरू करने से पहले safety permit और process team की approval जरूरी है। Approval मिलने के बाद ही काम शुरू करना है",
    "model": "Safety permit and process team approval required before starting work",
    "judgment": "PARTIAL_MATCH"
  }
}
```

### voice_012.wav

```json
{
  "assets": {
    "ground_truth": "Crusher area में जो छोटी slurry pump",
    "model": "slurry pump",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 fitter",
      "tag number not available"
    ],
    "model": [
      "1 fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
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

### voice_013.wav

```json
{
  "assets": {
    "ground_truth": "compressor number two",
    "model": [
      "compressor number 2",
      "air filter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 air filter",
      "1 technician",
      "1 helper"
    ],
    "model": [
      "1 technician",
      "1 helper",
      "1 air filter"
    ],
    "judgment": "EXACT_MATCH"
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
    "ground_truth": "Monday at 10 AM",
    "model": [
      "Monday at 10 AM"
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

### voice_014.wav

```json
{
  "assets": {
    "ground_truth": "Cement mill की lubrication line",
    "model": [
      "cement mill",
      "lubrication line"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "0.5 kg grease",
      "3 grease nipples",
      "2 fitters"
    ],
    "model": [
      "3 new grease nipples",
      "2 fitters",
      "half kg grease"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "1 hour"
      }
    ],
    "model": [
      "1 hour"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "today afternoon 3:00",
    "model": "today at 3 PM",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_015.wav

```json
{
  "assets": {
    "ground_truth": "Packing plant के screw conveyor",
    "model": [
      "Packing plant screw conveyor chain"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 fitter",
      "chain quantity/specification not confirmed",
      "chain replacement pending inspection"
    ],
    "model": [
      "1 fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
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

### voice_016.wav

```json
{
  "assets": {
    "ground_truth": "motor of conveyor CV-21",
    "model": "conveyor CV-21 motor",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician"
    ],
    "model": [
      "1 electrician"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "2 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "current shift",
    "model": "current shift",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_017.wav

```json
{
  "assets": {
    "ground_truth": "Kiln burner",
    "model": "kiln burner",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 technicians",
      "1 fitter",
      "spare material not confirmed"
    ],
    "model": [
      "2 technicians",
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
      "4 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Saturday (exact time process team बताएगी)",
    "model": "Saturday (exact time will be provided by process team)",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_018.wav

```json
{
  "assets": {
    "ground_truth": "Raw mill hydraulic pump",
    "model": "Raw mill hydraulic pump",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 filters",
      "1 technician",
      "1 helper"
    ],
    "model": [
      "2 filters",
      "1 technician",
      "1 helper"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "1.5 hours"
      }
    ],
    "model": [
      "1.5 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Wednesday morning",
    "model": "Wednesday morning",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_019.wav

```json
{
  "assets": {
    "ground_truth": "clinker cooler fan",
    "model": "clinker cooler fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 6318 C3 bearings",
      "1 kg grease",
      "8 M20 bolts",
      "2 fitters"
    ],
    "model": [
      "2 bearings",
      "6318 C3",
      "1 kilogram grease",
      "8 M20 bolts",
      "2 fitters"
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
      "4 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Friday at 2 PM",
    "model": "Friday at 2 PM",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_020.wav

```json
{
  "assets": {
    "ground_truth": "Bucket elevator नंबर चार",
    "model": "Bucket Elevator number 4",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 mechanical engineer",
      "1 fitter"
    ],
    "model": [
      "1 mechanical engineer",
      "1 fitter"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "2 hours"
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

### voice_021.wav

```json
{
  "assets": {
    "ground_truth": "Cement mill की chute liner",
    "model": "Cement mill",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "12 M16 bolts",
      "6 liner plates",
      "4 fitters",
      "1 helper",
      "exact time not confirmed"
    ],
    "model": [
      "4 fitters",
      "1 helper",
      "6 liner plates",
      "12 M16 bolts"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "8 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "3 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "8 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "3 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Sunday (exact time not confirmed)",
    "model": "Sunday (exact time not confirmed)",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_022.wav

```json
{
  "assets": {
    "ground_truth": "conveyor number twelve",
    "model": "conveyor number 12",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 welder",
      "2 fitters",
      "material not confirmed until site inspection"
    ],
    "model": [
      "one welder",
      "two fitters"
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
    "ground_truth": "A hot work permit and process team approval are required before starting the job",
    "model": "hot work permit and process team approval required before starting the job",
    "judgment": "SEMANTIC_MATCH"
  }
}
```

### voice_023.wav

```json
{
  "assets": {
    "ground_truth": "Compressor नंबर चार",
    "model": "compressor number 4",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "4 liters compressor oil",
      "1 air filter",
      "1 technician",
      "1 helper"
    ],
    "model": [
      "1 technician",
      "1 helper",
      "1 air filter",
      "4 litres compressor oil"
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
      "3 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Monday morning 9:30",
    "model": "Monday at 9:30 AM",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_024.wav

```json
{
  "assets": {
    "ground_truth": "Workshop के पास जो बड़ा exhaust fan",
    "model": "exhaust fan",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "1 fitter",
      "equipment tag not available",
      "bearing replacement or balancing pending confirmation"
    ],
    "model": [
      "1 electrician",
      "1 fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "2 hours"
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

### voice_025.wav

```json
{
  "assets": {
    "ground_truth": "cooling tower fan",
    "model": "cooling tower fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 fitter"
    ],
    "model": [
      "1 fitter"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "2 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "today at 4 PM",
    "model": "today at 4 PM",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": "No approval is required for the inspection",
    "model": null,
    "judgment": "MISSING"
  }
}
```

### voice_026.wav

```json
{
  "assets": {
    "ground_truth": "Raw water pump नंबर दो",
    "model": "raw water pump number 2",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "8 M12 bolts",
      "1 coupling",
      "2 fitters",
      "1 helper"
    ],
    "model": [
      "2 fitters",
      "1 helper",
      "1 coupling",
      "8 M12 bolts"
    ],
    "judgment": "EXACT_MATCH"
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
    "ground_truth": "today night 8:00",
    "model": "tonight at 8 PM",
    "judgment": "PARTIAL_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_027.wav

```json
{
  "assets": {
    "ground_truth": "Kiln main drive",
    "model": "kiln main drive",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 mechanical engineer",
      "2 fitters",
      "bearing size/quantity not known"
    ],
    "model": [
      "1 mechanical engineer",
      "2 fitters"
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

### voice_028.wav

```json
{
  "assets": {
    "ground_truth": "compressor number five",
    "model": "compressor number 5",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 technician",
      "1 mechanical engineer",
      "material not confirmed until inspection"
    ],
    "model": [
      "1 technician",
      "1 mechanical engineer"
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

### voice_029.wav

```json
{
  "assets": {
    "ground_truth": "Cement mill separator",
    "model": [
      "cement mill separator"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 kg grease",
      "1 belt",
      "2 pulley bearings",
      "3 fitters"
    ],
    "model": [
      "3 fitters",
      "1 belt",
      "2 pulley bearings",
      "1 kg grease"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "5 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "2 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "5 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "2 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Tuesday morning 8:00",
    "model": [
      "Tuesday at 8 AM"
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

### voice_030.wav

```json
{
  "assets": {
    "ground_truth": "Packing machine number seven",
    "model": "Packing machine number 7",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "morning/afternoon not confirmed"
    ],
    "model": [
      "1 electrician"
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
    "ground_truth": "Friday (morning/afternoon not confirmed) (Exact time maintenance supervisor बताएगा)",
    "model": "Friday (exact time to be confirmed by maintenance supervisor)",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_031.wav

```json
{
  "assets": {
    "ground_truth": "hydraulic cylinder on the roller press",
    "model": [
      "hydraulic cylinder",
      "roller press"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 mechanical fitter",
      "1 hydraulic technician",
      "seal kit and oil quantity not known",
      "materials not confirmed until inspection"
    ],
    "model": [
      "1 mechanical fitter",
      "1 hydraulic technician"
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
        "value": "3 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
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

### voice_032.wav

```json
{
  "assets": {
    "ground_truth": "Conveyor number six",
    "model": "conveyor number 6",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "8 liters gear oil",
      "1 fitter",
      "1 helper",
      "filter change not required"
    ],
    "model": [
      "1 fitter",
      "1 helper",
      "8 liter gear oil"
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
    "ground_truth": "Saturday evening",
    "model": "Saturday evening",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_033.wav

```json
{
  "assets": {
    "ground_truth": "Kiln ID fan",
    "model": "Kiln ID fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 6315 C3 bearings",
      "1 kg grease",
      "10 M16 bolts",
      "2 fitters"
    ],
    "model": [
      "2 6315 C3 bearings",
      "1 kg grease",
      "10 M16 bolts",
      "2 fitters"
    ],
    "judgment": "EXACT_MATCH"
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
    "ground_truth": "Sunday (exact time process team confirm करेगी)",
    "model": "Sunday (exact time process team will confirm)",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_034.wav

```json
{
  "assets": {
    "ground_truth": "bag filter fan",
    "model": "bag filter fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "1 fitter",
      "no replacement assumed before inspection"
    ],
    "model": [
      "1 electrician",
      "1 fitter"
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
    "ground_truth": "Thursday at 11 AM",
    "model": "Thursday at 11 AM",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_035.wav

```json
{
  "assets": {
    "ground_truth": "Raw mill fan",
    "model": "raw mill fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "6 bolts",
      "1 coupling",
      "2 fitters",
      "1 helper"
    ],
    "model": [
      "2 fitters",
      "1 helper",
      "1 coupling",
      "6 bolts"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "4 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "2 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "4 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "2 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Friday afternoon 1:00",
    "model": "Friday at 1 PM",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_036.wav

```json
{
  "assets": {
    "ground_truth": "Conveyor BC-20",
    "model": "Conveyor BC-20",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 splice kit",
      "3 fitters",
      "1 supervisor"
    ],
    "model": [
      "3 fitters",
      "1 supervisor",
      "1 splice kit"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "6 hours"
      }
    ],
    "model": [
      "6 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  },
  "approval_intent": {
    "ground_truth": "काम शुरू करने से पहले process team की approval और safety permit दोनों चाहिए। Approval के बिना काम शुरू नहीं करना है",
    "model": "Process team approval and safety permit required before starting work",
    "judgment": "PARTIAL_MATCH"
  }
}
```

### voice_037.wav

```json
{
  "assets": {
    "ground_truth": "small pump near the clinker cooler",
    "model": "small pump near the clinker cooler",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 fitter",
      "equipment tag not available",
      "do not order bearings until inspection confirms cause"
    ],
    "model": [
      "1 fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
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

### voice_038.wav

```json
{
  "assets": {
    "ground_truth": "Compressor नंबर एक",
    "model": "compressor number 1",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "5 liters compressor oil",
      "1 air filter",
      "1 technician",
      "1 helper"
    ],
    "model": [
      "1 technician",
      "1 helper",
      "1 filter",
      "5 litres compressor oil"
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
    "ground_truth": "Monday morning 10:00",
    "model": "Monday at 10 AM",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_039.wav

```json
{
  "assets": {
    "ground_truth": "Packing conveyor PC-14",
    "model": "Packing conveyor PC-14 motor",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "1 mechanical fitter",
      "spare material not confirmed"
    ],
    "model": [
      "1 electrician",
      "1 mechanical fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "1.5 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "1.5 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "today second shift",
    "model": "today, second shift",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_040.wav

```json
{
  "assets": {
    "ground_truth": "damaged handrail near the kiln platform",
    "model": "handrail near the kiln platform",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 welder",
      "1 fitter",
      "steel material quantity not confirmed until site measurement"
    ],
    "model": [
      "one welder",
      "one fitter"
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
      "4 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  },
  "approval_intent": {
    "ground_truth": "A work-at-height permit is required before starting",
    "model": "work at height permit required before starting",
    "judgment": "PARTIAL_MATCH"
  }
}
```

### voice_041.wav

```json
{
  "assets": {
    "ground_truth": "Bucket elevator BE-09 के head pulley",
    "model": [
      "Bucket elevator BE-09"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 22218 bearings",
      "4 kg grease",
      "12 M20 bolts",
      "3 fitters"
    ],
    "model": [
      "2 bearings (22218)",
      "4 kg grease",
      "12 M20 bolts",
      "3 fitters"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "5 hours"
      }
    ],
    "model": [
      "5 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Wednesday morning 7:00",
    "model": [
      "Wednesday at 7:00 AM"
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

### voice_042.wav

```json
{
  "assets": {
    "ground_truth": "Crusher number two",
    "model": [
      "Crusher number 2",
      "gearbox"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 mechanical engineer",
      "1 fitter",
      "material not confirmed until leakage source found",
      "gearbox replacement not to be done yet"
    ],
    "model": [
      "one mechanical engineer",
      "one fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "2 hours"
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

### voice_043.wav

```json
{
  "assets": {
    "ground_truth": "cement mill lubrication system",
    "model": "cement mill lubrication system",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 fitters",
      "spare parts not known yet"
    ],
    "model": [
      "2 fitters"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "2 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Saturday (exact time will be provided by the process team)",
    "model": "Saturday (exact time will be provided by the process team)",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_044.wav

```json
{
  "assets": {
    "ground_truth": "Packing plant की motor starter panel",
    "model": [
      "packing plant motor starter panel"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "1 engineer",
      "replacement material not confirmed"
    ],
    "model": [
      "1 electrician",
      "1 engineer"
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
    "ground_truth": "today shift",
    "model": "today's shift",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_045.wav

```json
{
  "assets": {
    "ground_truth": "Raw mill conveyor",
    "model": "raw mill conveyor",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "6 M20 bolts",
      "2 fitters",
      "1 helper",
      "exact time not confirmed yet"
    ],
    "model": [
      "6 M20 bolts",
      "2 fitters",
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
    "ground_truth": "Thursday morning (exact time later confirm)",
    "model": "Thursday morning (exact time to be confirmed later)",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_046.wav

```json
{
  "assets": {
    "ground_truth": "kiln hydraulic system",
    "model": "kiln hydraulic system",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 seal kit",
      "2 fitters",
      "1 hydraulic technician"
    ],
    "model": [
      "2 fitters",
      "1 hydraulic technician",
      "1 seal kit"
    ],
    "judgment": "EXACT_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "6 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "1.5 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "6 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "90 minutes"
      }
    ],
    "judgment": "PARTIAL_MATCH"
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

### voice_047.wav

```json
{
  "assets": {
    "ground_truth": "Boiler feed pump",
    "model": "boiler feed pump",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 technicians",
      "spare parts not confirmed until site inspection"
    ],
    "model": [
      "2 technicians"
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
      "4 hours"
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  },
  "approval_intent": {
    "ground_truth": "काम शुरू करने से पहले utilities team की approval जरूरी है। Approval मिलने के बाद ही job शुरू करना है",
    "model": "Approval required from utilities team before starting job",
    "judgment": "PARTIAL_MATCH"
  }
}
```

### voice_048.wav

```json
{
  "assets": {
    "ground_truth": "Cooling tower pump",
    "model": "cooling tower pump",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 bearings",
      "1 kg grease",
      "2 fitters",
      "bearing number not confirmed"
    ],
    "model": [
      "2 bearings (bearing number not confirmed)",
      "2 fitters",
      "1 kg grease"
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
    "ground_truth": "Friday afternoon",
    "model": "Friday afternoon",
    "judgment": "EXACT_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```

### voice_049.wav

```json
{
  "assets": {
    "ground_truth": "motor of conveyor CV-31",
    "model": "conveyor CV-31 motor",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "1 mechanical fitter",
      "motor replacement not to be raised yet"
    ],
    "model": [
      "1 electrician",
      "1 mechanic fitter"
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
    "ground_truth": "night shift",
    "model": [
      "night shift"
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

### voice_050.wav

```json
{
  "assets": {
    "ground_truth": "Cement mill fan",
    "model": "cement mill fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 bearings",
      "1 belt",
      "2 fitters"
    ],
    "model": [
      "2 fitters",
      "1 belt",
      "2 bearings"
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
    "ground_truth": "Sunday (exact time maintenance team बताएगी)",
    "model": "Sunday (exact time maintenance team will inform)",
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  }
}
```


## Sarvam + Gemini — per-recording results

Non-correct fields: 75. Every field below includes its ground truth, model value and classification.

### voice001.wav

```json
{
  "assets": {
    "ground_truth": "Kiln auxiliary drive",
    "model": "Kiran auxiliary drive",
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "2 6205 C3 bearings",
      "0.5 kg grease",
      "8 M60 bolts",
      "2 fitters"
    ],
    "model": [
      "two 6205 C3 bearings",
      "half a kilo of grease",
      "eight M60 bolts",
      "two fitters"
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
      "four hours"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Saturday (exact time process team बताएगी)",
    "model": [
      "Saturday"
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

### voice_002.wav

```json
{
  "assets": {
    "ground_truth": "सीमेंट मिल नंबर एक के मोटर",
    "model": "motor of cement mill number one",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 6312 C3 bearings",
      "0.5 kg grease",
      "2 fitters"
    ],
    "model": [
      "two fitters",
      "two 6312 C3 bearings",
      "half a kilo of grease"
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
      "approximately three hours"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "tomorrow morning 10:00",
    "model": [
      "tomorrow morning at 10 AM"
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

### voice_003.wav

```json
{
  "assets": {
    "ground_truth": "Belt conveyor BC-15",
    "model": "belt conveyor BC15",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 mechanical fitter",
      "1 engineer"
    ],
    "model": [
      "one mechanical fitter",
      "one engineer"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "2 hours"
      }
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "dates": {
    "ground_truth": "today afternoon",
    "model": [
      "this afternoon"
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

### voice_004.wav

```json
{
  "assets": {
    "ground_truth": "cooling water pump number six",
    "model": "cooling water pump number six",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 fitters",
      "material not confirmed until inspection"
    ],
    "model": [
      "two fitters"
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
        "value": "3 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
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

### voice_005.wav

```json
{
  "assets": {
    "ground_truth": "रॉ मिल के फीडर",
    "model": "raw mill feeder",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 seal kit",
      "4 gaskets",
      "1 mechanical fitter",
      "1 helper"
    ],
    "model": [
      "1 mechanical fitter",
      "1 helper",
      "1 seal kit",
      "4 gas kits"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "2 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "1 hour"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "2 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "1 hour"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Friday morning 11:00",
    "model": [
      "Friday at 11 AM"
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

### voice_006.wav

```json
{
  "assets": {
    "ground_truth": "Packing plant की conveyor PC-09 का motor",
    "model": [
      "motor",
      "conveyor PC9",
      "packing plant"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "1 fitter",
      "spare not confirmed"
    ],
    "model": [
      "one electrician",
      "one fitter"
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
        "value": "two hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "tomorrow evening",
    "model": [
      "tomorrow evening"
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

### voice_007.wav

```json
{
  "assets": {
    "ground_truth": "gearbox of bucket elevator BE-11",
    "model": [
      "gearbox",
      "bucket elevator BE11"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 mechanical engineer",
      "1 fitter"
    ],
    "model": [
      "one mechanical engineer",
      "one fitter"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "two hours"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Wednesday at nine in the morning",
    "model": [
      "Wednesday at 9:00 in the morning"
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

### voice_008.wav

```json
{
  "assets": {
    "ground_truth": "पैकिंग मशीन नंबर तीन",
    "model": [
      "packing machine number three",
      "pneumatic valve"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 technician",
      "valve/material not confirmed"
    ],
    "model": [
      "one technician"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "1.5 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "one and a half hours"
      }
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "dates": {
    "ground_truth": "today shift",
    "model": [
      "today's shift"
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

### voice_009.wav

```json
{
  "assets": {
    "ground_truth": "Kiln ID fan",
    "model": "kiln ID fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "4 22220 spherical roller bearings",
      "2 kg grease",
      "3 fitters"
    ],
    "model": [
      "four 22,220 spherical roller bearings",
      "two kilos of grease",
      "three feet"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "6 hours"
      }
    ],
    "model": [
      "six hours"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Saturday (exact time process team बताएगी)",
    "model": [
      "Saturday"
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

### voice_010.wav

```json
{
  "assets": {
    "ground_truth": "raw mill feeder",
    "model": "raw mill feeder",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 seal kit",
      "6 gaskets",
      "2 fitters",
      "1 helper"
    ],
    "model": [
      "two fitters",
      "one helper",
      "one seal kit",
      "six gaskets"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "5 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "2 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "5 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "2 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Thursday afternoon",
    "model": [
      "Thursday afternoon"
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

### voice_011.wav

```json
{
  "assets": {
    "ground_truth": "क्लिंकर बेल्ट कन्वेयर",
    "model": "clicker belt conveyor",
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "1 welder",
      "1 fitter"
    ],
    "model": [
      "a welder",
      "a fitter"
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
        "value": "about three hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  },
  "approval_intent": {
    "ground_truth": "काम शुरू करने से पहले safety permit और process team की approval जरूरी है। Approval मिलने के बाद ही काम शुरू करना है",
    "model": "Before starting the work, safety permit and process team approval are necessary.",
    "judgment": "PARTIAL_MATCH"
  }
}
```

### voice_012.wav

```json
{
  "assets": {
    "ground_truth": "Crusher area में जो छोटी slurry pump",
    "model": "small slurry pump",
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "1 fitter",
      "tag number not available"
    ],
    "model": [
      "one fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
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

### voice_013.wav

```json
{
  "assets": {
    "ground_truth": "compressor number two",
    "model": [
      "compressor number two"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 air filter",
      "1 technician",
      "1 helper"
    ],
    "model": [
      "one technician",
      "one helper",
      "one air filter"
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
      {
        "kind": "work_duration",
        "value": "4 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Monday at 10 AM",
    "model": [
      "Monday at 10:00 a.m."
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

### voice_014.wav

```json
{
  "assets": {
    "ground_truth": "Cement mill की lubrication line",
    "model": "cement mill's lubrication line",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "0.5 kg grease",
      "3 grease nipples",
      "2 fitters"
    ],
    "model": [
      "three new grease snips",
      "two fitters",
      "half a kilo of grease"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "1 hour"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "one hour"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "today afternoon 3:00",
    "model": [
      "3 PM today"
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

### voice_015.wav

```json
{
  "assets": {
    "ground_truth": "Packing plant के screw conveyor",
    "model": [
      "screw conveyor",
      "packing plant"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 fitter",
      "chain quantity/specification not confirmed",
      "chain replacement pending inspection"
    ],
    "model": [
      "one fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
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

### voice_016.wav

```json
{
  "assets": {
    "ground_truth": "motor of conveyor CV-21",
    "model": [
      "conveyor CV21",
      "motor"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician"
    ],
    "model": [
      "one electrician"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "two hours"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "current shift",
    "model": [
      "current shift"
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

### voice_017.wav

```json
{
  "assets": {
    "ground_truth": "Kiln burner",
    "model": [
      "kiln burner"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 technicians",
      "1 fitter",
      "spare material not confirmed"
    ],
    "model": [
      "two technicians",
      "one fitter"
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
    "ground_truth": "Saturday (exact time process team बताएगी)",
    "model": [
      "Saturday"
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

### voice_018.wav

```json
{
  "assets": {
    "ground_truth": "Raw mill hydraulic pump",
    "model": "raw mill hydraulic pump filter",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 filters",
      "1 technician",
      "1 helper"
    ],
    "model": [
      "two filters",
      "one technician",
      "one helper"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "1.5 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "one and a half hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Wednesday morning",
    "model": [
      "Wednesday morning"
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

### voice_019.wav

```json
{
  "assets": {
    "ground_truth": "clinker cooler fan",
    "model": [
      "Klinkner cooler fan"
    ],
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "2 6318 C3 bearings",
      "1 kg grease",
      "8 M20 bolts",
      "2 fitters"
    ],
    "model": [
      "two bearings",
      "1 kilogram of grease",
      "8 M20 bolts",
      "two fitters"
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
        "value": "four hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Friday at 2 PM",
    "model": [
      "Friday at 2:00 p.m."
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

### voice_020.wav

```json
{
  "assets": {
    "ground_truth": "Bucket elevator नंबर चार",
    "model": [
      "bucket elevator number four"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 mechanical engineer",
      "1 fitter"
    ],
    "model": [
      "a mechanical engineer",
      "a fitter"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "2 hours"
      }
    ],
    "judgment": "PARTIAL_MATCH"
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

### voice_021.wav

```json
{
  "assets": {
    "ground_truth": "Cement mill की chute liner",
    "model": [
      "cement mill"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "12 M16 bolts",
      "6 liner plates",
      "4 fitters",
      "1 helper",
      "exact time not confirmed"
    ],
    "model": [
      "four fitters",
      "one helper",
      "six liner plates",
      "twelve M16 bolts"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "8 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "3 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "eight hours"
      },
      {
        "kind": "machine_downtime",
        "value": "three hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Sunday (exact time not confirmed)",
    "model": [
      "Sunday"
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

### voice_022.wav

```json
{
  "assets": {
    "ground_truth": "conveyor number twelve",
    "model": "conveyor number 12",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 welder",
      "2 fitters",
      "material not confirmed until site inspection"
    ],
    "model": [
      "one welder",
      "two fitters"
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
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  },
  "approval_intent": {
    "ground_truth": "A hot work permit and process team approval are required before starting the job",
    "model": "A hot work permit and process team approval are required before starting the job",
    "judgment": "EXACT_MATCH"
  }
}
```

### voice_023.wav

```json
{
  "assets": {
    "ground_truth": "Compressor नंबर चार",
    "model": [
      "compressor number four"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "4 liters compressor oil",
      "1 air filter",
      "1 technician",
      "1 helper"
    ],
    "model": [
      "one technician",
      "one helper",
      "one air filter",
      "four liters of compressor oil"
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
        "value": "three hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Monday morning 9:30",
    "model": [
      "Monday at 9:30 AM"
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

### voice_024.wav

```json
{
  "assets": {
    "ground_truth": "Workshop के पास जो बड़ा exhaust fan",
    "model": "large exhaust fan",
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "1 fitter",
      "equipment tag not available",
      "bearing replacement or balancing pending confirmation"
    ],
    "model": [
      "one electrician",
      "one fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "two hours"
      }
    ],
    "judgment": "PARTIAL_MATCH"
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

### voice_025.wav

```json
{
  "assets": {
    "ground_truth": "cooling tower fan",
    "model": "cooling tower fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 fitter"
    ],
    "model": [
      "One fitter"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "two hours"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "today at 4 PM",
    "model": [
      "today at 4:00 p.m."
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "approval_intent": {
    "ground_truth": "No approval is required for the inspection",
    "model": null,
    "judgment": "MISSING"
  }
}
```

### voice_026.wav

```json
{
  "assets": {
    "ground_truth": "Raw water pump नंबर दो",
    "model": [
      "row water pump number two"
    ],
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "8 M12 bolts",
      "1 coupling",
      "2 fitters",
      "1 helper"
    ],
    "model": [
      "Two fitters",
      "one helper",
      "One coupling",
      "eight M12 bolts"
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
      {
        "kind": "work_duration",
        "value": "4 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "today night 8:00",
    "model": [
      "tonight at 8 PM"
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

### voice_027.wav

```json
{
  "assets": {
    "ground_truth": "Kiln main drive",
    "model": [
      "kiln main drive"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 mechanical engineer",
      "2 fitters",
      "bearing size/quantity not known"
    ],
    "model": [
      "one mechanical engineer",
      "two fitters"
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

### voice_028.wav

```json
{
  "assets": {
    "ground_truth": "compressor number five",
    "model": "compressor number five",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 technician",
      "1 mechanical engineer",
      "material not confirmed until inspection"
    ],
    "model": [
      "one technician",
      "one mechanical engineer"
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

### voice_029.wav

```json
{
  "assets": {
    "ground_truth": "Cement mill separator",
    "model": "cement mill separator",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 kg grease",
      "1 belt",
      "2 pulley bearings",
      "3 fitters"
    ],
    "model": [
      "Three fitters",
      "One belt",
      "two pulley bearings",
      "one kilogram of grease"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "5 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "2 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "about five hours"
      },
      {
        "kind": "machine_downtime",
        "value": "two hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Tuesday morning 8:00",
    "model": [
      "Tuesday at 8 AM"
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

### voice_030.wav

```json
{
  "assets": {
    "ground_truth": "Packing machine number seven",
    "model": "packing machine number 7",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "morning/afternoon not confirmed"
    ],
    "model": [
      "1 electrician"
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
    "ground_truth": "Friday (morning/afternoon not confirmed) (Exact time maintenance supervisor बताएगा)",
    "model": [
      "Friday"
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

### voice_031.wav

```json
{
  "assets": {
    "ground_truth": "hydraulic cylinder on the roller press",
    "model": [
      "roller press",
      "hydraulic cylinder"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 mechanical fitter",
      "1 hydraulic technician",
      "seal kit and oil quantity not known",
      "materials not confirmed until inspection"
    ],
    "model": [
      "one mechanical fitter",
      "one hydraulic technician"
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

### voice_032.wav

```json
{
  "assets": {
    "ground_truth": "Conveyor number six",
    "model": [
      "conveyor number six"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "8 liters gear oil",
      "1 fitter",
      "1 helper",
      "filter change not required"
    ],
    "model": [
      "one fitter",
      "one helper",
      "eight liters of gear oil"
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
      "two hours"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Saturday evening",
    "model": [
      "Saturday evening"
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

### voice_033.wav

```json
{
  "assets": {
    "ground_truth": "Kiln ID fan",
    "model": "kiln ID fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 6315 C3 bearings",
      "1 kg grease",
      "10 M16 bolts",
      "2 fitters"
    ],
    "model": [
      "Two 6315 C3 bearings",
      "one kilo of grease",
      "ten M16 bolts",
      "Two fitters"
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
      {
        "kind": "work_duration",
        "value": "four hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Sunday (exact time process team confirm करेगी)",
    "model": [
      "Sunday"
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

### voice_034.wav

```json
{
  "assets": {
    "ground_truth": "bag filter fan",
    "model": "bag filter fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "1 fitter",
      "no replacement assumed before inspection"
    ],
    "model": [
      "one electrician",
      "one fitter"
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
        "value": "3 hours"
      }
    ],
    "judgment": "EXACT_MATCH"
  },
  "dates": {
    "ground_truth": "Thursday at 11 AM",
    "model": [
      "Thursday at 11:00 a.m."
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

### voice_035.wav

```json
{
  "assets": {
    "ground_truth": "Raw mill fan",
    "model": "raw mill fan",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "6 bolts",
      "1 coupling",
      "2 fitters",
      "1 helper"
    ],
    "model": [
      "two fitters",
      "one helper",
      "one coupling",
      "six bolts"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "4 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "2 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "four hours"
      },
      {
        "kind": "machine_downtime",
        "value": "two hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Friday afternoon 1:00",
    "model": [
      "Friday at 1 PM"
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

### voice_036.wav

```json
{
  "assets": {
    "ground_truth": "Conveyor BC-20",
    "model": [
      "conveyor BC20 belt"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 splice kit",
      "3 fitters",
      "1 supervisor"
    ],
    "model": [
      "three fitters",
      "one supervisor",
      "one splice kit"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "6 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "about six hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  },
  "approval_intent": {
    "ground_truth": "काम शुरू करने से पहले process team की approval और safety permit दोनों चाहिए। Approval के बिना काम शुरू नहीं करना है",
    "model": "Process team approval and safety permit are required before starting work",
    "judgment": "PARTIAL_MATCH"
  }
}
```

### voice_037.wav

```json
{
  "assets": {
    "ground_truth": "small pump near the clinker cooler",
    "model": [
      "small pump",
      "clinker cooler"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 fitter",
      "equipment tag not available",
      "do not order bearings until inspection confirms cause"
    ],
    "model": [
      "one fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
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

### voice_038.wav

```json
{
  "assets": {
    "ground_truth": "Compressor नंबर एक",
    "model": [
      "compressor number one"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "5 liters compressor oil",
      "1 air filter",
      "1 technician",
      "1 helper"
    ],
    "model": [
      "a technician",
      "a helper",
      "a filter",
      "five liters of compressor oil"
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
    "ground_truth": "Monday morning 10:00",
    "model": [
      "Monday morning at 10 AM"
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

### voice_039.wav

```json
{
  "assets": {
    "ground_truth": "Packing conveyor PC-14",
    "model": [
      "packing conveyor PC14 motor"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "1 mechanical fitter",
      "spare material not confirmed"
    ],
    "model": [
      "one electrician",
      "one mechanical fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "1.5 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "one and a half hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "today second shift",
    "model": [
      "today's second shift"
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

### voice_040.wav

```json
{
  "assets": {
    "ground_truth": "damaged handrail near the kiln platform",
    "model": "handrail near the clean platform",
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "1 welder",
      "1 fitter",
      "steel material quantity not confirmed until site measurement"
    ],
    "model": [
      "one welder",
      "one fitter"
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
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  },
  "approval_intent": {
    "ground_truth": "A work-at-height permit is required before starting",
    "model": "work at height permit required before starting",
    "judgment": "PARTIAL_MATCH"
  }
}
```

### voice_041.wav

```json
{
  "assets": {
    "ground_truth": "Bucket elevator BE-09 के head pulley",
    "model": [
      "head pulley of bucket elevator B9"
    ],
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "2 22218 bearings",
      "4 kg grease",
      "12 M20 bolts",
      "3 fitters"
    ],
    "model": [
      "two bearings",
      "4 kg of grease",
      "12 M20 bolts",
      "three fitters"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "5 hours"
      }
    ],
    "model": [
      "five hours"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Wednesday morning 7:00",
    "model": [
      "7 AM on Wednesday"
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

### voice_042.wav

```json
{
  "assets": {
    "ground_truth": "Crusher number two",
    "model": [
      "crosser number two",
      "gearbox"
    ],
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "1 mechanical engineer",
      "1 fitter",
      "material not confirmed until leakage source found",
      "gearbox replacement not to be done yet"
    ],
    "model": [
      "one mechanical engineer",
      "one fitter"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      "2 hours"
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

### voice_043.wav

```json
{
  "assets": {
    "ground_truth": "cement mill lubrication system",
    "model": "cement mill lubrication system",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 fitters",
      "spare parts not known yet"
    ],
    "model": [
      "two fitters"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "inspection_duration",
        "value": "2 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "two hours"
      }
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "dates": {
    "ground_truth": "Saturday (exact time will be provided by the process team)",
    "model": [
      "Saturday"
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

### voice_044.wav

```json
{
  "assets": {
    "ground_truth": "Packing plant की motor starter panel",
    "model": [
      "motor starter panel",
      "packing plant"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "1 engineer",
      "replacement material not confirmed"
    ],
    "model": [
      "an electrician",
      "an engineer"
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
        "value": "three hours"
      }
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "dates": {
    "ground_truth": "today shift",
    "model": [
      "today's shift"
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

### voice_045.wav

```json
{
  "assets": {
    "ground_truth": "Raw mill conveyor",
    "model": [
      "raw mill conveyor"
    ],
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "6 M20 bolts",
      "2 fitters",
      "1 helper",
      "exact time not confirmed yet"
    ],
    "model": [
      "Six M20 balls",
      "two fitters",
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
      "three hours"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Thursday morning (exact time later confirm)",
    "model": [
      "Thursday morning"
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

### voice_046.wav

```json
{
  "assets": {
    "ground_truth": "kiln hydraulic system",
    "model": "Keilin hydraulic system",
    "judgment": "INCORRECT"
  },
  "quantities": {
    "ground_truth": [
      "1 seal kit",
      "2 fitters",
      "1 hydraulic technician"
    ],
    "model": [
      "two fitters",
      "one hydraulic technician",
      "one seal kit"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "hours": {
    "ground_truth": [
      {
        "kind": "work_duration",
        "value": "6 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "1.5 hours"
      }
    ],
    "model": [
      {
        "kind": "work_duration",
        "value": "6 hours"
      },
      {
        "kind": "machine_downtime",
        "value": "90 minutes"
      }
    ],
    "judgment": "PARTIAL_MATCH"
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

### voice_047.wav

```json
{
  "assets": {
    "ground_truth": "Boiler feed pump",
    "model": "boiler feed pump",
    "judgment": "EXACT_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 technicians",
      "spare parts not confirmed until site inspection"
    ],
    "model": [
      "Two technicians"
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
        "value": "four hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": null,
    "model": null,
    "judgment": "CORRECT_NULL"
  },
  "approval_intent": {
    "ground_truth": "काम शुरू करने से पहले utilities team की approval जरूरी है। Approval मिलने के बाद ही job शुरू करना है",
    "model": "Approval from the utilities team is necessary before starting the work",
    "judgment": "INCORRECT"
  }
}
```

### voice_048.wav

```json
{
  "assets": {
    "ground_truth": "Cooling tower pump",
    "model": [
      "cooling tower pump",
      "bearing"
    ],
    "judgment": "PARTIAL_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 bearings",
      "1 kg grease",
      "2 fitters",
      "bearing number not confirmed"
    ],
    "model": [
      "two bearings",
      "two fitters",
      "one kilo of grease"
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
        "value": "about three hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Friday afternoon",
    "model": [
      "Friday afternoon"
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

### voice_049.wav

```json
{
  "assets": {
    "ground_truth": "motor of conveyor CV-31",
    "model": "conveyor CV31 motor",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "1 electrician",
      "1 mechanical fitter",
      "motor replacement not to be raised yet"
    ],
    "model": [
      "one electrician",
      "one mechanic fitter"
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
        "value": "two hours"
      }
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "night shift",
    "model": [
      "night shift"
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

### voice_050.wav

```json
{
  "assets": {
    "ground_truth": "Cement mill fan",
    "model": "cement mill fan belt",
    "judgment": "SEMANTIC_MATCH"
  },
  "quantities": {
    "ground_truth": [
      "2 bearings",
      "1 belt",
      "2 fitters"
    ],
    "model": [
      "Two pulleys",
      "One belt",
      "two bearings"
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
      "about three hours"
    ],
    "judgment": "SEMANTIC_MATCH"
  },
  "dates": {
    "ground_truth": "Sunday (exact time maintenance team बताएगी)",
    "model": [
      "Sunday"
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

## Limitations and comparison notes

- The legacy speaker mapping labels jigishbhai_* as Mahesh. Reports display this group as Jigish (legacy mapping: Mahesh); grouping and scoring are unchanged.
- The extraction intervention included the dictionary plus explicit source-only safeguards; Agent 1 used fresh Sarvam transcripts. These results measure observed changes, not an isolated dictionary-only causal effect.
- The dictionary declares that its vocabulary was informed by these 59 recordings. Results do not establish held-out generalization.
- Scoring uses the existing deterministic heuristic comparers, not a new human audio review. HALLUCINATION is an evaluator classification against ground truth.
- No extraction API calls, regeneration, dictionary-based scoring, or changes to evaluation/normalization were made.
