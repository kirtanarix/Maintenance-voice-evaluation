import json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.config import GEMINI_MODEL,load_gemini_settings
from src.direct_extractor import DIRECT_EXTRACTION_SYSTEM_INSTRUCTION
from src.gemini_audio_client import GeminiAudioClient
from src.schema import MaintenanceExtraction
R=Path(__file__).resolve().parents[3]; O=Path(__file__).resolve().parent
V1=R/'inputs/dictionary/India_Cement_Industry_and_Generic_Maintenance_Dictionary_v1.0.json'; V2=R/'outputs/dictionary_v2/reference/reference_dictionary.json'; C=R/'outputs/dictionary_v2/experiment_direct_gemini_combined/combined_reference.json'; GT=R/'outputs/ground_truth/ground_truth_final.json'; IDS=['sanjaybhai_voice_051.wav','sanjaybhai_voice_052.wav','sanjaybhai_voice_053.wav','julfikar_voice_054.wav','julfikar_voice_055.wav','julfikar_voice_056.wav','jigishbhai_voice_057.wav','jigishbhai_voice_058.wav','jigishbhai_voice_059.wav']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 gt=json.loads(GT.read_text(encoding='utf-8')); refs={'baseline':None,'dictionary_v1':json.loads(V1.read_text(encoding='utf-8')),'dictionary_v2':json.loads(V2.read_text(encoding='utf-8')),'combined_v1_v2':json.loads(C.read_text(encoding='utf-8'))}; files=[R/'audio'/n for n in IDS]; assert len(IDS)==9 and all(p.is_file() and p.stat().st_size for p in files) and all(n in gt for n in IDS)
 man={'experiment_version':'dictionary-v2-9-recordings-four-pipeline-v1','recording_ids':IDS,'audio_sha256':{n:sha(R/'audio'/n) for n in IDS},'ground_truth_sha256':sha(GT),'v1_reference_sha256':sha(V1),'v2_reference_sha256':sha(V2),'combined_reference_sha256':sha(C),'gemini_model':GEMINI_MODEL,'temperature':0.0,'proxy_variables_removed_for_process':True,'pipelines':list(refs)}; O.mkdir(parents=True,exist_ok=True); (O/'manifest.json').write_text(json.dumps(man,indent=2)+'\n',encoding='utf-8'); client=GeminiAudioClient(load_gemini_settings())
 for name,ref in refs.items():
  d=O/name; (d/'prompts').mkdir(parents=True,exist_ok=True); pred={}; fails=[]; context='' if ref is None else '\nUse this reference only as contextual vocabulary, never as evidence. Extract only audio-supported facts; do not invent identifiers, substitute terms, add components, or split composite assets.\n<reference>\n'+json.dumps(ref,ensure_ascii=False,separators=(',',':'))+'\n</reference>\n'
  for p in files:
   system=DIRECT_EXTRACTION_SYSTEM_INSTRUCTION+context; (d/'prompts'/f'{p.name}.json').write_text(json.dumps({'filename':p.name,'audio_sha256':sha(p),'system_instruction':system,'user_prompt':'Listen to the attached maintenance voice recording and return the five-field JSON extraction.','model':GEMINI_MODEL},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
   try:
    x=client.extract_from_audio_file(p,system_instruction=system,user_prompt='Listen to the attached maintenance voice recording and return the five-field JSON extraction.'); payload=x.model_dump(mode='json'); MaintenanceExtraction.model_validate(payload); pred[p.name]=payload
   except Exception as e: fails.append({'filename':p.name,'error':f'{type(e).__name__}: {e}'})
   (d/'predictions.json').write_text(json.dumps(pred,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); (d/'failures.json').write_text(json.dumps(fails,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  man[name]={'success_count':len(pred),'failure_count':len(fails)}; (O/'manifest.json').write_text(json.dumps(man,indent=2)+'\n',encoding='utf-8'); print(name,len(pred),len(fails),flush=True)
if __name__=='__main__': main()
