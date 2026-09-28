# Maintenance Voice Model Evaluation

## 1. Evaluation Overview

- Evaluation version: **semantic-v2**
- Pipelines compared against human-verified Ground Truth:
  1. Sarvam STT → Gemini extraction
  2. Direct Gemini audio extraction
- Parameters: assets, quantities, hours, dates, approval_intent

## 2. Dataset Size

- Ground Truth recording count: **50**
- Sarvam + Gemini recording count: **50**
- Direct Gemini recording count: **50**
- Parameters per recording: **5**
- Comparisons per model: **250**
- Total comparisons (both models): **500**

## 3. Evaluation Methodology

Judgments per parameter:

- **EXACT_MATCH** / **SEMANTIC_MATCH** / **CORRECT_NULL** → count as correct
- **PARTIAL_MATCH** → incomplete overlap; **not** counted in accuracy numerator
- **MISSING** / **INCORRECT** / **HALLUCINATION** → not correct

Hours kinds are compared separately when specified (`work_duration`, `inspection_duration`, `machine_downtime`). Same numeric duration with a different kind is PARTIAL_MATCH, not full credit.

Quantity order does not matter. Conflicting numeric values for the same item are INCORRECT (e.g. 1 fitter vs 2 fitters).

## 4. Semantic Normalization Rules

- number words → digits
- equipment IDs: BC-15 / BC15 → bc15
- unit aliases: kg/kilogram, hour/hours, liter/litre
- time forms: 10:00 / 10 AM
- Hindi↔English day names and common asset synonyms
- possessives and punctuation stripped

## 5. Overall Accuracy

| Metric | Sarvam + Gemini | Direct Gemini |
|---|---:|---:|
| Overall accuracy | 162 / 250 = 64.8% | 197 / 250 = 78.8% |
| Exact matches | 44 | 112 |
| Semantic matches | 63 | 30 |
| Correct nulls | 55 | 55 |
| Partial matches | 68 | 49 |
| Missing | 8 | 0 |
| Incorrect | 11 | 4 |
| Hallucinations | 1 | 0 |

## 6. Parameter-wise Accuracy

| Parameter | Sarvam + Gemini | Direct Gemini |
|---|---:|---:|
| Assets | 31 / 50 = 62% | 43 / 50 = 86% |
| Quantities | 16 / 50 = 32% | 23 / 50 = 46% |
| Hours | 30 / 50 = 60% | 36 / 50 = 72% |
| Dates | 40 / 50 = 80% | 49 / 50 = 98% |
| Approval intent | 45 / 50 = 90% | 46 / 50 = 92% |

## Detailed Recording Results

### voice001.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Kiln auxiliary drive | Kiran auxiliary drive | Kiln auxiliary drive |
| quantities | 2 6205 C3 bearings; 0.5 kg grease; 8 M60 bolts; 2 fitters | two 6205 C3 bearings; half a kilo of grease; eight M60 bolts; two fitters | 2 6205 C3 bearings; 0.5 kg grease; 8 M60 bolts; 2 fitters |
| hours | work_duration: 4 hours | work_duration: four hours | 4 hours |
| dates | Saturday (exact time process team बताएगी) | Saturday | Saturday (exact time process team will provide) |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | INCORRECT | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | PARTIAL_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_002.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | सीमेंट मिल नंबर एक के मोटर | motor of cement mill number one | Cement mill number 1 motor |
| quantities | 2 6312 C3 bearings; 0.5 kg grease; 2 fitters | Two fitters; Two 6312 C3 bearings; half a kilo of grease | 2 fitters; 2 6312 C3 bearings; 0.5 kg grease |
| hours | work_duration: 3 hours | work_duration: approximately three hours | work_duration: 3 hours |
| dates | tomorrow morning 10:00 | tomorrow morning at 10 AM | Tomorrow at 10 AM |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | SEMANTIC_MATCH | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | SEMANTIC_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_003.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Belt conveyor BC-15 | belt conveyor BC15 | Belt conveyor BC-15 |
| quantities | 1 mechanical fitter; 1 engineer | a mechanical fitter; an engineer | 1 mechanical fitter; 1 engineer |
| hours | inspection_duration: 2 hours | work_duration: two-hour | work_duration: 2 hours |
| dates | today afternoon | this afternoon | today afternoon |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | MISSING | PARTIAL_MATCH |
| dates | SEMANTIC_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_004.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | cooling water pump number six | cooling a water pump number six | cooling water pump number 6 |
| quantities | 2 fitters; material not confirmed until inspection | two-fitter | two fitters |
| hours | work_duration: 3 hours | work_duration: 3 hours | work_duration: 3 hours |
| dates | Tuesday morning | Tuesday morning | Tuesday morning |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | HALLUCINATION | PARTIAL_MATCH |
| hours | EXACT_MATCH | EXACT_MATCH |
| dates | EXACT_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_005.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | रॉ मिल के फीडर | raw mill's feeder | Raw mill feeder |
| quantities | 1 seal kit; 4 gaskets; 1 mechanical fitter; 1 helper | A mechanical fitter; a helper; A seal kit; four gas kits | 1 mechanical fitter; 1 helper; 1 seal kit; 4 gaskets |
| hours | work_duration: 2 hours; machine_downtime: 1 hour | work_duration: two-hour; machine_downtime: one hour | work_duration: 2 hours; machine_downtime: 1 hour |
| dates | Friday morning 11:00 | Friday at 11 AM | Friday at 11:00 AM |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | EXACT_MATCH |
| hours | PARTIAL_MATCH | EXACT_MATCH |
| dates | SEMANTIC_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_006.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Packing plant की conveyor PC-09 का motor | motor of the conveyor PC9 of the packing plant | Packing plant conveyor BC-9 motor |
| quantities | 1 electrician; 1 fitter; spare not confirmed | Two electricians; one electrician; one fitter | 1 electrician; 1 fitter |
| hours | work_duration: 2 hours | four hours; about two hours | 2 hours |
| dates | tomorrow evening | tomorrow evening | tomorrow evening |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | INCORRECT | INCORRECT |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | PARTIAL_MATCH | EXACT_MATCH |
| dates | EXACT_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_007.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | gearbox of bucket elevator BE-11 | gearbox of bucket elevator BE11 | gearbox of bucket elevator BE 11 |
| quantities | 1 mechanical engineer; 1 fitter | One mechanical engineer; one fitter | 1 mechanical engineer; 1 fitter |
| hours | inspection_duration: 2 hours | work_duration: two hours | work_duration: 2 hours |
| dates | Wednesday at nine in the morning | Wednesday at 9:00 in the morning | Wednesday at 9 in the morning |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | PARTIAL_MATCH | PARTIAL_MATCH |
| dates | SEMANTIC_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_008.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | पैकिंग मशीन नंबर तीन | packing machine number three; pneumatic valve | packing machine number 3; pneumatic valve |
| quantities | 1 technician; valve/material not confirmed | a technician | 1 technician |
| hours | inspection_duration: 1.5 hours | work_duration: about one and a half hours | work_duration: 1.5 hours |
| dates | today shift | today's shift | today's shift |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | PARTIAL_MATCH | PARTIAL_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | PARTIAL_MATCH | PARTIAL_MATCH |
| dates | SEMANTIC_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_009.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Kiln ID fan | kiln ID fan | kiln ID fan |
| quantities | 4 22220 spherical roller bearings; 2 kg grease; 3 fitters | four 22,220 spherical roller bearings; two kilos of grease; three feet | 4 22220 spherical roller bearings; 2 kg grease; 3 fitters |
| hours | work_duration: 6 hours | work_duration: six hours | 6 hours |
| dates | Saturday (exact time process team बताएगी) | Saturday | Saturday (exact time will be provided by process team) |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | EXACT_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | PARTIAL_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_010.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | raw mill feeder | raw mill feeder | raw mill feeder |
| quantities | 1 seal kit; 6 gaskets; 2 fitters; 1 helper | two fitters; one helper; one seal kit; six gaskets | 2 fitters; 1 helper; 1 seal kit; 6 gaskets |
| hours | work_duration: 5 hours; machine_downtime: 2 hours | work_duration: 5 hours; machine_downtime: 2 hours | work_duration: 5 hours; machine_downtime: 2 hours |
| dates | Thursday afternoon | Thursday afternoon | Thursday afternoon |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | EXACT_MATCH | EXACT_MATCH |
| dates | EXACT_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_011.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | क्लिंकर बेल्ट कन्वेयर | clicker belt conveyor | Clicker belt conveyor guard |
| quantities | 1 welder; 1 fitter | A welder; a fitter | 1 welder; 1 fitter |
| hours | work_duration: 3 hours | work_duration: about three hours | 3 hours |
| dates | null | null | null |
| approval_intent | काम शुरू करने से पहले safety permit और process team की approval जरूरी है। Approval मिलने के बाद ही काम शुरू करना है | safety permit and process team approval are necessary | Safety permit and process team approval required before starting work |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | INCORRECT | INCORRECT |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | CORRECT_NULL | CORRECT_NULL |
| approval_intent | PARTIAL_MATCH | PARTIAL_MATCH |

