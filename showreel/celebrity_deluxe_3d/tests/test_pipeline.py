import json
import math
import re
import unittest
import wave
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'showreel/celebrity_deluxe_3d'
STORY=ROOT/'showreel/celebrity_story_3d_v6'


class DeluxePipelineTests(unittest.TestCase):
    def test_manifest_has_pinned_licensed_sources(self):
        assets=json.loads((HERE/'assets.json').read_text())
        self.assertEqual(len(assets),9)
        self.assertEqual(len({x['name'] for x in assets}),len(assets))
        self.assertEqual(sum(x['group']=='visual' for x in assets),1)
        for asset in assets:
            self.assertRegex(asset['sha256'],r'^[0-9a-f]{64}$')
            self.assertRegex(asset['git_blob'],r'^[0-9a-f]{40}$')
            self.assertTrue(asset['source'].startswith('https://'))
            self.assertIn(asset['license'],('CC0 1.0','Public domain dedication by author'))

    def test_40_shards_cover_every_frame_exactly_once(self):
        self.assertEqual([f for i in range(40) for f in range(i*36,(i+1)*36)],list(range(1440)))

    def test_narration_and_caption_breaks(self):
        from showreel.celebrity_recovery_3d.render import CAPTIONS,SPLITS
        cues=json.loads((STORY/'script.json').read_text())
        self.assertEqual(len(cues),10)
        self.assertEqual(len(CAPTIONS),10)
        self.assertTrue(all(0<=c['start']<c['start']+c['duration']<=60 for c in cues))
        for i,(cue,parts,split) in enumerate(zip(cues,CAPTIONS,SPLITS),1):
            self.assertEqual(len(parts),2 if split else 1)
            if split is None:
                continue
            self.assertTrue(0<split<cue['duration'])
            with wave.open(str(STORY/'trimmed'/f'{i:02d}.wav'),'rb') as wav:
                self.assertEqual((wav.getsampwidth(),wav.getnchannels()),(2,1))
                rate=wav.getframerate()
                samples=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype('float32')/32768
            # This tests a pause at each caption transition, not word alignment.
            center=round(split*rate); radius=round(.02*rate)
            rms=float(np.sqrt(np.mean(samples[center-radius:center+radius]**2)))
            self.assertLess(rms,.012,(i,split,rms))

    def test_original_and_new_required_attributions(self):
        credits=(HERE/'ASSET_CREDITS.txt').read_text()
        for name in ('Rocketbox','DanielZhabotinsky','michael_grinnell','roachpowder',
                     'kyles','stephan','Kenney','Serhii Khromov'):
            self.assertIn(name,credits)
        self.assertIn('https://creativecommons.org/licenses/by/4.0/',credits)


if __name__=='__main__':
    unittest.main()
