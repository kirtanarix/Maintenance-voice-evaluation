# Speaker/Dialect Evaluation

## 1. Objective

This evaluation tests whether model performance varies across individual speakers on a fixed set of maintenance voice recordings. It is separate from the full-dataset Agent 4 evaluation and does not replace it.

## 2. Dataset

- 3 recordings from Sanjay
- 3 recordings from Mahesh
- 3 recordings from Julfikar
- 9 recordings total
- 5 parameters per recording (assets, quantities, hours, dates, approval_intent)
- 45 field comparisons per pipeline

Speaker identity is taken from `inputs/speaker_mapping.json`. Speaker labels follow inputs/speaker_mapping.json. The Mahesh group uses jigishbhai_* filenames as listed in that mapping; identity is not inferred from transcript text.

Evaluated filenames:

- **Sanjay**: `sanjaybhai_voice_051.wav`, `sanjaybhai_voice_052.wav`, `sanjaybhai_voice_053.wav`
- **Mahesh**: `jigishbhai_voice_057.wav`, `jigishbhai_voice_058.wav`, `jigishbhai_voice_059.wav`
- **Julfikar**: `julfikar_voice_054.wav`, `julfikar_voice_055.wav`, `julfikar_voice_056.wav`

## 3. Speaker-wise Results

| Speaker | Pipeline | Assets | Quantities | Hours | Dates | Approval | Overall |
|---------|----------|--------|------------|-------|-------|----------|---------|
| Sanjay | Sarvam + Gemini | 2/3 (66.67%) | 0/3 (0%) | 3/3 (100%) | 3/3 (100%) | 3/3 (100%) | 11/15 (73.33%) |
| Sanjay | Direct Gemini | 3/3 (100%) | 1/3 (33.33%) | 3/3 (100%) | 3/3 (100%) | 2/3 (66.67%) | 12/15 (80%) |
| Mahesh | Sarvam + Gemini | 2/3 (66.67%) | 0/3 (0%) | 2/3 (66.67%) | 2/3 (66.67%) | 3/3 (100%) | 9/15 (60%) |
| Mahesh | Direct Gemini | 2/3 (66.67%) | 1/3 (33.33%) | 2/3 (66.67%) | 3/3 (100%) | 3/3 (100%) | 11/15 (73.33%) |
| Julfikar | Sarvam + Gemini | 1/3 (33.33%) | 1/3 (33.33%) | 1/3 (33.33%) | 3/3 (100%) | 3/3 (100%) | 9/15 (60%) |
| Julfikar | Direct Gemini | 1/3 (33.33%) | 2/3 (66.67%) | 3/3 (100%) | 3/3 (100%) | 3/3 (100%) | 12/15 (80%) |

## 4. Pipeline Comparison

Nine-recording aggregate (this speaker evaluation only):

- Sarvam + Gemini: **29 / 45 = 64.44%**
- Direct Gemini: **35 / 45 = 77.78%**

On this 9-recording speaker evaluation, Direct Gemini achieved 77.78% (35/45) compared with 64.44% (29/45) for Sarvam + Gemini.

These figures apply only to this 9-recording subset and do not replace the existing full-dataset Agent 4 results.

## 5. Speaker/Dialect Comparison

- **Sanjay**: Sarvam + Gemini 73.33%; Direct Gemini 80.0%.
- **Mahesh**: Sarvam + Gemini 60.0%; Direct Gemini 73.33%.
- **Julfikar**: Sarvam + Gemini 60.0%; Direct Gemini 80.0%.

Performance varied across the three speakers.

- Sarvam + Gemini speaker range: 60.0% to 73.33% (spread 13.33 percentage points).
- Direct Gemini speaker range: 73.33% to 80.0% (spread 6.67 percentage points).

No dialect label is assigned beyond the named speakers in the mapping file.

## 6. Parameter-wise Comparison

| Parameter | Sarvam + Gemini | Direct Gemini |
|---|---:|---:|
| Assets | 5/9 (55.56%) | 6/9 (66.67%) |
| Quantities | 1/9 (11.11%) | 4/9 (44.44%) |
| Hours | 6/9 (66.67%) | 8/9 (88.89%) |
| Dates | 8/9 (88.89%) | 9/9 (100%) |
| Approval | 9/9 (100%) | 8/9 (88.89%) |

