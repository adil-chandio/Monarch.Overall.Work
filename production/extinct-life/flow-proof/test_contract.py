"""Delivery regressions only. These tests do NOT grade artistic/editing quality."""
from pathlib import Path
import hashlib,json,re,subprocess,unittest
import imageio_ffmpeg
import numpy as np
BASE=Path('production/extinct-life/flow-proof');MOVIE=Path('deliverables/Extinct_Life_24s_Continuity_Proof_1080p.mp4');FF=imageio_ffmpeg.get_ffmpeg_exe()

class Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q=json.loads((BASE/'QC.json').read_text())
    def test_actual_video_stream(self):
        p=subprocess.run([FF,'-hide_banner','-i',str(MOVIE),'-map','0:v:0','-c:v','copy','-progress','pipe:1','-f','null','-'],capture_output=True,text=True,check=True)
        self.assertIn('1920x1080',p.stderr);self.assertIn('30 fps',p.stderr)
        self.assertEqual(int(re.findall(r'^frame=(\d+)',p.stdout,re.M)[-1]),720)
        self.assertIn('Duration: 00:00:24.00',p.stderr)
    def test_natural_speed_selected_voice(self):
        v=json.loads((BASE/'voice-provenance.json').read_text());self.assertEqual(v['duration_seconds'],23.36)
        p=subprocess.run([FF,'-v','error','-i',str(BASE/'voice.flac'),'-f','s16le','-acodec','pcm_s16le','-'],capture_output=True,check=True)
        self.assertEqual(hashlib.sha256(p.stdout).hexdigest(),v['pcm_sha256'])
        self.assertFalse(self.q['voice_time_stretched'])
    def test_shot_windows_and_persistent_action(self):
        self.assertEqual(len(self.q['shots']),8)
        for i,s in enumerate(self.q['shots']):
            self.assertEqual(s['first_frame'],i*90);self.assertEqual(s['last_frame'],i*90+89);self.assertLessEqual(s['duration_seconds'],3)
        states=json.loads(Path('.cache/extinct-flow/states.json').read_text())
        for state in states:
            self.assertGreater(state['camera'][2],state['hero'][2]);self.assertTrue(np.isfinite(state['focus']))
            delta=np.array(state['camera'])-state['hero'];self.assertGreater(1.28*delta[0]+3.53*delta[2],0)
        for previous,current in zip(states,states[1:]):
            if current['t']-previous['t']<.04:
                self.assertLess(np.linalg.norm(np.array(current['hero'])-previous['hero']),.04)
        # Bound fragment's world position stays fixed across the later cuts.
        settled=[s['hero'] for s in states if s['t']>=15]
        self.assertTrue(all(np.allclose(p,settled[0]) for p in settled))
    def test_encoded_sample_variation_not_creative_quality(self):
        p=subprocess.run([FF,'-v','error','-i',str(MOVIE),'-vf','fps=2,scale=160:90','-an','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True)
        a=np.frombuffer(p.stdout,np.uint8).reshape(-1,90,160,3);self.assertEqual(len(a),48)
        self.assertEqual(len({hashlib.sha256(f.tobytes()).digest() for f in a}),48)
        self.assertGreater(float(a.mean(axis=(1,2,3)).min()),12)
    def test_encoded_audio_and_file_identity(self):
        self.assertLessEqual(abs(float(self.q['audio_measurement']['input_i'])+16),.5)
        self.assertLessEqual(float(self.q['audio_measurement']['input_tp']),-1.0)
        self.assertEqual(hashlib.sha256(MOVIE.read_bytes()).hexdigest(),self.q['sha256'])
        self.assertEqual(MOVIE.stat().st_size,self.q['bytes'])

if __name__=='__main__':unittest.main(verbosity=2)