### voice_012.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Crusher area में जो छोटी slurry pump | small slurry pump; bearing | small slurry pump |
| quantities | 1 fitter; tag number not available | a fitter | 1 fitter |
| hours | null | null | null |
| dates | tomorrow morning | tomorrow morning | tomorrow morning |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | INCORRECT | INCORRECT |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | CORRECT_NULL | CORRECT_NULL |
| dates | EXACT_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_013.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | compressor number two | compressor number two; air filter | compressor number 2 |
| quantities | 1 air filter; 1 technician; 1 helper | one technician; one helper; one | 1 technician; 1 helper; 1 air filter |
| hours | work_duration: 4 hours | work_duration: 4 hours | 4 hours |
| dates | Monday at 10 AM | Monday at 10:00 a.m. | Monday at 10 AM |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | PARTIAL_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | EXACT_MATCH |
| hours | EXACT_MATCH | EXACT_MATCH |
| dates | SEMANTIC_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_014.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Cement mill की lubrication line | cement mill's lubrication line | Cement mill lubrication line |
| quantities | 0.5 kg grease; 3 grease nipples; 2 fitters | Three new grease snips; Two fitters; Three grease snips; half a kilo of grease | 3 grease nipples; 2 fitters; 0.5 kg grease |
| hours | work_duration: 1 hour | work_duration: about a one-hour | work_duration: 1 hour |
| dates | today afternoon 3:00 | 3 PM today | Today at 3 PM |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | EXACT_MATCH |
| hours | MISSING | EXACT_MATCH |
| dates | SEMANTIC_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_015.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Packing plant के screw conveyor | screw conveyor of the packing plant; chain | packing plant screw conveyor chain |
| quantities | 1 fitter; chain quantity/specification not confirmed; chain replacement pending inspection | A fitter | 1 fitter |
| hours | inspection_duration: 2 hours | work_duration: two hours | work_duration: 2 hours |
| dates | tomorrow morning | tomorrow morning | tomorrow morning |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | PARTIAL_MATCH | SEMANTIC_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | PARTIAL_MATCH | PARTIAL_MATCH |
| dates | EXACT_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_016.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | motor of conveyor CV-21 | conveyor CV21; motor | motor of conveyor CV-21 |
| quantities | 1 electrician | one electrician | 1 electrician |
| hours | inspection_duration: 2 hours | work_duration: two hours | work_duration: 2 hours |
| dates | current shift | current shift | current shift |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | PARTIAL_MATCH | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | PARTIAL_MATCH | PARTIAL_MATCH |
| dates | EXACT_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_017.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Kiln burner | kiln burner | Kiln burner |
| quantities | 2 technicians; 1 fitter; spare material not confirmed | Two technicians; one fitter | 2 technicians; 1 fitter |
| hours | work_duration: 4 hours | work_duration: four-hour | work_duration: 4 hours |
| dates | Saturday (exact time process team बताएगी) | Saturday | Saturday (exact time will be provided by process team) |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | MISSING | EXACT_MATCH |
| dates | PARTIAL_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_018.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Raw mill hydraulic pump | raw mill hydraulic pump filter | Raw mill hydraulic pump |
| quantities | 2 filters; 1 technician; 1 helper | three filters; two filters; one technician; one helper | 2 filters; 1 technician; 1 helper |
| hours | work_duration: 1.5 hours | work_duration: one and a half hours | work_duration: 1.5 hours |
| dates | Wednesday morning | Wednesday morning | Wednesday morning |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | SEMANTIC_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | EXACT_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | EXACT_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_019.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | clinker cooler fan | Klinkner cooler fan | clinker cooler fan |
| quantities | 2 6318 C3 bearings; 1 kg grease; 8 M20 bolts; 2 fitters | two bearings; 1 kilogram of grease; 8 M20 bolts; two fitters | 2 bearings; 6318 C3; 1 kg of grease; 8 M20 bolts; 2 fitters |
| hours | work_duration: 4 hours | four hours | 4 hours |
| dates | Friday at 2 PM | Friday at 2:00 p.m. | Friday at 2 PM |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | INCORRECT | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | SEMANTIC_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_020.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Bucket elevator नंबर चार | bucket elevator number four | bucket elevator number 4 |
| quantities | 1 mechanical engineer; 1 fitter | a mechanical engineer; a fitter | 1 mechanical engineer; 1 fitter |
| hours | inspection_duration: 2 hours | work_duration: two-hour | work_duration: 2 hours |
| dates | today evening | this evening | today evening |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | MISSING | PARTIAL_MATCH |
| dates | SEMANTIC_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_021.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Cement mill की chute liner | cement mill; cut liner | Cement mill |
| quantities | 12 M16 bolts; 6 liner plates; 4 fitters; 1 helper; exact time not confirmed | Four fitters; one helper; Six liner plates; twelve M16 bolts | 4 fitters; 1 helper; 6 liner plates; 12 M16 bolts |
| hours | work_duration: 8 hours; machine_downtime: 3 hours | work_duration: eight hours; machine_downtime: three hours | work_duration: 8 hours; machine_downtime: 3 hours |
| dates | Sunday (exact time not confirmed) | Sunday | Sunday (exact time not confirmed) |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | PARTIAL_MATCH | SEMANTIC_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | PARTIAL_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_022.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | conveyor number twelve | conveyor number 12 | conveyor number 12 |
| quantities | 1 welder; 2 fitters; material not confirmed until site inspection | One welder; two fitters | one welder; two fitters |
| hours | work_duration: 3 hours | work_duration: three hours | work_duration: 3 hours |
| dates | null | null | null |
| approval_intent | A hot work permit and process team approval are required before starting the job | A hot work permit and process team approval are required before starting the job | hot work permit and process team approval are required before starting the job |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | CORRECT_NULL | CORRECT_NULL |
| approval_intent | EXACT_MATCH | SEMANTIC_MATCH |

