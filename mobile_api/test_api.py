"""Offline tests: no credentials loaded and no Gemini network calls."""
import io
import json
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from mobile_api.app import app
from mobile_api import service
from src.config import PROJECT_ROOT, GEMINI_MODEL
from src.gemini_audio_client import GeminiAudioClient
from src.schema import MaintenanceExtraction

DATA = dict(assets="pump", quantities=["2 bolts"], hours=["2 hours"],
            dates="tomorrow", approval_intent=None)


def wav_bytes():
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(16000)
        stream.writeframes(b"\0\0" * 160)
    return buffer.getvalue()


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()

    def upload(self, filename="recording.wav", content=None):
        return self.client.post("/api/v1/transcribe", files={
            "audio": (filename, wav_bytes() if content is None else content, "application/octet-stream")
        })

    def test_success_and_cleanup(self):
        paths = []
        def extract(path):
            paths.append(path)
            self.assertEqual(path.read_bytes(), wav_bytes())
            return MaintenanceExtraction(**DATA)
        with patch("mobile_api.app.transcribe", side_effect=extract):
            response = self.upload("../../recording.WAV")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "data": DATA})
        self.assertFalse(paths[0].parent.exists())

    def test_missing_audio(self):
        response = self.client.post("/api/v1/transcribe")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "INVALID_AUDIO")

    def test_unsupported_audio(self):
        with patch("mobile_api.app.transcribe") as mock:
            response = self.upload("file.txt")
        self.assertEqual(response.status_code, 415)
        mock.assert_not_called()

    def test_empty_audio(self):
        self.assertEqual(self.upload(content=b"").status_code, 400)

    def test_oversized_audio(self):
        with patch("mobile_api.app.MAX_AUDIO_BYTES", 10):
            self.assertEqual(self.upload().status_code, 413)

    def test_api_failure_and_cleanup(self):
        paths = []
        def fail(path):
            paths.append(path)
            raise RuntimeError("secret key and C:/private/internal.wav")
        with patch("mobile_api.app.transcribe", side_effect=fail):
            response = self.upload()
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["error"]["code"], "EXTRACTION_FAILED")
        self.assertNotIn("secret", response.text)
        self.assertNotIn("private", response.text)
        self.assertFalse(paths[0].parent.exists())

    def test_invalid_schema_response(self):
        with patch("mobile_api.app.transcribe", return_value={"transcript": "private"}):
            response = self.upload()
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["error"]["code"], "INVALID_MODEL_RESPONSE")
        self.assertNotIn("private", response.text)

    def test_configuration_failure(self):
        with patch("mobile_api.app.transcribe", side_effect=service.ConfigurationError()):
            self.assertEqual(self.upload().status_code, 503)

    def test_existing_pipeline_prompt_and_transport(self):
        audit = json.loads((PROJECT_ROOT / "outputs/dictionary_v1/50_recordings/prompts/direct_gemini/voice001.wav.json").read_text(encoding="utf-8"))
        with patch("mobile_api.service.load_gemini_settings", return_value="fake"), patch("src.gemini_audio_client.genai.Client") as sdk:
            sdk.return_value.models.generate_content.return_value = SimpleNamespace(text=json.dumps(DATA))
            response = self.upload()
            self.assertEqual(response.status_code, 200)
            args = sdk.return_value.models.generate_content.call_args.kwargs
        self.assertEqual(args["model"], GEMINI_MODEL)
        self.assertEqual(args["model"], "gemini-3.6-flash")
        self.assertEqual(args["config"].temperature, 0.0)
        self.assertEqual(args["config"].response_mime_type, "application/json")
        self.assertEqual(args["config"].system_instruction, audit["system_instruction"])
        parts = args["contents"][0].parts
        self.assertEqual(parts[1].text, audit["user_prompt"])
        self.assertEqual(parts[0].inline_data.data, wav_bytes())
        self.assertEqual(parts[0].inline_data.mime_type, "audio/wav")

    def test_invalid_gemini_json(self):
        for raw in ["not json", "[]", "", '{"assets":null}']:
            with self.subTest(raw=raw), patch("mobile_api.service.load_gemini_settings", return_value="fake"), patch("src.gemini_audio_client.genai.Client") as sdk:
                sdk.return_value.models.generate_content.return_value = SimpleNamespace(text=raw)
                response = self.upload()
                self.assertEqual(response.status_code, 502)
                self.assertEqual(response.json()["error"]["code"], "INVALID_MODEL_RESPONSE")

    def test_mobile_extensions(self):
        with patch("mobile_api.app.transcribe", return_value=MaintenanceExtraction(**DATA)):
            for extension in ["wav", "mp3", "m4a", "flac", "ogg", "aac", "webm"]:
                self.assertEqual(self.upload("audio." + extension).status_code, 200)


if __name__ == "__main__":
    unittest.main()
