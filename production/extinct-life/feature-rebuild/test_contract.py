"""Measurable edit/media checks; no engagement or word-perfect alignment certificate."""
from pathlib import Path
import unittest,json,hashlib,subprocess
import imageio_ffmpeg
P=Path(__file__).resolve().parent
class RebuildContract(unittest.TestCase):
 def test_hard_shot_limit_and_complete_coverage(self):
  p=json.loads((P/'timeline.json').read_text());s=p['shots']
  self.assertEqual(p['frames'],12144);self.assertEqual(len(s),231)
  self.assertEqual(s[0]['start_frame'],0);self.assertEqual(s[-1]['end_frame'],p['frames'])
  for a in s:self.assertGreater(a['end_frame']-a['start_frame'],0);self.assertLessEqual(a['end_frame']-a['start_frame'],90)
  for a,b in zip(s,s[1:]):self.assertEqual(a['end_frame'],b['start_frame'])
  self.assertFalse(p['opening_reused']);self.assertGreaterEqual(len(set(a['subject'] for a in s)),40)
  self.assertTrue(all(a['phrase'] and a['action'] and a['char_end']>a['char_start'] for a in s))

 def test_no_old_video_or_generic_woodland_inputs(self):
  renderer=(P/'render.mjs').read_text();finish=(P/'finish.py').read_text();objects=(P/'objects.js').read_text()
  self.assertNotIn('world(',objects)
  for name in ['Extinct_Life_Opening','Amber_Atlas_Full_1080p']:
   self.assertNotIn(name,renderer+finish)
  for x in ['<img','TextureLoader','data:image','https://','http://','.jpg','.png','Date.now','requestAnimationFrame']:self.assertNotIn(x,objects)

 def test_temporary_voice_and_preserved_meaning(self):
  a=json.loads((P/'narration-ur.json').read_text());self.assertEqual(len(a),8)
  self.assertIn('Original English',(P/'SCRIPT_REVIEW.md').read_text())
  v=json.loads((P/'voice-provenance.json').read_text());self.assertEqual(v['voice_id'],'voice-01')
  for clip in v['clips']:
   pcm=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(P/clip['file']),'-f','s16le','-'],capture_output=True,check=True).stdout
   self.assertEqual(hashlib.sha256(pcm).hexdigest(),clip['pcm_sha256'])

 def test_timing_limits_are_not_hidden(self):
  p=json.loads((P/'timeline.json').read_text());self.assertIn('Not verified',p['timing_method'])
  self.assertTrue(all('not ASR verified' in a['cue_timing'] for a in p['shots']))
  curated=[a for a in p['shots'] if a.get('curated_anchor')];self.assertEqual(len(curated),5)

 def test_render_provenance_and_no_identical_midpoints(self):
  r=json.loads((P/'render-checks.json').read_text());samples=r['non_monotonic_seek_checks']
  self.assertEqual(len(samples),231);self.assertEqual(sum(x['repeat_verified'] for x in samples),24)
  self.assertEqual(len(set(x['sha256'] for x in samples)),231)
  helper=(P/'stage.html').read_text().split('<script>',1)[1].split('</script>',1)[0]
  digest=hashlib.sha256((helper+'\n'+(P/'objects.js').read_text()).encode()+(P/'timeline.json').read_bytes()).hexdigest()
  self.assertEqual(digest,r['provenance_sha256'])

 def test_final_encode(self):
  q=json.loads((P/'QC.json').read_text());self.assertEqual(q['decoded_frames'],12144)
  self.assertEqual(q['fps'],30);self.assertEqual(q['native_resolution'],[1920,1080]);self.assertAlmostEqual(q['duration_seconds'],404.8)
  self.assertLessEqual(q['max_shot_seconds'],3);self.assertEqual(q['original_opening_reused_seconds'],0)
  self.assertLess(float(q['audio_measurement']['input_tp']),-1)
  self.assertFalse(any('black_start:' in e for e in q['black_or_freeze_events']))
  self.assertGreaterEqual(q['half_second_samples']['count'],809);self.assertGreater(q['half_second_samples']['unique'],q['half_second_samples']['count']*.8)
  self.assertFalse(q['youtube_upload'])

if __name__=='__main__':unittest.main()
