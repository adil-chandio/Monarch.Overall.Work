from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from summarize import sample_channel, summarize


def vid(id, published, duration, views, channel='UCtest'):
    return {'id':id,'url':'https://www.youtube.com/watch?v='+id,'title':id,'channel_id':channel,
            'published_at':published,'duration_seconds':duration,'views':views,
            'default_audio_language':None,'default_metadata_language':None}

class SummaryTests(unittest.TestCase):
    def test_samples_are_capped_separated_and_mature(self):
        vids={}
        for i in range(35):
            x=vid('s'+str(i),'2026-10-01T00:00:00Z',45,i);vids[x['id']]=x
        for x in [vid('long','2026-10-02T00:00:00Z',600,800),
                  vid('verylong','2026-10-02T00:00:00Z',1200,1_000_000),
                  vid('ambiguous','2026-10-02T00:00:00Z',70,2),
                  vid('too_new','2026-10-23T00:00:00Z',45,1_000_000),
                  vid('wrong_channel','2026-10-02T00:00:00Z',45,3,'UCother')]:vids[x['id']]=x
        s={'channel_id':'UCtest','ids':list(vids)+['s1','missing']}
        result,skipped=sample_channel(s,vids)
        a=result['short_candidate_le60s'];b=result['long_proxy_ge4min']
        self.assertEqual(a['sample_n'],30);self.assertEqual(a['median_views'],14.5)
        self.assertEqual(b['sample_n'],2);self.assertEqual(b['ge20min_sample_ids'],['verylong'])
        self.assertEqual(result['ambiguous_61_to_239s']['sample_n'],1)
        self.assertEqual(skipped['not_mature'],1);self.assertEqual(skipped['channel_mismatch'],1)
        self.assertEqual(skipped['duplicate_ids'],1);self.assertEqual(skipped['missing_metadata'],1)

    def test_sample_cap_uses_publication_time_not_playlist_order(self):
        d={str(i):vid(str(i),f'2026-09-{i:02}T00:00:00Z',45,i) for i in range(1,11)}
        result,_=sample_channel({'channel_id':'UCtest','ids':list(d)},d,cap=3)
        self.assertEqual(result['short_candidate_le60s']['sample_ids'],['10','9','8'])
        self.assertEqual(result['short_candidate_le60s']['median_views'],9)

    def test_missing_views_do_not_become_zero(self):
        d={'x':vid('x','2026-01-01T00:00:00Z',45,None)}
        result,skipped=sample_channel({'channel_id':'UCtest','ids':['x']},d)
        self.assertEqual(result['short_candidate_le60s']['sample_n'],0)
        self.assertIsNone(result['short_candidate_le60s']['median_views'])
        self.assertEqual(skipped['missing_or_invalid_views'],1)

if __name__=='__main__':unittest.main()
