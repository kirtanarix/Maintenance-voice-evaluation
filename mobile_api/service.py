"""Reuse extraction without the experiment adapter's disk audit writes."""
import json
from pathlib import Path

from src.config import load_gemini_settings
from src.direct_extractor import extract_from_audio
from src.gemini_audio_client import GeminiAudioClient
from src.run_dictionary_v1 import DICTIONARY, RULES
from src.schema import MaintenanceExtraction


class ConfigurationError(Exception):
    pass


def dictionary_context() -> str:
    dictionary = json.loads(DICTIONARY.read_text(encoding="utf-8"))
    return (
        "\n" + RULES + "\n<industry_vocabulary_reference_json>\n"
        + json.dumps(dictionary, ensure_ascii=False)
        + "\n</industry_vocabulary_reference_json>\n"
    )


class VocabularyClient:
    def __init__(self, client, context: str):
        self.client, self.context = client, context

    def extract_from_audio_file(self, audio_path, *, system_instruction, user_prompt):
        return self.client.extract_from_audio_file(
            audio_path,
            system_instruction=system_instruction + self.context,
            user_prompt=user_prompt,
        )


def transcribe(audio_path: Path) -> MaintenanceExtraction:
    try:
        context = dictionary_context()
        key = load_gemini_settings()
    except Exception as exc:
        raise ConfigurationError() from exc
    client = GeminiAudioClient(key)
    return extract_from_audio(VocabularyClient(client, context), audio_path)
