"""Read public videos.list metadata for selected IDs; never download video.

The key remains in the process environment/header and is never included in
results or errors. Returned metadata/embedding eligibility is not playback.
"""
import json, os, urllib.error, urllib.parse, urllib.request
from pathlib import Path

IDS = ('aWHX5Awe_TI','8wtQAI_ZZlQ','GHT3RyE9wGI')
ENDPOINT = 'https://www.googleapis.com/youtube/v3/videos'

def normalize(item):
    snippet=item.get('snippet',{})
    content=item.get('contentDetails',{})
    status=item.get('status',{})
    stats=item.get('statistics',{})
    return {
        'id':item.get('id'), 'title':snippet.get('title'),
        'channel':snippet.get('channelTitle'), 'published_at':snippet.get('publishedAt'),
        'duration':content.get('duration'), 'caption_flag':content.get('caption'),
        'definition':content.get('definition'), 'region_restriction':content.get('regionRestriction'),
        'privacy_status':status.get('privacyStatus'), 'embeddable':status.get('embeddable'),
        'youtube_license_field':status.get('license'),
        'player_embed_html_present':bool(item.get('player',{}).get('embedHtml')),
        'view_count':stats.get('viewCount'), 'like_count':stats.get('likeCount'),
        'thumbnail_urls':{k:v.get('url') for k,v in snippet.get('thumbnails',{}).items()},
    }

def run():
    result={'method':'One videos.list request; public metadata only; no audiovisual data or frame access. embeddable is a metadata flag, not verified playback.', 'requested_ids':list(IDS), 'result':'not_attempted'}
    key=os.environ.get('YOUTUBE_API_KEY','')
    if not key:
        result['result']='no_configured_key'
        return result
    query=urllib.parse.urlencode({'part':'snippet,contentDetails,status,statistics,player','id':','.join(IDS),'maxResults':len(IDS)})
    req=urllib.request.Request(ENDPOINT+'?'+query,headers={'x-goog-api-key':key,'Accept':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=30) as resp:data=json.load(resp)
        items=[normalize(x) for x in data.get('items',[])]
        found={x['id'] for x in items}
        result.update(result='ok',videos=items,not_returned=[x for x in IDS if x not in found])
    except urllib.error.HTTPError as e:
        try:error=json.loads(e.read()).get('error',{})
        except Exception:error={}
        result.update(result='api_error',http_status=e.code,error_status=error.get('status','UNKNOWN'))
        result['reasons']=[x.get('reason') for x in error.get('errors',[]) if isinstance(x,dict) and x.get('reason')]
    except Exception as e:result.update(result='request_failed',error_type=type(e).__name__)
    return result

if __name__=='__main__':
    result=run();Path('audit-output').mkdir(exist_ok=True)
    Path('audit-output/youtube-videos-resource-probe.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
