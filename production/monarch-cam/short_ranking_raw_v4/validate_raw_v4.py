#!/usr/bin/env python3
# Local contract validation for the V4 package. No media tools are required here.
from __future__ import annotations
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v4'
spec = json.loads((BASE / 'ranking_short_spec.json').read_text())
manifest = json.loads((BASE / 'source_manifest_ranking.json').read_text())
meta = json.loads((BASE / 'ranking_v4_metadata.json').read_text())
assert spec['duration'] == 35.0 and spec['frame_count'] == 1050 and spec['width'] == 1080 and spec['height'] == 1920 and spec['fps'] == 30
assert len(spec['scenes']) == 5 and [s['rank'] for s in spec['scenes']] == [5, 4, 3, 2, 1]
assert abs(sum(s['duration'] for s in spec['scenes']) - 35.0) < 1e-9
assert spec['audio_policy']['raw_only'] and spec['audio_policy']['no_spoken_voice_over'] and spec['audio_policy']['no_score'] and spec['audio_policy']['no_effects']
assert spec['audio_policy']['no_added_layers'] and spec['audio_policy']['no_fabricated_animal_calls']
assert all(s['audio_present'] for s in spec['scenes'])
assert spec['audio_policy']['source_audio_present_segments'] == 5
assert spec['audio_policy']['silent_segments'] == 0
assert spec['audio_policy']['all_five_native_audio_audible'] is True
assert spec['audio_policy']['final_gain_calibration'] is True
assert spec['audio_policy']['final_peak_limit_linear'] == 0.75
assert spec['audio_policy']['final_calibration_iterations'] == 4
assert spec['visual']['full_screen'] and spec['visual']['cover_mode'] == 'dynamic_subject_safe_cover'
assert spec['visual']['no_letterbox'] and spec['visual']['no_black_bars'] and spec['visual']['no_blurred_background']
assert spec['visual']['rank_title_overlay_only'] and spec['visual']['five_moments_only']
assert spec['visual']['no_hook_scene'] and spec['visual']['no_payoff_scene'] and spec['visual']['no_loop']
assert len(manifest['assets']) == 5 and all(a['role'] == 'video' and a['license'] == 'CC0-1.0' for a in manifest['assets'])
assert meta['video_category'] == 'Entertainment' and meta['youtube_category_id'] == 24
blob = json.dumps({k: meta[k] for k in ('primary', 'comments')}, ensure_ascii=False).lower()
claims = [
    r'\bvoiceover\b', r'\bmusic\b', r'\bsfx\b', r'\bhuman\b', r'\bapproval\b', r'\bviral\b',
    r'\bguarantee\b', r'\bretention\b', r'\bhypnosis\b', r'\b3x\b', r'\bsubscribe\b', r'\blike\b',
    r'\bsame-path\b', r'\bmost impressive ever\b', r'\bpart-2\b', r'\b25m\b', r'\bbear\b', r'\bcar\b',
    r'\bhandle\b', r'\bdoor\b', r'\bfood-reward\b', r'\bthird-party short-form\b', r'\bai\b', r'\bgenerated\b',
    r'\bearshot\b', r'\bmodel\b', r'\bperfection\b', r'\bvirality\b', r'\bnarration:\b', r'\bmusic:\b', r'\bsfx:\b',
    r'\bsound design\b', r'\bsub-bloom\b', r'\bnative_ambience\b', r'\bambience\b', r'\bsub_bloom\b', r'\bcue\b'
]
for pat in claims:
    assert not re.search(pat, blob), 'Forbidden claim: ' + pat
for p in ['deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short.mp4',
          'deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short_PREMIUM.mp4',
          'deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short_CLEAN_PREMIUM.mp4',
          'deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short_CLEAN_PREMIUM_V2.mp4',
          'deliverables/MONARCH_CAM_5_Unexpected_Animal_Skills_Ranked_35s_Short_CLEAN_PREMIUM_V3.mp4']:
    assert (ROOT / p).is_file(), 'Missing preserved file ' + p
print('Raw full-screen V4 35s, five CC0 sources, full-screen, rank/title, raw-audio and preservation contracts OK')
