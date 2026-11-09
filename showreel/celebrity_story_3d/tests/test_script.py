import json,unittest,wave
from pathlib import Path
p=Path(__file__).resolve().parents[1]
class TestAudio(unittest.TestCase):
 def test_cues(self):
  cues=json.loads((p/'script.json').read_text());self.assertEqual(len(cues),8)
  for i,c in enumerate(cues):
   with wave.open(str(p/'audio'/f'{i+1:02}.wav')) as f:d=f.getnframes()/f.getframerate()
   self.assertLessEqual(c['start']+d,cues[i+1]['start'] if i+1<len(cues) else 60)
if __name__=='__main__':unittest.main()
