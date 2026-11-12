"""Bounded retry of two transient 503 video-input failures, plus overlap checks."""
import datetime as dt
import json
import os
from pathlib import Path
import time
from forensic_followup import gemini_window
from collect_youtube import API, compact_channel

key=os.getenv('GEMINI_API_KEY');ykey=os.getenv('YOUTUBE_API_KEY')
targets=[('O68pHy2gRSw',20,'retry lower-view stickman day'),
         ('G-qnKRnnnAI',31,'retry ordinary Mischief upload'),
         ('fMrGLuNe67U',5,'independent repeated bridge opening'),
         ('F1rTsvWTbZc',5,'independent repeated map opening')]
rows=[]
for vid,end,label in targets:
    for attempt in (1,2):
        r=gemini_window(key,vid,label,0,end,3 if end==5 else 1);r['attempt']=attempt;rows.append(r)
        print(vid,attempt,r['status'],r.get('http_status',''),flush=True)
        if r['status']=='ok' or r.get('http_status')!=503:break
        time.sleep(6)
    time.sleep(2)
channel=None;calls=[]
if ykey:
    a=API(ykey);payload=a.get('channels',part='snippet,contentDetails,statistics',id='UCW8ZE5m7AjINN9EzpxNYGCA',maxResults=1)
    items=(payload or {}).get('items',[]);channel=compact_channel(items[0]) if items else None;calls=a.calls
report={'method':'Bounded retries after transient HTTP 503; model outputs are unverified sampled descriptions, not inspected frames or exact scripts. Overlap consistency does not prove truth.',
        'runner_reported_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'visual_descriptions':rows,
        'monarchs_edit_channel':channel,'api_call_receipts':calls}
Path('/tmp/monarch-visual-retry.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
