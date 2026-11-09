#!/usr/bin/env python3
# Validate the static V7 contracts before CI downloads or renders anything.
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v7'
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
MANIFEST = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
META = json.loads((BASE / 'ranking_v7_metadata.json').read_text(encoding='utf-8'))
V = SPEC['visual']
A = SPEC['audio_policy']
assets = MANIFEST['assets']

errors = []
if [SPEC['width'], SPEC['height'], SPEC['fps'], SPEC['frame_count'], SPEC['duration']] != [1080, 1920, 30, 1800, 60.0]:
    errors.append('timeline contract mismatch')
if len(assets) != 10 or len({a['id'] for a in assets}) != 10:
    errors.append('expected 10 distinct rights-cleared social-origin candidates')
for a in assets:
    if a['license'] not in MANIFEST['policy']['allowed_license_ids']:
        errors.append('disallowed licence for ' + a['id'])
    if not a['download_urls'] or not a['source_page'].startswith('https://commons.wikimedia.org/wiki/File:'):
        errors.append('missing Commons URL for ' + a['id'])
    if not a.get('commercial_reuse_allowed') or not a.get('no_unverified_repost'):
        errors.append('rights guardrail missing for ' + a['id'])
    if not a.get('platform_tokens'):
        errors.append('social-origin token missing for ' + a['id'])
    if a['duration_seconds'] < 8.7:
        errors.append('source too short for 8.6s window: ' + a['id'])
for key in ['full_frame_preserved','no_crop','no_cut_off','blurred_background_fill','no_black_bars','no_letterbox','no_black_empty_top','no_hook_black_fill','reference_style_hook','persistent_numbered_list','left_list_fully_visible','progressive_labels','right_platform_ui','bottom_caption_subscribe','app_chrome','no_third_party_handle','no_fake_engagement_counts','no_v6_boxed_list','no_v5_right_panel','no_v5_bottom_rank_burst','seven_moments_only','safe_area_check','social_origin_check','rights_verified_per_title']:
    if not bool(V.get(key)):
        errors.append('visual contract false: ' + key)
for key in ['raw_only','native_source_audio_only','raw_per_window_native_audio_only','no_added_layers','no_spoken_voice_over','no_score','no_effects','no_bed','all_seven_native_audio_audible','require_continuous_native_audio','zero_quiet_half_second_blocks']:
    if not bool(A.get(key)):
        errors.append('audio contract false: ' + key)
if float(A['continuous_native_audio_half_second_min_rms_dbfs']) != float(A['native_audible_segment_rms_dbfs_min']):
    errors.append('continuous native-audio threshold must match the unchanged audible-segment threshold')
if [float(A['web_lufs_tolerance']), float(A['web_true_peak_ceiling_dbtp']), float(A['web_lra_min_lu']), float(A['web_lra_max_lu'])] != [0.7, -1.0, 1.0, 10.0]:
    errors.append('unchanged web-gate policy mismatch')
if any(META['flags'].values()):
    errors.append('metadata guardrail flags must all be false')
if not SPEC['rights_policy']['no_unverified_trending_reposts'] or not SPEC['rights_policy']['no_current_trending_claim']:
    errors.append('rights boundary must reject unverified trending reposts and current-trending claims')
for p in ['CREDITS.md','RANKING_V7_PLAN_AND_METADATA.md','RANKING_V7_UPLOAD_METADATA.md','RENDER_TRIGGER_V7.md','review/UPLOAD_METADATA_RANKING_V7.txt']:
    if not (BASE / p).is_file():
        errors.append('missing V7 document: ' + p)

if errors:
    print('V7 CONTRACT FAILED', json.dumps(errors, indent=2), file=sys.stderr)
    raise SystemExit(1)
print('V7 contract OK: 10 rights-cleared social-origin candidates, 60s/1800f, full-frame reference-style layout, native audio only.')
