"""Evaluate saved dictionary outputs with unchanged baseline scoring; no API calls."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.evaluator import PARAMETERS, CORRECT_JUDGMENTS, JUDGMENTS, evaluate
from src.report_generator import _build_summary
from src.speaker_evaluator import evaluate_speaker_subset
from src.schema import MaintenanceExtraction

PROJECT = Path(__file__).resolve().parent.parent
ROOT = PROJECT / 'outputs/dictionary_v1'
GT = PROJECT / 'outputs/ground_truth/ground_truth_final.json'
BASELINES = {
    50: PROJECT / 'outputs/evaluation/evaluation_summary.json',
    9: PROJECT / 'outputs/evaluation_speaker/speaker_dialect_evaluation_summary.json',
}
PIPES = {'direct_gemini': 'Direct Gemini', 'sarvam_gemini': 'Sarvam + Gemini'}
DISPLAY = {'Sanjay': 'Sanjay', 'Julfikar': 'Julfikar', 'Mahesh': 'Jigish (legacy mapping: Mahesh)'}
LIMITATIONS = [
    'The legacy speaker mapping labels jigishbhai_* as Mahesh. Reports display this group as Jigish (legacy mapping: Mahesh); grouping and scoring are unchanged.',
    'The extraction intervention included the dictionary plus explicit source-only safeguards; Agent 1 used fresh Sarvam transcripts. These results measure observed changes, not an isolated dictionary-only causal effect.',
    'The dictionary declares that its vocabulary was informed by these 59 recordings. Results do not establish held-out generalization.',
    'Scoring uses the existing deterministic heuristic comparers, not a new human audio review. HALLUCINATION is an evaluator classification against ground truth.',
    'No extraction API calls, regeneration, dictionary-based scoring, or changes to evaluation/normalization were made.',
]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        f.write(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2))
        f.write('\n')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def params(summary, size, pipe):
    return ({p: summary['per_parameter'][p][pipe] for p in PARAMETERS}
            if size == 50 else summary['overall'][pipe]['per_parameter'])


def pipeline_result(summary, size, pipe, metadata):
    rows = []
    for record in summary['recordings']:
        fields = record[pipe] if size == 50 else {
            p: {'ground_truth': record['parameters'][p]['ground_truth'],
                'model': record['parameters'][p][pipe]['value'],
                'judgment': record['parameters'][p][pipe]['judgment']}
            for p in PARAMETERS}
        row = {'filename': record['filename'], 'parameters': fields}
        if size == 9:
            row.update(speaker=DISPLAY[record['speaker']], legacy_speaker=record['speaker'])
        rows.append(row)
    errors = [{'filename': r['filename'], 'parameter': p, **f}
              for r in rows for p, f in r['parameters'].items()
              if f['judgment'] not in CORRECT_JUDGMENTS]
    result = {'experiment': metadata, 'pipeline': pipe, 'pipeline_name': PIPES[pipe],
              'recording_count': size, 'overall': summary['overall'][pipe],
              'per_parameter': params(summary, size, pipe), 'recordings': rows, 'errors': errors}
    if size == 9:
        result['speakers'] = {DISPLAY[s]: {'legacy_speaker': s, 'recordings': v['recordings'],
                                          'filenames': v['filenames'], **v[pipe]}
                              for s, v in summary['speakers'].items()}
    return result


def validate_result(result, expected, gt, extraction):
    rows = result['recordings']
    require(len(rows) == len(expected) and {r['filename'] for r in rows} == set(expected), 'Result IDs mismatch')
    flat = []
    for r in rows:
        require(set(r['parameters']) == set(PARAMETERS), 'Result parameter schema mismatch')
        for p, field in r['parameters'].items():
            require(set(field) == {'ground_truth', 'model', 'judgment'}, 'Field result schema mismatch')
            require(field['ground_truth'] == gt[r['filename']][p], 'Ground truth changed')
            require(field['model'] == extraction[r['filename']][p], 'Extraction value changed')
            require(field['judgment'] in JUDGMENTS, 'Invalid judgment')
            flat.append(field['judgment'])
    for stats, judgments in [(result['overall'], flat)] + [
        (result['per_parameter'][p], [r['parameters'][p]['judgment'] for r in rows]) for p in PARAMETERS]:
        correct = sum(j in CORRECT_JUDGMENTS for j in judgments)
        require(stats['correct'] == correct and stats['total'] == len(judgments), 'Invalid score counts')
        require(stats['accuracy_percent'] == round(100 * correct / len(judgments), 2), 'Invalid accuracy')
        require(sum(stats['counts'].values()) == len(judgments), 'Invalid judgment totals')


def report(size, results):
    lines = [f'# Dictionary v1.0 evaluation — {size} recordings', '',
             f'Ground truth: `{GT.relative_to(PROJECT)}`; exact baseline subset selected in memory.', '',
             'Unchanged Agent 4 field comparers and normalization; nine-recording grouping uses the existing speaker evaluator.',
             'Accuracy = 100 × (EXACT_MATCH + SEMANTIC_MATCH + CORRECT_NULL) / all field judgments, rounded to two decimals. PARTIAL_MATCH receives no accuracy credit.', '',
             f'{size} recordings × 5 fields = {size * 5} comparisons per pipeline; no missing, unexpected or skipped recordings.', '',
             '## Overall and parameter accuracy', '', '| Pipeline | Correct / Total | Accuracy |', '|---|---:|---:|']
    for pipe, r in results.items():
        s = r['overall']; lines.append(f"| {PIPES[pipe]} | {s['correct']}/{s['total']} | {s['accuracy_percent']:.2f}% |")
    lines += ['', '| Parameter | Direct Gemini | Sarvam + Gemini |', '|---|---:|---:|']
    for p in PARAMETERS:
        cells = [f"{r['per_parameter'][p]['correct']}/{r['per_parameter'][p]['total']} ({r['per_parameter'][p]['accuracy_percent']:.2f}%)" for r in results.values()]
        lines.append(f'| {p} | ' + ' | '.join(cells) + ' |')
    if size == 9:
        lines += ['', '## Speaker accuracy', '', '| Speaker | Pipeline | Recordings | Correct / Total | Accuracy |', '|---|---|---:|---:|---:|']
        for pipe, r in results.items():
            for speaker, s in r['speakers'].items():
                lines.append(f"| {speaker} | {PIPES[pipe]} | {s['recordings']} | {s['correct']}/{s['total']} | {s['accuracy_percent']:.2f}% |")
    for pipe, r in results.items():
        lines += ['', f'## {PIPES[pipe]} — per-recording results', '',
                  f"Non-correct fields: {len(r['errors'])}. Every field below includes its ground truth, model value and classification.", '']
        for row in r['recordings']:
            lines += [f"### {row['filename']}" + (f" — {row['speaker']}" if size == 9 else ''), '']
            lines += ['```json', json.dumps(row['parameters'], ensure_ascii=False, indent=2), '```', '']
    lines += ['## Limitations and comparison notes', ''] + ['- ' + x for x in LIMITATIONS]
    return '\n'.join(lines)


def main():
    targets = [ROOT / f'evaluation_{n}' for n in (50, 9)] + [ROOT / ('dictionary_v1_' + s) for s in
               ('baseline_comparison.md', 'baseline_comparison.json', 'evaluation_validation.json', 'evaluation_existing_files_sha256.json')]
    require(not any(p.exists() for p in targets), 'Evaluation destination already exists; refusing overwrite')
    protected = {str(p.relative_to(PROJECT)): sha(p) for folder in ('src', 'inputs', 'outputs', 'audio', 'audio_backup')
                 for p in (PROJECT / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    gt = load(GT)
    mapping = load(PROJECT / 'inputs/speaker_mapping.json')
    baseline_outputs = {p: load(PROJECT / f'outputs/{p}/{p}_final.json') for p in PIPES}
    comparisons, prepared, validation = [], {}, []
    for size in (50, 9):
        baseline = load(BASELINES[size])
        names = [r['filename'] for r in baseline['recordings']]
        require(len(names) == size and len(set(names)) == size, 'Baseline ID mismatch')
        subset = {n: gt[n] for n in names}
        for record in subset.values():
            MaintenanceExtraction.model_validate(record)
        if size == 9:
            require({n for group in mapping.values() for n in group} == set(names), 'Speaker mapping IDs mismatch')
            require(all(len(group) == 3 for group in mapping.values()), 'Speaker counts mismatch')
        def score(values):
            if size == 50:
                return _build_summary(evaluate(subset, values['sarvam_gemini'], values['direct_gemini']))
            return evaluate_speaker_subset(ground_truth=subset, sarvam=values['sarvam_gemini'],
                                           direct=values['direct_gemini'], speaker_mapping=mapping)
        reproduced = score({p: {n: baseline_outputs[p][n] for n in names} for p in PIPES})
        require(reproduced['recordings'] == baseline['recordings'] and reproduced['overall'] == baseline['overall'], 'Baseline not reproduced')
        for p in PIPES:
            require(params(reproduced, size, p) == params(baseline, size, p), 'Baseline parameter stats not reproduced')
        values = {p: load(ROOT / f'{size}_recordings/{p}_dictionary_v1_{size}.json') for p in PIPES}
        for pipe, records in values.items():
            require(len(records) == size and set(records) == set(names), 'Extraction IDs mismatch')
            for record in records.values():
                MaintenanceExtraction.model_validate(record)
        manifest = load(ROOT / f'{size}_recordings/manifest.json')
        audio_dir = PROJECT / ('audio_backup' if size == 50 else 'audio')
        require(manifest['audio_sha256'] == {n: sha(audio_dir / n) for n in names}, 'Audio changed since extraction')
        require(manifest['dictionary_sha256'] == sha(Path(manifest['dictionary_path'])), 'Dictionary changed since extraction')
        metadata = {'dictionary_version': '1.0', 'ground_truth_path': str(GT.relative_to(PROJECT)),
                    'ground_truth_sha256': sha(GT), 'recording_ids': names,
                    'baseline_summary': str(BASELINES[size].relative_to(PROJECT)),
                    'baseline_exactly_reproduced': True, 'methodology_unchanged': True,
                    'speaker_display_labels': DISPLAY if size == 9 else {}, 'limitations': LIMITATIONS}
        summary = score(values)
        summary['experiment'] = metadata
        results = {p: pipeline_result(summary, size, p, metadata) for p in PIPES}
        for pipe, r in results.items():
            validate_result(r, names, subset, values[pipe])
            base = baseline['overall'][pipe]; current = r['overall']
            change = lambda b, c: {'baseline_accuracy': b['accuracy_percent'], 'dictionary_accuracy': c['accuracy_percent'],
                'difference_pp': round(100 * (c['correct']/c['total'] - b['correct']/b['total']), 2),
                'baseline_correct': b['correct'], 'dictionary_correct': c['correct'], 'total': c['total']}
            row = {'dataset': size, 'pipeline': pipe, **change(base, current),
                   'parameters': {p: change(params(baseline, size, pipe)[p], r['per_parameter'][p]) for p in PARAMETERS}}
            comparisons.append(row)
            validation.append({'dataset': size, 'pipeline': pipe, 'recordings': len(r['recordings']),
                               'missing': [], 'unexpected': [], 'skipped': [], 'schema_valid': True,
                               'comparisons': current['total'], 'not_evaluable': current['counts']['NOT_EVALUABLE'],
                               'speakers': {DISPLAY[s]: len(v) for s, v in mapping.items()} if size == 9 else None})
        prepared[size] = (summary, results)
    # Only write after both experiments and baseline reproduction pass all checks.
    save(ROOT / 'dictionary_v1_evaluation_existing_files_sha256.json', protected)
    for size, (summary, results) in prepared.items():
        directory = ROOT / f'evaluation_{size}'; directory.mkdir(exist_ok=False)
        stem = f'dictionary_v1_{"speaker_dialect_" if size == 9 else ""}evaluation'
        save(directory / f'{stem}_summary_{size}.json', summary)
        save(directory / f'{stem}_report_{size}.md', report(size, results))
        for pipe, result in results.items():
            save(directory / f'{pipe}_dictionary_v1_evaluation_{size}.json', result)
    # Comparison is built from saved evaluation files, not hard-coded new scores.
    for row in comparisons:
        saved = load(ROOT / f"evaluation_{row['dataset']}/{row['pipeline']}_dictionary_v1_evaluation_{row['dataset']}.json")
        require(saved['overall']['accuracy_percent'] == row['dictionary_accuracy'], 'Saved score mismatch')
    save(ROOT / 'dictionary_v1_baseline_comparison.json', {'comparisons': comparisons, 'limitations': LIMITATIONS})
    lines = ['# Baseline versus dictionary v1.0', '',
             'Baseline scores read from existing reports and exactly reproduced with current ground truth and unchanged evaluators. New scores verified against saved dictionary evaluation files.', '',
             '| Dataset | Pipeline | Baseline | Dictionary v1 | Difference | Correct fields |', '|---|---|---:|---:|---:|---:|']
    for r in comparisons:
        lines.append(f"| {r['dataset']} | {PIPES[r['pipeline']]} | {r['baseline_accuracy']:.2f}% | {r['dictionary_accuracy']:.2f}% | {r['difference_pp']:+.2f} pp | {r['baseline_correct']} → {r['dictionary_correct']} / {r['total']} |")
    lines += ['', 'Differences use unrounded correct/total fractions, then round to two decimals. This avoids subtracting already-rounded percentages.', '']
    for r in comparisons:
        lines += [f"## {r['dataset']} recordings — {PIPES[r['pipeline']]}", '', '| Parameter | Baseline | Dictionary v1 | Difference | Correct fields |', '|---|---:|---:|---:|---:|']
        for p, v in r['parameters'].items():
            lines.append(f"| {p} | {v['baseline_accuracy']:.2f}% | {v['dictionary_accuracy']:.2f}% | {v['difference_pp']:+.2f} pp | {v['baseline_correct']} → {v['dictionary_correct']} / {v['total']} |")
        lines.append('')
    lines += ['## Execution and methodology', '',
              'Command: `.venv/bin/python -m src.run_dictionary_v1_evaluation`.', '',
              'New wrapper: `src/run_dictionary_v1_evaluation.py`. Existing `src/evaluator.py`, `src/normalizer.py`, `src/report_generator.py:_build_summary`, and `src/speaker_evaluator.py:evaluate_speaker_subset` are reused unchanged. The wrapper only selects subsets, validates, and formats new reports.', '',
              'Ground truth for both datasets: `outputs/ground_truth/ground_truth_final.json`, selecting original baseline IDs in memory. Baseline field-level judgments were reproduced exactly before scoring dictionary results.', '',
              'Outputs: four files each under `outputs/dictionary_v1/evaluation_50/` and `outputs/dictionary_v1/evaluation_9/`: combined summary, detailed Markdown report, Direct Gemini evaluation JSON and Sarvam + Gemini evaluation JSON.', '',
              'All requested 50/50/9/9 records were evaluated with five fields each. No missing, unexpected or silently skipped recordings; input and result schemas checked. No evaluation exceptions occurred.', '',
              '## Anomalies and interpretation limits', ''] + ['- ' + x for x in LIMITATIONS]
    changed = [name for name, h in protected.items() if not (PROJECT / name).is_file() or sha(PROJECT / name) != h]
    require(not changed, f'Protected files changed: {changed}')
    lines += ['', f'Integrity check: all {len(protected)} protected pre-existing files match their SHA-256 snapshots. Baseline evaluations, ground truth, dictionary, all extraction artifacts, and existing evaluation/normalization code were untouched. No extraction agents were rerun.']
    save(ROOT / 'dictionary_v1_baseline_comparison.md', '\n'.join(lines))
    save(ROOT / 'dictionary_v1_evaluation_validation.json', {'passed': True, 'checks': validation,
         'protected_files': len(protected), 'modified_files': changed, 'baseline_reproduced_exactly': True,
         'ground_truth': str(GT.relative_to(PROJECT)), 'methodology_unchanged': True, 'extraction_rerun': False})
    print(json.dumps(comparisons, indent=2))


if __name__ == '__main__':
    main()
