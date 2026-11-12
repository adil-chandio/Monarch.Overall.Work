"""Recalculate descriptive audit figures from the checked-in API snapshots.

Numbers are cumulative public counters for selected videos, not audience growth,
retention, a platform-wide hit rate, or projections for a new channel.
"""
from __future__ import annotations
import json
from pathlib import Path
import statistics

HERE=Path(__file__).resolve().parent


def summarize(broad,follow=None):
    vm={v['id']:v for v in broad['videos']};cm={c['id']:c for c in broad['channels']}
    qids={vid for q in broad['queries'] for vid in q['video_ids']}
    selections=[]
    for sample in broad['upload_samples']:
        videos=[vm[i] for i in sample['ids'] if i in vm]
        views=[v['views'] for v in videos if v['views'] is not None]
        selections.append({'channel_id':sample['channel_id'],
            'channel_title':cm.get(sample['channel_id'],{}).get('title'),
            'purpose':sample['purpose'],'sample_status':sample['status'],
            'playlist_ids':len(sample['ids']),'resolved_videos':len(videos),
            'views_observed_n':len(views),'sample_median_views':statistics.median(views) if views else None,
            'sample_min_views':min(views) if views else None,'sample_max_views':max(views) if views else None})
    exact=[q for q in broad['queries'] if q['group']=='exact_celebrity']
    edit=next((s for s in broad['upload_samples'] if s['channel_id']=='UCW8ZE5m7AjINN9EzpxNYGCA'),None)
    edit_views=[vm[i]['views'] for i in edit['ids'] if i in vm and vm[i]['views'] is not None] if edit else []
    laser=vm.get('fFG5M8Gkxbo',{}).get('views')
    result={'method':'Descriptive, non-random public API snapshots. Cutoff and clock warning in source JSON.',
      'broad_runner_reported_utc':broad['runner_reported_utc'],
      'search_count':len(broad['queries']),'successful_searches':sum(q['status']=='ok' for q in broad['queries']),
      'search_unique_ids':len(qids),'resolved_videos_total':len(broad['videos']),'resolved_channels_total':len(broad['channels']),
      'selected_channel_samples':len(selections),'exact_celebrity_queries':len(exact),
      'exact_celebrity_unique_ids':len({i for q in exact for i in q['video_ids']}),
      'samples':selections,
      'monarchs_edit_visible_upload_views_sum':sum(edit_views) if edit_views else None,
      'monarchs_edit_visible_upload_count_with_views':len(edit_views),
      'monarchs_edit_laser_views':laser,
      'monarchs_edit_laser_share_of_sum':round(laser/sum(edit_views),6) if laser and edit_views and sum(edit_views) else None}
    if follow is not None:
        result['followup_runner_reported_utc']=follow['runner_reported_utc']
        result['followup_channel_samples']=len(follow['channel_samples'])
        result['model_windows']=len(follow['visual_descriptions'])
        result['model_windows_ok']=sum(r['status']=='ok' for r in follow['visual_descriptions'])
        result['model_target_videos']=len({r['video_id'] for r in follow['visual_descriptions']})
        result['thumbnail_successes']=sum(t['status']=='ok' for t in follow['thumbnail_receipts'])
        result['caption_statuses']={s:sum(t['status']==s for t in follow['caption_attempts']) for s in sorted({t['status'] for t in follow['caption_attempts']})}
    return result


def main():
    broad=json.loads((HERE/'youtube_snapshot.json').read_text())
    fp=HERE/'forensic_followup.json'
    follow=json.loads(fp.read_text()) if fp.exists() else None
    data=summarize(broad,follow)
    (HERE/'evidence_summary.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k!='samples'},indent=2))

if __name__=='__main__':main()
