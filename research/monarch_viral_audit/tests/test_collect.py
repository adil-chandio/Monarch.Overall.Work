import unittest
from research.monarch_viral_audit.collect_youtube import before_cutoff, chunks, compact_video, duration_seconds

class CollectionTests(unittest.TestCase):
    def test_iso_duration(self):
        self.assertEqual(duration_seconds('PT1M32S'),92)
        self.assertEqual(duration_seconds('PT2H3S'),7203)
        self.assertIsNone(duration_seconds('not-a-duration'))
    def test_fixed_session_cutoff(self):
        self.assertTrue(before_cutoff('2026-11-05T23:59:59Z'))
        self.assertFalse(before_cutoff('2026-11-06T00:00:00Z'))
        self.assertFalse(before_cutoff(None))
    def test_missing_counts_are_not_zero(self):
        row=compact_video({'id':'known','snippet':{},'statistics':{},'contentDetails':{}})
        self.assertIsNone(row['views']);self.assertIsNone(row['likes']);self.assertIsNone(row['comments'])
    def test_batches(self):
        self.assertEqual([len(x) for x in chunks(range(101))],[50,50,1])


class ChannelSummaryTests(unittest.TestCase):
    def test_hidden_subscribers_and_channel_views(self):
        from research.monarch_viral_audit.collect_youtube import compact_channel
        c=compact_channel({'id':'x','statistics':{'subscriberCount':'100','hiddenSubscriberCount':True,'viewCount':'987'},'snippet':{}})
        self.assertIsNone(c['public_subscribers'])
        self.assertEqual(c['public_channel_views'],987)

class FollowupChoiceTests(unittest.TestCase):
    def test_median_excludes_too_new_and_wrong_duration(self):
        from research.monarch_viral_audit.forensic_followup import choose_median
        rows=[
            {'id':'a','views':100,'duration_seconds':20,'published_at':'2026-10-01T00:00:00Z'},
            {'id':'b','views':300,'duration_seconds':20,'published_at':'2026-10-02T00:00:00Z'},
            {'id':'c','views':200,'duration_seconds':20,'published_at':'2026-10-03T00:00:00Z'},
            {'id':'recent','views':1,'duration_seconds':20,'published_at':'2026-11-05T00:00:00Z'},
            {'id':'long','views':1,'duration_seconds':900,'published_at':'2026-10-01T00:00:00Z'},
        ]
        chosen,n=choose_median(rows)
        self.assertEqual(chosen['id'],'c');self.assertEqual(n,3)


class SummaryTests(unittest.TestCase):
    def test_median_and_missing_public_counts(self):
        from research.monarch_viral_audit.summarize import summarize
        broad={'videos':[{'id':'1','views':10},{'id':'2','views':30},{'id':'3','views':None}],
               'channels':[{'id':'c','title':'C'}],
               'queries':[{'group':'exact_celebrity','status':'ok','video_ids':['1','2']}],
               'runner_reported_utc':'clock',
               'upload_samples':[{'channel_id':'c','purpose':'test','status':'ok','ids':['1','2','3']}] }
        data=summarize(broad)
        self.assertEqual(data['samples'][0]['sample_median_views'],20)
        self.assertEqual(data['samples'][0]['views_observed_n'],2)
        self.assertEqual(data['exact_celebrity_unique_ids'],2)

if __name__=='__main__':unittest.main()
