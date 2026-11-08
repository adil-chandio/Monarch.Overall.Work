import copy,csv,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('contact',Path(__file__).with_name('package-native-contact-review.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ContactReviewTests(unittest.TestCase):
 def setUp(self):
  self.base=ROOT/'docs/research/zack-original-access/actual-editions-evidence';self.notes=json.loads((self.base/'second-pass/observations.json').read_text())
 def test_exact_deduplicated_scope_counts(self):
  rows,s=m.compile_coverage(self.base,self.notes)
  self.assertEqual(len(rows),9772);self.assertEqual(s['native_full_stills_opened_unique'],31);self.assertEqual(s['native_ROI_positions_opened_unique'],102);self.assertEqual(s['unique_positions_opened_in_any_visual_scope'],452)
 def test_no_source_or_audio_completion_claim(self):
  rows,s=m.compile_coverage(self.base,self.notes)
  self.assertFalse(any(x['source_exhaustive_review_complete'] or x['continuous_audio_listened'] for x in rows));self.assertEqual(s['fully_manually_reviewed_sources'],0)
 def test_contiguous_splinter_window(self):
  rows,_=m.compile_coverage(self.base,self.notes)
  actual=[int(r['frame']) for r in rows if r['key']=='03-splinter' and r['native_ROI_opened']]
  self.assertEqual(actual,list(range(686,725)))
 def test_out_of_range_window_rejected(self):
  self.notes['windows'][0]['end_frame_inclusive']=999999
  with self.assertRaisesRegex(ValueError,'Out-of-range'):m.compile_coverage(self.base,self.notes)
 def test_false_complete_attestation_rejected(self):
  self.notes['windows'][0]['every_frame_of_source_reviewed']=True
  with self.assertRaisesRegex(ValueError,'attestation'):m.compile_coverage(self.base,self.notes)
if __name__=='__main__':unittest.main()
