from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.config import GEMINI_MODEL, load_gemini_settings
from src.direct_extractor import DIRECT_EXTRACTION_SYSTEM_INSTRUCTION
from src.gemini_audio_client import GeminiAudioClient
from src.schema import MaintenanceExtraction

OUT = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
REF = OUT / "compact_reference.json"
FROZEN = ROOT / "outputs/dictionary_v2/reference/reference_dictionary.json"
GT = ROOT / "outputs/ground_truth/ground_truth_final.json"
LIST = ROOT / "outputs/dictionary_v1/50_recordings/manifest.json"
EXPECTED_REF = "646fbb6aa44ff46680a1f82b3a37417bfdb2d97b0197790e6b2876456255d7e1"
EXPECTED_FROZEN = "ddbe7b2130e8aca3f588daf7b5fae0eb80411648f9abae6d4d66eacc4842204c"

def sha(p):
    h = hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def main():
    ref = json.loads(REF.read_text(encoding="utf-8"))
    assert sha(REF) == EXPECTED_REF and sha(FROZEN) == EXPECTED_FROZEN
    names = json.loads(LIST.read_text(encoding="utf-8"))["recording_ids"]
    gt = json.loads(GT.read_text(encoding="utf-8"))
    files = [ROOT / "audio_backup" / n for n in names]
    assert len(names) == 50 and all(p.is_file() and p.stat().st_size for p in files)
    assert all(n in gt for n in names)
    concept_ids = {x["reference_id"] for x in ref["concepts"]}
    assert len(ref["concepts"]) == 124 and len(ref["variants"]) == 17
    assert all(x["parent_concept"] in concept_ids for x in ref["variants"])
    context = "\nYou are given a compact company-derived asset/equipment reference. Use it only as contextual vocabulary. Do not treat reference membership as evidence that an asset was mentioned. Extract only information explicitly present in the audio. Do not invent identifiers, substitute unrelated entries, add unsupported components, or split a spoken composite asset into separate assets. Preserve spoken identifiers and quantities exactly.\n<company_asset_reference_json>\n" + json.dumps(ref, ensure_ascii=False, separators=(",", ":")) + "\n</company_asset_reference_json>\n"
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    failures = []
    (OUT / "prompts").mkdir(exist_ok=True)
    manifest = {"experiment_version":"dictionary-v2-compact-direct-gemini-v1","gemini_model":GEMINI_MODEL,"recording_ids":names,"audio_sha256":{n:sha(ROOT/'audio_backup'/n) for n in names},"compact_reference_sha256":sha(REF),"frozen_v2_reference_sha256":sha(FROZEN),"ground_truth_sha256":sha(GT),"prompt_version":"direct_extractor_plus_compact_company_reference_v1","compact_reference_characters":len(json.dumps(ref,ensure_ascii=False,separators=(",",":"))),"compact_reference_estimated_tokens":round(len(json.dumps(ref,ensure_ascii=False,separators=(",",":")))/4),"full_v2_reference_characters":906470,"proxy_variables_removed_for_process":True,"success_count":0,"failure_count":0,"retry_information":{},"api_key_value_recorded":False}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    client = GeminiAudioClient(load_gemini_settings())
    for i, p in enumerate(files, 1):
        print(f"[{i}/50] {p.name}", flush=True)
        audit = OUT/'prompts'/f'{p.name}.json'
        system = DIRECT_EXTRACTION_SYSTEM_INSTRUCTION + context
        audit.write_text(json.dumps({'system_instruction':system,'user_prompt':'Listen to the attached maintenance voice recording. Internally interpret the spoken content in English, then return the five-field JSON extraction.','audio_path':str(p),'audio_sha256':sha(p)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        attempts = 0
        while True:
            attempts += 1
            try:
                result = client.extract_from_audio_file(p, system_instruction=system, user_prompt='Listen to the attached maintenance voice recording. Internally interpret the spoken content in English, then return the five-field JSON extraction.')
                payload = result.model_dump(mode='json'); MaintenanceExtraction.model_validate(payload)
                results[p.name] = payload; manifest['retry_information'][p.name] = attempts - 1
                (OUT/'predictions.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(' success',flush=True); break
            except Exception as e:
                msg = f'{type(e).__name__}: {e}'
                low = msg.lower()
                if attempts < 4 and ('429' in low or 'quota' in low or 'rate' in low):
                    delay = 30 * attempts; print(f' retrying after {delay}s', flush=True); time.sleep(delay); continue
                failures.append({'filename':p.name,'error':msg,'attempts':attempts}); (OUT/'failures.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(' failure',flush=True); break
        manifest['success_count']=len(results); manifest['failure_count']=len(failures); (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if not failures: (OUT/'failures.json').write_text('[]\n',encoding='utf-8')
    if failures: raise SystemExit(f"{len(failures)} recording(s) failed")

if __name__ == '__main__': main()
