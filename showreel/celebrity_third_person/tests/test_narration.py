import json,unittest,wave
from pathlib import Path
P=Path(__file__).resolve().parents[1]
class TestAudioTiming(unittest.TestCase):
 def test_cues_fit(self):
  cues=json.loads((P/'script.json').read_text())
  for i,cue in enumerate(cues):
   with wave.open(str(P/'audio'/f'{i+1:02}.wav')) as f:duration=f.getnframes()/f.getframerate()
   end=cues[i+1]['start'] if i+1<len(cues) else 60
   self.assertLessEqual(cue['start']+duration,end)
if __name__=='__main__':unittest.main()
