import json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.config import load_gemini_settings
from src.direct_extractor import DIRECT_EXTRACTION_SYSTEM_INSTRUCTION
from src.gemini_audio_client import GeminiAudioClient
from src.schema import MaintenanceExtraction
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent; REF=OUT/'combined_reference.json'
def main():
 pred=json.loads((OUT/'predictions.json').read_text(encoding='utf-8')); fails=json.loads((OUT/'failures.json').read_text(encoding='utf-8')); ref=json.loads(REF.read_text(encoding='utf-8')); ctx='\nUse this unified V1+V2 reference only as contextual vocabulary. Reference membership is not evidence. Extract only audio-supported facts. Do not invent identifiers, substitute identifiers, add unsupported components, or split composite assets unless audio supports it. Preserve spoken identifiers/specifications.\n<combined_reference_json>\n'+json.dumps(ref,ensure_ascii=False,separators=(',',':'))+'\n</combined_reference_json>\n'; client=GeminiAudioClient(load_gemini_settings()); remain=[]
 for f in fails:
  p=ROOT/'audio_backup'/f['filename']
  try:
   r=client.extract_from_audio_file(p,system_instruction=DIRECT_EXTRACTION_SYSTEM_INSTRUCTION+ctx,user_prompt='Listen to the attached maintenance voice recording and return the five-field JSON extraction.'); payload=r.model_dump(mode='json'); MaintenanceExtraction.model_validate(payload); pred[p.name]=payload
  except Exception as e: remain.append({'filename':p.name,'error':f'{type(e).__name__}: {e}'})
 (OUT/'predictions.json').write_text(json.dumps(pred,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); (OUT/'failures.json').write_text(json.dumps(remain,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print('predictions',len(pred),'remaining_failures',len(remain))
if __name__=='__main__': main()
