"""Offline integrity checks for the immutable, bounded research receipts."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from summarize_evidence import summarize
RECEIPTS = {
    'youtube_refresh.json': '65505329c5301bac050fb3edaa03429f42d239440c5164abd57648aab8d9c964',
    'search_retry.json': 'bd4af6cd979c48c6615cfba7615008bfd96ef9729304751fd2f2b960fc398dbd',
    'visual_media.json': '1488a24e7332f90ea0dcab10ea89fbce3861dcecdeba7f03ee23b9c7b2ebbd0c',
    'reference_channel_snapshot.json': '68e3cc09e11f54c31ee00a62fccea1d7bd747d4e6b0057732e62426e8a916cda',
    'reference_channel_alternate_snapshot.json': '1d9c397def872d4e136faddf2529e0a2cd8ab2e797fa806ccf0aba8829ea417a',
}


def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


class RecordedEvidenceTests(unittest.TestCase):
    def test_raw_receipts_match_independently_recorded_checksums(self):
        for name, expected in RECEIPTS.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)

    def test_search_retry_only_recovers_one_original_error(self):
        original = load('youtube_refresh.json')['queries']
        retry = load('search_retry.json')['queries']
        fields = ('lane', 'bucket', 'query', 'order', 'duration_filter', 'published_after', 'published_before')
        signature = lambda q: tuple(q[k] for k in fields)
        errors = {signature(q) for q in original if q['status'] != 'ok'}
        recovered = {signature(q) for q in retry if q['status'] == 'ok'}
        self.assertEqual(len(original), 39)
        self.assertEqual(sum(q['status'] == 'ok' for q in original), 3)
        self.assertEqual(len(retry), 4)
        self.assertEqual(len(recovered), 1)
        self.assertTrue(recovered <= errors)
        self.assertEqual(len(errors - recovered), 35)

    def test_saved_channel_summaries_match_the_raw_nonpooled_receipts(self):
        summary = load('evidence_summary.json')
        for saved in summary['snapshots']:
            name = saved['snapshot']
            with self.subTest(name=name):
                self.assertIn(name, RECEIPTS)
                self.assertEqual(summarize(load(name), name), saved)
        self.assertEqual(len(summary['snapshots']), 3)

    def test_high_low_counts_used_in_the_report_match_the_sources(self):
        expected = {
            'youtube_refresh.json': {
                'BTTccTEjjyQ': 30615711, 'e4lhVG25HIw': 31681,
                'NArAKj4zbB8': 38908662, 'qhBUAOIXvbY': 39124,
                'HKYQqRcAeEU': 1100515, 'sW8ZEn4Ce2Y': 69898,
            },
            'reference_channel_snapshot.json': {
                '49_Ph2q6uIM': 18755466, 'TQd2k1pEXp4': 3433942,
                'cxiLIjIxzqY': 577972, 'LHKVUG3ClQA': 202,
                'J-S6d0ECOrU': 2205519,
            },
            'reference_channel_alternate_snapshot.json': {
                'IV2PbYeyaSY': 988825, 'NrTaztG29rw': 913, 'IjqD8SetAeQ': 4396,
            },
        }
        for name, wanted in expected.items():
            videos = {v['id']: v for v in load(name)['videos']}
            for vid, count in wanted.items():
                with self.subTest(name=name, vid=vid):
                    self.assertEqual(videos[vid]['views'], count)

    def test_alternate_channel_identity_has_multiple_video_matches(self):
        data = load('reference_channel_alternate_snapshot.json')
        resolutions = {r['handle'].lower(): r for r in data['handle_resolutions']}
        candidate = resolutions['@oddlyhuma-n']
        similar = resolutions['@oddlyhuman007']
        self.assertEqual(candidate['status'], 'resolved_name_match')
        self.assertNotEqual(candidate['channel_id'], similar['channel_id'])
        videos = {v['id']: v for v in data['videos']}
        expected = {
            'IV2PbYeyaSY': ('DARKEST things ancient humans did to Survive the cold', 515),
            'IjqD8SetAeQ': ('What Did Humans Do Before Jobs Existed?', 431),
            'NrTaztG29rw': ('How Did Tiny Ancient Humans Hunted the Deadliest Predators on Earth?', 338),
        }
        for vid, (title, seconds) in expected.items():
            with self.subTest(vid=vid):
                self.assertEqual(videos[vid]['channel_id'], candidate['channel_id'])
                self.assertEqual(videos[vid]['title'], title)
                self.assertEqual(videos[vid]['duration_seconds'], seconds)
                self.assertNotEqual(videos[vid]['channel_id'], similar['channel_id'])

    def test_growth_receipt_preserves_historical_rows_and_clock_limit(self):
        data = load('growth_historical_receipts.json')
        self.assertEqual(data['trusted_session_date_utc'], '2026-11-05')
        monthly = {row['channel']: row for row in data['monthly_provider_reported_history']}
        self.assertEqual(monthly['3D Eye']['period'], '2026-10')
        self.assertEqual(monthly['3D Eye']['reported_subscriber_change'], 39900)
        self.assertEqual(monthly['3D Eye']['reported_channel_view_change'], 20041365)
        daily = data['daily_provider_reported_history'][0]['rows_reported_utc']
        self.assertEqual([row['date'] for row in daily], ['2026-10-29', '2026-11-04'])
        self.assertTrue(all(row['date'] <= data['trusted_session_date_utc'] for row in daily))
        self.assertIn('later than the trusted session date', data['method'])

    def test_ledger_covers_each_review_index_once(self):
        text = (ROOT / 'ARCHIVE_OBSERVATION_LEDGER.md').read_text(encoding='utf-8')
        seen = []
        for match in re.finditer(r'^\|\s*(\d+(?:\s*[–,]\s*\d+)?)\s*\|', text, re.M):
            spec = match.group(1)
            if '–' in spec:
                first, last = map(int, spec.split('–'))
                seen.extend(range(first, last + 1))
            else:
                seen.extend(map(int, spec.split(',')))
        self.assertEqual(Counter(seen), Counter(range(1, 72)))

    def test_report_local_links_resolve(self):
        for name in ('README.md', 'ARCHIVE_OBSERVATION_LEDGER.md',
                     'SHORTS_VS_LONG_FORM_RESEARCH_ROMAN_URDU.md'):
            text = (ROOT / name).read_text(encoding='utf-8')
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if target.startswith(('https://', 'http://', '#', 'mailto:')):
                    continue
                with self.subTest(file=name, target=target):
                    self.assertTrue((ROOT / target.split('#', 1)[0]).exists())


if __name__ == '__main__':
    unittest.main()
