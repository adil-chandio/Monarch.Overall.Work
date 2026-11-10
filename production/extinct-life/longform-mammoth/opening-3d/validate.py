"""Structural checks for the 3D opening. Passing these is not a certification of creative quality."""
import json
import unittest
from pathlib import Path

B = Path(__file__).resolve().parent
S = json.loads((B / 'timeline.json').read_text())
ALIGN = json.loads((B / 'caption-alignment.json').read_text())
SOUND = json.loads((B / 'SOUND-DESIGN.json').read_text())
SCENE = (B / 'scene.mjs').read_text()


class Opening3DTests(unittest.TestCase):
    def test_duration_and_frames(self):
        self.assertEqual((S['width'], S['height'], S['fps']), (1920, 1080, 30))
        self.assertEqual(S['duration'], 60.0)
        self.assertEqual(S['total_frames'], 1800)

    def test_shots_are_contiguous_and_cover_the_film(self):
        shots = S['shots']
        self.assertEqual(shots[0]['start'], 0)
        self.assertEqual(shots[-1]['end'], S['duration'])
        for a, b in zip(shots, shots[1:]):
            self.assertEqual(a['end'], b['start'])
        for s in shots:
            self.assertGreater(s['end'] - s['start'], 0.8)

    def test_real_3d_is_used(self):
        # scene.mjs imports three.js as a namespace under the alias `T`
        for token in ['WebGLRenderer(', "import * as T from 'three'", 'InstancedMesh', 'TubeGeometry', 'ShaderMaterial']:
            self.assertIn(token, SCENE)

    def test_no_external_model_or_media_imports(self):
        for forbidden in ['.glb', '.gltf', 'loadTexture(', 'TextureLoader', 'FBXLoader', 'GLTFLoader']:
            self.assertNotIn(forbidden, SCENE)

    def test_captions_are_aligned_to_the_narration(self):
        cues = S['captions']
        self.assertGreater(len(cues), 20)
        for c in cues:
            self.assertLess(c['start'], c['end'])
            self.assertLessEqual(c['end'], S['duration'])
            self.assertLessEqual(len(c['text'].split()), 8)
        for a, b in zip(cues, cues[1:]):
            self.assertLessEqual(a['end'], b['start'] + 1e-6)
        self.assertIn('forced alignment', ALIGN['alignment_caveat'])

    def test_corrected_coat_and_population_language(self):
        text = ' '.join(c['text'] for c in S['captions']).lower()
        self.assertIn('predicted a silky coat', text)
        self.assertIn('later study of ancient genomes', text)
        self.assertNotIn('gene that makes wool', text)
        self.assertNotIn('lost its insulation', text)
        self.assertIn('final ten generations: no sampled genomes', SCENE)

    def test_caption_offset_matches_voice_start(self):
        self.assertAlmostEqual(S['captions'][0]['start'] - ALIGN['cues'][0]['start'],
                               SOUND['narration_start_seconds'], places=2)

    def test_narration_is_not_speed_changed(self):
        self.assertFalse(SOUND['speech_rate_change'])
        self.assertEqual(SOUND['narration_voice_id'], 'voice-04')

    def test_music_and_sfx_are_original(self):
        self.assertTrue(SOUND['original_composition'])
        self.assertFalse(SOUND['third_party_music_samples'])
        self.assertFalse(SOUND['field_recordings_used'])
        self.assertFalse(SOUND['competitor_audio_used'])
        self.assertGreaterEqual(SOUND['sfx_count'], 5)

    def test_reconstruction_disclaimer_is_present(self):
        self.assertIn('illustration', S['reconstruction_note'])
        readme = (B / 'README.md').read_text().lower()
        self.assertIn('illustration', readme)
        self.assertIn('not a photograph', readme)

    def test_no_publication_claim(self):
        readme = (B / 'README.md').read_text().lower()
        self.assertIn('no youtube publication', readme)


if __name__ == '__main__':
    unittest.main()
