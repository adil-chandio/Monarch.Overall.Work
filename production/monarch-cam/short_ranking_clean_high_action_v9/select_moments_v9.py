#!/usr/bin/env python3
# Lock the seven high-action V9 payoff windows after the clean V8 clip-quality
# rejection. Exact source starts come from the committed 0.5 s curated contact
# sheets, not from a generic loudness/motion score. Every window is rechecked
# against the runner's own half-second RMS probe and the curated-window report.
# No human full-motion/native-audio listening or creative approval is claimed.
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_clean_high_action_v9'
SCOUT_BASE = ROOT / 'production/monarch-cam/short_ranking_high_action_v9'
REVIEW = BASE / 'review'
REVIEW.mkdir(parents=True, exist_ok=True)

MANIFEST = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
CURATED_SELECTION = json.loads((BASE / 'curated_selection_v9.json').read_text(encoding='utf-8'))
CURATED_REPORT = json.loads((SCOUT_BASE / 'review/curated_windows/curated_window_report.json').read_text(encoding='utf-8'))
PROBE_MANIFEST = json.loads((REVIEW / 'candidates/candidate_review_manifest.json').read_text(encoding='utf-8'))
AUDIO_PROBE = json.loads((REVIEW / 'candidates/candidate_audio_probe.json').read_text(encoding='utf-8'))
VIDEO_LEDGER = json.loads((REVIEW / 'candidates/candidate_video_ledger.json').read_text(encoding='utf-8'))
ASSETS = {a['id']: a for a in MANIFEST['assets']}
LEDGER = {e['id']: e for e in VIDEO_LEDGER['assets']}
CURATED_BY_KEY = {(w['id'], float(w['start'])): w for w in CURATED_REPORT['windows'] if w.get('probe_completed')}
FPS = int(SPEC['fps'])
FRAME_DURATIONS = [257, 257, 257, 257, 257, 257, 258]
assert sum(FRAME_DURATIONS) == int(SPEC['frame_count']) == 1800
assert FPS == 30 and abs(SPEC['duration'] - 60.0) < 1e-9
assert [w['rank'] for w in CURATED_SELECTION['windows']] == [7, 6, 5, 4, 3, 2, 1]
assert len({w['source_id'] for w in CURATED_SELECTION['windows']}) == 7


def window_stats(aid, start):
    asset = AUDIO_PROBE['assets'].get(aid)
    if not asset or not asset.get('windows'):
        raise RuntimeError('No runner half-second RMS probe for curated window: ' + aid)
    blocks = {round(float(w['start']), 1): float(w['rms_dbfs']) for w in asset['windows']}
    values = [blocks.get(round(start + i * 0.5, 1)) for i in range(17)]
    if any(v is None for v in values):
        raise RuntimeError('Curated window is outside the probed source: ' + aid)
    threshold = float(SPEC['audio_policy']['native_audible_segment_rms_dbfs_min'])
    quiet = sum(1 for v in values if v <= threshold)
    duration = float(asset.get('duration_seconds') or 0.0)
    if start + 8.6 > duration:
        raise RuntimeError('Curated window exceeds source duration: ' + aid)
    if quiet != 0:
        raise RuntimeError('Curated window has quiet half-second blocks: ' + aid)
    return {
        'min_full_block_rms_dbfs': round(min(values), 2),
        'quiet_full_block_count': quiet,
        'continuous_native_audio': True,
        'mean_block_rms_dbfs': round(sum(values) / len(values), 2),
        'duration_seconds': duration,
    }


def curated_stats(aid, start):
    entry = CURATED_BY_KEY.get((aid, float(start)))
    if not entry:
        raise RuntimeError('Curated runner window missing for ' + aid + ' @ ' + str(start))
    if not entry.get('window_eligible'):
        raise RuntimeError('Curated runner window not eligible: ' + aid)
    if not entry['audio']['native_audio_confirmed']:
        raise RuntimeError('Curated direct native audio not confirmed: ' + aid)
    if entry['audio']['quiet_half_second_block_count'] != 0:
        raise RuntimeError('Curated direct native audio has quiet blocks: ' + aid)
    if float(entry['motion']['curated_motion_score']) < float(CURATED_SELECTION['minimum_curated_motion_score']):
        raise RuntimeError('Curated visible motion below threshold: ' + aid)
    sheet = ROOT / entry['contact_sheet']
    if not sheet.is_file():
        raise RuntimeError('Curated contact sheet missing: ' + str(sheet))
    return entry


