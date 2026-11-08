#!/usr/bin/env python3
# Local contract validation for the V5 package. No media tools are required here.
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v5'
spec = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
manifest = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
meta = json.loads((BASE / 'ranking_v5_metadata.json').read_text(encoding='utf-8'))
gitignore = (ROOT / '.gitignore').read_text(encoding='utf-8')

assert spec['duration'] == 60.0 and spec['frame_count'] == 1800 and spec['width'] == 1080 and spec['height'] == 1920 and spec['fps'] == 30
assert spec['new_v5_file'] and spec['preserve_previous']
assert spec['scenes_source'].endswith('selected_windows.json')
assert len(spec['visual']['rank_steps']) == 7 and spec['visual']['rank_steps'] == [7, 6, 5, 4, 3, 2, 1]
assert spec['audio_policy']['raw_only'] and spec['audio_policy']['no_spoken_voice_over']
assert spec['audio_policy']['no_score'] and spec['audio_policy']['no_effects'] and spec['audio_policy']['no_bed']
assert spec['audio_policy']['no_added_layers'] and spec['audio_policy']['no_fabricated_animal_calls']
assert spec['audio_policy']['native_source_audio_only'] and spec['audio_policy']['raw_per_window_native_audio_only']
assert spec['audio_policy']['source_audio_present_segments'] == 7
assert spec['audio_policy']['silent_segments'] == 0
assert spec['audio_policy']['all_seven_native_audio_audible'] is True
assert spec['audio_policy']['target_integrated_lufs'] == -14.2
assert spec['audio_policy']['true_peak_target_dbtp'] == -2.2
assert spec['audio_policy']['sample_rate'] == 48000 and spec['audio_policy']['channels'] == 2
assert spec['audio_policy']['edge_fade_ms'] == 30
assert spec['audio_policy']['final_gain_calibration'] is True
assert spec['audio_policy']['final_peak_limit_linear'] == 0.75
assert spec['audio_policy']['final_calibration_iterations'] == 5
assert spec['audio_policy']['final_technical_click_threshold'] == 0.45
assert spec['audio_policy']['final_declick_threshold'] == 0.35
assert spec['audio_policy']['final_declick_width_samples'] == 24
assert spec['audio_policy']['native_audible_segment_rms_dbfs_min'] == -55.0
assert spec['audio_policy']['web_lufs_target'] == -14.0 and spec['audio_policy']['web_lufs_tolerance'] == 0.7
assert spec['audio_policy']['web_true_peak_ceiling_dbtp'] == -1.0
assert spec['audio_policy']['web_lra_min_lu'] == 1.0 and spec['audio_policy']['web_lra_max_lu'] == 10.0
assert spec['audio_policy']['web_movement_min_db'] == 3.0

v = spec['visual']
assert v['full_screen'] and v['cover_mode'] == 'dynamic_subject_safe_cover'
assert v['no_letterbox'] and v['no_black_bars'] and v['no_blurred_background'] and v['no_action_window']
assert v['full_reference_mechanic'] and v['colorful_hook_title'] and v['persistent_numbered_list']
assert v['progressive_labels'] and v['payoff_cuts_zoom'] and v['punchy_zoom']
assert v['reaction_pops'] and v['emoji_pops'] and v['seven_moments_only'] and v['rank_numbers']
assert v['rank_title_overlay_only'] is False
assert v['no_hook_scene'] is False and v['no_payoff_scene'] is False
assert v['no_hook_or_end_question_in_video'] is False
assert v['no_extra_text'] is False and v['no_bottom_captions'] is False
assert v['no_badges'] and v['no_progress'] and v['no_footer'] and v['no_source_labels']
assert v['no_brand_watermark'] and v['no_cut_flashes'] and v['no_loop'] and v['hard_cuts_only']
assert v['seven_cc0_sources'] and v['subjective_ranking_not_science'] and v['runner_probe_required']
assert 'WHAT!!' in [a['reaction_text'] for a in manifest['assets']]
assert 'WAIT... WHAT!!' in [a['reaction_text'] for a in manifest['assets']]