## 7. Detailed Errors

26 non-correct field comparisons (PARTIAL_MATCH, MISSING, INCORRECT, HALLUCINATION, etc.):

### Error 1

- Speaker: **Sanjay**
- Audio: `sanjaybhai_voice_051.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `quantities`
- Ground Truth: `2 kg grease; 1 seal kit; 2 fitters; 1 helper`
- Model output: `Two filters; a helper; One seal kit; two kilos of grease`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 2

- Speaker: **Sanjay**
- Audio: `sanjaybhai_voice_051.wav`
- Pipeline: Direct Gemini
- Parameter: `approval_intent`
- Ground Truth: `Process team से shutdown confirmation लेना है`
- Model output: `null`
- Classification: **MISSING**
- Explanation: Ground Truth contains a spoken fact that the model omitted.

### Error 3

- Speaker: **Sanjay**
- Audio: `sanjaybhai_voice_052.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `quantities`
- Ground Truth: `1 technician; 1 helper; mechanical seal replacement pending inspection confirmation`
- Model output: `one technician; one helper`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 4

- Speaker: **Sanjay**
- Audio: `sanjaybhai_voice_052.wav`
- Pipeline: Direct Gemini
- Parameter: `quantities`
- Ground Truth: `1 technician; 1 helper; mechanical seal replacement pending inspection confirmation`
- Model output: `1 technician; 1 helper; mechanical seal`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 5

- Speaker: **Sanjay**
- Audio: `sanjaybhai_voice_053.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `assets`
- Ground Truth: `Crusher की discharge chute`
- Model output: `discharge tube of the cluster`
- Classification: **INCORRECT**
- Explanation: Model value differs from Ground Truth (GT=Crusher की discharge chute; model=discharge tube of the cluster).

### Error 6

- Speaker: **Sanjay**
- Audio: `sanjaybhai_voice_053.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `quantities`
- Ground Truth: `1 welder; 1 fitter; plate material not confirmed`
- Model output: `a welder; a filter`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 7

- Speaker: **Sanjay**
- Audio: `sanjaybhai_voice_053.wav`
- Pipeline: Direct Gemini
- Parameter: `quantities`
- Ground Truth: `1 welder; 1 fitter; plate material not confirmed`
- Model output: `1 welder; 1 fitter`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 8

- Speaker: **Mahesh**
- Audio: `jigishbhai_voice_057.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `quantities`
- Ground Truth: `2 fitters; material not required currently`
- Model output: `Two fitters`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 9

- Speaker: **Mahesh**
- Audio: `jigishbhai_voice_057.wav`
- Pipeline: Direct Gemini
- Parameter: `quantities`
- Ground Truth: `2 fitters; material not required currently`
- Model output: `2 fitters`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 10

- Speaker: **Mahesh**
- Audio: `jigishbhai_voice_058.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `assets`
- Ground Truth: `clinker cooler motor`
- Model output: `Clicker collar motor`
- Classification: **INCORRECT**
- Explanation: Model value differs from Ground Truth (GT=clinker cooler motor; model=Clicker collar motor).

### Error 11

- Speaker: **Mahesh**
- Audio: `jigishbhai_voice_058.wav`
- Pipeline: Direct Gemini
- Parameter: `assets`
- Ground Truth: `clinker cooler motor`
- Model output: `clean car cooler motor`
- Classification: **INCORRECT**
- Explanation: Model value differs from Ground Truth (GT=clinker cooler motor; model=clean car cooler motor).

### Error 12

- Speaker: **Mahesh**
- Audio: `jigishbhai_voice_058.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `quantities`
- Ground Truth: `1 6316 C3 bearing; 2 kg grease; 4 M18 bolts; 2 fitters`
- Model output: `16316 C3 bearing; 2 kilogram of grease; 4 M18 bolts`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 13

- Speaker: **Mahesh**
- Audio: `jigishbhai_voice_059.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `quantities`
- Ground Truth: `1 engineer; 1 fitter; gearbox replacement not to be assumed`
- Model output: `an engineer; a fitter`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 14

