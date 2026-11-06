"""Measure selected fresh speech, force-align words, author phrase-driven coverage.
No time stretching. Alignment is acoustic estimation, not manually verified onsets.
"""
import hashlib,json,math,re,subprocess,wave
from pathlib import Path
import imageio_ffmpeg
from pocketsphinx import Decoder
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2];CACHE=ROOT/'.cache/extinct-v3';CACHE.mkdir(parents=True,exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe();FPS=30
master=ROOT/'production/extinct-life/script-lab/master-v3.json'
m=json.loads(master.read_text())
# One authored semantic choice per spoken sentence, not a keyword slideshow.
PLANS=[
'habit-mastodon coast-ground coast-ground macro-trace macro-fragments coast-wide habit-mastodon coast-wide habit-mastodon habit-wide lab-sample evidence-plant macro-archive habit-mastodon macro-trace lab-extract',
'habit-mastodon river-shed river-decay river-flow river-flow macro-fragments river-flow river-source sediment-layers sediment-layers sediment-age macro-trace',
'macro-trace macro-break macro-damage macro-loss macro-cold macro-bind sediment-clay macro-bind macro-hold lab-extract macro-fragments macro-mix macro-trace compare-match compare-family',
'compare-match compare-match compare-family compare-missing compare-family lab-control compare-match lab-control compare-damage macro-damage compare-damage macro-fragments lab-control habit-wide',
'habit-hare habit-reindeer habit-goose habit-rodent habit-mastodon habit-plants habit-mastodon coast-wide habit-wide evidence-plant evidence-pollen lab-sample habit-mastodon habit-wide evidence-plant',
'habit-wide habit-mastodon habit-takeoff habit-plants habit-wide habit-wide river-flow habit-mastodon habit-wide sediment-layers lab-sample habit-wide evidence-plant',
'evidence-gaps evidence-gaps macro-loss river-source compare-missing evidence-gaps evidence-plant evidence-pollen evidence-gaps evidence-combine habit-wide coast-wide',
'coast-ground coast-ground sediment-layers macro-fragments macro-trace habit-wide habit-mastodon coast-wide habit-wide coast-wide evidence-plant coast-wide coast-wide sediment-layers lab-sample coast-wide']

def tokens(text):
 text=text.lower().replace('’',"'").replace('2022','twenty twenty two')
 return re.findall(r"[a-z]+(?:'[a-z]+)?",text)
chapters=[];global_frame=0;allshots=[]
for idx,c in enumerate(m['chapters']):
 source=BASE/'voice'/f'{c["id"]}.flac';wavpath=CACHE/f'{c["id"]}.wav'
 subprocess.run([FF,'-y','-loglevel','error','-i',str(source),'-ac','1','-ar','16000',str(wavpath)],check=True)
 with wave.open(str(wavpath)) as w:raw=w.readframes(w.getnframes());duration=w.getnframes()/w.getframerate()
 decoder=Decoder(logfn='/dev/null');decoder.add_word('kap','K AE P',False);decoder.add_word("greenland's",decoder.lookup_word('greenland')+' Z',True)
 words=tokens(c['en']);missing=[w for w in words if not decoder.lookup_word(w)]
 if missing:raise ValueError(missing)
 decoder.set_align_text(' '.join(words));decoder.start_utt();decoder.process_raw(raw,full_utt=True);decoder.end_utt()
 aligned=[{'word':re.sub(r'\(\d+\)$','',s.word),'start':s.start_frame/100,'end':(s.end_frame+1)/100} for s in decoder.seg() if s.word not in ['<sil>','<s>','</s>','[SPEECH]','[NOISE]']]
 if [a['word'] for a in aligned]!=words:raise ValueError(f'Alignment word mismatch {c["id"]}')
 sentences=re.split(r'(?<=[.!?])\s+',c['en']);plans=PLANS[idx].split();assert len(plans)==len(sentences)
 nframes=math.ceil((duration+.36)*FPS);localshots=[];offset=0;sentence_rows=[]
 for j,(text,plan) in enumerate(zip(sentences,plans)):
  n=len(tokens(text));first=aligned[offset]['start'];last=aligned[offset+n-1]['end'];offset+=n
  sentence_rows.append({'text':text,'mode':plan,'start':first,'end':last})
 # Boundary at next spoken sentence; the preceding shot owns the natural pause.
 for j,row in enumerate(sentence_rows):
  first=0 if j==0 else round(row['start']*FPS)
  last=round(sentence_rows[j+1]['start']*FPS) if j+1<len(sentence_rows) else nframes
  # Subdivide long phrases at acoustically estimated word onsets, never >3 seconds.
  word_frames=[round(a['start']*FPS) for a in aligned if first<round(a['start']*FPS)<last]
  start=first;coverage=0
  while start<last:
   if last-start<=90:end=last
   else:
    choices=[f for f in word_frames if start+48<=f<=start+86]
    end=min(choices,key=lambda f:abs(f-(start+76))) if choices else min(start+84,last)
   localshots.append({'id':f'{c["id"]}-S{len(localshots)+1:02}','start_frame':start,'end_frame':end,'duration_seconds':(end-start)/FPS,'mode':row['mode'],'sentence':j,'sentence_start':row['start'],'coverage':coverage,'narration':row['text'],'source':'manual sentence subject + acoustic word-boundary subdivision'})
   start=end;coverage+=1
 chapter={'id':c['id'],'index':idx,'voice':str(source.relative_to(ROOT)),'voice_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'voice_id':'voice-02','voice_seconds':duration,'frames':nframes,'start_frame':global_frame,'duration_seconds':nframes/FPS,'word_alignment':aligned,'sentences':sentence_rows,'shots':localshots}
 chapters.append(chapter)
 for s in localshots:allshots.append({**s,'start_frame':s['start_frame']+global_frame,'end_frame':s['end_frame']+global_frame,'chapter':idx})
 global_frame+=nframes
 print(c['id'],round(duration,3),nframes,len(localshots),flush=True)
manifest={'script_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'fps':FPS,'width':1920,'height':1080,'voice_id':'voice-02','voice_language':'en','voice_speed_changed':False,'alignment_method':'PocketSphinx forced word alignment, not human-verified; sentence-cut intervals acoustically estimated','total_frames':global_frame,'duration_seconds':global_frame/FPS,'narration_seconds':sum(c['voice_seconds'] for c in chapters),'chapters':chapters,'shots':allshots,'status':'authored and measured; render/QC pending','full_film_complete':False,'youtube_upload_authorized':False}
assert 360<=manifest['duration_seconds']<=480
assert all(0<s['duration_seconds']<=3 for s in allshots)
(BASE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Browser-facing compact scene schedule, no raw audio duplication.
(BASE/'schedule.json').write_text(json.dumps({k:v for k,v in manifest.items() if k not in ['chapters','shots']} | {'chapters':[{k:v for k,v in c.items() if k not in ['word_alignment','voice_sha256']} for c in chapters]},ensure_ascii=False,separators=(',',':'))+'\n')
provenance={'voice_id':'voice-02','audition_selected_this_session':True,'master_sha256':manifest['script_sha256'],'generated_from':'exact English chapter texts in master-v3.json','time_stretching':False,'total_natural_voice_seconds':manifest['narration_seconds'],'clips':[{k:c[k] for k in ['id','voice','voice_sha256','voice_seconds']} for c in chapters]}
(BASE/'voice-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print('Measured film window',manifest['duration_seconds'],'shots',len(allshots))
