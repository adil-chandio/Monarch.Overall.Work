"""Guard frozen evidence and the headline descriptive figures; no network needed."""
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from multilingual_youtube import MATURE_END, TRUSTED_END, before_timestamp, format_bucket
from summarize import summarize

EXPECTED_SHA256 = 'b014ab6b9efbb98354f17e798ee5f1bd9d2ea51db87279b75d71b1b95495c72e'


class RecordedMultilingualEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / 'multilingual_snapshot.json').read_bytes()
        cls.data = json.loads(cls.raw)
        cls.summary = json.loads((ROOT / 'multilingual_summary.json').read_text())
        cls.videos = {v['id']: v for v in cls.data['videos']}
        cls.samples = {r['title']: r for r in cls.summary['channel_samples']}

    def test_frozen_receipt_and_reproducible_summary(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), EXPECTED_SHA256)
        self.assertEqual(self.summary, summarize(self.data, EXPECTED_SHA256))
        self.assertEqual(self.data['trusted_session_date'], '2026-11-05')
        self.assertEqual(self.data['published_before'], '2026-11-06T00:00:00Z')
        self.assertIn('not verified Nov 5', self.data['clock_warning'])

    def test_age_windows_use_distinct_reference_times(self):
        maturity = datetime.fromisoformat(MATURE_END.replace('Z', '+00:00'))
        session_start = datetime(2026, 11, 5, tzinfo=timezone.utc)
        session_end = datetime.fromisoformat(TRUSTED_END.replace('Z', '+00:00'))
        runner_start = datetime.fromisoformat(self.data['runner_reported_started_utc'])
        self.assertEqual(session_start - maturity, timedelta(days=13))
        self.assertEqual(session_end - maturity, timedelta(days=14))
        self.assertGreaterEqual(runner_start - maturity, timedelta(days=21, hours=5))
        self.assertLess(runner_start - maturity, timedelta(days=21, hours=6))
        self.assertEqual(self.data['maturity_published_before'], MATURE_END)
        self.assertTrue(all(before_timestamp(v['published_at'], TRUSTED_END)
                            for v in self.data['videos']))

    def test_failed_searches_are_not_coverage(self):
        queries = self.data['queries']
        self.assertEqual(len(queries), 46)
        self.assertEqual(Counter(q['status'] for q in queries),
                         {'error': 3, 'skipped_backoff_circuit': 43})
        self.assertEqual(sum(len(q['attempts']) for q in queries), 9)
        self.assertTrue(all(a['http_status'] == 429 and a['reason'] == 'rateLimitExceeded'
                            for q in queries for a in q['attempts']))
        self.assertTrue(all(not q['video_ids'] for q in queries))
        self.assertFalse(self.data['dynamic_winner_selections'])
        self.assertEqual(Counter(s['status'] for s in self.data['seed_resolution']),
                         {'resolved': 25, 'not_found': 3})
        self.assertEqual(len(self.data['upload_samples']), 25)
        self.assertTrue(all(s['status'] == 'ok' for s in self.data['upload_samples']))
        self.assertEqual((len(self.data['videos']), len(self.data['channels'])), (2987, 32))

    def test_reported_medians_are_channel_specific(self):
        examples = {
            '3D Eye': (155000, 30, 127920.5, 0, None),
            'Engineer Explain in hindi': (502000, 30, 114513.0, 0, None),
            'Professor Of How': (16200000, 4, 4077203.5, 16, 2511918),
            'The Engineer': (223000, 30, 7088, 30, 934),
            'Animagraffs': (1940000, 12, 97409, 30, 3025934),
            'Jared Owen': (4450000, 30, 77860, 30, 5716235.5),
            'Discover Inside': (107000, 30, 3331.5, 4, 191),
            'Sabin Ingeniería Civil': (965000, 2, 52589, 30, 466586.5),
            'JAES Company Español': (50500, 25, 863, 30, 11482),
            'Manual do Mundo': (20600000, 30, 744134, 30, 1101328),
            'JAES Company Português': (635000, 29, 3493, 30, 117085),
            'JAES Company شركة جايس العربية': (11000, 0, None, 14, 17930.5),
            'JAES Company Indonesian': (1340000, 23, 19062, 30, 611433.5),
            'JAES Company Deutsch': (224000, 28, 3349.5, 30, 64752.5),
            'JAES Company Türkçe': (3160, 25, 145, 11, 1514),
            'Geopop': (3030000, 6, 39522, 30, 529099.5),
            'Science Bee': (8860, 2, 839.5, 15, 1655),
        }
        for title, (subs, sn, sm, ln, lm) in examples.items():
            with self.subTest(title=title):
                r = self.samples[title]
                short, long = r['buckets']['short_candidate_le60s'], r['buckets']['long_proxy_ge4min']
                self.assertEqual((r['public_subscribers'], short['sample_n'], short['median_views'],
                                  long['sample_n'], long['median_views']), (subs, sn, sm, ln, lm))
        self.assertEqual(len(self.samples['Animagraffs']['buckets']['long_proxy_ge4min']
                             ['ge20min_sample_ids']), 22)

    def test_selected_video_examples_are_preserved(self):
        examples = {
            'QAeAkiYhid8': (716, 977, '2026-09-25'),
            'fj0l4SC4FYE': (5185, 704, '2025-05-04'),
            'fMrGLuNe67U': (41685031, 48, '2026-02-09'),
            'BTTccTEjjyQ': (30615738, 53, '2026-05-05'),
            'e4lhVG25HIw': (31681, 49, '2026-02-24'),
            'cW8fVC4my1g': (2397028, 25, '2026-10-20'),
            'oeBOgv9iU8s': (73006681, 20, '2025-07-28'),
            'dpUUb32Q0KI': (34202, 14, '2026-09-24'),
            'DxyOpu84-EE': (23636, 26, '2022-10-21'),
            'ac8u1GrHTVw': (3277, 67, '2026-10-18'),
            'RM9BeNFGuls': (7350793, 896, '2023-06-29'),
            '67H2LEar7vM': (4898261, 995, '2023-07-11'),
            'BFzpswX9iRg': (6572005, 928, '2023-10-17'),
            'wp_-bJ5uzLw': (1033445, 945, '2023-10-27'),
            'oyoPVuvKCKI': (40997, 802, '2026-10-01'),
            'ZnSxfhAgLS0': (13697, 307, '2026-07-11'),
            'ZBEA2OBCL9Q': (425, 308, '2026-08-12'),
            'NZLbTuBDhJg': (19471413, 1556, '2022-06-18'),
            'FiyrzMmA1zk': (68657, 2918, '2025-10-01'),
            'HLrBUwNSEo0': (22910496, 1291, '2022-11-17'),
            'BVhUUOnKRns': (464856, 1285, '2025-10-27'),
            'zroVYYAcEV8': (1497493, 1642, '2026-04-11'),
            'k89tQ9cB_hM': (1635947, 1656, '2026-05-18'),
            'Aw4zbVHIKk0': (205350, 1622, '2026-06-19'),
        }
        for vid, (views, seconds, day) in examples.items():
            with self.subTest(vid=vid):
                v = self.videos[vid]
                self.assertEqual((v['views'], v['duration_seconds'], v['published_at'][:10]),
                                 (views, seconds, day))
                self.assertTrue(before_timestamp(v['published_at'], TRUSTED_END))
        self.assertNotIn('oeBOgv9iU8s',
                         self.samples['Engineer Explain in hindi']['buckets']['short_candidate_le60s']['sample_ids'])
        self.assertEqual(format_bucket(self.videos['ac8u1GrHTVw']['duration_seconds']),
                         'ambiguous_61_to_239s')

    def test_report_local_links_and_narration_length(self):
        report = (ROOT / 'MULTILINGUAL_YOUTUBE_RESEARCH_ROMAN_URDU.md').read_text()
        targets = re.findall(r'\]\(([^)]+)\)', report)
        local = [unquote(t.split('#', 1)[0]) for t in targets
                 if not t.startswith(('http://', 'https://', '#'))]
        self.assertTrue(local)
        for target in local:
            self.assertTrue((ROOT / target).exists(), target)
        text = report.split('### 7.2', 1)[1].split('### 7.3', 1)[0]
        narration = ' '.join(line[2:].strip() for line in text.splitlines()
                             if line.startswith('> '))
        words = re.findall(r"[\w]+(?:['’-][\w]+)*", narration)
        self.assertGreaterEqual(len(words), 75)
        self.assertLessEqual(len(words), 125)
        self.assertIn('Gravity moves the water', narration)
        self.assertIn('machinery still operates', narration)
        citations = re.findall(r'\[(\d+)\]\(https?://[^)]+\)', report)
        self.assertGreaterEqual(len(citations), 75)
        self.assertIn('0 successful', report)

    def test_every_summary_item_is_mature_and_in_its_bucket(self):
        for row in self.summary['channel_samples']:
            for bucket, data in row['buckets'].items():
                self.assertLessEqual(data['sample_n'], 30)
                self.assertEqual(len(data['sample_ids']), data['sample_n'])
                for vid in data['sample_ids']:
                    v = self.videos[vid]
                    self.assertEqual(v['channel_id'], row['channel_id'])
                    self.assertTrue(before_timestamp(v['published_at'], MATURE_END))
                    self.assertEqual(format_bucket(v['duration_seconds']), bucket)


if __name__ == '__main__':
    unittest.main()
