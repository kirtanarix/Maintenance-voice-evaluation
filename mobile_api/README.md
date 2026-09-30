# Maintenance mobile API

Run commands from the repository root with Python 3.10+:

```powershell
python -m pip install -r mobile_api/requirements.txt
python -m uvicorn mobile_api.app:app --host 127.0.0.1 --port 8000
```

Set `GEMINI_API_KEY` in the existing project-root `.env` or server environment.
See `.env.example` in this folder for the placeholder. Never ship the key to the
mobile app. `src.config.load_gemini_settings()` loads the existing configuration;
no Sarvam key is needed. Keep the repository's `src/` and V1 dictionary available.
The original requirements are included because the V1 module imports existing
Sarvam classes, although this API never calls Sarvam.

Local OpenAPI documentation: http://127.0.0.1:8000/docs

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/transcribe -F "audio=@recording.wav"
python -m pip install -r mobile_api/requirements-test.txt
python -B -m unittest mobile_api.test_api -v
```

Tests mock the Gemini SDK or extraction boundary. They never use real credentials
or send audio to Gemini. A real request to the running server does call Gemini.

Import `postman_collection.json` into Postman, set `base_url` (default
`http://127.0.0.1:8000`), and select a file in the `audio` form-data field. Let
Postman/mobile multipart libraries set Content-Type and its boundary.

The endpoint runs synchronous extraction in FastAPI's worker thread pool. It
creates a generated temporary filename, removes it on success/failure, and closes
the multipart upload. It writes no predictions, prompts, transcripts, or audio
to experiment folders. There is no API-level retry or persistent job state.

Audio is limited to 20 MiB after multipart parsing. Configure an ingress request
size limit as well when deploying: multipart parsing can spool the incoming file
before the endpoint checks its size. Extension validation is not codec/content
verification; bytes are forwarded unchanged, just as in the existing client.
Authentication/deployment are outside this local API deliverable; use your
backend's existing access controls when exposing it to mobile clients.

See `CONTRACT.md` and `VERIFICATION.md` for the contract and exact pipeline reuse.
