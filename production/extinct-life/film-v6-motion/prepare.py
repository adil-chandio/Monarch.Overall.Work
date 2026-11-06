"""Selected native-3D development excerpt, NOT the completed full film."""
import json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent
m=json.loads((B.parent/'film-v3/manifest.json').read_text());c=m['chapters']
first=c[1]['start_frame']+round(c[1]['sentences'][3]['start']*30)
split=c[1]['start_frame']+round(c[1]['sentences'][8]['start']*30)
end=c[1]['start_frame']+round(c[1]['sentences'][11]['start']*30)
last=c[5]['start_frame']+round(c[5]['sentences'][6]['start']*30)
segments=[{'id':'transport','world':'river','start_frame':0,'end_frame':split-first,'source_start_frame':first},{'id':'time-averaging','world':'deposits','start_frame':split-first,'end_frame':end-first,'source_start_frame':split},{'id':'imagined-encounter','world':'living','start_frame':end-first,'end_frame':end-first+last-c[5]['start_frame'],'source_start_frame':c[5]['start_frame']}]
plan={'status':'ACTUAL 3D DEVELOPMENT; NOT FINAL FILM','fps':30,'width':1920,'height':1080,'script_sha256':m['script_sha256'],'total_frames':segments[-1]['end_frame'],'segments':segments,'voice_clips':[{'chapter':'B02','local_start_frame':first-c[1]['start_frame'],'local_end_frame':end-c[1]['start_frame']},{'chapter':'B06','local_start_frame':0,'local_end_frame':last-c[5]['start_frame']}],'rejected_v5_image_assets_used':False,'source':'V4 moving-3D infrastructure and new source animation; no old rendered video','full_film_complete':False}
(B/'schedule.json').write_text(json.dumps(plan,indent=2)+'\n');print(plan['total_frames'],plan['total_frames']/30)
