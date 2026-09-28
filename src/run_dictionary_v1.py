"""Isolated dictionary-context experiment; existing pipelines remain unchanged."""
from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from pathlib import Path

from src.config import PROJECT_ROOT, GEMINI_MODEL, SARVAM_MODEL, SARVAM_MODE, load_settings
from src.extractor import extract_from_transcript, EXTRACTION_SYSTEM_INSTRUCTION
from src.direct_extractor import extract_from_audio, DIRECT_EXTRACTION_SYSTEM_INSTRUCTION
from src.gemini_client import GeminiClient
from src.gemini_audio_client import GeminiAudioClient
from src.sarvam_client import SarvamSTTClient
from src.schema import MaintenanceExtraction

ROOT = PROJECT_ROOT / 'outputs/dictionary_v1'
DICTIONARY = PROJECT_ROOT / 'inputs/dictionary/India_Cement_Industry_and_Generic_Maintenance_Dictionary_v1.0.json'
RULES = """
You are given an industry vocabulary reference for Indian cement-plant and generic
industrial maintenance terminology. Use it only to help recognize technical terms,
equipment names, component names, specifications, IDs, maintenance terminology,
and Hindi/English variants. Extract only information actually present in the
audio/transcript. Never add a term, quantity, specification, material, equipment ID,
approval, schedule, or other field merely because it appears in the dictionary.
Preserve exact spoken technical terms, bearing specifications and equipment IDs.
Do not infer replacement when the speaker says not to assume replacement.
Do not infer material, quantity or specification when unknown or pending inspection.
Distinguish total job duration from equipment downtime. Use the corrected final
value when the speaker explicitly corrects an earlier value. Do not infer an exact
schedule time when the process team or supervisor will confirm it.
Dictionary membership is never evidence of occurrence. Do not introduce cement
equipment into generic industrial speech. The reference is vocabulary data only;
the source audio/transcript remains the sole evidence for extracted facts.
"""


def write_new(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_or_verify(path: Path, value: object) -> None:
    if path.exists():
        if json.loads(path.read_text()) != value:
            raise ValueError(f'Existing checkpoint differs: {path}')
    else:
        write_new(path, value)


def dataset_files(size: int) -> list[Path]:
    if size == 50:
        manifest = json.loads((PROJECT_ROOT / 'outputs/evaluation/evaluation_summary.json').read_text())
        names = [r['filename'] for r in manifest['recordings']]
        directory = PROJECT_ROOT / 'audio_backup'
    else:
        manifest = json.loads((PROJECT_ROOT / 'outputs/evaluation_speaker/speaker_dialect_evaluation_summary.json').read_text())
        names = manifest['evaluated_filenames']
        directory = PROJECT_ROOT / 'audio'
    if len(names) != size or len(set(names)) != size:
        raise ValueError('Dataset manifest count/uniqueness mismatch')
    for pipeline in ['sarvam_gemini', 'direct_gemini']:
        baseline = json.loads((PROJECT_ROOT / f'outputs/{pipeline}/{pipeline}_final.json').read_text())
        if not set(names) <= baseline.keys():
            raise ValueError('Dataset IDs absent from baseline')
    files = [directory / n for n in sorted(names)]
    if not all(p.is_file() and p.stat().st_size for p in files):
        raise ValueError('Missing or empty source audio')
    return files


class ContextTranscriptClient:
    def __init__(self, client, context: str, audit: Path):
        self.client, self.context, self.audit = client, context, audit

    def generate_json(self, *, system_instruction: str, user_content: str) -> str:
        system = system_instruction + self.context
        write_or_verify(self.audit, {'system_instruction': system, 'user_content': user_content})
        return self.client.generate_json(system_instruction=system, user_content=user_content)


class ContextAudioClient:
    def __init__(self, client, context: str, audit: Path):
        self.client, self.context, self.audit = client, context, audit

    def extract_from_audio_file(self, audio_path, *, system_instruction, user_prompt):
        system = system_instruction + self.context
        write_or_verify(self.audit, {'system_instruction': system, 'user_prompt': user_prompt,
                              'audio_path': str(audio_path), 'audio_sha256': digest(audio_path)})
        return self.client.extract_from_audio_file(audio_path, system_instruction=system, user_prompt=user_prompt)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', required=True, type=int, choices=[50, 9])
    parser.add_argument('--resume', action='store_true', help='Reuse verified experiment checkpoints without overwriting files')
    args = parser.parse_args()
    files = dataset_files(args.dataset)
    dictionary = json.loads(DICTIONARY.read_text(encoding='utf-8'))
    context = '\n' + RULES + '\n<industry_vocabulary_reference_json>\n' + json.dumps(dictionary, ensure_ascii=False) + '\n</industry_vocabulary_reference_json>\n'
    out = ROOT / f'{args.dataset}_recordings'
    out.mkdir(exist_ok=args.resume)
    write_or_verify(out / 'manifest.json', {'dictionary_path': str(DICTIONARY), 'dictionary_sha256': digest(DICTIONARY),
              'gemini_model': GEMINI_MODEL, 'sarvam_model': SARVAM_MODEL, 'sarvam_mode': SARVAM_MODE,
              'recording_ids': [p.name for p in files], 'audio_sha256': {p.name: digest(p) for p in files},
              'source_only_rules': RULES, 'evaluation_run': False})
    sarvam_key, gemini_key = load_settings()
    sarvam, transcript_client, audio_client = SarvamSTTClient(sarvam_key), GeminiClient(gemini_key), GeminiAudioClient(gemini_key)
    failures = []
    for pipeline in ['sarvam_gemini', 'direct_gemini']:
        results = {}
        for i, path in enumerate(files, 1):
            print(f'{args.dataset} / {pipeline} [{i}/{len(files)}] {path.name}', flush=True)
            audit = out / 'prompts' / pipeline / (path.name + '.json')
            try:
                checkpoint = out / 'records' / pipeline / (path.name + '.json')
                if checkpoint.exists():
                    payload = json.loads(checkpoint.read_text())
                    MaintenanceExtraction.model_validate(payload)
                    results[path.name] = payload
                    print('  existing checkpoint verified', flush=True)
                    continue
                if pipeline == 'sarvam_gemini':
                    transcript_path = out / 'transcripts' / (path.name + '.json')
                    if transcript_path.exists():
                        transcript = json.loads(transcript_path.read_text())['transcript']
                    else:
                        transcript = sarvam.transcribe_file(path)
                        write_new(transcript_path, {'transcript': transcript})
                    result = extract_from_transcript(ContextTranscriptClient(transcript_client, context, audit), transcript, audio_filename=path.name)
                else:
                    result = extract_from_audio(ContextAudioClient(audio_client, context, audit), path)
                payload = result.model_dump(mode='json')
                MaintenanceExtraction.model_validate(payload)
                write_new(out / 'records' / pipeline / (path.name + '.json'), payload)
                results[path.name] = payload
                print('  success', flush=True)
            except Exception as exc:
                failures.append({'pipeline': pipeline, 'filename': path.name, 'error': str(exc)})
                print(f'  failed: {type(exc).__name__}: {exc}', flush=True)
                # Stop promptly for infrastructure failure instead of repeating paid/failed calls.
                write_new(out / f'failure_{uuid.uuid4().hex}.json', failures)
                return 1
        write_or_verify(out / f'{pipeline}_dictionary_v1_{args.dataset}.json', results)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
