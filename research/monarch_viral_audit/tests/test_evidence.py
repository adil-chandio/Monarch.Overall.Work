"""Integrity checks for the published snapshot and numbers in the report."""
import hashlib
import json
from pathlib import Path
import re
import unittest

from research.monarch_viral_audit.collect_youtube import before_cutoff, before_timestamp
from research.monarch_viral_audit.forensic_followup import choose_median
from research.monarch_viral_audit.summarize import summarize

ROOT=Path(__file__).resolve().parents[1]

class EvidenceIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.broad=json.loads((ROOT/'youtube_snapshot.json').read_text())
        cls.focus=json.loads((ROOT/'forensic_followup.json').read_text())
        cls.retry=json.loads((ROOT/'visual_retry.json').read_text())
        cls.texts=json.loads((ROOT/'transcript_receipts.json').read_text())
        cls.growth=json.loads((ROOT/'growth_source_receipts.json').read_text())

    def test_broad_blob_checksum_and_publication_boundary(self):
        digest=hashlib.sha256((ROOT/'youtube_snapshot.json').read_bytes()).hexdigest()
        self.assertEqual(digest,'91bc724983ee9aadf80b91bebe73c45b6053867f7b20802ddbeeef40316d94d4')
        for source in (self.broad,self.focus):
            for video in source['videos']:
                self.assertTrue(before_cutoff(video.get('published_at')),video['id'])

    def test_reported_scope_counts_and_retry_status(self):
        summary=summarize(self.broad,self.focus,self.retry)
        self.assertEqual((summary['successful_searches'],summary['search_count']),(16,16))
        self.assertEqual(summary['search_unique_ids'],393)
        self.assertEqual(summary['resolved_videos_total'],780)
        self.assertEqual(summary['broad_records_at_least_1m_views'],187)
        self.assertEqual(summary['distinct_video_ids_across_snapshots'],881)
        self.assertEqual((summary['model_windows_ok'],summary['model_windows']),(18,20))
        self.assertEqual((summary['retry_model_windows_ok'],summary['retry_model_windows']),(3,4))
        self.assertEqual(summary['distinct_video_ids_with_model_response'],13)
        self.assertEqual(summary['thumbnail_successes'],13)
        self.assertEqual(summary['caption_statuses'],{'blocked_bot_verification':5})

    def test_user_channel_and_counterexample_numbers(self):
        summary=summarize(self.broad,self.focus,self.retry)
        self.assertEqual(summary['monarchs_edit_visible_upload_views_sum'],632357)
        self.assertEqual(summary['monarchs_edit_laser_views'],583297)
        self.assertAlmostEqual(summary['monarchs_edit_laser_share_of_sum'],0.922417)
        sample={v['channel_id']:v for v in summary['samples']}
        self.assertEqual(sample['UCdcJDQafWwwCyDiaYcehm0w']['sample_median_views'],208306)
        self.assertEqual(sample['UCqLSt_CKF-D6UQF8Npu94ZA']['sample_median_views'],46403)
        videos={v['id']:v for v in self.focus['videos']}
        self.assertEqual(videos['NMiz-UKbMw4']['views'],23100781)
        self.assertEqual(videos['CB4TydNS5Hs']['views'],2254)
        self.assertEqual(videos['NMiz-UKbMw4']['title'],videos['CB4TydNS5Hs']['title'])
        self.assertEqual(videos['NMiz-UKbMw4']['duration_seconds'],videos['CB4TydNS5Hs']['duration_seconds'])

    def test_comment_text_and_authors_are_not_committed(self):
        for row in self.focus['comments_sample']:
            self.assertNotIn('comments',row)
            self.assertTrue(row['comment_text_not_committed'])
        self.assertEqual(sum(r.get('returned',0) for r in self.focus['comments_sample']),96)
        neymar=next(r for r in self.focus['comments_sample'] if r['video_id']=='aWHX5Awe_TI')
        self.assertEqual(neymar['mentions_thumbnail_case_insensitive'],5)

    def test_fallback_and_retry_specifics(self):
        videos={v['id']:v for v in self.focus['videos']}
        sample=next(s for s in self.focus['channel_samples'] if s['channel']['id']=='UC0Badcq36RBDHN-e3N1Papg')
        pool=[videos[i] for i in sample['upload_ids'] if i in videos]
        eligible=[v for v in pool if v.get('views') is not None and v.get('duration_seconds') is not None
                  and 8<=v['duration_seconds']<=60 and before_timestamp(v['published_at'],'2026-10-23T00:00:00Z')]
        self.assertEqual(eligible,[])
        chosen,n=choose_median(pool)
        self.assertEqual((chosen['id'],n),('G-qnKRnnnAI',25))
        attempts={r['video_id']:r for r in self.retry['visual_descriptions']}
        self.assertEqual(attempts['O68pHy2gRSw']['status'],'ok')
        self.assertEqual(attempts['G-qnKRnnnAI']['status'],'ok')
        self.assertEqual(attempts['F1rTsvWTbZc']['error_type'],'TimeoutError')

    def test_text_receipts_account_for_selected_videos(self):
        entries=self.texts['entries']
        self.assertEqual(len(entries),self.texts['video_count'])
        self.assertEqual(len({e['video_id'] for e in entries}),25)
        self.assertEqual(sum(e['transcript_section_returned'] for e in entries),20)
        self.assertEqual(sum(not e['transcript_section_returned'] for e in entries),5)
        self.assertEqual(self.texts['no_transcript_section_returned'],5)
        metadata_ids={v['id'] for source in (self.broad,self.focus) for v in source['videos']}
        self.assertTrue({e['video_id'] for e in entries}.issubset(metadata_ids))
        self.assertTrue(all('transcript' not in e for e in entries))

    def test_third_party_historical_arithmetic(self):
        row=self.growth['sources'][0]
        start,end=row['recorded_rows']
        self.assertEqual(end['channel_views']-start['channel_views'],row['public_channel_view_difference'])
        self.assertEqual(end['displayed_public_subscribers']-start['displayed_public_subscribers'],
                         row['displayed_subscriber_step_difference'])
        self.assertEqual(row['public_channel_view_difference'],399202505)
        self.assertEqual(row['displayed_subscriber_step_difference'],80000)
        self.assertEqual(self.growth['trusted_session_date'],'2026-11-05')

    def test_stored_summary_matches_calculation(self):
        stored=json.loads((ROOT/'evidence_summary.json').read_text())
        self.assertEqual(stored,summarize(self.broad,self.focus,self.retry,self.texts,self.growth))

    def test_report_local_links_and_narration_length(self):
        for filename in ('README.md','DEEP_YOUTUBE_NICHE_REPORT_ROMAN_URDU.md'):
            text=(ROOT/filename).read_text()
            for target in re.findall(r'\]\(([^)]+)\)',text):
                if not target.startswith(('http://','https://','#','mailto:')):
                    self.assertTrue((ROOT/target.split('#',1)[0]).exists(),target)
        report=(ROOT/'DEEP_YOUTUBE_NICHE_REPORT_ROMAN_URDU.md').read_text()
        section=report.split('### 6.1 Original English narration — draft, not competitor transcript',1)[1].split('### 6.2',1)[0]
        narration=' '.join(line[1:] for line in section.splitlines() if line.startswith('>'))
        self.assertEqual(len(re.findall(r"[\w’'-]+",narration)),94)

if __name__=='__main__':
    unittest.main()
