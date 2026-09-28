# Dictionary v1.0 extraction experiment

Completed both experiments, producing 118 extraction records in four separate JSON files. No accuracy evaluation was run or improvement claimed.

## A. Existing files changed

None. SHA-256 checks confirm all 89 pre-existing source, input, audio and output files remain byte-identical. Baseline extractions (both contain 59 IDs), ground-truth inputs/results, Agent 3, Agent 4, normalization and evaluation reports were untouched.

## B. Files created

- `src/run_dictionary_v1.py`: isolated runner and context adapters; reuses existing extractors, clients, schema and configured models.
- `src/validate_dictionary_v1.py`: structural/provenance validation only.
- Four aggregate JSON files listed below.
- `outputs/dictionary_v1/existing_files_sha256.json`, `validation.json`, `created_files.json` and this report.
- Each dataset directory contains a manifest, 59 total Sarvam transcripts across both datasets, 118 prompt audits and 118 per-record checkpoints across both pipelines/datasets. Initial/transient failure files are retained. See `created_files.json` for the complete inventory.

## C. Prompt/context change

Agent 1's original prompt is built by `src/extractor.py:extract_from_transcript`; its Gemini request is made by `src/gemini_client.py:GeminiClient.generate_json`. Agent 2's prompts are in `src/direct_extractor.py:extract_from_audio`; its audio request is made by `src/gemini_audio_client.py:GeminiAudioClient.extract_from_audio_file`.

The new adapters append source-only safeguards and the full dynamically loaded external dictionary JSON, delimited by `<industry_vocabulary_reference_json>`, to each original system instruction immediately before the existing Gemini client call. The dictionary includes metadata, categories (including Hindi/Hinglish variants), model-context rules, experiment rules and classification notes. The exact requested v1.0 file is used; terms are not embedded in Python. Replacing its data with a future dictionary does not require rewriting extraction logic (a new versioned experiment configuration/output root should be used).

Safeguards preserve spoken terms, IDs and specifications, respect negation, unknown/pending values and corrections, distinguish work duration from downtime, and prohibit inferred schedules or cement equipment. User prompts and audio transport are unchanged. Sarvam receives no dictionary. Model settings remain `gemini-3.6-flash`, temperature 0.0, and Sarvam `saaras:v4` translate mode.

Model results are validated and serialized through the existing five-field schema. No dictionary-based normalization, correction, enrichment or result rewriting occurs.

## D. Commands used

Run from the project root:

```bash
.venv/bin/python -m src.run_dictionary_v1 --dataset 50
.venv/bin/python -m src.run_dictionary_v1 --dataset 50 --resume
.venv/bin/python -m src.run_dictionary_v1 --dataset 9
.venv/bin/python -m src.run_dictionary_v1 --dataset 9 --resume
.venv/bin/python -m src.validate_dictionary_v1
```

Resume commands were repeated after transient DNS/upload/TLS failures. Network-enabled execution was required. Resume reuses existing experiment checkpoints without overwriting them; mismatching manifests, transcripts or prompts are rejected. New outputs use exclusive creation. The validator also creates its report exclusively and will refuse to overwrite an existing validation report.

Local fake-client checks verified prompt transport for both pipelines, unchanged all-null results (no automatic term insertion), schema preservation, exclusive-write refusal and rejection of differing checkpoint content. These checks do not establish real-model factual fidelity.

The original batch entry points, `python -m src.run_agent1` and `python -m src.run_direct_gemini`, scan `audio/` and merge into existing baseline JSON files. They were inspected but not run.

## E. 50-recording outputs

- `outputs/dictionary_v1/50_recordings/sarvam_gemini_dictionary_v1_50.json`
- `outputs/dictionary_v1/50_recordings/direct_gemini_dictionary_v1_50.json`

Dataset selection uses filenames from the existing 50-recording evaluation manifest, checks baseline membership, and reads audio from `audio_backup/`.

## F. Nine-recording outputs

- `outputs/dictionary_v1/9_recordings/sarvam_gemini_dictionary_v1_9.json`
- `outputs/dictionary_v1/9_recordings/direct_gemini_dictionary_v1_9.json`

Dataset selection uses `evaluated_filenames` from the existing speaker/dialect evaluation manifest, checks baseline membership, and reads audio from `audio/`. Filenames are preserved exactly, including the existing jigishbhai filenames.

## G. Validation results

All four aggregates pass: 50, 50, 9 and 9 records respectively; exact corresponding baseline subset IDs; no missing/unexpected recordings; all five fields valid under the existing schema. Every record equals its saved model-result checkpoint. All 118 saved Gemini request prompts contain JSON equal to the requested dictionary. Dictionary and audio hashes match their manifests. See `validation.json`.

## H. Integrity confirmation

All 89 pre-existing files match the initial SHA-256 snapshot. No baseline or ground-truth file was modified. No Agent 3, Agent 4, Agent 5 or normalization/evaluation logic was changed or executed. Evaluation manifests were read only to select filenames; ground-truth values were never supplied to extraction models.

## I. Issues and limitations

- Transient network failures were recovered; completed records were reused, not regenerated. Failure logs remain for provenance.
- No code automatically inserts dictionary terms. However, schema and prompt checks cannot prove that every model-generated term occurred in the source. Full source audio/transcript fidelity review remains pending; this report does not certify absence of model hallucination.
- Agent 1 uses fresh Sarvam transcriptions because no original transcript archive was present. STT variation may affect later baseline comparisons. Saved experiment transcripts make this run auditable.
- The dictionary declares that its vocabulary was informed by these 59 recordings. A later comparison should disclose this dataset-informed context and should not claim held-out generalization.
- The intervention includes both the dictionary and explicit source-only safeguards requested by the user. Later comparisons should describe that full prompt intervention.
- Temperature 0 does not guarantee repeatability or identical hosted-model behavior over time.

Extraction and evaluation remain separate. No accuracy calculation has been performed.
