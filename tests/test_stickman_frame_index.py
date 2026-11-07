"""Calibration clips only; these tests are not the unapproved creative experiment."""
import csv,gzip,hashlib,importlib.util,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('forensics',ROOT/'scripts/stickman-frame-forensics.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class FrameIndexTests(unittest.TestCase):
 def run_clip(self,vfr=False):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d);f=p/'calibration.mp4';args=[m.FF,'-v','error','-f','lavfi','-i','testsrc2=size=160x90:rate=24:duration=2']
   if vfr:args+=['-vf','select=not(mod(n\\,3))','-fps_mode','vfr']
   subprocess.run(args+['-c:v','libx264','-pix_fmt','yuv420p',str(f)],check=True)
   before=hashlib.sha256(f.read_bytes()).hexdigest();r=m.inspect(f,'calibration',p,p)
   self.assertEqual(before,hashlib.sha256(f.read_bytes()).hexdigest());self.assertFalse(r['every_frame_human_inspected']);self.assertFalse(r['audio_listening_claimed']);self.assertFalse(r['actual_visual_review_completed'])
   with gzip.open(r['frame_index'],'rt')as z:rows=list(csv.DictReader(z))
   self.assertEqual(len(rows),16 if vfr else 48)
   self.assertAlmostEqual(float(rows[1]['actual_pts_seconds']),.125 if vfr else 1/24,places=5)
   self.assertTrue(all(0<=q['frame']<len(rows)for q in r['adjacent_quoted_frames']))
   self.assertTrue((p/'calibration-adjacent-quotes.jpg').exists())
 def test_cfr_native_frame_count(self):self.run_clip()
 def test_sparse_pts_not_nominal_fps_inference(self):self.run_clip(True)
if __name__=='__main__':unittest.main()