### voice_023.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Compressor नंबर चार | compressor number four | Compressor number 4 |
| quantities | 4 liters compressor oil; 1 air filter; 1 technician; 1 helper | One technician; one helper; One air filter; four liters of compressor oil | 1 technician; 1 helper; 1 air filter; 4 liters compressor oil |
| hours | work_duration: 3 hours | work_duration: three hours | work_duration: 3 hours |
| dates | Monday morning 9:30 | Monday at 9:30 AM | Monday at 9:30 AM |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | SEMANTIC_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_024.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Workshop के पास जो बड़ा exhaust fan | large exhaust fan near the workshop; bearing | exhaust fan |
| quantities | 1 electrician; 1 fitter; equipment tag not available; bearing replacement or balancing pending confirmation | an electrician; a fitter | 1 electrician; 1 fitter |
| hours | inspection_duration: 2 hours | work_duration: two hours | work_duration: 2 hours |
| dates | null | null | null |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | PARTIAL_MATCH | SEMANTIC_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | PARTIAL_MATCH | PARTIAL_MATCH |
| dates | CORRECT_NULL | CORRECT_NULL |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_025.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | cooling tower fan | cooling tower fan | cooling tower fan |
| quantities | 1 fitter | One fitter | 1 fitter |
| hours | inspection_duration: 2 hours | work_duration: two hours | work_duration: 2 hours |
| dates | today at 4 PM | today at 4:00 p.m. | today at 4 PM |
| approval_intent | No approval is required for the inspection | null | No approval is required for the inspection |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | PARTIAL_MATCH | PARTIAL_MATCH |
| dates | SEMANTIC_MATCH | EXACT_MATCH |
| approval_intent | MISSING | EXACT_MATCH |