assert len(manifest['assets']) >= 7
for a in manifest['assets']:
    assert a['role'] == 'candidate_video' and a['license'] == 'CC0-1.0'
    assert a['license_url'].startswith('https://creativecommons.org/publicdomain/zero/1.0/')
    assert a['source_page'].startswith('https://commons.wikimedia.org/wiki/File:')
    assert a['download_urls'] and a['api_verification_required'] is True
    assert a['original_cc0_file_only'] is True and a['no_transcodes'] is True
    assert a['expected_audio_codec'] in ('vorbis', 'opus')
    assert all(word in a['creative_intent'] for word in ('surprising', 'funny', 'dynamic'))

assert meta['video_category'] == 'Entertainment' and meta['youtube_category_id'] == 24
blob = json.dumps({k: meta[k] for k in ('primary', 'comments')}, ensure_ascii=False).lower()
claims = [
    r'\bvoiceover\b', r'\bmusic\b', r'\bsfx\b', r'\bhuman\b', r'\bapproval\b', r'\bviral\b',
    r'\bguarantee\b', r'\bretention\b', r'\bhypnosis\b', r'\b3x\b', r'\bsubscribe\b', r'\blike\b',
    r'\bsame-path\b', r'\bmost impressive ever\b', r'\bpart-2\b', r'\b25m\b', r'\bbear\b', r'\bcar\b',
    r'\bhandle\b', r'\bdoor\b', r'\bfood-reward\b', r'\bthird-party short-form\b', r'\bai\b', r'\bgenerated\b',
    r'\bearshot\b', r'\bmodel\b', r'\bperfection\b', r'\bvirality\b', r'\bnarration:\b', r'\bmusic:\b', r'\bsfx:\b',
    r'\bsound design\b', r'\bsub-bloom\b', r'\bnative_ambience\b', r'\bambience\b', r'\bsub_bloom\b', r'\bcue\b',
    r'\baudience results\b', r'\bhuman approval\b', r'\bfull-motion\b', r'\bnative-audio listening\b',
]
for pat in claims:
    assert not re.search(pat, blob), 'Forbidden claim: ' + pat
for k in ['full_motion_review', 'native_audio_listening', 'human_approval', 'sign_off',
          'audience_result_promise', 'virality_guarantee', 'perfection_claim', 'retention_claim',
          'hypnosis_claim', 'three_x_claim', 'subscribe_claim', 'like_claim', 'same_path_replacement',
          'factual_superlative_claim', 'third_party_repost', 'ai_audio', 'generated_calls',
          'v3_audio_packages', 'audio_substitution', 'earshot_claim', 'model_claim',
          'sound_design_layers', 'sub_bloom_layers', 'native_ambience_layers', 'ambience_layers', 'cue_layers']:
    assert meta['flags'][k] is False, 'Flag must be false: ' + k
for k in ['runner_probe_passed', 'runner_audio_visual_probe_passed', 'runner_visual_motion_probe',
          'contact_sheets_written', 'source_review_recorded', 'visual_lock_written']:
    assert meta['flags'][k] is False, 'Static runner record must not claim pass: ' + k

assert '!deliverables/MONARCH_CAM_7_Unexpected_Animal_Moments_Ranked_60s_Short_RAW_FULLSCREEN_V5.mp4' in gitignore
assert (ROOT / 'public/showreel/fonts/Manrope-800.ttf').is_file()
assert (ROOT / 'public/showreel/fonts/IBMPlexMono-400.ttf').is_file()
for p in [
    'deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short.mp4',
    'deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short_PREMIUM.mp4',
    'deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short_CLEAN_PREMIUM.mp4',
    'deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short_CLEAN_PREMIUM_V2.mp4',
    'deliverables/MONARCH_CAM_5_Unexpected_Animal_Skills_Ranked_35s_Short_CLEAN_PREMIUM_V3.mp4',
    'deliverables/MONARCH_CAM_5_Unexpected_Animal_Skills_Ranked_35s_Short_RAW_FULLSCREEN_V4.mp4',
]:
    assert (ROOT / p).is_file(), 'Missing preserved file ' + p
print('Raw full-screen V5 60s, full reference mechanic, seven CC0 candidates, raw-audio and preservation contracts OK')
