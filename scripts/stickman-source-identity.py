"""Canonical-source candidate lookup for acquired movies, never an automatic identity/3D claim."""
import datetime,json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from yt_intel import client,http
B=Path('docs/research/stickman-study/source-identity');B.mkdir(parents=True,exist_ok=True)
queries=['Gildedguy vs Jade Story 2','Gildedguy Basement Busk Story 3','Gildedguy vs Bog Story 4','Gildedguy Green Eyed Cowboy Story 5','Gildedguy Violet vs Dummy','JzBoy stickman vs king slime','JzBoy stickman vs skeletron','JzBoy stickman vs wall of flesh','JzBoy stickman vs castle crashers','JzBoy stickman vs baldi basics','Hyun LoL StickFigure Spotlight','Terkoiz Rushed 4','Alan Becker Animator vs Animation original']
report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'queries':[],'videos':[],'errors':[],'canonical_identity_not_automatically_assigned':True,'no_3d_or_retention_claim_from_metadata':True};ids=[]
for p in Path('docs/research/stickman-study/archive-footage').glob('results-shard-*.json'):
 for r in json.load(open(p)).get('results',[]):
  if not r.get('media_acquired'):continue
  found=re.search(r'youtube-([\w-]{11})$',r['archive_identifier'])or re.search(r'\[([\w-]{11})\]',r.get('archived_filename',''))
  if found:ids.append(found[1])
ids+=['B1J6Ou4q8vE','VEJWE6cpqw0','KoB2cqmYZNg']
if client.API_KEY:
 for q in queries:
  try:
   d=client._api('search',{'part':'snippet','q':q,'type':'video','maxResults':5,'relevanceLanguage':'en'},'search');got=[r['id']['videoId']for r in d.get('items',[])if r.get('id',{}).get('videoId')];ids+=got;report['queries'].append({'query':q,'video_ids':got})
  except Exception as e:report['errors'].append({'query':q,'error':http.scrub(str(e))})
 ids=list(dict.fromkeys(ids))
 for n in range(0,len(ids),50):
  try:report['videos']+=client.videos(ids[n:n+50]).items
  except Exception as e:report['errors'].append({'batch':n,'error':http.scrub(str(e))})
else:report['errors'].append({'error':'Existing API key not resolved; no credential requested.'})
(B/'candidates.json').write_text(json.dumps(report,indent=2)+'\n');print('Source metadata candidates',len(report['videos']),'errors',len(report['errors']))
