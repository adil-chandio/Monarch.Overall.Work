"""Measure verified workprint coverage; never promote a partial edit to final."""
import hashlib,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[5];base=Path(__file__).resolve().parent
story=json.loads((base.parent/'storyboard-retime/storyboard-retimed-reblocked.json').read_text())
# Candidate placements, not listening-approved. Offsets are exact at 30 fps.
segments=[{'name':'opening','start_frame':0,'frames':2550,'qc':'opening-qc.json','file':'opening-incomplete-workprint.mp4'},
 {'name':'hypothesis','start_frame':11100,'frames':420,'qc':'hypothesis-qc.json','file':'hypothesis-incomplete-workprint.mp4'},
 {'name':'genomic-gap','start_frame':18872,'frames':510,'qc':'genomic-gap-qc.json','file':'genomic-gap-incomplete-workprint.mp4'}]
end=math.ceil(story['narration_duration_seconds']*30);cursor=0;holes=[]
for x in segments:
 qc=root/'.cache/mammoth-edit'/x['qc'];file=root/'.cache/mammoth-edit'/x['file'];x['built']=False
 if qc.is_file() and file.is_file():
  data=json.loads(qc.read_text());digest=hashlib.sha256(file.read_bytes()).hexdigest();count=data.get('frames',data.get('duration_frames'));expected=data.get('output_sha256',data.get('sha256'))
  x['built']=count==x['frames'] and data.get('fps')==30 and digest==expected
 if not x['built']:continue
 if x['start_frame']<cursor:raise SystemExit('Overlapping workprint sections')
 if x['start_frame']>cursor:holes.append([cursor,x['start_frame']])
 cursor=x['start_frame']+x['frames']
if cursor<end:holes.append([cursor,end])
result={'status':'INCOMPLETE: no final film','timeline_frames':end,'fps':30,'segments':segments,'missing_ranges_frames':holes,'verified_assembled_seconds':sum(s['frames'] for s in segments if s['built'])/30,'uncovered_seconds':sum(b-a for a,b in holes)/30,'note':'Mechanical QC and candidate placements do not mean artistic, science, sound, rights or editorial approval.'}
print(json.dumps(result,indent=2))
