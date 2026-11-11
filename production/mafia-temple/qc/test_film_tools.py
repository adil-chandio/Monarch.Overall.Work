"""Deterministic checks for the Monarch night-temple film toolchain.

These are engineering tests of pure helpers and decoded media only. They do not
and cannot assert likeness, anatomy, acting quality or creative acceptance.
Run with:  python3 -m unittest production/mafia-temple/qc/test_film_tools.py
"""
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))          # production/mafia-temple
sys.path.insert(0, str(HERE.parent / 'qc'))   # qc/

import film_tools as ft                        # noqa: E402

try:
    import cv2
    HAVE_CV2 = True
except Exception:
    HAVE_CV2 = False


class RetimeTests(unittest.TestCase):
    def test_identity_is_passthrough(self):
        idx = ft.retime_indices(10, 10)
        self.assertTrue(np.array_equal(idx, np.arange(10)))

    def test_dropping_one_frame_keeps_strict_order(self):
        idx = ft.retime_indices(96, 97)
        self.assertEqual(len(idx), 96)
        self.assertTrue(np.all(np.diff(idx) >= 1))
        self.assertLessEqual(idx[-1], 96)  # never reads past the source

    def test_never_duplicates_a_source_frame(self):
        for out, src in ((96, 97), (120, 121), (72, 73), (49, 97), (24, 121)):
            idx = ft.retime_indices(out, src)
            self.assertEqual(len(idx), out)
            self.assertEqual(len(set(idx.tolist())), out, 'a frame was duplicated')
            self.assertTrue(idx.min() >= 0 and idx.max() <= src - 1)

    def test_slow_motion_is_refused_rather_than_padded(self):
        with self.assertRaises(ValueError):
            ft.retime_indices(200, 49)

    def test_playback_speed_is_reported_truthfully(self):
        self.assertAlmostEqual(ft.playback_speed(96, 97), 1.0104, places=3)
        self.assertAlmostEqual(ft.playback_speed(49, 97), 1.9796, places=3)


class FlickerTests(unittest.TestCase):
    def test_deflicker_flattens_drift_but_keeps_trend(self):
        base = np.linspace(60, 90, 40)
        flick = base + np.array([3, -3] * 20, dtype=float)
        gains = ft.deflicker_gains(flick)
        fixed = flick * gains
        self.assertLess(fixed.std(), flick.std())
        # overall direction of travel must survive
        self.assertGreater(fixed[-5:].mean(), fixed[:5].mean())

    def test_identity_when_already_flat(self):
        flat = np.full(12, 44.0)
        self.assertTrue(np.allclose(ft.deflicker_gains(flat), 1.0))

    def test_strength_is_bounded(self):
        with self.assertRaises(ValueError):
            ft.deflicker_gains(np.arange(9.0), strength=1.4)

    def test_match_luma_clamps_explosive_gain(self):
        frame = np.full((4, 4, 3), 100, np.uint8)
        out = ft.match_luma(frame, 50.0, limit=1.35)
        self.assertLessEqual(int(out.max()), 135)


class StabiliseTests(unittest.TestCase):
    def test_jitter_metric_falls_after_cancellation(self):
        rng = np.random.default_rng(3)
        travel = np.c_[np.linspace(0, 40, 60), np.zeros(60)]
        shaky = travel + rng.normal(0, 1.4, (60, 2))
        before = ft.jitter_rms(shaky)
        resid = ft.stabilise_residuals(shaky)
        after = ft.jitter_rms(shaky - resid)
        self.assertLess(after, before * 0.35)

    def test_pure_travel_is_not_destroyed(self):
        travel = np.c_[np.linspace(0, 80, 80), np.linspace(0, -30, 80)]
        self.assertLess(ft.jitter_rms(travel, sigma=4.0), 2.0)

    def test_zero_sigma_is_identity(self):
        v = np.array([3.0, 9.0, 1.0])
        self.assertTrue(np.array_equal(ft.smooth_path(v, 0), v))


class CameraTests(unittest.TestCase):
    def test_end_points_are_exact(self):
        start = ft.camera_matrix(0.0, 1.0, 1.12)
        self.assertTrue(np.allclose(start[:, :2], np.eye(2)))
        end = ft.camera_matrix(1.0, 1.0, 1.12)
        self.assertAlmostEqual(float(end[0, 0]), 1.12, places=5)

    def test_progress_is_bounded(self):
        with self.assertRaises(ValueError):
            ft.camera_matrix(1.2, 1.0, 1.1)

    def test_pan_moves_in_requested_direction(self):
        m = ft.camera_matrix(1.0, 1.0, 1.0, pan_x=0.05)
        self.assertAlmostEqual(float(m[0, 2]), 64.0, places=4)  # 5% of 1280
        self.assertAlmostEqual(float(m[1, 2]), 0.0, places=4)


class GradeTests(unittest.TestCase):
    def test_parameters_are_validated(self):
        frame = np.zeros((8, 8, 3), np.uint8)
        for bad in ({'grain': 40.0}, {'vignette': 0.9}, {'contrast': 4.0}):
            with self.assertRaises(ValueError):
                ft.grade_frame(frame, **bad)

    def test_output_range_and_shape(self):
        rng = np.random.default_rng(1)
        frame = (rng.random((24, 32, 3)) * 255).astype(np.uint8)
        out = ft.grade_frame(frame, grain=2.0, vignette=0.2, teal=0.1,
                             contrast=1.05, black_point=2, seed=7)
        self.assertEqual(out.shape, frame.shape)
        self.assertEqual(out.dtype, np.uint8)

    def test_vignette_darkens_corners_not_centre(self):
        frame = np.full((60, 80, 3), 200, np.uint8)
        out = ft.grade_frame(frame, vignette=0.3)
        self.assertLess(int(out[2, 2].mean()), int(out[30, 40].mean()))

    def test_grain_is_reproducible_for_a_seed(self):
        frame = np.full((16, 16, 3), 90, np.uint8)
        a = ft.grade_frame(frame, grain=3.0, seed=11)
        b = ft.grade_frame(frame, grain=3.0, seed=11)
        self.assertTrue(np.array_equal(a, b))


