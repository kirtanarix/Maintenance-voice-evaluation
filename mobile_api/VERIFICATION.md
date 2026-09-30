# Verification report

## Repository inspection and reuse

- Extraction: `src.direct_extractor.extract_from_audio()`.
- Transport: `src.gemini_audio_client.GeminiAudioClient.extract_from_audio_file()`.
- Dictionary: `inputs/dictionary/India_Cement_Industry_and_Generic_Maintenance_Dictionary_v1.0.json`.
- Prompt: original `DIRECT_EXTRACTION_SYSTEM_INSTRUCTION`, followed by the exact
  `src.run_dictionary_v1.RULES` and full dictionary serialized with
  `json.dumps(..., ensure_ascii=False)` inside the original vocabulary delimiters.
- User prompt: unchanged `DIRECT_USER_PROMPT` through the existing extractor.
- Model: `gemini-3.6-flash`; temperature `0.0`; response MIME `application/json`.
- Schema: unchanged `src.schema.MaintenanceExtraction`; the API wraps it inside
  `{ "success": true, "data": ... }`. Approval intent remains string/null.
- Configuration: existing `src.config.load_gemini_settings()`, project-root `.env`
  or environment `GEMINI_API_KEY`. No real key is included in new files.
- No existing API framework was found. Added FastAPI, Uvicorn, and multipart
  parsing requirements separately without changing the original requirements.

The API adapter reproduces the V1 context injection but omits the experiment
adapter's persistent prompt/audio-hash audit writes. It does not invoke the batch
runner, evaluator, ground-truth generator, or Sarvam. No extraction logic changed.

## Test result

Executed: `.venv_windows/Scripts/python.exe -B -m unittest mobile_api.test_api -v`

**11 tests passed**, including success/schema compatibility, missing/empty audio,
unsupported extensions, size limit, service configuration failure, provider failure,
malformed/empty/list/incomplete model JSON, and temporary-file cleanup. The mocked
SDK test exercises the real extractor/client and asserts exact system/user prompt
equality with the saved 50-recording V1 prompt for `voice001.wav`, unchanged audio
bytes, model identifier, temperature, and JSON response format.

No real Gemini calls were made. No accuracy experiment was rerun. This verifies
the HTTP integration and preservation of the existing pipeline, not live provider
availability or accuracy on new audio.

Test environment: FastAPI 0.142.2, Uvicorn 0.54.0, python-multipart 0.0.32.
Starlette emitted a non-failing deprecation warning about its httpx TestClient.
The sandbox blocked temporary-file operations; the passing run used approved
execution outside that restriction. All provider interactions remained mocked.

SHA-256 comparison before/after implementation confirmed the pre-existing files
under `src/`, `inputs/`, `outputs/`, `audio/`, and `audio_backup/` were unchanged
(Python bytecode excluded). Pre-existing unrelated working-tree changes were left
untouched. Added API files are isolated in `mobile_api/`; dependencies were installed
in the existing local `.venv_windows` environment.

Postman collection: `mobile_api/postman_collection.json`. Parsed successfully;
its successful response example validates against the existing schema.

## Deliverables

- `app.py`, `service.py`, `__init__.py`: API boundary and V1 adapter.
- `requirements.txt`, `requirements-test.txt`: isolated dependency entry points.
- `.env.example`: placeholder-only server configuration guidance.
- `README.md`: setup, local run/test commands, operational scope.
- `CONTRACT.md`: request, response, field types, and error contract.
- `test_api.py`: offline API and prompt-parity tests.
- `postman_collection.json`: one mobile upload request and response examples.
- `VERIFICATION.md`: this report.
