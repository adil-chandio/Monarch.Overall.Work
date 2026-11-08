"""Test YT-Navigator's pinned transcript dependency; no media download.
Only statuses/counts are stored; never assume captions are visual evidence.
"""
import json
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
rows=[]
for name,vid in [('DusanFC Neymar','aWHX5Awe_TI'),('LV Animation','8wtQAI_ZZlQ'),('Stickman Snooze','GHT3RyE9wGI'),('public control Me at the zoo','jNQXAC9IVRw')]:
    row={'name':name,'video_id':vid}
    try:
        segments=YouTubeTranscriptApi.get_transcript(vid)
        row.update(status='retrieved',segment_count=len(segments))
    except Exception as e:
        row.update(status='unavailable',error_type=type(e).__name__)
    rows.append(row)
    print(json.dumps(row))
Path('audit-output').mkdir(exist_ok=True)
Path('audit-output/yt-navigator-transcript-probe.json').write_text(json.dumps({'method':'youtube-transcript-api 0.6.3 on a fresh unauthenticated GitHub runner; captions only, not video frame analysis; a missing transcript can be due to absent captions or access failure.', 'rows':rows},indent=2)+'\n')