### voice_026.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Raw water pump नंबर दो | row water pump number two | raw water pump number 2 |
| quantities | 8 M12 bolts; 1 coupling; 2 fitters; 1 helper | Two fitters; one helper; One coupling; eight M12 bolts | 2 fitters; 1 helper; 1 coupling; 8 M12 bolts |
| hours | work_duration: 4 hours | work_duration: about four hours | work_duration: 4 hours |
| dates | today night 8:00 | tonight at 8 PM | tonight at 8 PM |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | INCORRECT | SEMANTIC_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | PARTIAL_MATCH | PARTIAL_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_027.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Kiln main drive | kiln main drive; bearing | Kiln main drive |
| quantities | 1 mechanical engineer; 2 fitters; bearing size/quantity not known | One mechanical engineer; two fitters | 1 mechanical engineer; 2 fitters |
| hours | inspection_duration: 3 hours | work_duration: three-hour | work_duration: 3 hours |
| dates | tomorrow morning | tomorrow morning | tomorrow morning |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | PARTIAL_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | MISSING | PARTIAL_MATCH |
| dates | EXACT_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_028.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | compressor number five | compressor number five | compressor number 5 |
| quantities | 1 technician; 1 mechanical engineer; material not confirmed until inspection | one technician; one mechanical engineer | 1 technician; 1 mechanical engineer |
| hours | inspection_duration: 3 hours | work_duration: three-hour | work_duration: 3 hours |
| dates | null | null | null |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | MISSING | PARTIAL_MATCH |
| dates | CORRECT_NULL | CORRECT_NULL |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_029.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Cement mill separator | cement mill separator | cement mill separator |
| quantities | 1 kg grease; 1 belt; 2 pulley bearings; 3 fitters | Three fitters; One belt; two pulley bearings; one kilogram of grease | 3 fitters; 1 belt; 2 pulley bearings; 1 kg grease |
| hours | work_duration: 5 hours; machine_downtime: 2 hours | work_duration: about five hours; machine_downtime: two hours | work_duration: 5 hours; machine_downtime: 2 hours |
| dates | Tuesday morning 8:00 | Tuesday at 8 AM | Tuesday at 8:00 AM |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | SEMANTIC_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_030.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Packing machine number seven | packing machine number seven | packing machine number 7 |
| quantities | 1 electrician; morning/afternoon not confirmed | An electrician | 1 electrician |
| hours | work_duration: 2 hours | work_duration: two hours | work_duration: 2 hours |
| dates | Friday (morning/afternoon not confirmed) (Exact time maintenance supervisor बताएगा) | Friday | Friday (morning or afternoon not confirmed; exact time will be provided by maintenance supervisor) |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | PARTIAL_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_031.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | hydraulic cylinder on the roller press | hydraulic cylinder; roller press | hydraulic cylinder; roller press |
| quantities | 1 mechanical fitter; 1 hydraulic technician; seal kit and oil quantity not known; materials not confirmed until inspection | One mechanical fitter; one hydraulic technician | 1 mechanical fitter; 1 hydraulic technician |
| hours | work_duration: 3 hours | work_duration: 3 hours | work_duration: 3 hours |
| dates | tomorrow morning | tomorrow morning | tomorrow morning |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | PARTIAL_MATCH | PARTIAL_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | EXACT_MATCH | EXACT_MATCH |
| dates | EXACT_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_032.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Conveyor number six | conveyor number six | Conveyor number 6 gearbox |
| quantities | 8 liters gear oil; 1 fitter; 1 helper; filter change not required | One fitter; one helper; Eight liters of gear oil | 1 fitter; 1 helper; 8 liters gear oil |
| hours | work_duration: 2 hours | four hours; about two hours | work_duration: 2 hours |
| dates | Saturday evening | Saturday evening | Saturday evening |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | SEMANTIC_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | PARTIAL_MATCH | EXACT_MATCH |
| dates | EXACT_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_033.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Kiln ID fan | kiln ID fan | Kiln ID fan |
| quantities | 2 6315 C3 bearings; 1 kg grease; 10 M16 bolts; 2 fitters | Two 6315 C3 bearings; one kilo of grease; ten M16 bolts; Two fitters | 2 6315 C3 bearings; 1 kilo grease; 10 M16 bolts; 2 fitters |
| hours | work_duration: 4 hours | work_duration: four hours | work_duration: 4 hours |
| dates | Sunday (exact time process team confirm करेगी) | Sunday | Sunday (Exact time process team will confirm) |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | SEMANTIC_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | PARTIAL_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_034.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | bag filter fan | bag filter fan | bag filter fan |
| quantities | 1 electrician; 1 fitter; no replacement assumed before inspection | one electrician; one fitter | 1 electrician; 1 fitter |
| hours | work_duration: 3 hours | work_duration: 3 hours | 3 hours |
| dates | Thursday at 11 AM | Thursday at 11:00 a.m. | Thursday at 11 AM |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | EXACT_MATCH | EXACT_MATCH |
| dates | SEMANTIC_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_035.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Raw mill fan | raw mill fan | raw mill fan |
| quantities | 6 bolts; 1 coupling; 2 fitters; 1 helper | Two fitters; one helper; One coupling; six bolts | 2 fitters; 1 helper; 1 coupling; 6 bolts |
| hours | work_duration: 4 hours; machine_downtime: 2 hours | work_duration: four hours; machine_downtime: two hours | work_duration: 4 hours; machine_downtime: 2 hours |
| dates | Friday afternoon 1:00 | Friday at 1 PM | Friday at 1 PM |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | SEMANTIC_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_036.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Conveyor BC-20 | conveyor BC20 belt | conveyor BC 20 |
| quantities | 1 splice kit; 3 fitters; 1 supervisor | Three fitters; a supervisor; An splice kit | 3 fitters; 1 supervisor; 1 splice kit |
| hours | work_duration: 6 hours | work_duration: about six hours | work_duration: 6 hours |
| dates | null | null | null |
| approval_intent | काम शुरू करने से पहले process team की approval और safety permit दोनों चाहिए। Approval के बिना काम शुरू नहीं करना है | both process team approval and safety permit are required | Approval from process team and safety permit required before starting work |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | SEMANTIC_MATCH | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | CORRECT_NULL | CORRECT_NULL |
| approval_intent | PARTIAL_MATCH | PARTIAL_MATCH |

### voice_037.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | small pump near the clinker cooler | small pump near the clinker cooler | small pump near the clinker cooler |
| quantities | 1 fitter; equipment tag not available; do not order bearings until inspection confirms cause | one fitter | 1 fitter |
| hours | null | null | null |
| dates | tomorrow morning | tomorrow morning | tomorrow morning |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | CORRECT_NULL | CORRECT_NULL |
| dates | EXACT_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_038.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Compressor नंबर एक | air filter of compressor number one | Compressor number 1 |
| quantities | 5 liters compressor oil; 1 air filter; 1 technician; 1 helper | a technician; a helper; a filter; five liters of compressor oil | 1 technician; 1 helper; 1 filter; 5 liter compressor oil |
| hours | work_duration: 2 hours | about two hours | work_duration: 2 hours |
| dates | Monday morning 10:00 | Monday morning at 10 AM | Monday at 10 AM |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | SEMANTIC_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | SEMANTIC_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_039.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Packing conveyor PC-14 | packing conveyor PC14 motor | packing conveyor PC 14 motor |
| quantities | 1 electrician; 1 mechanical fitter; spare material not confirmed | Two electricians; one electrician; one mechanical fitter | 1 electrician; 1 mechanical fitter |
| hours | work_duration: 1.5 hours | work_duration: three hours; work_duration: about one and a half hours | work_duration: 1.5 hours |
| dates | today second shift | today's second shift | today second shift |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | SEMANTIC_MATCH | SEMANTIC_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | PARTIAL_MATCH | EXACT_MATCH |
| dates | SEMANTIC_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_040.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | damaged handrail near the kiln platform | damaged handrail near the clean platform | handrail near the kiln platform |
| quantities | 1 welder; 1 fitter; steel material quantity not confirmed until site measurement | One welder; one fitter | 1 welder; 1 fitter |
| hours | work_duration: 4 hours | work_duration: 4 hours | work_duration: 4 hours |
| dates | null | null | null |
| approval_intent | A work-at-height permit is required before starting | null | Work at height permit is required before starting |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | INCORRECT | SEMANTIC_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | EXACT_MATCH | EXACT_MATCH |
| dates | CORRECT_NULL | CORRECT_NULL |
| approval_intent | MISSING | PARTIAL_MATCH |

