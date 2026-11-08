import csv,hashlib,json,unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'docs/research/zack-original-access/actual-editions-evidence'
class ThirdPassTests(unittest.TestCase):
 def test_ten_audio_inputs_without_manual_listening_claim(self):
  d=json.loads((BASE/'third-pass/audio-model-summary.json').read_text())
  self.assertEqual(d['model_analyzed_sources'],10);self.assertEqual(d['total_asr_words_MODEL_DERIVED'],867);self.assertEqual(d['total_event_windows_MODEL_DERIVED'],69);self.assertEqual(d['continuous_perceptual_listened_sources'],0)
  self.assertTrue(all(r['source_audio_verified'] for r in d['cases']))
  self.assertEqual(Counter(r['input_association_method'] for r in d['cases']),{'exact_encoded_audio_packet_hash':8,'authenticated_local_PCM_transfer':2})
 def test_exact_visual_scopes_not_expanded_to_full_sources(self):
  d=json.loads((BASE/'third-pass/visual-review-status.json').read_text());self.assertEqual(d['native_full_stills_opened_unique'],33);self.assertEqual(d['native_ROI_positions_opened_unique'],227);self.assertEqual(d['unique_positions_opened_in_any_visual_scope'],572)
  with (BASE/'third-pass/manual-coverage.csv').open() as f:rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),9772);self.assertTrue(all(r['source_exhaustive_review_complete']=='False' and r['continuous_audio_listened']=='False' for r in rows))
 def test_original_pcm_upload_bound_to_original_sources_and_recipient(self):
  base=ROOT/'refs/research-audio-bridge';u=json.loads((base/'upload-manifest.json').read_text());recipient=json.loads((base/'receiver.json').read_text());sources={r['key']:r for r in json.loads((ROOT/'refs/research-transfer/manifest.json').read_text())['cases']}
  self.assertFalse(u['local_private_key_used']);self.assertEqual(u['receiver_run_id'],recipient['run_id']);self.assertEqual(hashlib.sha256((base/'receiver-public.pem').read_bytes()).hexdigest(),u['receiver_public_key_sha256'])
  self.assertEqual({r['key'] for r in u['cases']},{'02-stomach','08-ai'})
  for r in u['cases']:
   self.assertEqual(r['source_mp4_sha256'],sources[r['key']]['plaintext_sha256']);e=r['envelope'];self.assertTrue(e['file'].endswith('.enc'));self.assertEqual(hashlib.sha256((base/e['file']).read_bytes()).hexdigest(),e['ciphertext_sha256']);self.assertEqual(e['aad'],u['receiver_run_id']+':'+r['key']+':'+r['pcm_sha256'])
 def test_low_model_scores_remain_visible(self):
  d=json.loads((BASE/'third-pass/audio-model-summary.json').read_text());self.assertEqual(sum(r['words_with_model_score_below_0_8'] for r in d['cases']),44)
  self.assertTrue(all(not r['sound_effects_music_verified'] and not r['word_alignment_manually_verified'] for r in d['cases']))
if __name__=='__main__':unittest.main()
