import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from summarize_evidence import metric, summarize


class SummaryTests(unittest.TestCase):
    def test_even_median_and_empty_sample(self):
        rows = [dict(id='a', views=4), dict(id='b', views=10)]
        self.assertEqual(metric(rows)['median_views'], 7)
        self.assertEqual(metric([])['n'], 0)
        self.assertIsNone(metric([])['median_views'])

    def test_long20_is_subset_and_bad_sample_is_rejected(self):
        sample = {'channel_id':'UCx', 'status':'ok', 'ids':['x','y'], 'format_samples': {
            'short_candidate_le60s': [], 'ambiguous_61_to_239s': [], 'long_proxy_ge4min':['x','y']}}
        video = {'id':'x', 'channel_id':'UCx', 'title':'a', 'published_at':'2026-10-22T00:00:00Z', 'duration_seconds':1200, 'views':20}
        data = {'runner_reported_utc':'unverified', 'channels':[{'id':'UCx'}], 'videos':[video,dict(video,id='y',duration_seconds=500,views=10)], 'channel_samples':[sample]}
        stats = summarize(data, 'fixture')['channel_samples'][0]['groups']
        self.assertEqual(stats['long_proxy_ge4min']['median_views'], 15)
        self.assertEqual(stats['long_ge20min_subset']['n'], 1)
        bad = copy.deepcopy(data)
        bad['videos'][0]['published_at'] = '2026-10-23T00:00:00Z'
        with self.assertRaises(ValueError): summarize(bad, 'fixture')
        bad = copy.deepcopy(data)
        bad['videos'][0]['duration_seconds'] = 59
        with self.assertRaises(ValueError): summarize(bad, 'fixture')
        bad = copy.deepcopy(data)
        bad['videos'][0]['channel_id'] = 'UCother'
        with self.assertRaises(ValueError): summarize(bad, 'fixture')
        bad = copy.deepcopy(data)
        bad['channel_samples'][0]['ids'].remove('x')
        with self.assertRaises(ValueError): summarize(bad, 'fixture')


if __name__ == '__main__':
    unittest.main()
