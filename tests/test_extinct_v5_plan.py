"""Coverage/provenance checks only. These do NOT certify creative quality or listening."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'production/extinct-life/film-v5-plan'
class V5ApprovalPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads((P/'storyboard.json').read_text())
        cls.baseline=json.loads((P.parent/'film-v3/manifest.json').read_text())
        cls.rows=cls.plan['beats']
    def test_approval_gate_still_closed(self):
        self.assertEqual(self.plan['status'],'AWAITING_OWNER_APPROVAL')
        self.assertFalse(self.plan['render_enabled'])
        self.assertFalse(self.plan['new_voice_authorized'])
        self.assertFalse(self.plan['competitor_media_reuse_in_film'])
    def test_approved_master_identity(self):
        self.assertEqual(self.plan['master_sha256'],'42e26885947d4cb9447074f9a63f4504ba4cc87906492703e8ee2f87ba5738f6')
        self.assertEqual(self.plan['master_sha256'],self.baseline['script_sha256'])
    def test_all_native_frames_covered_without_overlap_or_gaps(self):
        cursor=0
        for r in self.rows:
            self.assertEqual(cursor,r['start_frame'])
            self.assertGreater(r['end_frame'],r['start_frame'])
            cursor=r['end_frame']
        self.assertEqual(cursor,13163)
        self.assertEqual(cursor,self.baseline['total_frames'])
        self.assertAlmostEqual(cursor/30,self.plan['duration_seconds'],places=5)
    def test_every_approved_sentence_once_and_unchanged(self):
        for c in self.baseline['chapters']:
            rows=[r for r in self.rows if r['chapter']==c['id']]
            self.assertEqual([i for r in rows for i in r['sentence_indices']],list(range(len(c['sentences']))))
            for r in rows:self.assertEqual(r['narration'],' '.join(c['sentences'][i]['text'] for i in r['sentence_indices']))
    def test_all_proposed_beats_have_directing_fields(self):
        self.assertEqual(len(self.rows),58)
        for r in self.rows:
            for key in ['new_setup','meaningful_action','proposed_short_text','handoff','designed_sound_not_observed_competitor_audio','timing_status']:
                self.assertTrue(r[key].strip())
            self.assertEqual(r['status'],'proposed, not rendered or approved')
        # Unique records are administrative coverage, not proof that rendered scenes will look different.
        self.assertEqual(len({r['composition_id'] for r in self.rows}),58)
    def test_long_beats_have_phrase_linked_internal_development(self):
        for r in self.rows:
            cues=r['internal_phrase_cues']
            if r['duration_seconds']>=12:self.assertGreaterEqual(len(cues),3,r['id'])
            for cue in cues:self.assertIn(cue['spoken_anchor'].casefold(),r['narration'].casefold())
    def test_no_false_full_source_review_claim(self):
        self.assertFalse(self.plan['human_full_competitor_av_review_claimed'])
        evidence=json.loads((ROOT/'docs/research/extinct-production-study/evidence/retrieval.json').read_text())
        self.assertEqual(len(evidence['cases']),8)
        for c in evidence['cases']:
            self.assertEqual(c['status'],'publisher_media_decoded')
            self.assertFalse(c['human_full_video_watched'])
            self.assertFalse(c['human_audio_listened'])
            self.assertEqual(len(c['review_images']),3)
            for image in c['review_images']:self.assertTrue((ROOT/'docs/research/extinct-production-study/evidence'/image).is_file())
    def test_reader_storyboard_has_each_beat_once(self):
        import re
        headings=re.findall(r'^### (V5-\d+) ·', (P/'FULL-STORYBOARD.md').read_text(),re.M)
        self.assertEqual(headings,[r['id'] for r in self.rows])
    def test_no_video_or_audio_in_approval_deliverables(self):
        prohibited={'.mp4','.webm','.wav','.flac','.mp3','.m4a'}
        self.assertFalse(any(p.suffix.lower() in prohibited for p in P.rglob('*')))

if __name__=='__main__':unittest.main()
