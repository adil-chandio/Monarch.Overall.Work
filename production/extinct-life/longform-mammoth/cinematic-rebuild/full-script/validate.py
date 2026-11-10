"""Consistency tests for narration planning only; not creative or scientific certification."""
import hashlib, json, re, unittest
from pathlib import Path

B=Path(__file__).resolve().parent
S=json.loads((B/'narration.json').read_text())
T=json.loads((B/'take-timeline.json').read_text())
P=json.loads((B/'planned-shots.json').read_text())

class PlanningTests(unittest.TestCase):
    def test_sections_and_takes(self):
        self.assertEqual(len(S['sections']),10)
        self.assertEqual([x['id'] for x in S['sections']],[x['id'] for x in T['sections']])
        for x in T['sections']:
            f=B/(x['id']+'.mp3')
            self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),x['sha256'])
            self.assertGreater(x['duration'],1)
        for a,b in zip(T['sections'],T['sections'][1:]):self.assertGreaterEqual(b['start'],a['end'])
    def test_shots_continuous_and_planned(self):
        self.assertFalse(P['rendered'])
        self.assertEqual(P['duration_seconds'],T['duration_seconds'])
        self.assertEqual(len(P['shots']),58)
        for x in P['shots']:
            self.assertEqual(x['status'],'planned, not rendered')
            self.assertGreater(x['end'],x['start'])
        for a,b in zip(P['shots'],P['shots'][1:]):self.assertEqual(a['end'],b['start'])
        self.assertEqual(P['shots'][-1]['end'],P['duration_seconds'])
    def test_captions_are_ordered_and_nonempty(self):
        self.assertGreater(len(P['captions']),250)
        for cue in P['captions']:
            self.assertGreater(cue['end'],cue['start'])
            self.assertTrue(re.search(r'[A-Za-z]',cue['text']))
        for a,b in zip(P['captions'],P['captions'][1:]):self.assertGreaterEqual(b['start'],a['start'])
    def test_transcript_covers_the_story(self):
        text=' '.join(s['text'].lower() for s in S['sections'])
        for phrase in ['fox q one','collagen','archaeological','heterozygosity','homozygosity',
                       'ten generations','microbial','not proven','last question']:
            self.assertIn(phrase,text)

if __name__=='__main__':unittest.main()
