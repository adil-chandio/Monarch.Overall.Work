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

if __name__=='__main__':unittest.main()
