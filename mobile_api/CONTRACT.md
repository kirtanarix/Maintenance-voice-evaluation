# API contract

`POST /api/v1/transcribe`

Request: `multipart/form-data`, required file field **audio**. Supported filename
extensions: `.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`, `.aac`, `.webm`
(case-insensitive). Maximum audio size: 20 MiB; empty files are rejected.
No dictionary or Gemini key is provided by the caller. MIME mapping is inherited
from `src.config`; an upload's client-supplied MIME does not override it.

HTTP 200:

```json
{
  "success": true,
  "data": {
    "assets": "pump",
    "quantities": ["2 bolts"],
    "hours": ["2 hours"],
    "dates": "tomorrow",
    "approval_intent": null
  }
}
```

`data` is the existing `src.schema.MaintenanceExtraction`, with all five keys:

| Field | Type |
|---|---|
| assets | string, string array, or null |
| quantities | string array or null |
| hours | array of strings and/or objects, or null |
| dates | string, string array, or null |
| approval_intent | string or null (not an array) |

For example, hours can contain `{"kind":"work_duration","value":"2 hours"}`.
The existing schema permits arbitrary inner hour dictionaries; this API does not
tighten or change it. Values are not normalized or rewritten after extraction.
No transcript, dictionary, raw model response, or confidence is returned.

Errors have this shape:

```json
{"success":false,"error":{"code":"INVALID_AUDIO","message":"The audio file is empty."}}
```

| HTTP | Code | Condition |
|---|---|---|
| 400 | INVALID_AUDIO | Empty audio |
| 422 | INVALID_AUDIO | Missing audio file or invalid file field |
| 415 | UNSUPPORTED_AUDIO | Missing/unsupported filename extension |
| 413 | AUDIO_TOO_LARGE | Audio exceeds 20 MiB |
| 502 | EXTRACTION_FAILED | Gemini/network/extraction failure |
| 502 | INVALID_MODEL_RESPONSE | Empty/malformed JSON or schema mismatch |
| 503 | SERVICE_UNAVAILABLE | Missing configuration or unreadable dictionary |
| 500 | INTERNAL_ERROR | Unexpected backend failure |
| 4xx | INVALID_REQUEST | Framework HTTP error, including malformed multipart |

Provider error strings, keys, filesystem paths, and raw validation inputs are
not included in error responses. A 200 indicates schema-valid extraction, not
a guarantee of factual correctness or 83.6% accuracy on new mobile recordings.