def false_guardrails():
    return {
        'full_motion_review': False, 'native_audio_listening': False,
        'human_approval': False, 'sign_off': False,
        'audience_result_promise': False, 'virality_guarantee': False,
        'perfection_claim': False, 'retention_claim': False,
        'hypnosis_claim': False, 'three_x_claim': False,
        'subscribe_claim': False, 'like_claim': False,
        'same_path_replacement': False, 'factual_superlative_claim': False,
        'third_party_repost': False, 'ai_audio': False,
        'generated_calls': False, 'v3_audio_packages': False,
        'audio_substitution': False, 'earshot_claim': False,
        'model_claim': False, 'sound_design_layers': False,
        'sub_bloom_layers': False, 'native_ambience_layers': False,
        'ambience_layers': False, 'cue_layers': False,
        'current_trending_claim': False, 'unverified_social_repost': False,
        'exact_reference_match_claim': False,
    }


def main():
    pm = PROBE_MANIFEST['flags']
    required = ['runner_probe_passed', 'runner_audio_visual_probe_passed', 'runner_visual_motion_probe',
                'contact_sheets_written', 'source_review_recorded']
    if not all(bool(pm.get(k)) for k in required):
        raise RuntimeError('Runner probe manifest is incomplete: ' + repr({k: pm.get(k) for k in required}))
    start_frame = 0
    scenes = []
    for i, chosen in enumerate(CURATED_SELECTION['windows']):
        aid = chosen['source_id']
        source_start = float(chosen['start'])
        asset = ASSETS[aid]
        ledger_entry = LEDGER.get(aid, {})
        stats = window_stats(aid, source_start)
        curated = curated_stats(aid, source_start)
        if not ledger_entry.get('audio_stream_present'):
            raise RuntimeError('Runner ledger has no native audio stream for ' + aid)
        frames = FRAME_DURATIONS[i]
        end_frame = start_frame + frames
        duration = frames / FPS
        scenes.append({
            'id': f"rank{chosen['rank']}_{aid}", 'rank': int(chosen['rank']),
            'title': asset['moment_label'], 'moment_label': asset['moment_label'],
            'reaction_text': asset['reaction_text'], 'emoji': asset['emoji'],
            'source_id': aid, 'source_page': asset['source_page'],
            'license': asset['license'], 'creator': asset['creator'],
            'local_filename': asset['local_filename'],
            'start_frame': start_frame, 'end_frame': end_frame, 'frames': frames,
            'start': round(start_frame / FPS, 6), 'end': round(end_frame / FPS, 6),
            'duration': round(duration, 6), 'source_start': source_start,
            'source_out': round(source_start + duration, 6),
            'focus_x': asset['focus_x'], 'focus_y': asset['focus_y'],
            'zoom_start': 1.0, 'zoom_end': 1.0,
            'payoff_at': SPEC['visual']['payoff_at'],
            'reaction_at': SPEC['visual']['reaction_at'],
            'label_reveal_at': SPEC['visual']['label_reveal_at'],
            'payoff_zoom': SPEC['visual']['payoff_zoom'],
            'audio_present': bool(ledger_entry.get('audio_stream_present')),
            'audio_codec': ledger_entry.get('audio_codec'),
            'runner_audio_rms_dbfs': stats['mean_block_rms_dbfs'],
            'runner_motion_score': curated['motion']['curated_motion_score'],
            'runner_motion_score_is_from_different_window': False,
            'runner_window_score': curated['motion']['curated_motion_score'],
            'runner_min_full_block_rms_dbfs': stats['min_full_block_rms_dbfs'],
            'runner_quiet_full_block_count': stats['quiet_full_block_count'],
            'runner_continuous_native_audio': stats['continuous_native_audio'],
            'runner_window_selectable': bool(curated['window_eligible']),
            'visual_window_override': True,
            'visual_window_override_reason': chosen['reason'],
            'visual_window_override_continuous_native_audio_verified': True,
            'curated_visual_window': True,
            'curated_visual_reason': chosen['reason'],
            'curated_contact_sheet': curated['contact_sheet'],
            'curated_direct_native_audio_confirmed': True,
            'curated_direct_quiet_half_second_block_count': curated['audio']['quiet_half_second_block_count'],
            'curated_motion_score': curated['motion']['curated_motion_score'],
            'runner_audio_visual_probe_passed': True,
            'runner_visual_motion_probe': True,
            'selected_from_runner_probe': True,
            'selected_from_curated_visual_review': True,
            'rights_cleared_social_origin_file_only': True,
            'no_unverified_reposts': True,
            'api_verification_required': True,
            'added_audio_layers': 0,
        })
        start_frame = end_frame
    if start_frame != 1800 or abs(scenes[-1]['end'] - 60.0) > 1e-9:
        raise RuntimeError('Selected timeline does not end at exactly 1800 frames / 60.0 seconds')
    flags = {
        'runner_probe_passed': True, 'runner_audio_visual_probe_passed': True,
        'runner_visual_motion_probe': True, 'continuous_native_audio_windows': True,
        'zero_quiet_full_blocks': True, 'contact_sheets_written': True,
        'source_review_recorded': True, 'visual_lock_written': True,
        'curated_visual_review_locked': True, 'curated_runner_windows_eligible': True,
        'curated_high_action_motion_locked': True, **false_guardrails(),
    }
    selected = {
        'edition': 'high_action_clean_v9', 'duration': 60.0,
        'frame_count': 1800, 'fps': FPS, 'selected_count': 7,
        'rank_steps': [7, 6, 5, 4, 3, 2, 1], 'scenes': scenes,
        'flags': flags,
        'probe_basis': ('Seven distinct high-action windows locked from committed 0.5 s curated payoff '
                        'contact sheets; each exact 8.6 s window was rechecked against the runner '
                        'half-second RMS probe and direct curated native-audio/motion report. Clean V8 '
                        'clip quality was rejected for weak/static action. No crop or zoom.'),
        'continuous_native_audio_windows': True, 'zero_quiet_full_blocks': True,
        'source_order': [s['source_id'] for s in scenes],
        'runner_audio_visual_probe_passed': True, 'runner_probe_passed': True,
        'runner_visual_motion_probe': True, 'contact_sheets_written': True,
        'source_review_recorded': True, 'visual_lock_written': True,
        'full_motion_review': False, 'native_audio_listening': False,
        'human_approval': False, 'sign_off': False,
        'audience_result_promise': False, 'virality_guarantee': False,
    }
    (REVIEW / 'selected_windows.json').write_text(json.dumps(selected, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    lock = {
        'status': 'LOCKED_FOR_V9_RENDER', 'edition': 'high_action_clean_v9',
        'source': 'Seven distinct rights-cleared high-action social-origin Commons windows locked from curated runner payoff sheets after the V8 clip-quality rejection.',
        'review_basis': ('Runner 0.5 s curated contact sheets, direct 8.6 s native-audio RMS/17-block '
                         'continuity, visible frame-difference motion and unchanged clean content-first '
                         'layout. Not human full-motion/native-audio listening or creative approval.'),
        'flags': flags,
        'exact_timecodes': [{
            'rank': s['rank'], 'timeline_in': s['start'], 'timeline_out': s['end'],
            'source_id': s['source_id'], 'source_in': s['source_start'],
            'source_out': s['source_out'], 'frames': s['frames'],
            'title': s['title'], 'moment_label': s['moment_label'],
            'reaction_text': s['reaction_text'], 'emoji': s['emoji'],
            'runner_audio_rms_dbfs': s['runner_audio_rms_dbfs'],
            'runner_motion_score': s['runner_motion_score'],
            'runner_min_full_block_rms_dbfs': s['runner_min_full_block_rms_dbfs'],
            'runner_quiet_full_block_count': s['runner_quiet_full_block_count'],
            'runner_continuous_native_audio': s['runner_continuous_native_audio'],
            'curated_contact_sheet': s['curated_contact_sheet'],
        } for s in scenes],
        'runner_probe_passed': True, 'runner_audio_visual_probe_passed': True,
        'runner_visual_motion_probe': True, 'contact_sheets_written': True,
        'source_review_recorded': True, 'visual_lock_written': True,
        **false_guardrails(),
    }
    (REVIEW / 'visual_review_lock.json').write_text(json.dumps(lock, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Locked seven high-action V9 moments', selected['source_order'], flush=True)
    print('Exact frames', sum(FRAME_DURATIONS), 'duration', scenes[-1]['end'], flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
