"""Tentatively rebase V2 storyboard onto revised narration; NOT picture lock.

Unchanged takes use exact measured offsets. Two retakes are mapped using
matching words in machine-aligned cues, with interpolation; any interval
intersecting them is explicitly flagged for an editorial rebuild. Automatic
captions are not proof of spoken timing and this does not approve visuals.
"""
from pathlib import Path
from difflib import SequenceMatcher
import bisect,json,re
B=Path(__file__).resolve().parent.parent
old=json.loads((B/'full-script/take-timeline.json').read_text());new=json.loads((B/'full-script-v2/take-timeline.json').read_text())
text=(B/'FULL-FILM-STORYBOARD-V2.md').read_text()
def ts(x):
    parts=x.replace(',','.').split(':');return sum(float(v)*60**i for i,v in enumerate(reversed(parts)))
def srt(file):
    out=[]
    for chunk in re.split(r'\n\s*\n',file.read_text().strip()):
        lines=chunk.splitlines();m=re.match(r'(\d\d:\d\d:\d\d,\d+) --> (\d\d:\d\d:\d\d,\d+)',lines[1]);assert m
        out.append({'start':ts(m[1]),'end':ts(m[2]),'text':' '.join(lines[2:])})
    return out
oc=srt(B/'full-script/English-auto.srt');nc=json.loads((B/'full-script-v2/caption-data.json').read_text())['captions']
def words(cues,section):
    tokens=[]
    for c in cues:
        if not section['start']-.01<=c['start']<=section['end']+.01:continue
        ws=re.findall(r"[a-z0-9]+(?:['-][a-z0-9]+)*",c['text'].lower())
        for i,w in enumerate(ws):tokens.append((w,c['start']+(c['end']-c['start'])*(i+.5)/len(ws)))
    return tokens
mappings={};stats=[]
for a,b in zip(old['sections'],new['sections']):
    assert a['id']==b['id']
    if a['sha256']==b['sha256']:
        assert abs(a['duration']-b['duration'])<.005
        mappings[a['id']]=None;continue
    x,y=words(oc,a),words(nc,b);sm=SequenceMatcher(None,[p[0] for p in x],[p[0] for p in y],autojunk=False)
    points=[(a['start'],b['start'])]
    for block in sm.get_matching_blocks():
        for k in range(block.size):points.append((x[block.a+k][1],y[block.b+k][1]))
    points.append((a['end'],b['end']));points.sort()
    assert all(points[i][0]<=points[i+1][0] and points[i][1]<=points[i+1][1] for i in range(len(points)-1))
    mappings[a['id']]=points
    stats.append({'section':a['id'],'old_words':len(x),'new_words':len(y),'matching_word_anchors':len(points)-2,'method':'auto-aligned word-centre interpolation; changed editorial content requires manual rebuild'})

def map_time(t):
    if t<=old['sections'][0]['start']:return t
    for i,(a,b) in enumerate(zip(old['sections'],new['sections'])):
        if a['start']<=t<=a['end']:
            points=mappings[a['id']]
            if points is None:return t+b['start']-a['start']
            k=min(max(1,bisect.bisect_right([p[0] for p in points],t)),len(points)-1)
            x0,y0=points[k-1];x1,y1=points[k]
            return y0+(y1-y0)*(t-x0)/(x1-x0) if x1>x0 else y0
        if i+1<len(old['sections']) and a['end']<t<old['sections'][i+1]['start']:
            u=(t-a['end'])/(old['sections'][i+1]['start']-a['end'])
            return b['end']+u*(new['sections'][i+1]['start']-b['end'])
    return new['sections'][-1]['end']+(t-old['sections'][-1]['end'])

rows=[]
for line in text.splitlines():
    m=re.match(r'^\|\s*(\d+:\d+(?:\.\d+)?)\s*[–-]\s*(\d+:\d+(?:\.\d+)?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$',line)
    if not m:continue
    start,end=ts(m[1]),ts(m[2]);affected=[a['id'] for a in old['sections'] if mappings[a['id']] is not None and start<a['end'] and end>a['start']]
    rows.append({'old_start':start,'old_end':end,'start':round(map_time(start),3),'end':round(map_time(end),3),'story_visual':m[3],'takeaway':m[4],'retake_overlap':affected,'review':'EDITORIAL REBUILD REQUIRED' if affected else 'provisional; align to human-reviewed speech'})
assert len(rows)==82
assert rows[0]['start']==0 and abs(rows[-1]['end']-new['duration_seconds'])<.005
assert all(x['start']<x['end'] for x in rows)
assert all(abs(x['end']-y['start'])<.005 for x,y in zip(rows,rows[1:]))
result={'status':'AUTOMATIC DRAFT — not a locked edit, not footage','new_narration_duration_seconds':new['duration_seconds'],'method':'unchanged takes: measured offset; retakes: matching automatic caption words and interpolation. Edited sections require redesign; all captions require listening review.','retakes':stats,'blocks':rows}
(B/'storyboard-retime/storyboard-retimed-draft.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('PASS: 82 contiguous provisional blocks; duration',new['duration_seconds'],'seconds; affected blocks',sum(bool(r['retake_overlap']) for r in rows))
for x in stats:print(x)
