"""Full-master contracts; these are not aesthetic, biology or listening certificates."""
import importlib.util,json,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'production/extinct-life/film-v7-full'
m=json.loads((B/'schedule.json').read_text());base=json.loads((B.parent/'film-v3/manifest.json').read_text())
spec=importlib.util.spec_from_file_location('full_material_test',B/'full_sound.py');sound=importlib.util.module_from_spec(spec);spec.loader.exec_module(sound)
class FullMaster(unittest.TestCase):
 def test_approved_full_voice_and_timing(self):
  self.assertEqual(m['total_frames'],13163);self.assertEqual(m['script_sha256'],base['script_sha256']);self.assertEqual(m['chapters'],base['chapters']);self.assertFalse(m['voice_speed_changed']);self.assertEqual(m['voice_id'],'voice-02')
 def test_unbroken_master_coverage(self):
  rows=m['sequences'];self.assertEqual(rows[0]['start_frame'],0);self.assertEqual(rows[-1]['end_frame'],13163)
  for a,b in zip(rows,rows[1:]):self.assertEqual(a['end_frame'],b['start_frame'])
  for q in rows:self.assertGreater(q['end_frame']-q['start_frame'],100)
 def test_semantic_mapping_not_forced_cuts(self):
  coverage=json.loads((B/'coverage.json').read_text());self.assertEqual(len(coverage['beats']),58);self.assertEqual(len(m['sequences']),25)
  for b in coverage['beats']:self.assertTrue(b['implemented_3d_sequences']);self.assertTrue(b['not_a_creative_quality_certificate'])
 def test_genuinely_distinct_science_builders(self):
  src=(B/'science-worlds.mjs').read_text()
  for name in ['fragments','mineral','controls','branch','boundary','gaps','integration','sampleArrival']:self.assertIn('export function '+name+'(',src)
  self.assertNotIn('loadImage',src);self.assertNotIn('VideoTexture',src)
 def test_living_coverage_extends_beyond_the_old_excerpt(self):
  q=next(q for q in m['sequences'] if q['world']=='encounter');self.assertGreater((q['end_frame']-q['start_frame'])/30,39);self.assertIn('[40,-6,4,-15', (B/'worlds.mjs').read_text())
 def test_licenses_are_primary_and_not_procedural_score(self):
  lic=json.loads((B/'MUSIC-LICENSE.json').read_text());self.assertEqual([x['track'] for x in lic['tracks']],['Hiraeth','Undertow']);self.assertFalse(lic['looped_source_audio'])
  for x in lic['tracks']:self.assertTrue(x['official_track_page'].startswith('https://www.scottbuckley.com.au/library/'));self.assertIn('CC-BY 4.0',x['required_credit'])
 def test_full_timeline_material_engine_small_window(self):
  n=4*sound.SR;voice=np.ones(n,np.float32)*.03
  schedule={'sequences':[{'id':'test','world':'river','design':'transport-to-sample','start_frame':0,'end_frame':120}]}
  cues=json.loads((B.parent/'film-v6-motion/action-cues.json').read_text());a,env,report=sound.design(voice,schedule,cues)
  self.assertEqual(a.shape,(n,2));self.assertTrue(np.isfinite(a).all());self.assertTrue(np.all(a[0]==0));self.assertTrue(np.all(a[-1]==0));self.assertEqual(report['events'][0]['start'],2.2);self.assertFalse(report['tonal_oscillator_contacts']);self.assertFalse(report['human_listening_approval'])
 def test_closed_sample_has_no_phantom_pipette_drips(self):
  n=3*sound.SR;schedule={'sequences':[{'id':'test','world':'extraction','design':'sample-to-question','start_frame':0,'end_frame':90}]}
  _,_,r=sound.design(np.zeros(n,np.float32),schedule,{})
  self.assertFalse(any(e['kind']=='water' for e in r['events']))
if __name__=='__main__':unittest.main()
