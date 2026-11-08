import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('audio_package',Path(__file__).with_name('package-audio-model-results.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class AudioPackageTests(unittest.TestCase):
 def fixture(self):return {'key':'fixture','status':'model_analysis_complete','encoded_audio_matches_local':True,'decoded_audio_seconds':10,'asr_segments':[{'words':[{'start':0,'end':.5,'text':'fixture','probability':.9},{'start':1,'end':2,'text':'word','probability':.7}]}],'event_windows':[{'start':0,'end':10,'labels':[{'label':'Speech','model_score':.8}]},{'start':5,'end':10,'labels':[{'label':'Speech','model_score':.6}]}]}
 def test_model_metrics_not_perceptual_certification(self):
  s=m.summarize(self.fixture());self.assertEqual(s['asr_word_count'],2);self.assertEqual(s['words_per_full_clip_minute_MODEL_DERIVED'],12);self.assertEqual(s['words_with_model_score_below_0_8'],1);self.assertFalse(s['continuous_perceptual_listening']);self.assertFalse(s['sound_effects_music_verified'])
 def test_overlapping_windows_not_discrete_event_count(self):
  s=m.summarize(self.fixture());label=s['top_candidate_labels_NOT_confirmed'][0];self.assertEqual(s['event_window_count'],2);self.assertEqual(label['label'],'Speech');self.assertEqual(label['peak_model_score'],.8);self.assertEqual(label['number_of_top5_windows'],2)
 def test_bad_timestamp_flagged_not_silently_verified(self):
  f=self.fixture();f['asr_segments'][0]['words'][1]['end']=12
  self.assertEqual(m.summarize(f)['timestamp_review_word_indices'],[1])
if __name__=='__main__':unittest.main()
