import unittest
from pathlib import Path

from tools import sfx_sync


ROOT = Path(__file__).resolve().parents[1]
CATALOG = sfx_sync.read_json(ROOT / "production/audio-library/catalog.json")
CUES = sfx_sync.flatten_catalog(CATALOG)


class FrameSyncTests(unittest.TestCase):
    def test_frame_round_trip_at_30_fps(self):
        self.assertEqual(sfx_sync.seconds_to_frame(1.0, 30), 30)
        self.assertEqual(sfx_sync.seconds_to_frame(0.466666667, 30), 14)

    def test_explicit_catalog_cue_resolves(self):
        cue = sfx_sync.resolve_cue({"cue_id": "digitalClick"}, CUES)
        self.assertEqual(cue["source_id"], "user-reel-50-plus-sfx")

    def test_tag_match_prefers_requested_sound_family(self):
        cue = sfx_sync.resolve_cue({"tags": ["digital", "click"], "vibe": ["clean"]}, CUES)
        self.assertEqual(cue["id"], "digitalClick")

    def test_unverified_assets_are_private_review_only(self):
        cue = sfx_sync.resolve_cue({"cue_id": "softSweep"}, CUES)
        with self.assertRaisesRegex(RuntimeError, "private draft"):
            sfx_sync.ensure_rights(cue, private_review=False)
        sfx_sync.ensure_rights(cue, private_review=True)

    def test_cue_sheet_frame_and_time_must_agree(self):
        doc = {"fps": 30, "duration_seconds": 3, "events": [
            {"cue_id": "digitalClick", "frame": 30, "time": 1.0}
        ]}
        _, _, events = sfx_sync.normalise_events(doc, CATALOG, CUES)
        self.assertEqual(events[0]["frame"], 30)
        bad = {"fps": 30, "duration_seconds": 3, "events": [
            {"cue_id": "digitalClick", "frame": 31, "time": 1.0}
        ]}
        with self.assertRaisesRegex(RuntimeError, "inconsistent frame/time"):
            sfx_sync.normalise_events(bad, CATALOG, CUES)

    def test_cues_cannot_enter_declared_silence(self):
        doc = {
            "fps": 30, "duration_seconds": 4,
            "intentional_silence": [{"start_frame": 30, "end_frame": 60, "reason": "quiet line"}],
            "events": [{"cue_id": "softSweep", "frame": 29}]
        }
        with self.assertRaisesRegex(RuntimeError, "intentional-silence"):
            sfx_sync.normalise_events(doc, CATALOG, CUES)


if __name__ == "__main__":
    unittest.main()
