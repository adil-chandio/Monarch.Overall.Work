from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import multilingual_youtube as m

class MultilingualPlanTests(unittest.TestCase):
    def test_all_language_lanes_have_both_formats(self):
        plan=m.search_plan()
        self.assertEqual(len(plan),46)
        self.assertEqual(len(m.LANES),17)
        for lang,region,query in m.LANES:
            rows=[q for q in plan if q['lane']==lang and q['order']=='viewCount']
            self.assertEqual({q['duration_filter'] for q in rows},{'short','medium'})
            self.assertTrue(query.strip())
            self.assertTrue(all(q['published_before']==m.TRUSTED_END and q['region_code']==region for q in rows))
        self.assertEqual(len([q for q in plan if q['order']=='date']),12)

    def test_bucket_boundaries_are_honest_proxies(self):
        for seconds,expected in [(None,'unknown'),(0,'unknown'),(60,'short_candidate_le60s'),
                                 (61,'ambiguous_61_to_239s'),(239,'ambiguous_61_to_239s'),
                                 (240,'long_proxy_ge4min')]:
            self.assertEqual(m.format_bucket(seconds),expected)

    def test_metadata_fields_are_not_conflated(self):
        raw={'id':'vid','snippet':{'defaultAudioLanguage':'hi','defaultLanguage':'en'},'contentDetails':{'duration':'PT30S'}}
        row=m.with_separate_language_fields(raw)
        self.assertEqual(row['default_audio_language'],'hi')
        self.assertEqual(row['default_metadata_language'],'en')
        self.assertNotIn('language',row)

    def test_search_circuit_records_skips_without_key_leak(self):
        class Stub(m.ResearchAPI):
            pass
        api=Stub('sensitive',sleep=lambda _:None)
        api.search_circuit_open=True
        result,attempts,status=api.search({'q':'x'})
        self.assertIsNone(result);self.assertEqual(attempts,[])
        self.assertEqual(status,'skipped_backoff_circuit')
        self.assertNotIn('sensitive',str((attempts,status)))

    def test_rate_limit_opens_circuit_after_three_bounded_searches(self):
        def limited(api,resource,**params):
            api.calls.append({'resource':resource,'http_status':429,'reason':'rateLimitExceeded'})
            return None
        api=m.ResearchAPI('sensitive',sleep=lambda _:None)
        with patch.object(m.API,'get',new=limited):
            for _ in range(3):
                payload,attempts,status=api.search({'q':'x'})
                self.assertIsNone(payload);self.assertIsNone(status)
                self.assertEqual(len(attempts),3)
            payload,attempts,status=api.search({'q':'x'})
        self.assertEqual(len(api.calls),9)
        self.assertEqual(status,'skipped_backoff_circuit')
        self.assertEqual(attempts,[])
        self.assertNotIn('sensitive',str(api.calls))

    def test_trusted_cutoff(self):
        self.assertTrue(m.before_timestamp('2026-11-05T23:59:59Z',m.TRUSTED_END))
        self.assertFalse(m.before_timestamp('2026-11-06T00:00:00Z',m.TRUSTED_END))
        self.assertFalse(m.before_timestamp('2026-10-23T00:00:00Z',m.MATURE_END))
        self.assertFalse(m.before_timestamp('2026-10-20T00:00:00',m.TRUSTED_END))

if __name__=='__main__':unittest.main()
