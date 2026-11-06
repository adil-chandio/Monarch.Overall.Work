"""Full approved master, not a longer version of the selected development excerpt."""
import json
from pathlib import Path
B=Path(__file__).resolve().parent
m=json.loads((B.parent/'film-v3/manifest.json').read_text());old=json.loads((B.parent/'film-v4/schedule.json').read_text());plan=json.loads((B.parent/'film-v5-plan/storyboard.json').read_text())
def at(ch,s):return m['chapters'][ch]['start_frame']+round(m['chapters'][ch]['sentences'][s]['start']*30)
# Semantic scene changes, not one cut per sentence/beat. The narration itself is unchanged.
rows=[(0,'opening','opening-trace'),(at(0,1),'trace','fragment-not-bone'),(at(0,5),'coast','present-polar-shore'),(at(0,10),'section','formation-and-plant-evidence'),(at(0,15),'extraction','sample-to-question'),(m['chapters'][1]['start_frame'],'shedding','living-material-transfer'),(at(1,3),'river','transport-to-sample'),(at(1,8),'section','accumulation-and-deposit-age'),(at(1,11),'trace','survival-question'),(m['chapters'][2]['start_frame'],'weather','breakage-damage-loss'),(at(2,5),'mineral','adsorption-and-retention'),(at(2,9),'extraction','release-from-mineral'),(at(2,13),'reference','candidate-and-reference-library'),(at(3,5),'controls','alternative-explanations-and-damage'),(at(3,11),'branch','supported-branch-not-genome'),(m['chapters'][4]['start_frame'],'community','wetland-community-and-browsing'),(at(4,9),'proxies','pollen-remains-dna-complement'),(m['chapters'][5]['start_frame'],'encounter','imagined-moving-encounter'),(at(5,9),'boundary','reconstruction-evidence-boundary'),(m['chapters'][6]['start_frame'],'gaps','survival-transport-reference-gaps'),(at(6,6),'integration','complementary-incomplete-records'),(at(6,10),'coast','return-to-handful-scale'),(at(7,3),'trace','incomplete-fragments-return'),(at(7,5),'canopy','green-world-inference-not-recovery'),(at(7,7),'closing','present-shore-and-incomplete-record')]
seq=[]
for i,(start,kind,design) in enumerate(rows):
 end=rows[i+1][0] if i+1<len(rows) else m['total_frames'];keys=[]
 for c in m['chapters']:
  for j,s in enumerate(c['sentences']):
   f=c['start_frame']+round(s['start']*30)
   if start<=f<end:keys.append({'frame':f,'mode':s['mode'],'text':s['text'],'chapter':c['index'],'sentence':j})
 if not keys or keys[0]['frame']>start:
  c=max((c for c in m['chapters'] if c['start_frame']<=start),key=lambda c:c['start_frame']);prior=[s for s in c['sentences'] if c['start_frame']+round(s['start']*30)<=start];s=prior[-1] if prior else c['sentences'][0];keys.insert(0,{'frame':start,'mode':s['mode'],'text':s['text'],'chapter':c['index'],'sentence':max(0,len(prior)-1)})
 seq.append({'id':f'FULL-{i+1:02}','start_frame':start,'end_frame':end,'world':kind,'design':design,'seed':71000+i*997,'chapter':keys[0]['chapter'],'blend_frames':0 if i==0 else 36,'keys':keys})
assert seq[0]['start_frame']==0 and seq[-1]['end_frame']==13163
for a,b in zip(seq,seq[1:]):assert a['end_frame']==b['start_frame']
m.update(version='V7 full moving-3D candidate',status='FULL MASTER SOURCE IMPLEMENTED; RENDER/CREATIVE ACCEPTANCE NOT IMPLIED',full_film_complete=False,sequences=seq,forced_three_second_cuts=False,visual_beats_not_forced_cuts=58,selected_excerpt=False,old_rendered_movies_used=False,generated_scene_plates_used=False)
(B/'schedule.json').write_text(json.dumps(m,indent=2)+'\n')
audit=[]
for b in plan['beats']:
 covered=[s['id'] for s in seq if max(b['start_frame'],s['start_frame'])<min(b['end_frame'],s['end_frame'])]
 assert covered;audit.append({'beat':b['id'],'start_frame':b['start_frame'],'end_frame':b['end_frame'],'implemented_3d_sequences':covered,'not_a_creative_quality_certificate':True})
(B/'coverage.json').write_text(json.dumps({'master_frames':13163,'script_sha256':m['script_sha256'],'voice':'voice-02 unchanged; no time stretch','beats':audit},indent=2)+'\n')
print('FULL MASTER:',m['total_frames'],'frames;',m['duration_seconds'],'seconds;',len(seq),'continuous stages;',len(audit),'semantic beats accounted for')
