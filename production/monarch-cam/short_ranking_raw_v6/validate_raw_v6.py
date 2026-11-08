#!/usr/bin/env python3
# Local contract validation for the V6 package. No media tools are required here.
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v6'
spec = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
manifest = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
meta = json.loads((BASE / 'ranking_v6_metadata.json').read_text(encoding='utf-8'))
selected = json.loads((BASE / 'review' / 'selected_windows.json').read_text(encoding='utf-8'))
gitignore = (ROOT / '.gitignore').read_text(encoding='utf-8')

assert spec['duration'] == 60.0 and spec['frame_count'] == 1800 and spec['width'] == 1080 and spec['height'] == 1920 and spec['fps'] == 30
assert spec['new_v6_file'] and spec['preserve_previous']
assert spec['scenes_source'].endswith('selected_windows.json')
assert len(spec['visual']['rank_steps']) == 7 and spec['visual']['rank_steps'] == [7, 6, 5, 4, 3, 2, 1]
assert spec['audio_policy']['raw_only'] and spec['audio_policy']['no_spoken_voice_over']
assert spec['audio_policy']['no_score'] and spec['audio_policy']['no_effects'] and spec['audio_policy']['no_bed']
assert spec['audio_policy']['no_added_layers'] and spec['audio_policy']['no_fabricated_animal_calls']
assert spec['audio_policy']['native_source_audio_only'] and spec['audio_policy']['raw_per_window_native_audio_only']
assert spec['audio_policy']['source_audio_present_segments'] == 7 and spec['audio_policy']['silent_segments'] == 0
assert spec['audio_policy']['sample_rate'] == 48000 and spec['audio_policy']['channels'] == 2

v = spec['visual']
assert v['full_screen'] and v['cover_mode'] == 'dynamic_subject_safe_cover'
assert v['no_letterbox'] and v['no_black_bars'] and v['no_blurred_background'] and v['no_action_window']
assert v['full_reference_mechanic'] and v['colorful_hook_title'] and v['persistent_numbered_list']
assert v['progressive_labels'] and v['payoff_cuts_zoom'] and v['punchy_zoom']
assert v['reaction_pops'] and v['emoji_pops'] and v['seven_moments_only'] and v['rank_numbers']
assert v['runner_probe_required'] is False and 'V5' in v['runner_probe_basis']
assert v['centered_hook_visible'] and v['left_list_fully_visible']
assert v['no_v5_right_panel'] and v['no_v5_bottom_rank_burst']
assert v['right_platform_ui'] and v['bottom_comment_subscribe']
assert v['safe_area_check'] and v['social_origin_check'] and v['rights_verified_per_title']
assert v['list_x'] < spec['width'] / 2 and v['list_x'] + v['list_width'] < v['reaction_x']
assert v['hook_line_y'][-1] + v['hook_font_size'] < v['question_y']
assert v['question_y'] + v['question_font_size'] < v['label_y']
assert v['label_y'] + v['label_font_size'] < v['list_y']
assert v['list_y'] + v['list_header_height'] + 7 * v['list_row_height'] < v['bottom_bar_y']
assert v['reaction_y'] + v['reaction_height'] < v['bottom_bar_y']
assert v['safe_area']['top'] < min(v['hook_line_y']) and v['safe_area']['right'] > 0

assert len(manifest['assets']) >= 7
for a in manifest['assets']:
    assert a['role'] == 'candidate_video' and a['license'] == 'CC0-1.0'
    assert a['license_url'].startswith('https://creativecommons.org/publicdomain/zero/1.0/')
    assert a['source_page'].startswith('https://commons.wikimedia.org/wiki/File:')
    assert a['download_urls'] and a['api_verification_required'] is True
    assert a['original_cc0_file_only'] is True and a['no_transcodes'] is True

assert selected['edition'] == 'raw_fullscreen_v6' and len(selected['scenes']) == 7
assert 'V5' in selected['probe_basis'] and selected['frame_count'] == 1800
assert meta['video_category'] == 'Entertainment' and meta['youtube_category_id'] == 24
blob = json.dumps({k: meta[k] for k in ('primary', 'comments')}, ensure_ascii=False).lower()
claims = [
    r'\bvoiceover\b', r'\bmusic\b', r'\bsfx\b', r'\bviral\b', r'\bguarantee\b',
    r'\bretention\b', r'\bhypnosis\b', r'\b3x\b', r'\bperfection\b',
    r'\bsame-path\b', r'\bmost impressive ever\b', r'\bpart-2\b',
    r'\bfull-motion\b', r'\bnative-audio listening\b', r'\baudience results\b',
]
for pat in claims:
    assert not re.search(pat, blob), 'Forbidden claim: ' + pat
for k in ['full_motion_review', 'native_audio_listening', 'human_approval', 'sign_off',
          'audience_result_promise', 'virality_guarantee', 'perfection_claim', 'retention_claim',
          'third_party_repost', 'ai_audio', 'generated_calls', 'v3_audio_packages',
          'audio_substitution', 'earshot_claim', 'model_claim', 'sound_design_layers']:
    assert meta['flags'][k] is False, 'Flag must be false: ' + k

assert '!deliverables/MONARCH_CAM_7_Unexpected_Animal_Moments_Ranked_60s_Short_RAW_FULLSCREEN_V6.mp4' in gitignore
assert (ROOT / 'public/showreel/fonts/Manrope-800.ttf').is_file()
assert (ROOT / 'public/showreel/fonts/IBMPlexMono-400.ttf').is_file()
assert (ROOT / 'public/showreel/fonts/Anton-Regular.ttf').is_file()
for p in [
    'deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short.mp4',
    'deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short_PREMIUM.mp4',
    'deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short_CLEAN_PREMIUM.mp4',
    'deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short_CLEAN_PREMIUM_V2.mp4',
    'deliverables/MONARCH_CAM_5_Unexpected_Animal_Skills_Ranked_35s_Short_CLEAN_PREMIUM_V3.mp4',
    'deliverables/MONARCH_CAM_5_Unexpected_Animal_Skills_Ranked_35s_Short_RAW_FULLSCREEN_V4.mp4',
    'deliverables/MONARCH_CAM_7_Unexpected_Animal_Moments_Ranked_60s_Short_RAW_FULLSCREEN_V5.mp4',
]:
    assert (ROOT / p).is_file(), 'Missing preserved file ' + p
print('Raw full-screen V6 60s, corrected hook/list geometry, per-title rights, raw-audio and preservation contracts OK')