### voice_041.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Bucket elevator BE-09 के head pulley | head pulley of bucket elevator B9; bearings 22218 | bucket elevator BE-09; head pulley |
| quantities | 2 22218 bearings; 4 kg grease; 12 M20 bolts; 3 fitters | Two bearings; 4 kg of grease; 12 M20 bolts; Three fitters | 2 bearings (22218); 4 kg grease; 12 M20 bolts; 3 fitters |
| hours | work_duration: 5 hours | work_duration: five hours | work_duration: 5 hours |
| dates | Wednesday morning 7:00 | 7 AM on Wednesday | Wednesday morning at 7:00 AM |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | INCORRECT | PARTIAL_MATCH |
| quantities | PARTIAL_MATCH | SEMANTIC_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | SEMANTIC_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_042.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Crusher number two | crosser number two; gearbox | Crusher number 2; gearbox |
| quantities | 1 mechanical engineer; 1 fitter; material not confirmed until leakage source found; gearbox replacement not to be done yet | a mechanical engineer; a fitter | 1 mechanical engineer; 1 fitter |
| hours | inspection_duration: 2 hours | work_duration: two hours | work_duration: 2 hours |
| dates | null | null | null |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | INCORRECT | PARTIAL_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | PARTIAL_MATCH | PARTIAL_MATCH |
| dates | CORRECT_NULL | CORRECT_NULL |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_043.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | cement mill lubrication system | cement mill lubrication system | cement mill lubrication system |
| quantities | 2 fitters; spare parts not known yet | two fitters | two fitters |
| hours | inspection_duration: 2 hours | work_duration: two hours | work_duration: 2 hours |
| dates | Saturday (exact time will be provided by the process team) | Saturday | Saturday, exact time will be provided by the process team |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | PARTIAL_MATCH | PARTIAL_MATCH |
| dates | PARTIAL_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_044.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Packing plant की motor starter panel | motor starter panel in the packing plant | Packing plant motor starter panel |
| quantities | 1 electrician; 1 engineer; replacement material not confirmed | an electrician; an engineer | 1 electrician; 1 engineer |
| hours | inspection_duration: 3 hours | work_duration: three hours | work_duration: 3 hours |
| dates | today shift | today's shift | today's shift |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | SEMANTIC_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | PARTIAL_MATCH | PARTIAL_MATCH |
| dates | SEMANTIC_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_045.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Raw mill conveyor | raw mill conveyor | raw mill conveyor |
| quantities | 6 M20 bolts; 2 fitters; 1 helper; exact time not confirmed yet | Four M20 balls; Six M20 balls; two fitters; one helper | 6 M20 bolts; 2 fitters; 1 helper |
| hours | work_duration: 3 hours | work_duration: three hours | work_duration: 3 hours |
| dates | Thursday morning (exact time later confirm) | Thursday morning | Thursday morning, exact time will be confirmed later |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | PARTIAL_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_046.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | kiln hydraulic system | Keilin hydraulic system; Keilin | kiln hydraulic system |
| quantities | 1 seal kit; 2 fitters; 1 hydraulic technician | two fitters; one hydraulic technician; one seal kit | 2 fitters; 1 hydraulic technician; 1 seal kit |
| hours | work_duration: 6 hours; machine_downtime: 1.5 hours | work_duration: 6 hours; machine_downtime: 90 minutes | work_duration: 6 hours; machine_downtime: 90 minutes |
| dates | null | null | null |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | INCORRECT | EXACT_MATCH |
| quantities | SEMANTIC_MATCH | EXACT_MATCH |
| hours | PARTIAL_MATCH | PARTIAL_MATCH |
| dates | CORRECT_NULL | CORRECT_NULL |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_047.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Boiler feed pump | boiler feed pump | Boiler feed pump |
| quantities | 2 technicians; spare parts not confirmed until site inspection | Two technicians | 2 technicians |
| hours | work_duration: 4 hours | work_duration: four hours | work_duration: 4 hours |
| dates | null | null | null |
| approval_intent | काम शुरू करने से पहले utilities team की approval जरूरी है। Approval मिलने के बाद ही job शुरू करना है | Approval from the utilities team is necessary before starting the work | Approval required from utilities team before starting work |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | CORRECT_NULL | CORRECT_NULL |
| approval_intent | INCORRECT | INCORRECT |

### voice_048.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Cooling tower pump | cooling tower pump; bearings | Cooling tower pump |
| quantities | 2 bearings; 1 kg grease; 2 fitters; bearing number not confirmed | two bearings; two fitters; one kilo of grease | 2 bearings; 2 fitters; 1 kg grease |
| hours | work_duration: 3 hours | work_duration: about three hours | work_duration: 3 hours |
| dates | Friday afternoon | Friday afternoon | Friday afternoon |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | PARTIAL_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | EXACT_MATCH | EXACT_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_049.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | motor of conveyor CV-31 | motor of conveyor CV31 | motor of conveyor CV31 |
| quantities | 1 electrician; 1 mechanical fitter; motor replacement not to be raised yet | one electrician; one mechanic fitter | 1 electrician; 1 mechanic fitter |
| hours | work_duration: 2 hours | work_duration: two hours | work_duration: 2 hours |
| dates | night shift | night shift | during the night shift |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | EXACT_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | PARTIAL_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | EXACT_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

### voice_050.wav

| Parameter | Ground Truth | Sarvam + Gemini | Direct Gemini |
|---|---|---|---|
| assets | Cement mill fan | cement mill fan belt | Cement mill fan |
| quantities | 2 bearings; 1 belt; 2 fitters | Two pulleys; One belt; two bearings | 2 fitters; 1 belt; 2 bearings |
| hours | work_duration: 3 hours | work_duration: about three hours | 3 hours |
| dates | Sunday (exact time maintenance team बताएगी) | Sunday | Sunday (exact time maintenance team will tell) |
| approval_intent | null | null | null |

| Parameter | Sarvam judgment | Direct Gemini judgment |
|---|---|---|
| assets | SEMANTIC_MATCH | EXACT_MATCH |
| quantities | PARTIAL_MATCH | EXACT_MATCH |
| hours | SEMANTIC_MATCH | EXACT_MATCH |
| dates | PARTIAL_MATCH | SEMANTIC_MATCH |
| approval_intent | CORRECT_NULL | CORRECT_NULL |