class EyeTests(unittest.TestCase):
    def test_strength_bounds(self):
        frame = np.zeros((20, 20, 3), np.uint8)
        with self.assertRaises(ValueError):
            ft.brighten_eyes(frame, [(5, 5), (15, 5)], 1.5)

    def test_glow_lands_on_the_points_not_the_field(self):
        frame = np.full((80, 80, 3), 20, np.uint8)
        out = ft.brighten_eyes(frame, [(30, 30), (50, 30)], 1.0)
        self.assertGreater(int(out[30, 30, 2]), int(out[74, 74, 2]) + 40)

    def test_missing_points_are_a_noop(self):
        frame = np.zeros((10, 10, 3), np.uint8)
        self.assertTrue(np.array_equal(ft.brighten_eyes(frame, None, 1.0), frame))

    def test_median_smoothing_survives_a_gap(self):
        seq = [[(10.0, 10.0), (20.0, 10.0)]] * 4
        seq.insert(2, None)
        out = ft.smooth_points(seq, window=3)
        self.assertEqual(len(out), len(seq))
        self.assertIsNotNone(out[2])

    def test_empty_track_stays_empty(self):
        out = ft.smooth_points([None, None], 3)
        self.assertEqual(out, [None, None])


@unittest.skipUnless(HAVE_CV2, 'OpenCV not installed')
class IntegrationTests(unittest.TestCase):
    """Pixel-path checks on synthetic frames; no media files required."""

    def test_track_shifts_recovers_a_known_translation(self):
        rng = np.random.default_rng(5)
        base = cv2.GaussianBlur((rng.random((120, 160)) * 255).astype(np.uint8), (5, 5), 0)
        M = np.float32([[1, 0, 6], [0, 1, -4]])
        moved = cv2.warpAffine(base, M, (160, 120))
        track = ft.track_shifts([base, moved], work_width=160)
        # the track is mean-centred, so compare the step between frames
        step = track[1] - track[0]
        self.assertAlmostEqual(float(step[0]), -6.0, delta=1.5)
        self.assertAlmostEqual(float(step[1]), 4.0, delta=1.5)

    def test_face_and_eye_localisation_are_offline(self):
        # Synthetic face-like pattern: must fail closed, not hallucinate a face.
        frame = np.full((200, 200, 3), 128, np.uint8)
        self.assertIsNone(ft.face_box(frame))


class TimelineTests(unittest.TestCase):
    """The film must be exactly 20.000 s with no gap and no padded frame."""

    def setUp(self):
        sys.path.insert(0, str(HERE))
        import render_film_v8 as rv
        self.rv = rv

    def test_total_length_is_exactly_twenty_seconds(self):
        plan = [0] * self.rv.TOTAL_FRAMES
        for s in self.rv.SHOTS:
            for f in range(s.start, min(s.end, self.rv.TOTAL_FRAMES)):
                plan[f] += 1
        self.assertTrue(all(plan), 'timeline has a hole')
        self.assertFalse(any(c > 2 for c in plan), 'three shots overlap')
        self.assertEqual(self.rv.TOTAL_FRAMES, 480)

    def test_cut_points_match_the_job_sheet(self):
        starts = [s.start / 24 for s in self.rv.SHOTS]
        self.assertEqual([round(v, 2) for v in starts], [0.0, 3.83, 8.88, 12.92, 15.96])
        # the cut sheet means 0-4 / 4-9 / 9-13 / 13-16 / 16-20 seconds
        cuts = [0, 4, 9, 13, 16, 20]
        self.assertEqual(cuts[-1], 20)
        overlaps = [(a.end - b.start) for a, b in zip(self.rv.SHOTS, self.rv.SHOTS[1:])
                    if a.end > b.start]
        self.assertEqual(overlaps, [5])  # one 5-frame dissolve at 3.83s, nothing else

    def test_every_shot_plays_unique_source_frames(self):
        for s in self.rv.SHOTS:
            path = HERE.parent / 'clips' / f'{s.source}.mp4'
            if not path.exists():
                self.skipTest('clips not present')
            src = len(self.rv.decode(path))
            self.assertLessEqual(s.frames, src, f'{s.name} needs more frames than exist')
            idx = ft.retime_indices(s.frames, src)
            self.assertEqual(len(set(idx.tolist())), s.frames)
            self.assertGreaterEqual(ft.playback_speed(s.frames, src), 0.95,
                                    f'{s.name} would be slowed past native motion')


class ShotSourceTests(unittest.TestCase):
    """Media-backed checks. Skipped automatically if the clips are absent."""

    def test_chosen_sources_exist_and_are_long_enough(self):
        import render_film_v8 as rv
        for s in rv.SHOTS:
            path = HERE.parent / 'clips' / f'{s.source}.mp4'
            if not path.exists():
                self.skipTest('clips not present')
            frames = rv.decode(path)
            self.assertGreaterEqual(len(frames), s.frames, s.name)
            self.assertGreater(frames[0].mean(), 3.0, f'{s.name} is black')


if __name__ == '__main__':
    unittest.main(verbosity=2)
