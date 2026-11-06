"""Offline integrity/scope checks; not retention, performance or semantic proof."""
import csv,hashlib,importlib.util,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
LAB=ROOT/'production/extinct-life/script-lab';F=ROOT/'docs/research/extinct-script-forensics'
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('research',ROOT/'scripts/research-extinct-scripts.py');research=importlib.util.module_from_spec(spec);spec.loader.exec_module(research)
class PacketTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=json.loads((LAB/'master-v2.json').read_text());cls.v=json.loads((LAB/'validation.json').read_text());cls.r=json.loads((ROOT/'docs/research/data/extinct-script-study/retrieval.json').read_text())
 def test_canonical_hash_and_word_count(self):
  self.assertEqual(self.v['master_sha256'],hashlib.sha256((LAB/'master-v2.json').read_bytes()).hexdigest())
  self.assertEqual(sum(len(c['en'].split()) for c in self.s['chapters']),1045)
 def test_eight_paired_blocks(self):
  self.assertEqual([c['id'] for c in self.s['chapters']],[f'B{x:02}' for x in range(1,9)])
  self.assertTrue(all(c['en'] and c['ur'] for c in self.s['chapters']))
 def test_early_reveal_and_numerical_translation_anchors(self):
  c=self.s['chapters'][0];self.assertEqual(c['en'].split()[1],'mastodon');self.assertIn('2022',c['ur']);self.assertIn('بیس لاکھ',c['ur'])
 def test_document_generated_text_matches_canonical_master(self):
  en=(LAB/'ENGLISH-MASTER-v2.md').read_text();pair=(LAB/'OWNER-REVIEW-v2.md').read_text()
  for c in self.s['chapters']:
   self.assertIn(c['en'],en);self.assertIn(c['en'],pair);self.assertIn(c['ur'],pair)
 def test_every_caption_cue_coded_once(self):
  for case in self.r['cases']:
   if case['status']!='timed_captions_retrieved':continue
   beats=json.loads((F/f'{case["key"]}-coded-beats.json').read_text());covered=[i for b in beats for i in range(b['first_cue'],b['last_cue']+1)]
   self.assertEqual(covered,list(range(case['cue_count'])))
 def test_every_publisher_second_present(self):
  for name,duration in [('eons-dna',682),('eons-whales',296)]:
   with (F/f'{name}-every-second.csv').open() as f:rows=list(csv.DictReader(f))
   self.assertEqual([int(r['publisher_second']) for r in rows],list(range(duration)))
   self.assertTrue(all(r['visuals_audio_retention']=='not reviewed / not available' for r in rows))
 def test_no_full_caption_text_or_descriptions_published(self):
  self.assertFalse(self.r['raw_captions_published'])
  for case in self.r['cases']:
   for cue in case.get('cues',[]):self.assertNotIn('text',cue);self.assertIn('text_sha256',cue)
   self.assertLessEqual(len(case.get('brief_opening_excerpt','').split()),13)
  for row in self.r['metadata']['videos']+self.r['metadata']['channels']:
   self.assertNotIn('description',row);self.assertNotIn('snippet',row);self.assertNotIn('tags',row)
 def test_unknown_audio_is_not_estimated_as_measured(self):
  self.assertIsNone(self.v['measured_v2_english_audio_seconds']);self.assertIsNone(self.v['measured_v2_urdu_audio_seconds']);self.assertFalse(self.v['finished_film_review'])
 def test_render_hold_and_incomplete_status(self):
  manifest=json.loads((ROOT/'production/extinct-life/feature-3d/sequence.json').read_text())
  self.assertFalse(manifest['render_enabled']);self.assertFalse(manifest['full_film_complete'])
 def test_blocked_attempt_not_retried_even_with_refresh(self):
  case=research.CASES[2];previous={'checked_at':'2026-11-06','cases':[{'key':case[0],'status':'unavailable','diagnostic':'bot blocked'}]}
  self.assertTrue(research.cached_case(case,previous,refresh=True)['reused_prior_attempt'])
 def test_successful_track_refresh_only_on_opt_in(self):
  case=research.CASES[0];previous={'checked_at':'2026-11-06','cases':[{'key':case[0],'status':'timed_captions_retrieved'}]}
  self.assertTrue(research.cached_case(case,previous)['reused_prior_attempt']);self.assertIsNone(research.cached_case(case,previous,refresh=True))
if __name__=='__main__':unittest.main(verbosity=2)