## 7. Error Analysis

### Assets

- `voice001.wav` / Sarvam + Gemini: **INCORRECT** — Ground Truth `Kiln auxiliary drive` vs model `Kiran auxiliary drive`.
- `voice_006.wav` / Sarvam + Gemini: **INCORRECT** — Ground Truth `Packing plant की conveyor PC-09 का motor` vs model `motor of the conveyor PC9 of the packing plant`.
- `voice_006.wav` / Direct Gemini: **INCORRECT** — Ground Truth `Packing plant की conveyor PC-09 का motor` vs model `Packing plant conveyor BC-9 motor`.
- `voice_008.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `पैकिंग मशीन नंबर तीन` vs model `packing machine number three; pneumatic valve`.
- `voice_008.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `पैकिंग मशीन नंबर तीन` vs model `packing machine number 3; pneumatic valve`.
- `voice_011.wav` / Sarvam + Gemini: **INCORRECT** — Ground Truth `क्लिंकर बेल्ट कन्वेयर` vs model `clicker belt conveyor`.
- `voice_011.wav` / Direct Gemini: **INCORRECT** — Ground Truth `क्लिंकर बेल्ट कन्वेयर` vs model `Clicker belt conveyor guard`.
- `voice_012.wav` / Sarvam + Gemini: **INCORRECT** — Ground Truth `Crusher area में जो छोटी slurry pump` vs model `small slurry pump; bearing`.
- `voice_012.wav` / Direct Gemini: **INCORRECT** — Ground Truth `Crusher area में जो छोटी slurry pump` vs model `small slurry pump`.
- `voice_013.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `compressor number two` vs model `compressor number two; air filter`.
- `voice_015.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Packing plant के screw conveyor` vs model `screw conveyor of the packing plant; chain`.
- `voice_016.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `motor of conveyor CV-21` vs model `conveyor CV21; motor`.
- `voice_019.wav` / Sarvam + Gemini: **INCORRECT** — Ground Truth `clinker cooler fan` vs model `Klinkner cooler fan`.
- `voice_021.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Cement mill की chute liner` vs model `cement mill; cut liner`.
- `voice_024.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Workshop के पास जो बड़ा exhaust fan` vs model `large exhaust fan near the workshop; bearing`.
- `voice_026.wav` / Sarvam + Gemini: **INCORRECT** — Ground Truth `Raw water pump नंबर दो` vs model `row water pump number two`.
- `voice_027.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Kiln main drive` vs model `kiln main drive; bearing`.
- `voice_031.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `hydraulic cylinder on the roller press` vs model `hydraulic cylinder; roller press`.
- `voice_031.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `hydraulic cylinder on the roller press` vs model `hydraulic cylinder; roller press`.
- `voice_040.wav` / Sarvam + Gemini: **INCORRECT** — Ground Truth `damaged handrail near the kiln platform` vs model `damaged handrail near the clean platform`.
- `voice_041.wav` / Sarvam + Gemini: **INCORRECT** — Ground Truth `Bucket elevator BE-09 के head pulley` vs model `head pulley of bucket elevator B9; bearings 22218`.
- `voice_041.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `Bucket elevator BE-09 के head pulley` vs model `bucket elevator BE-09; head pulley`.
- `voice_042.wav` / Sarvam + Gemini: **INCORRECT** — Ground Truth `Crusher number two` vs model `crosser number two; gearbox`.
- `voice_042.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `Crusher number two` vs model `Crusher number 2; gearbox`.
- `voice_046.wav` / Sarvam + Gemini: **INCORRECT** — Ground Truth `kiln hydraulic system` vs model `Keilin hydraulic system; Keilin`.
- `voice_048.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Cooling tower pump` vs model `cooling tower pump; bearings`.

### Quantities