- Speaker: **Mahesh**
- Audio: `jigishbhai_voice_059.wav`
- Pipeline: Direct Gemini
- Parameter: `quantities`
- Ground Truth: `1 engineer; 1 fitter; gearbox replacement not to be assumed`
- Model output: `1 engineer; 1 fitter`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 15

- Speaker: **Mahesh**
- Audio: `jigishbhai_voice_059.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `hours`
- Ground Truth: `inspection_duration: 3 hours`
- Model output: `work_duration: 3-hour`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 16

- Speaker: **Mahesh**
- Audio: `jigishbhai_voice_059.wav`
- Pipeline: Direct Gemini
- Parameter: `hours`
- Ground Truth: `inspection_duration: 3 hours`
- Model output: `work_duration: 3 hours`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 17

- Speaker: **Mahesh**
- Audio: `jigishbhai_voice_059.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `dates`
- Ground Truth: `today night shift`
- Model output: `tonight in the night shift`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 18

- Speaker: **Julfikar**
- Audio: `julfikar_voice_054.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `assets`
- Ground Truth: `Conveyor CV-18 के tail pulley`
- Model output: `bearing of the tail pulley of the conveyor track`
- Classification: **INCORRECT**
- Explanation: Model value differs from Ground Truth (GT=Conveyor CV-18 के tail pulley; model=bearing of the tail pulley of the conveyor track).

### Error 19

- Speaker: **Julfikar**
- Audio: `julfikar_voice_054.wav`
- Pipeline: Direct Gemini
- Parameter: `assets`
- Ground Truth: `Conveyor CV-18 के tail pulley`
- Model output: `Conveyor C-2`
- Classification: **INCORRECT**
- Explanation: Model value differs from Ground Truth (GT=Conveyor CV-18 के tail pulley; model=Conveyor C-2).

### Error 20

- Speaker: **Julfikar**
- Audio: `julfikar_voice_054.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `hours`
- Ground Truth: `work_duration: 3 hours`
- Model output: `work_duration: three-hour`
- Classification: **MISSING**
- Explanation: Ground Truth contains a spoken fact that the model omitted.

### Error 21

- Speaker: **Julfikar**
- Audio: `julfikar_voice_055.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `quantities`
- Ground Truth: `6 M12 bolts; 1 coupling; 2 fitters`
- Model output: `One coupling; 6 M12 bolts`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 22

- Speaker: **Julfikar**
- Audio: `julfikar_voice_055.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `hours`
- Ground Truth: `work_duration: 3 hours; machine_downtime: 3 hours`
- Model output: `work_duration: 3 hours; machine_downtime: full 3 hours`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 23

- Speaker: **Julfikar**
- Audio: `julfikar_voice_056.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `assets`
- Ground Truth: `Packing machine number two का pneumatic valve`
- Model output: `pneumatic wall of packing machine number two`
- Classification: **INCORRECT**
- Explanation: Model value differs from Ground Truth (GT=Packing machine number two का pneumatic valve; model=pneumatic wall of packing machine number two).

### Error 24

- Speaker: **Julfikar**
- Audio: `julfikar_voice_056.wav`
- Pipeline: Direct Gemini
- Parameter: `assets`
- Ground Truth: `Packing machine number two का pneumatic valve`
- Model output: `packing machine number 2; pneumatic valve`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 25

- Speaker: **Julfikar**
- Audio: `julfikar_voice_056.wav`
- Pipeline: Sarvam + Gemini
- Parameter: `quantities`
- Ground Truth: `1 technician; valve replacement pending inspection`
- Model output: `two technicians; one technician`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

### Error 26

- Speaker: **Julfikar**
- Audio: `julfikar_voice_056.wav`
- Pipeline: Direct Gemini
- Parameter: `quantities`
- Ground Truth: `1 technician; valve replacement pending inspection`
- Model output: `1 technician`
- Classification: **PARTIAL_MATCH**
- Explanation: Partial overlap with Ground Truth; not counted as fully correct.

## 8. Limitations

- Only 9 recordings were evaluated.
- Only 3 speakers were represented.
- Only 3 recordings per speaker were used.
- Results measure this specific dataset only.
- Results should not be generalized to all speakers or dialects.
- This report does not modify or replace Agent 4 full-dataset evaluation outputs.
