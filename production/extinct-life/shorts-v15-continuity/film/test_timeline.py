import unittest,json,hashlib,re
from pathlib import Path
from PIL import ImageFont
P=Path(__file__).resolve().parent;ROOT=P.parents[3];B=P.parent
class RebuildTests(unittest.TestCase):
 def setUp(self):self.s=json.loads((P/'timeline.json').read_text())
 def test_native_portrait(self):self.assertEqual((self.s['width'],self.s['height'],self.s['fps']),(1080,1920,30))
 def test_complete_duration(self):self.assertEqual(self.s['duration']*self.s['fps'],self.s['total_frames']);self.assertEqual(self.s['total_frames'],1305)
 def test_clock_mapping(self):self.assertAlmostEqual(self.s['duration']*self.s['story_time_scale'],50)
 def test_same_approved_text_not_same_speed_claim(self):
  old=json.loads((ROOT/'production/extinct-life/shorts-v14/film/timeline.json').read_text());self.assertEqual([c['lines'] for c in self.s['captions']],[c['lines'] for c in old['captions']]);self.assertTrue(self.s['voice_speed_changed'])
 def test_caption_clock_mapping(self):
  old=json.loads((ROOT/'production/extinct-life/shorts-v14/film/timeline.json').read_text());r=self.s['story_time_scale']
  for a,b in zip(self.s['captions'],old['captions']):self.assertAlmostEqual(a['start']*r,b['start']);self.assertAlmostEqual(a['end']*r,b['end'])
 def test_caption_order_and_end(self):
  last=0
  for c in self.s['captions']:self.assertGreaterEqual(c['start'],last);self.assertGreater(c['end'],c['start']);self.assertLess(c['end'],self.s['duration']);last=c['end']
 def test_actual_font_width_safe(self):
  f=ImageFont.truetype(str(ROOT/'public/showreel/fonts/Manrope-800.ttf'),56)
  for c in self.s['captions']:
   for line in c['lines']:self.assertLessEqual(f.getlength(line),850)
 def test_context_and_limits_in_actual_scene(self):
  t=(P/'scene.mjs').read_text()
  for marker in ['NORTH GREENLAND','RECONSTRUCTION','SCHEMATIC','NOT A COMPLETE GENOME.','NOT RESURRECTION.','NOT TO SCALE']:self.assertIn(marker,t)
 def test_new_original_sound_and_tempo_disclosure(self):
  d=json.loads((B/'SOUND-DESIGN.json').read_text());self.assertFalse(d['copied_competitor_audio']);self.assertTrue(d['original_music']);self.assertIn('50/43.5',d['voice_retiming'])
 def test_old_assets_and_short_preserved(self):
  d=json.loads((B/'PROTECTED-BASELINES.json').read_text());self.assertGreater(len(d),10)
  for name,sha in d.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),sha,name)
 def test_subtitles_retimed(self):
  text=(B/'English.srt').read_text();times=re.findall(r'(\d\d):(\d\d):(\d\d),(\d\d\d)',text);seconds=[int(h)*3600+int(m)*60+int(s)+int(ms)/1000 for h,m,s,ms in times];self.assertTrue(seconds);self.assertLessEqual(max(seconds),self.s['duration']);self.assertLess(min(seconds),.3)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RebuildTests));(B/'TEST-RESULTS.json').write_text(json.dumps({'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'successful':result.wasSuccessful(),'not_creative_acceptance':True},indent=2)+'\n');raise SystemExit(0 if result.wasSuccessful() else 1)
