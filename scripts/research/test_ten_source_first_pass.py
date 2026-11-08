import copy,importlib.util,json,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('first_pass',Path(__file__).with_name('build-ten-source-first-pass.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=Path(__file__).resolve().parents[2]
class FirstPassTests(unittest.TestCase):
 def setUp(self):
  self.base=ROOT/'docs/research/zack-original-access/actual-editions-evidence'
  self.corpus={'cases':[json.loads(p.read_text()) for p in sorted(self.base.glob('*/evidence.json'))]}
  self.obs=json.loads((ROOT/'docs/research/zack-original-access/first-pass-observations.json').read_text())
 def test_live_evidence_and_coverage_counts(self):
  cases=m.validate(self.corpus,self.obs)
  self.assertEqual(sum(r['decoded_frame_count'] for r in cases),9772)
  self.assertEqual(sum(len(r['sampled_source_frame_ids']) for r in cases),342)
  self.assertEqual(sum(len(v.split(';')) for v in self.obs.values()),332)
 def test_missing_case_rejected(self):
  self.corpus['cases'].pop()
  with self.assertRaisesRegex(ValueError,'exactly ten'):m.validate(self.corpus,self.obs)
 def test_missing_second_note_rejected(self):
  self.obs['01-hearts']=';'.join(self.obs['01-hearts'].split(';')[:-1])
  with self.assertRaisesRegex(ValueError,'per second'):m.validate(self.corpus,self.obs)
 def test_blank_note_rejected(self):
  self.obs['01-hearts']=self.obs['01-hearts'].replace('Open chest and implanted artificial device','')
  with self.assertRaisesRegex(ValueError,'nonempty'):m.validate(self.corpus,self.obs)
 def test_exhaustive_review_claim_rejected(self):
  for flag in ['every_frame_visually_inspected','continuous_audio_listened']:
   corpus=copy.deepcopy(self.corpus);corpus['cases'][0][flag]=True
   with self.assertRaisesRegex(ValueError,'exhaustive'):m.validate(corpus,self.obs)
if __name__=='__main__':unittest.main()
