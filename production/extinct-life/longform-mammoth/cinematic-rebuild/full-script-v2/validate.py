"""Consistency checks only; these do not certify film, speech or science quality."""
import hashlib, json, re, unittest
from pathlib import Path

B=Path(__file__).resolve().parent
S=json.loads((B/'narration.json').read_text())
T=json.loads((B/'take-timeline.json').read_text())
C=json.loads((B/'caption-data.json').read_text())
Q=json.loads((B/'NARRATION-QC.json').read_text())
TOKEN=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+")
def words(s): return [x.lower() for x in TOKEN.findall(s)]

class DraftTests(unittest.TestCase):
    def test_take_hashes_and_timeline(self):
        self.assertEqual(len(S['sections']),10)
        self.assertEqual([x['id'] for x in S['sections']],[x['id'] for x in T['sections']])
        for item in T['sections']:
            f=B/(item['id']+'.mp3')
            self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),item['sha256'])
            self.assertGreater(item['duration'],1)
        for a,b in zip(T['sections'],T['sections'][1:]):self.assertAlmostEqual(b['start']-a['end'],.8,places=2)
        self.assertAlmostEqual(T['duration_seconds']-T['sections'][-1]['end'],5,places=2)
    def test_unchanged_and_retaken_inputs(self):
        earlier=B.parent/'full-script/take-timeline.json'
        old={s['id']:s['sha256'] for s in json.loads(earlier.read_text())['sections']}
        for x in T['sections']:
            if x['id'] in ('04-coat','09-missing'):self.assertNotEqual(x['sha256'],old[x['id']])
            else:self.assertEqual(x['sha256'],old[x['id']])
    def test_captions_preserve_every_display_token_including_years(self):
        expected=words(' '.join(x['text'] for x in S['sections']))
        actual=words(' '.join(x['text'] for x in C['captions']))
        self.assertEqual(actual,expected)
        self.assertEqual(C['duration_seconds'],T['duration_seconds'])
        self.assertGreater(len(C['captions']),250)
        for cue in C['captions']:
            self.assertGreater(cue['end'],cue['start'])
            self.assertTrue(0<=cue['start']<T['duration_seconds'])
        for a,b in zip(C['captions'],C['captions'][1:]):self.assertGreaterEqual(b['start'],a['start'])
    def test_master_hash_and_limits(self):
        f=B/Q['file']
        self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),Q['sha256'])
        self.assertEqual(Q['expected_duration_seconds'],T['duration_seconds'])
        self.assertLess(Q['true_peak_dbtp'],-1)
        self.assertFalse(Q['music_or_sfx'])
        self.assertFalse(Q['speed_change'])
        self.assertFalse(Q['full_decode_errors'])
    def test_guardrail_concepts_still_present(self):
        text=' '.join(s['text'].lower() for s in S['sections'])
        for phrase in ['fox q one','collagen','archaeological','heterozygosity','homozygosity',
                       'ten generations','microbial','not proven','last question']:
            self.assertIn(phrase,text)

if __name__=='__main__':unittest.main()
