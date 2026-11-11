"""Measure verified workprint coverage; never promote a partial edit to final."""
import hashlib,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[5];base=Path(__file__).resolve().parent
story=json.loads((base.parent/'storyboard-retime/storyboard-retimed-reblocked.json').read_text())
# Candidate placements, not listening-approved. Offsets are exact at 30 fps.
segments=[{'name':'opening','start_frame':0,'frames':2550,'qc':'opening-qc.json','file':'opening-incomplete-workprint.mp4'},
 {'name':'island-approach','start_frame':3900,'frames':300,'qc':'island-approach-qc.json','file':'island-approach-incomplete-workprint.mp4'},
 {'name':'island-chapter','start_frame':4200,'frames':900,'qc':'island-chapter-qc.json','file':'island-chapter-incomplete-workprint.mp4'},
 {'name':'island-chapter-2','start_frame':6600,'frames':900,'qc':'island-chapter-2-qc.json','file':'island-chapter-2-incomplete-workprint.mp4'},
 {'name':'coat-section','start_frame':7500,'frames':720,'qc':'coat-section-qc.json','file':'coat-section-incomplete-workprint.mp4'},
 {'name':'genome-comparison','start_frame':5182,'frames':600,'qc':'genome-comparison-qc.json','file':'genome-comparison-incomplete-workprint.mp4'},
 {'name':'stream','start_frame':10620,'frames':480,'qc':'stream-qc.json','file':'stream-incomplete-workprint.mp4'},
 {'name':'hypothesis','start_frame':11100,'frames':420,'qc':'hypothesis-qc.json','file':'hypothesis-incomplete-workprint.mp4'},
 {'name':'verdict-section','start_frame':22770,'frames':720,'qc':'verdict-section-qc.json','file':'verdict-section-incomplete-workprint.mp4'},
 {'name':'final-crossing','start_frame':23490,'frames':390,'qc':'final-crossing-qc.json','file':'final-crossing-incomplete-workprint.mp4'},
 {'name':'genomic-gap','start_frame':18872,'frames':510,'qc':'genomic-gap-qc.json','file':'genomic-gap-incomplete-workprint.mp4'}]
end=math.ceil(story['narration_duration_seconds']*30)
intervals=[]
for x in segments:
 qc=root/'.cache/mammoth-edit'/x['qc'];file=root/'.cache/mammoth-edit'/x['file'];x['built']=False
 if qc.is_file() and file.is_file():
  data=json.loads(qc.read_text());digest=hashlib.sha256(file.read_bytes()).hexdigest();count=data.get('frames',data.get('duration_frames'));expected=data.get('output_sha256',data.get('sha256'))
  x['built']=count==x['frames'] and data.get('fps')==30 and digest==expected
  if x['name']!='opening':
   x['built']=x['built'] and abs(data.get('narration_offset_seconds',-1)*30-x['start_frame'])<1e-4 and data.get('audio_sha256')=='434f2c344b428982edf8b00607b8361c4c45bec95da6ac5330c87428a45c3760'
 if not x['built']:continue
 intervals.append((x['start_frame'],x['start_frame']+x['frames'],x['name']))
# Candidate windows may overlap while alternatives are being compared; coverage is
# the union of verified windows, and overlaps are reported rather than hidden.
intervals.sort();windows=[];overlaps=[]
for a,b,name in intervals:
 if windows and a<windows[-1][1]:
  overlaps.append([a,min(b,windows[-1][1]),windows[-1][2],name]);windows[-1][1]=max(windows[-1][1],b)
  windows[-1][2]=windows[-1][2]+' + '+name
 else:windows.append([a,b,name])
merged=[(a,b) for a,b,_ in windows]
holes=[];cursor=0
for a,b in merged:
 if a>cursor:holes.append([cursor,a])
 cursor=max(cursor,b)
if cursor<end:holes.append([cursor,end])
result={'status':'INCOMPLETE: no final film','timeline_frames':end,'fps':30,'segments':segments,'verified_windows':windows,'verified_windows_frames':merged,'overlap_frames':overlaps,'missing_ranges_frames':holes,'verified_assembled_seconds':sum(b-a for a,b in merged)/30,'uncovered_seconds':sum(b-a for a,b in holes)/30,'note':'Mechanical QC and candidate placements do not mean artistic, science, sound, rights or editorial approval.'}
print(json.dumps(result,indent=2))
