"""Measure verified workprint coverage; never promote a partial edit to final."""
import hashlib,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[5];base=Path(__file__).resolve().parent
story=json.loads((base.parent/'storyboard-retime/storyboard-retimed-reblocked.json').read_text())
# Candidate placements, not listening-approved. Offsets are exact at 30 fps.
# The placed list is DERIVED, not hand-maintained. Every build writes
# <name>-qc.json with its own narration offset and frame count, so the timeline is read
# back from the artefacts. A hand-written table kept drifting out of sync with what had
# actually been built, which is how two inserts ended up stacked on one window.
# These sections still exist on disk but are not in the cut.
SUPERSEDED={'verdict-section','reversal-section','contact-section'}
segments=[]
for qc in sorted((root/'.cache/mammoth-edit').glob('*-qc.json')):
    name=qc.name[:-len('-qc.json')]
    if name in SUPERSEDED:continue
    try:d=json.loads(qc.read_text())
    except Exception:continue
    if 'narration_offset_seconds' in d and 'frames' in d:
        # Most builds are <name>-incomplete-workprint.mp4; a few older sequences use
        # their own filename, which the qc records as `file` when it differs.
        fname=d.get('file',name+'-incomplete-workprint.mp4')
        segments.append({'name':name,'start_frame':round(d['narration_offset_seconds']*30),
                         'frames':d['frames'],'qc':qc.name,'file':fname})
segments.sort(key=lambda x:x['start_frame'])
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
