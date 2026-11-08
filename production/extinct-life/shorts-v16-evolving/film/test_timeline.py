"""Editorial, preservation and actual export gates; not an aesthetic-quality score."""
from pathlib import Path
import hashlib,json,re,unittest
ROOT=Path(__file__).resolve().parents[4]
B=ROOT/'production/extinct-life/shorts-v16-evolving'
OLD=ROOT/'production/extinct-life/shorts-v15-continuity'
S=json.loads((B/'film/timeline.json').read_text())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
class Editorial(unittest.TestCase):
 def test_native_duration(self):
  self.assertEqual((S['width'],S['height'],S['fps'],S['total_frames']),(1080,1920,30,1305));self.assertEqual(S['duration']*S['fps'],S['total_frames'])
 def test_selected_narration_and_captions_preserved(self):
  old=json.loads((OLD/'film/timeline.json').read_text());self.assertEqual(S['captions'],old['captions']);self.assertEqual(S['voice_starts'],old['voice_starts']);self.assertEqual(S['story_time_scale'],old['story_time_scale']);self.assertFalse(S['voice_speed_changed_vs_v15']);self.assertEqual((B/'English.srt').read_bytes(),(OLD/'English.srt').read_bytes())
 def test_captions_bounded_nonoverlapping(self):
  last=0
  for c in S['captions']:
   self.assertGreaterEqual(c['start'],last);self.assertLess(c['start'],c['end']);self.assertLessEqual(c['end'],S['duration']);last=c['end']
 def test_ten_distinct_scene_objects_no_returned_set(self):
  source=(B/'film/scene.mjs').read_text();pairs=re.findall(r"s=(\w+);id='([^']+)'",source)
  self.assertEqual(len(pairs),10);self.assertEqual(len({s for s,i in pairs}),10);self.assertEqual(len({i for s,i in pairs}),10);self.assertEqual([i for s,i in pairs],['opening','sampling','lab-reveal','shedding','binding','alignment','ecosystem','limits','verification','investigation'])
 def test_no_science_result_or_genome_claim(self):
  source=(B/'film/scene.mjs').read_text()
  for label in ['NOT A COMPLETE GENOME','NOT A RESURRECTED ANIMAL','ILLUSTRATION','SCHEMATIC','IMAGINED RECONSTRUCTION','PROTECTED DOES NOT MEAN PERFECT']:
   self.assertIn(label,source)
  self.assertIn("text('?'",source)
 def test_voice_sources_preserved(self):
  p=json.loads((B/'VOICE-PROVENANCE.json').read_text());self.assertFalse(p['new_speech_synthesis_called'])
  for name,h in p['source_recordings_sha256'].items():self.assertEqual(digest(ROOT/name),h)
 def test_existing_movies_and_thumbnail_preserved(self):
  for name,h in json.loads((B/'PROTECTED-BASELINES.json').read_text()).items():self.assertEqual(digest(ROOT/name),h,name)
 def test_original_sound_cues_not_retimed_voice(self):
  sound=json.loads((B/'SOUND-DESIGN.json').read_text());self.assertFalse(sound['new_tempo_change_from_v15']);self.assertFalse(sound['copied_competitor_audio']);self.assertEqual(len(sound['additional_original_synthetic_events']),3)
@unittest.skipUnless((B/'QC.json').exists(),'Final export not built yet')
class ActualExport(unittest.TestCase):
 def setUp(self):self.q=json.loads((B/'QC.json').read_text())
 def test_exact_final_movie(self):
  d=json.loads((B/'DELIVERY.json').read_text());p=ROOT/d['file'];self.assertEqual(digest(p),d['sha256']);self.assertEqual(d['sha256'],self.q['file_sha256']);self.assertEqual(p.stat().st_size,d['bytes'])
 def test_source_binding(self):
  build=hashlib.sha256((B/'film/scene.mjs').read_bytes()+(B/'film/timeline.json').read_bytes()).hexdigest();self.assertEqual(build,self.q['source_build_sha256'])
  for name,h in self.q['source_sha256'].items():self.assertEqual(digest(ROOT/name),h,name)
 def test_actual_decode(self):
  q=self.q;self.assertEqual(q['decoded_frames'],1305);self.assertTrue(q['all_frames_nonblack']);self.assertEqual(q['native_3d_resolution'],[1080,1920]);self.assertFalse(q['interpolated_frames']);self.assertFalse(q['upscaled_3d'])
 def test_full_coverage_and_no_reentry(self):
  a=self.q['assembly'];runs=a['actual_scene_runs'];self.assertEqual(len(runs),10);self.assertEqual(len({r['scene'] for r in runs}),10);self.assertEqual(runs[0]['from'],0);self.assertEqual(runs[-1]['to'],1305)
  for x,y in zip(runs,runs[1:]):self.assertEqual(x['to'],y['from'])
  self.assertEqual(a['retained_v15_frames'],[0,323]);self.assertEqual(a['new_native_render_frames'],[323,1305]);self.assertEqual(a['new_native_frame_count'],982);self.assertFalse(a['looped_or_repeated_edit_segments'])
 def test_actual_aac_loudness(self):
  a=self.q['encoded_audio'];self.assertGreater(float(a['input_i']),-19);self.assertLess(float(a['input_i']),-13);self.assertLessEqual(float(a['input_tp']),-.5)
 def test_no_fabricated_perceptual_or_three_times_approval(self):
  self.assertFalse(self.q['full_perceptual_listening_certified']);self.assertFalse(self.q['assembly']['quality_multiplier_verified']);self.assertFalse(self.q['youtube_published']);self.assertFalse(self.q['competitor_exhaustive_study_complete'])
if __name__=='__main__':unittest.main(verbosity=2)
