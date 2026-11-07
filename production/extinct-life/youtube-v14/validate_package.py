"""Validate packaging contracts, not virality or scientific expert approval."""
import argparse
import json
from pathlib import Path
from PIL import Image

B = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--require-thumbnails', action='store_true')
args = p.parse_args()
m = json.loads((B/'UPLOAD-METADATA.json').read_text())
c = json.loads((B/'RESEARCH-CORPUS.json').read_text())
t = json.loads((B/'TITLE-OPTIONS.json').read_text())
s = json.loads((B/'../film-v14-directed/schedule.json').read_text())
checks = []
def require(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)
require(len(c['videos']) == c['verified_metadata_count'] == 20, '20 successful public-page records')
require(len({v['video_id'] for v in c['videos']}) == 20, '20 distinct video IDs')
require(sum(v['fetched_views'] >= 1_000_000 for v in c['videos']) == c['fetched_over_one_million_count'] == 15, '15 fetched million-plus comparators, not all twenty')
require(all(v['fetched_views'] >= 0 and v['fetched_likes'] >= 0 and not v['complete_video_watched'] for v in c['videos']), 'honest metadata scope, no false complete-watch flags')
require(len(t) == 15 and all(1 <= len(r['title']) <= 100 and r['characters'] == len(r['title']) for r in t), '15 correctly counted titles, at most 100 characters')
require(m['title'] == t[0]['title'], 'selected launch title matches shortlist B')
require(0 < len(m['description']) <= 5000, 'description within 5000 characters')
require(len(', '.join(m['tags'])) <= 500, 'tags conservatively within 500 characters including separators')
require((B/'DESCRIPTION.txt').read_text() == m['description'], 'copy-paste and JSON descriptions identical')
require((B/m['caption_file']).read_bytes() == (B/'../film-v14-directed/English.srt').read_bytes(), 'included English captions byte-identical to approved master')
require(m['video_language'] == 'en' and m['duration_seconds'] == s['duration_seconds'], 'language and full-film duration agree with final schedule')
ch = m['chapters']
require(len(ch) == len(s['chapters']) == 8 and ch[0]['start_seconds'] == 0, 'eight chapters beginning 00:00')
require(all(x['start_seconds'] == round(y['start_frame']/s['fps']) and x['source_start_frame'] == y['start_frame'] for x,y in zip(ch,s['chapters'])), 'chapter timings derived from actual master schedule')
ends = [x['start_seconds'] for x in ch[1:]] + [m['duration_seconds']]
require(all(end-x['start_seconds'] >= 10 for x,end in zip(ch,ends)), 'ascending chapters, each at least ten seconds')
require(all(x['timestamp']+' '+x['title'] in m['description'] for x in ch), 'all chapter lines in upload description')
require(all(text in m['description'] for text in ['Hiraeth','Undertow','Scott Buckley','CC-BY 4.0','creativecommons.org/licenses/by/4.0/','2022','animated science explainer','complete mastodon genome']), 'music credits and core scientific/reconstruction boundaries retained')
require(not m['public_upload_performed'] and not m['views_guaranteed'], 'no fabricated upload or guaranteed outcome')
assets = []
missing = []
for name in ['thumbnail-B.jpg','thumbnail-B-1280.jpg']:
    f = B/'thumbnails'/name
    if not f.exists():
        missing.append(name)
        continue
    im = Image.open(f)
    expected = (1280,720) if '-1280' in name else (3840,2160)
    require(im.size == expected and im.format == 'JPEG' and im.mode == 'RGB', name+': correct RGB JPEG dimensions')
    require(f.stat().st_size < 2_000_000, name+': under conservative 2 MB export target')
    assets.append({'file':str(f.relative_to(B)),'dimensions':list(im.size),'bytes':f.stat().st_size})
if args.require_thumbnails:
    require(not missing, 'both selected B thumbnail exports present')
result = {'checks_passed':len(checks),'checks':checks,'thumbnail_exports':assets,'missing_thumbnail_exports':missing,'production_status':'complete package exports' if not missing else 'metadata/research complete; artwork selection/export pending','not_certified':['virality','CTR','million views','owner acceptance','full-video creative quality']}
(B/'PACKAGE-VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
