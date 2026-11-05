"""Read-only YouTube Data API inventory. Key stays in the runner environment."""
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request
import urllib.error

OUT = pathlib.Path('audit-output')
OUT.mkdir(exist_ok=True)
key = os.environ.get('YOUTUBE_API_KEY', '')
if not key:
    print('No YouTube API secret is available to this workflow.', file=sys.stderr)
    sys.exit(1)

def api(resource, **params):
    params['key'] = key
    url = 'https://www.googleapis.com/youtube/v3/' + resource + '?' + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        # Never log a URL: it contains the API key.
        detail = json.loads(e.read().decode('utf-8', 'replace')).get('error', {})
        reasons = [x.get('reason', '') for x in detail.get('errors', [])]
        raise RuntimeError(f'{resource}: HTTP {e.code}, reasons={reasons}') from None

try:
    result = api('channels', part='snippet,contentDetails,statistics,brandingSettings', forHandle='monarchsedit')
    if not result.get('items'):
        raise RuntimeError('No channel found for @monarchsedit')
    channel = result['items'][0]
    playlist = channel['contentDetails']['relatedPlaylists']['uploads']
    uploads = []
    token = None
    while True:
        args = dict(part='snippet,contentDetails', playlistId=playlist, maxResults=50)
        if token:
            args['pageToken'] = token
        page = api('playlistItems', **args)
        uploads.extend(page.get('items', []))
        token = page.get('nextPageToken')
        if not token:
            break
    ids = [x['contentDetails']['videoId'] for x in uploads]
    videos = []
    for i in range(0, len(ids), 50):
        result = api('videos', part='snippet,contentDetails,statistics,status', id=','.join(ids[i:i+50]), maxResults=50)
        videos.extend(result.get('items', []))
    comments = {}
    for video in videos:
        vid = video['id']
        try:
            page = api('commentThreads', part='snippet', videoId=vid, maxResults=100, textFormat='plainText', order='relevance')
            comments[vid] = [{'text': item['snippet']['topLevelComment']['snippet'].get('textDisplay', ''),
                              'likes': item['snippet']['topLevelComment']['snippet'].get('likeCount', 0),
                              'replies': item['snippet'].get('totalReplyCount', 0)} for item in page.get('items', [])]
        except RuntimeError as exc:
            comments[vid] = {'unavailable': str(exc)}
    out = {'channel': channel, 'uploads': uploads, 'videos': videos, 'comments': comments,
           'note': 'Public data only; private videos and YouTube Studio analytics are not returned.'}
    (OUT / 'channel.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Channel: {channel['snippet']['title']}; uploads listed: {len(uploads)}; video details: {len(videos)}")
except Exception as exc:
    # Network errors may carry the key-bearing URL; log only safe exception class.
    print(f'Audit failed: {exc if isinstance(exc, RuntimeError) else type(exc).__name__}', file=sys.stderr)
    sys.exit(1)
