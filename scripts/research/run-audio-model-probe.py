"""Capture bounded runner failures without publishing media/transcripts/credentials."""
import datetime,json,re,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=root/'refs/research-audio-models';out.mkdir(parents=True,exist_ok=True)
p=subprocess.run([sys.executable,str(root/'scripts/research/zack-audio-model-analysis.py')],capture_output=True,text=True)
# The research script prints only case status/counts, never recognized words or audio.
text=p.stdout+'\n'+p.stderr
text=re.sub(r'https?://\S+','[URL]',text)
text=re.sub(r'(?i)(token|authorization|api[_-]?key)\s*[:=]\s*\S+',r'\1=[REDACTED]',text)
record={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'production_hold':True,'process_exit_code':p.returncode,'bounded_status_log':text[-7000:],'perceptual_audio_listening':False,'warning':'Exit zero or a successful workflow is not proof that ten cases were analyzed; inspect the encrypted-results manifest counts.'}
(out/'runner-status.json').write_text(json.dumps(record,indent=2)+'\n')
print('Research process exit:',p.returncode,'; bounded diagnostic saved, no raw audio/transcript printed')
sys.exit(p.returncode)