- `voice_004.wav` / Sarvam + Gemini: **HALLUCINATION** — Ground Truth `2 fitters; material not confirmed until inspection` vs model `two-fitter`.
- `voice_004.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `2 fitters; material not confirmed until inspection` vs model `two fitters`.
- `voice_005.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 seal kit; 4 gaskets; 1 mechanical fitter; 1 helper` vs model `A mechanical fitter; a helper; A seal kit; four gas kits`.
- `voice_006.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 electrician; 1 fitter; spare not confirmed` vs model `Two electricians; one electrician; one fitter`.
- `voice_006.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `1 electrician; 1 fitter; spare not confirmed` vs model `1 electrician; 1 fitter`.
- `voice_008.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 technician; valve/material not confirmed` vs model `a technician`.
- `voice_008.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `1 technician; valve/material not confirmed` vs model `1 technician`.
- `voice_009.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `4 22220 spherical roller bearings; 2 kg grease; 3 fitters` vs model `four 22,220 spherical roller bearings; two kilos of grease; three feet`.
- `voice_012.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 fitter; tag number not available` vs model `a fitter`.
- `voice_012.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `1 fitter; tag number not available` vs model `1 fitter`.
- `voice_013.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 air filter; 1 technician; 1 helper` vs model `one technician; one helper; one`.
- `voice_014.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `0.5 kg grease; 3 grease nipples; 2 fitters` vs model `Three new grease snips; Two fitters; Three grease snips; half a kilo of grease`.
- `voice_015.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 fitter; chain quantity/specification not confirmed; chain replacement pending inspection` vs model `A fitter`.
- `voice_015.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `1 fitter; chain quantity/specification not confirmed; chain replacement pending inspection` vs model `1 fitter`.
- `voice_017.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `2 technicians; 1 fitter; spare material not confirmed` vs model `Two technicians; one fitter`.
- `voice_017.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `2 technicians; 1 fitter; spare material not confirmed` vs model `2 technicians; 1 fitter`.
- `voice_018.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `2 filters; 1 technician; 1 helper` vs model `three filters; two filters; one technician; one helper`.
- `voice_019.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `2 6318 C3 bearings; 1 kg grease; 8 M20 bolts; 2 fitters` vs model `two bearings; 1 kilogram of grease; 8 M20 bolts; two fitters`.
- `voice_019.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `2 6318 C3 bearings; 1 kg grease; 8 M20 bolts; 2 fitters` vs model `2 bearings; 6318 C3; 1 kg of grease; 8 M20 bolts; 2 fitters`.
- `voice_021.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `12 M16 bolts; 6 liner plates; 4 fitters; 1 helper; exact time not confirmed` vs model `Four fitters; one helper; Six liner plates; twelve M16 bolts`.
- `voice_021.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `12 M16 bolts; 6 liner plates; 4 fitters; 1 helper; exact time not confirmed` vs model `4 fitters; 1 helper; 6 liner plates; 12 M16 bolts`.
- `voice_022.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 welder; 2 fitters; material not confirmed until site inspection` vs model `One welder; two fitters`.
- `voice_022.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `1 welder; 2 fitters; material not confirmed until site inspection` vs model `one welder; two fitters`.
- `voice_024.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 electrician; 1 fitter; equipment tag not available; bearing replacement or balancing pending confirmation` vs model `an electrician; a fitter`.
- `voice_024.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `1 electrician; 1 fitter; equipment tag not available; bearing replacement or balancing pending confirmation` vs model `1 electrician; 1 fitter`.
- `voice_027.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 mechanical engineer; 2 fitters; bearing size/quantity not known` vs model `One mechanical engineer; two fitters`.
- `voice_027.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `1 mechanical engineer; 2 fitters; bearing size/quantity not known` vs model `1 mechanical engineer; 2 fitters`.
- `voice_028.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 technician; 1 mechanical engineer; material not confirmed until inspection` vs model `one technician; one mechanical engineer`.
- `voice_028.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `1 technician; 1 mechanical engineer; material not confirmed until inspection` vs model `1 technician; 1 mechanical engineer`.
- `voice_030.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 electrician; morning/afternoon not confirmed` vs model `An electrician`.
- `voice_030.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `1 electrician; morning/afternoon not confirmed` vs model `1 electrician`.
- `voice_031.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 mechanical fitter; 1 hydraulic technician; seal kit and oil quantity not known; materials not confirmed until inspection` vs model `One mechanical fitter; one hydraulic technician`.
- `voice_031.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `1 mechanical fitter; 1 hydraulic technician; seal kit and oil quantity not known; materials not confirmed until inspection` vs model `1 mechanical fitter; 1 hydraulic technician`.
- `voice_032.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `8 liters gear oil; 1 fitter; 1 helper; filter change not required` vs model `One fitter; one helper; Eight liters of gear oil`.
- `voice_032.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `8 liters gear oil; 1 fitter; 1 helper; filter change not required` vs model `1 fitter; 1 helper; 8 liters gear oil`.
- `voice_034.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 electrician; 1 fitter; no replacement assumed before inspection` vs model `one electrician; one fitter`.
- `voice_034.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `1 electrician; 1 fitter; no replacement assumed before inspection` vs model `1 electrician; 1 fitter`.
- `voice_037.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `1 fitter; equipment tag not available; do not order bearings until inspection confirms cause` vs model `one fitter`.
- `voice_037.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `1 fitter; equipment tag not available; do not order bearings until inspection confirms cause` vs model `1 fitter`.
- `voice_038.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `5 liters compressor oil; 1 air filter; 1 technician; 1 helper` vs model `a technician; a helper; a filter; five liters of compressor oil`.
- … and 21 more.

### Hours

- `voice_003.wav` / Sarvam + Gemini: **MISSING** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: two-hour`.
- `voice_003.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: 2 hours`.
- `voice_005.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `work_duration: 2 hours; machine_downtime: 1 hour` vs model `work_duration: two-hour; machine_downtime: one hour`.
- `voice_006.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `work_duration: 2 hours` vs model `four hours; about two hours`.
- `voice_007.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: two hours`.
- `voice_007.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: 2 hours`.
- `voice_008.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 1.5 hours` vs model `work_duration: about one and a half hours`.
- `voice_008.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 1.5 hours` vs model `work_duration: 1.5 hours`.
- `voice_014.wav` / Sarvam + Gemini: **MISSING** — Ground Truth `work_duration: 1 hour` vs model `work_duration: about a one-hour`.
- `voice_015.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: two hours`.
- `voice_015.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: 2 hours`.
- `voice_016.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: two hours`.
- `voice_016.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: 2 hours`.
- `voice_017.wav` / Sarvam + Gemini: **MISSING** — Ground Truth `work_duration: 4 hours` vs model `work_duration: four-hour`.
- `voice_020.wav` / Sarvam + Gemini: **MISSING** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: two-hour`.
- `voice_020.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: 2 hours`.
- `voice_024.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: two hours`.
- `voice_024.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: 2 hours`.
- `voice_025.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: two hours`.
- `voice_025.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: 2 hours`.
- `voice_027.wav` / Sarvam + Gemini: **MISSING** — Ground Truth `inspection_duration: 3 hours` vs model `work_duration: three-hour`.
- `voice_027.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 3 hours` vs model `work_duration: 3 hours`.
- `voice_028.wav` / Sarvam + Gemini: **MISSING** — Ground Truth `inspection_duration: 3 hours` vs model `work_duration: three-hour`.
- `voice_028.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 3 hours` vs model `work_duration: 3 hours`.
- `voice_032.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `work_duration: 2 hours` vs model `four hours; about two hours`.
- `voice_039.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `work_duration: 1.5 hours` vs model `work_duration: three hours; work_duration: about one and a half hours`.
- `voice_042.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: two hours`.
- `voice_042.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: 2 hours`.
- `voice_043.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: two hours`.
- `voice_043.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 2 hours` vs model `work_duration: 2 hours`.
- `voice_044.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 3 hours` vs model `work_duration: three hours`.
- `voice_044.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `inspection_duration: 3 hours` vs model `work_duration: 3 hours`.
- `voice_046.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `work_duration: 6 hours; machine_downtime: 1.5 hours` vs model `work_duration: 6 hours; machine_downtime: 90 minutes`.
- `voice_046.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `work_duration: 6 hours; machine_downtime: 1.5 hours` vs model `work_duration: 6 hours; machine_downtime: 90 minutes`.

### Dates

- `voice001.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Saturday (exact time process team बताएगी)` vs model `Saturday`.
- `voice_009.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Saturday (exact time process team बताएगी)` vs model `Saturday`.
- `voice_017.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Saturday (exact time process team बताएगी)` vs model `Saturday`.
- `voice_021.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Sunday (exact time not confirmed)` vs model `Sunday`.
- `voice_026.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `today night 8:00` vs model `tonight at 8 PM`.
- `voice_026.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `today night 8:00` vs model `tonight at 8 PM`.
- `voice_030.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Friday (morning/afternoon not confirmed) (Exact time maintenance supervisor बताएगा)` vs model `Friday`.
- `voice_033.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Sunday (exact time process team confirm करेगी)` vs model `Sunday`.
- `voice_043.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Saturday (exact time will be provided by the process team)` vs model `Saturday`.
- `voice_045.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Thursday morning (exact time later confirm)` vs model `Thursday morning`.
- `voice_050.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `Sunday (exact time maintenance team बताएगी)` vs model `Sunday`.

