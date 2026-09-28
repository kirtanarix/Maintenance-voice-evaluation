"""Structural and provenance validation only; no accuracy evaluation."""
import json
from src.run_dictionary_v1 import ROOT, PROJECT_ROOT, DICTIONARY, digest, dataset_files, write_new
from src.schema import MaintenanceExtraction


def main():
    before = json.loads((ROOT / 'existing_files_sha256.json').read_text())
    changed = [name for name, sha in before.items() if not (PROJECT_ROOT / name).is_file() or digest(PROJECT_ROOT / name) != sha]
    checks = {'existing_files_modified': changed, 'outputs': [], 'evaluation_run': False,
              'automatic_dictionary_insertion': 'None: model output is schema-validated and serialized without term replacement or enrichment.',
              'source_fidelity': 'Not certified: requires independent source audio/transcript review; no accuracy evaluation performed.'}
    dictionary = json.loads(DICTIONARY.read_text())
    for size in [50, 9]:
        names = {p.name for p in dataset_files(size)}
        manifest = json.loads((ROOT / f'{size}_recordings/manifest.json').read_text())
        assert manifest['dictionary_sha256'] == digest(DICTIONARY)
        assert set(manifest['recording_ids']) == names
        assert manifest['audio_sha256'] == {p.name: digest(p) for p in dataset_files(size)}
        for pipeline in ['sarvam_gemini', 'direct_gemini']:
            directory = ROOT / f'{size}_recordings'
            path = directory / f'{pipeline}_dictionary_v1_{size}.json'
            if not path.exists():
                checks['outputs'].append({'path': str(path), 'complete': False})
                continue
            data = json.loads(path.read_text())
            assert set(data) == names, 'Recording IDs mismatch'
            for name, record in data.items():
                MaintenanceExtraction.model_validate(record)
                assert set(record) == set(MaintenanceExtraction.model_fields)
                audit = json.loads((directory / 'prompts' / pipeline / (name + '.json')).read_text())
                embedded = audit['system_instruction'].split('<industry_vocabulary_reference_json>\n')[1].split('\n</industry_vocabulary_reference_json>')[0]
                assert json.loads(embedded) == dictionary
                assert record == json.loads((directory / 'records' / pipeline / (name + '.json')).read_text())
            checks['outputs'].append({'path': str(path), 'complete': True, 'recordings': len(data), 'schema_valid': True, 'dictionary_in_all_prompts': True})
    write_new(ROOT / 'validation.json', checks)
    print(json.dumps(checks, indent=2))
    return 0 if not changed and all(x['complete'] for x in checks['outputs']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
