from __future__ import annotations
import json, re, time, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.config import PROJECT_ROOT, load_gemini_settings
from src.gemini_audio_client import GeminiAudioClient
from src.direct_extractor import DIRECT_EXTRACTION_SYSTEM_INSTRUCTION
from src.schema import MaintenanceExtraction

OUT=Path(__file__).resolve().parent; PRED=OUT/'predictions.json'; FAIL=OUT/'failures.json'; REF=PROJECT_ROOT/'outputs/dictionary_v2/reference/reference_dictionary.json'; BASE=PROJECT_ROOT/'outputs/dictionary_v1/50_recordings/manifest.json'
PROMPT='Listen to the attached maintenance voice recording and return exactly ONE JSON OBJECT, never an array, with exactly these five keys and no others: assets, quantities, hours, dates, approval_intent. Use null when absent. Extract only what is spoken.'
def main():
    pred=json.loads(PRED.read_text(encoding='utf-8')); failures=json.loads(FAIL.read_text(encoding='utf-8')) if FAIL.exists() else []
    names=json.loads(BASE.read_text(encoding='utf-8'))['recording_ids']; missing=[n for n in names if n not in pred]; ref=json.loads(REF.read_text(encoding='utf-8'))
    ctx='\nCompany-derived reference context only; reference membership is not evidence of occurrence. Do not invent or substitute values.\n<company_asset_reference_json>\n'+json.dumps(ref,ensure_ascii=False,separators=(',',':'))+'\n</company_asset_reference_json>\n'
    client=GeminiAudioClient(load_gemini_settings())
    for name in missing:
        p=PROJECT_ROOT/'audio_backup'/name; system=DIRECT_EXTRACTION_SYSTEM_INSTRUCTION+ctx; audit=OUT/'prompts'/f'{name}.json'; audit.parent.mkdir(parents=True,exist_ok=True); audit.write_text(json.dumps({'system_instruction':system,'user_prompt':PROMPT,'audio_path':str(p)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); last=None
        for attempt in range(1,4):
            try:
                obj=client.extract_from_audio_file(p,system_instruction=system,user_prompt=PROMPT); payload=obj.model_dump(mode='json'); MaintenanceExtraction.model_validate(payload); pred[name]=payload; failures=[f for f in failures if f['filename']!=name]; PRED.write_text(json.dumps(pred,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); FAIL.write_text(json.dumps(failures,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(name,'success'); break
            except Exception as e:
                last=f'{type(e).__name__}: {e}'; delay=0
                m=re.search(r'retry in ([0-9.]+)s',str(e),re.I)
                if m: delay=min(float(m.group(1))+2,90)
                elif '429' in str(e): delay=30*attempt
                if attempt<3 and delay: print(name,'retry',attempt,'delay',delay,flush=True); time.sleep(delay)
        else:
            failures=[f for f in failures if f['filename']!=name]+[{'filename':name,'error':last}]; FAIL.write_text(json.dumps(failures,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(name,'failed')
    print(json.dumps({'predictions':len(pred),'failures':len(failures),'remaining':[f['filename'] for f in failures]},indent=2))
if __name__=='__main__': main()
