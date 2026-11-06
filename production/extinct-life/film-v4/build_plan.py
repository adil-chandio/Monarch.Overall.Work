"""V4 overrides the old three-second-cut rule: 18 story-led continuous sequences.
Acoustic beat windows are retained for narration audit, NOT used as edit points.
"""
import copy,json
from pathlib import Path
B=Path(__file__).resolve().parent;old=json.loads((B.parent/'film-v3/manifest.json').read_text())
# (first sentence, stage, genuinely new physical set/action treatment)
TREATMENTS=[
[(0,'habit','opening-tracks-clearing'),(1,'macro','exposed-granular-trace'),(5,'coast','present-gravel-shore'),(10,'sediment','stratified-ravine-section'),(15,'lab','sample-intake-bench')],
[(0,'habit','living-animal-deadwood-bank'),(3,'river','tributary-and-settling-channel'),(8,'sediment','buried-depositional-cutbank')],
[(0,'macro','weathered-mineral-face-and-release'),(13,'compare','fragment-identification-tray')],
[(0,'compare','reference-control-and-damage-workstations')],
[(0,'habit','mixed-community-open-river-terrace'),(9,'evidence','pollen-leaf-and-sequence-collection')],
[(0,'habit','imagined-delta-takeoff-and-browsing'),(9,'evidence','reconstruction-versus-evidence-table')],
[(0,'evidence','missing-reference-and-complementary-proxies'),(10,'coast','unrecorded-ground-long-view')],
[(0,'coast','handful-scale-gravel-return'),(3,'macro','incomplete-fragment-mineral-ledge'),(5,'habit','last-green-canopy-and-deadwood'),(7,'coast','closing-stony-estuary-pullback')]
]
plan=[]
for ci,c in enumerate(old['chapters']):
 for n,(row,stage,design) in enumerate(TREATMENTS[ci]):
  start=c['start_frame']+(0 if row==0 else round(c['sentences'][row]['start']*30))
  plan.append({'id':f'V4-{len(plan)+1:02}','chapter':ci,'first_sentence':row,'start_frame':start,'world':stage,'design':design,'seed':44001+len(plan)*7919,'action':'one-off narrative progression; no recycled rendered clip'})
for i,p in enumerate(plan):p['end_frame']=plan[i+1]['start_frame'] if i+1<len(plan) else old['total_frames'];p['blend_frames']=min(54,(p['end_frame']-p['start_frame'])//3) if i else 0
# Semantic subject keys within each uninterrupted environment.
def focus_mode(p,row,index):
 stage=p['world'];original=row['mode'];suffix=original.split('-')[1]
 allowed={'river':['shed','decay','flow','source'],'habit':['mastodon','wide','hare','reindeer','goose','rodent','plants','takeoff'],'coast':['wide','ground'],'macro':['trace','fragments','break','damage','loss','cold','bind','hold','mix','archive'],'sediment':['layers','age','clay'],'lab':['sample','extract','control'],'compare':['match','family','missing','damage'],'evidence':['plant','pollen','gaps','combine']}
 if p['chapter']==4 and stage=='habit':
  return 'habit-wide' if index<5 else 'habit-plants' if index==5 else 'habit-mastodon' if index==6 else 'habit-wide'
 if p['chapter']==7 and stage=='habit':return 'habit-plants' if index==5 else 'habit-wide'
 if suffix in allowed[stage]:return stage+'-'+suffix
 fallback={'river':'flow','habit':'wide','coast':'ground' if p['chapter']==7 and index<3 else 'wide','macro':'fragments','sediment':'layers','lab':'sample','compare':'match','evidence':'combine'}
 if stage=='macro' and suffix=='extract':return 'macro-hold'
 return stage+'-'+fallback[stage]
for p in plan:
 p['keys']=[]
 for c in old['chapters']:
  for i,r in enumerate(c['sentences']):
   frame=c['start_frame']+(0 if i==0 else round(r['start']*30))
   if p['start_frame']<=frame<p['end_frame']:p['keys'].append({'frame':frame,'mode':focus_mode(p,r,i),'text':r['text']})
 assert p['keys']
# Do not force an edit at a chapter title when the subject and physical stage continue.
joined=[]
for p in plan:
 if joined and joined[-1]['world']==p['world']:
  joined[-1]['end_frame']=p['end_frame'];joined[-1]['keys'].extend(p['keys']);joined[-1]['design']+='--'+p['design']
 else:joined.append(p)
plan=joined
v=copy.deepcopy(old);v.update(version=4,status='continuous-flow revision; render pending',full_film_complete=False,editing_policy='latest owner correction supersedes <=3 second cuts; semantic beats are not cuts',sequences=plan,forced_three_second_cuts=False,previous_completed_candidate='https://github.com/adil-chandio/Monarch.Overall.Work/releases/tag/extinct-life-v3-42224196920')
(B/'manifest.json').write_text(json.dumps(v,indent=2)+'\n')
compact={k:x for k,x in v.items() if k not in ['chapters','shots']};compact['chapters']=[{k:x for k,x in c.items() if k not in ['word_alignment','voice_sha256']} for c in v['chapters']]
(B/'schedule.json').write_text(json.dumps(compact,separators=(',',':'))+'\n')
print(len(plan),'continuous sequences; durations',[(p['end_frame']-p['start_frame'])/30 for p in plan]);print('No three-second camera resets; unchanged natural narration.')
