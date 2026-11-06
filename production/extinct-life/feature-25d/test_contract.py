"""Full-film regressions. These do not certify creative quality or scientific anatomy."""
from pathlib import Path
import json,unittest,hashlib,subprocess
import imageio_ffmpeg
P=Path(__file__).resolve().parent
class FeatureContract(unittest.TestCase):
 def test_full_length_and_contiguous_shots(self):
  p=json.loads((P/'timeline.json').read_text());self.assertTrue(360<=p['total_seconds']<=480)
  self.assertEqual(p['body_frames']+1350,13519);self.assertEqual(len(p['chapters']),8);self.assertEqual(len(p['shots']),40)
  self.assertEqual(p['shots'][0]['start_frame'],0);self.assertEqual(p['shots'][-1]['end_frame'],p['body_frames'])
  for a,b in zip(p['shots'],p['shots'][1:]):self.assertEqual(a['end_frame'],b['start_frame'])
  self.assertGreaterEqual(len(set(s['kind'] for s in p['shots'])),20)

 def test_animation_not_external_scene_plates(self):
  s=(P/'stage.html').read_text()+(P/'scenes.js').read_text()
  for token in ['<img','TextureLoader','data:image','https://','http://','.jpg','.png','Date.now','requestAnimationFrame']:self.assertNotIn(token,s)
  for token in ['function mineral(','function pollen(','function transport(','function deer(','function hare(','function goose(','plateA','plateB','Math.sin','new Path2D']:self.assertIn(token,s)

 def test_scientific_disclosures_and_complete_script(self):
  scripts=json.loads((P/'narration.json').read_text());self.assertEqual(len(scripts),8)
  self.assertTrue(all(len(s['text'].split())>95 for s in scripts))
  s=(P/'scenes.js').read_text()
  for phrase in ['not actual reads','not a reconstructed event','not a DNA-derived portrait','not actual study-site footage','Approximate age','not a measured phylogeny']:self.assertIn(phrase,s)
  self.assertIn('10.1038/s41586-022-05453-y',(P/'SOURCES.md').read_text())

 def test_preserved_isolated_narration(self):
  v=json.loads((P/'voice-provenance.json').read_text());self.assertEqual(len(v['clips']),8)
  for clip in v['clips']:
   pcm=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(P/clip['file']),'-f','s16le','-'],capture_output=True,check=True).stdout
   self.assertEqual(hashlib.sha256(pcm).hexdigest(),clip['pcm_sha256'])

 def test_frame_seek_provenance(self):
  r=json.loads((P/'render-checks.json').read_text());self.assertEqual(len(r['non_monotonic_seek_checks']),40)
  helper=(P/'stage.html').read_text().split('<script>',1)[1].split('</script>',1)[0]
  sha=hashlib.sha256((helper+'\n'+(P/'scenes.js').read_text()).encode()+(P/'timeline.json').read_bytes()).hexdigest()
  self.assertEqual(sha,r['provenance_sha256'])

 def test_actual_final_media(self):
  q=json.loads((P/'QC.json').read_text());self.assertEqual(q['decoded_frames'],13519)
  self.assertEqual(q['native_resolution'],[1920,1080]);self.assertEqual(q['fps'],30)
  self.assertLess(q['bytes'],100*1024*1024);self.assertGreater(q['duration_seconds'],360);self.assertLess(q['duration_seconds'],480)
  self.assertLess(float(q['audio_measurement']['input_tp']),-.5)
  self.assertFalse(any('black_start:' in x for x in q['black_or_freeze_events']))
  self.assertGreaterEqual(q['half_second_samples']['count'],900)
  self.assertGreater(q['half_second_samples']['unique'],q['half_second_samples']['count']*.8)
  self.assertFalse(q['youtube_upload'])

if __name__=='__main__':unittest.main()
