"""Re-block the two rewritten chapters against provisional spoken cues.

Shot intent only: this creates no footage. Cues are automatic and must be
listened to before lock. Preserve the original V2 and raw mapped draft.
"""
from pathlib import Path
import json
B=Path(__file__).resolve().parent
src=json.loads((B/'storyboard-retimed-draft.json').read_text())
R={
 '04-coat':[
 (259.45,'A gloved researcher compares two markings on a reconstructed sample display; move with the hand toward a single illustrative hair strand.','Two independent FOXQ1 changes; keep the visual clearly illustrative.'),
 (269.11,'Change the light across the strand, then reveal a fully woolled animal moving.','Satin-like was predicted, not observed; no claim of wool or insulation loss.'),
 (276.0,'The moving animal and a separate sample occupy different depth planes before the sample comes into focus.','A molecular trace is not the living trait.'),
 (283.69,'Return to the animal transferring weight as its trunk moves toward vegetation; keep its environment active.','The genome cannot determine exactly how this animal looked or coped.'),
 (294.16,'Researcher places two distinct sample records side by side; neither is presented as a population census.','The 2017 comparison involved one island and one mainland genome.'),
 (None,'Follow the record edge into the wider 2024 comparison, then allow the landscape to open.','A larger study models a severe bottleneck and recovery while genetic strain persists.')],
 '09-missing':[
 (640.0,'A source-labelled genomic timeline reaches its youngest observation and the camera moves into an unfilled interval.','The final ten generations, around 300 years, are missing from the 2024 dataset.'),
 (647.08,'Keep the youngest sample marker and its calibrated date visible while the timeline extends beyond it.','The youngest sampled genome dates to roughly 4,300 calibrated years before present.'),
 (652.77,'A separate bone record remains in view as the genomic timeline recedes; a researcher turns to the next method.','The genomic gap does not mean that all other evidence is absent.'),
 (663.28,'Transition to a different sample-preparation workflow, with a few distinct specimen contexts rather than an invented collection count.','The 2025 microbial research examined hundreds of mammoth specimens.'),
 (672.4,'Place the wider time span in context, then briefly show a clearly labelled conceptual microbe and comparative record.','Some material is much older than Wrangel; relationship to known pathogens is not a diagnosis.'),
 (679.09,'Return to the researcher and keep the result unresolved; no staged outbreak.','The study did not identify a disease that killed the Wrangel mammoths.'),
 (686.62,'The researcher checks controls against comparative evidence, with continuous room tone.','Authentication, contamination control and living relatives inform interpretation.'),
 (None,'Let the unresolved record move into a tundra horizon as the next chapter begins.','No diagnosis has been established.')]
}
rows=src['blocks'];out=[];i=0
while i<len(rows):
 r=rows[i]
 if not r['retake_overlap']:out.append(r);i+=1;continue
 section=r['retake_overlap'][0];affected=[]
 while i<len(rows) and section in rows[i]['retake_overlap']:
  affected.append(rows[i]);i+=1
 start=affected[0]['start'];end=affected[-1]['end']
 for boundary,visual,takeaway in R[section]:
  stop=end if boundary is None else boundary
  assert start<stop<=end+1e-6,(section,start,stop,end)
  out.append({'start':round(start,3),'end':round(stop,3),'story_visual':visual,'takeaway':takeaway,'retake_overlap':[section],'review':'rewritten against provisional captions; continuous listening and editorial review required'})
  start=stop
 assert abs(start-end)<.001
assert all(a['start']<a['end'] for a in out)
assert all(abs(a['end']-b['start'])<.005 for a,b in zip(out,out[1:]))
assert out[0]['start']==0 and abs(out[-1]['end']-src['new_narration_duration_seconds'])<.005
result={'status':'PROVISIONAL EDITORIAL DRAFT — not locked, not rendered','narration_duration_seconds':src['new_narration_duration_seconds'],'method':'Unchanged material retimed from original block boundaries; the rewritten 04 and 09 sections are reblocked against auto-aligned v2 captions. Listening, creative, scientific and rights review required.','blocks':out}
(B/'storyboard-retimed-reblocked.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('PASS:',len(out),'contiguous provisional blocks including reblocked retakes; still requires listening/picture review')