### Approval intent

- `voice_011.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `काम शुरू करने से पहले safety permit और process team की approval जरूरी है। Approval मिलने के बाद ही काम शुरू करना है` vs model `safety permit and process team approval are necessary`.
- `voice_011.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `काम शुरू करने से पहले safety permit और process team की approval जरूरी है। Approval मिलने के बाद ही काम शुरू करना है` vs model `Safety permit and process team approval required before starting work`.
- `voice_025.wav` / Sarvam + Gemini: **MISSING** — Ground Truth `No approval is required for the inspection` vs model `null`.
- `voice_036.wav` / Sarvam + Gemini: **PARTIAL_MATCH** — Ground Truth `काम शुरू करने से पहले process team की approval और safety permit दोनों चाहिए। Approval के बिना काम शुरू नहीं करना है` vs model `both process team approval and safety permit are required`.
- `voice_036.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `काम शुरू करने से पहले process team की approval और safety permit दोनों चाहिए। Approval के बिना काम शुरू नहीं करना है` vs model `Approval from process team and safety permit required before starting work`.
- `voice_040.wav` / Sarvam + Gemini: **MISSING** — Ground Truth `A work-at-height permit is required before starting` vs model `null`.
- `voice_040.wav` / Direct Gemini: **PARTIAL_MATCH** — Ground Truth `A work-at-height permit is required before starting` vs model `Work at height permit is required before starting`.
- `voice_047.wav` / Sarvam + Gemini: **INCORRECT** — Ground Truth `काम शुरू करने से पहले utilities team की approval जरूरी है। Approval मिलने के बाद ही job शुरू करना है` vs model `Approval from the utilities team is necessary before starting the work`.
- `voice_047.wav` / Direct Gemini: **INCORRECT** — Ground Truth `काम शुरू करने से पहले utilities team की approval जरूरी है। Approval मिलने के बाद ही job शुरू करना है` vs model `Approval required from utilities team before starting work`.

## 8. Representative Examples

- Semantic match (`voice001.wav` / Sarvam + Gemini / quantities): GT `2 6205 C3 bearings; 0.5 kg grease; 8 M60 bolts; 2 fitters` ≈ model `two 6205 C3 bearings; half a kilo of grease; eight M60 bolts; two fitters`.
- Semantic match (`voice001.wav` / Sarvam + Gemini / hours): GT `work_duration: 4 hours` ≈ model `work_duration: four hours`.
- Semantic match (`voice001.wav` / Direct Gemini / dates): GT `Saturday (exact time process team बताएगी)` ≈ model `Saturday (exact time process team will provide)`.
- Semantic match (`voice_002.wav` / Sarvam + Gemini / assets): GT `सीमेंट मिल नंबर एक के मोटर` ≈ model `motor of cement mill number one`.
- Semantic match (`voice_002.wav` / Sarvam + Gemini / quantities): GT `2 6312 C3 bearings; 0.5 kg grease; 2 fitters` ≈ model `Two fitters; Two 6312 C3 bearings; half a kilo of grease`.
- Semantic match (`voice_002.wav` / Sarvam + Gemini / hours): GT `work_duration: 3 hours` ≈ model `work_duration: approximately three hours`.
- Semantic match (`voice_002.wav` / Sarvam + Gemini / dates): GT `tomorrow morning 10:00` ≈ model `tomorrow morning at 10 AM`.
- Semantic match (`voice_002.wav` / Direct Gemini / dates): GT `tomorrow morning 10:00` ≈ model `Tomorrow at 10 AM`.

- Partial (`voice001.wav` / Sarvam + Gemini / dates): GT `Saturday (exact time process team बताएगी)` vs model `Saturday`.
- Partial (`voice_003.wav` / Direct Gemini / hours): GT `inspection_duration: 2 hours` vs model `work_duration: 2 hours`.
- Partial (`voice_004.wav` / Direct Gemini / quantities): GT `2 fitters; material not confirmed until inspection` vs model `two fitters`.
- Partial (`voice_005.wav` / Sarvam + Gemini / quantities): GT `1 seal kit; 4 gaskets; 1 mechanical fitter; 1 helper` vs model `A mechanical fitter; a helper; A seal kit; four gas kits`.
- Partial (`voice_005.wav` / Sarvam + Gemini / hours): GT `work_duration: 2 hours; machine_downtime: 1 hour` vs model `work_duration: two-hour; machine_downtime: one hour`.
- Partial (`voice_006.wav` / Sarvam + Gemini / quantities): GT `1 electrician; 1 fitter; spare not confirmed` vs model `Two electricians; one electrician; one fitter`.

## 9. STT vs Extraction Error Attribution

Transcripts are not stored in Agent 1 outputs, so attribution is heuristic:

- **likely_stt_error**: Sarvam+Gemini incorrect on a parameter while Direct Gemini is correct (Direct recovered the fact from audio; Sarvam path likely lost it in STT or STT→extract).
- **direct_extraction_error**: Direct Gemini incorrect while Sarvam+Gemini is correct.
- **both_pipelines_error**: both pipelines incorrect on the same parameter.

| Attribution | Count |
|---|---:|
| likely_stt_error | 35 |
| direct_extraction_error | 0 |
| both_pipelines_error | 53 |
| both_correct | 162 |

## 10. Dataset Limitations

This evaluation measures only the supplied recordings against the human-verified Ground Truth. Partial matches are visible in counts but excluded from accuracy numerators. Error attribution is heuristic because Sarvam transcripts are not persisted in `outputs/sarvam_gemini/sarvam_gemini_final.json`.

## 11. Final Factual Comparison

On this dataset, Direct Gemini achieved 78.8% (197/250) compared with 64.8% (162/250) for Sarvam + Gemini.

These results are limited to the supplied recordings and should not be read as a universal claim that either pipeline is better in general.
