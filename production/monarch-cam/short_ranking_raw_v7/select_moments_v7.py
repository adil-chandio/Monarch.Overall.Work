#!/usr/bin/env python3
# Select seven distinct rights-cleared social-origin moments from the runner audio/motion probe and lock
# exact 60-second timeline windows. No human sign-off is claimed.
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v7'
REVIEW = BASE / 'review'
REVIEW.mkdir(parents=True, exist_ok=True)
MANIFEST = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
PROBE = json.loads((REVIEW / 'candidates/candidate_video_ledger.json').read_text(encoding='utf-8'))
PROBE_MANIFEST = json.loads((REVIEW / 'candidates/candidate_review_manifest.json').read_text(encoding='utf-8'))
ASSETS = {a['id']: a for a in MANIFEST['assets']}
LEDGER = {e['id']: e for e in PROBE['assets']}
FPS = int(SPEC['fps'])
FRAME_DURATIONS = [257, 257, 257, 257, 257, 257, 258]
assert sum(FRAME_DURATIONS) == int(SPEC['frame_count']) == 1800
assert FPS == 30 and abs(SPEC['duration'] - 60.0) < 1e-9


def false_guardrails():
    return {
        'full_motion_review': False,
        'native_audio_listening': False,
        'human_approval': False,
        'sign_off': False,
        'audience_result_promise': False,
        'virality_guarantee': False,
        'perfection_claim': False,
        'retention_claim': False,
        'hypnosis_claim': False,
        'three_x_claim': False,
        'subscribe_claim': False,
        'like_claim': False,
        'same_path_replacement': False,
        'factual_superlative_claim': False,
        'third_party_repost': False,
        'ai_audio': False,
        'generated_calls': False,
        'v3_audio_packages': False,
        'audio_substitution': False,
        'earshot_claim': False,
        'model_claim': False,
        'sound_design_layers': False,
        'sub_bloom_layers': False,
        'native_ambience_layers': False,
        'ambience_layers': False,
        'cue_layers': False,
        'current_trending_claim': False,
        'unverified_social_repost': False,
    }


def main():
    pm = PROBE_MANIFEST['flags']
    required = ['runner_probe_passed', 'runner_audio_visual_probe_passed', 'runner_visual_motion_probe', 'contact_sheets_written', 'source_review_recorded']
    if not all(bool(pm.get(k)) for k in required):
        raise RuntimeError('Runner probe manifest is incomplete: ' + repr({k: pm.get(k) for k in required}))
    eligible = []
    for aid, e in LEDGER.items():
        best = e.get('best_window')
        if not e.get('probe_completed') or not e.get('audio_stream_present') or not best:
            continue
        if not e.get('runner_audio_visual_probe_passed') or not e.get('runner_visual_motion_probe'):
            continue
        if best['rms_dbfs'] <= SPEC['audio_policy']['native_audible_segment_rms_dbfs_min']:
            continue
        if e.get('duration_seconds', 0.0) < best['start'] + 8.6:
            continue
        eligible.append({
            'id': aid,
            'score': float(best['score']),
            'best': best,
            'entry': e,
        })
    if len(eligible) < 7:
        raise RuntimeError('Only ' + str(len(eligible)) + ' runner-probed audio/motion candidates are eligible; need seven')
    eligible.sort(key=lambda z: z['score'], reverse=True)
    chosen = eligible[:7][::-1]  # lowest selected score opens at #7, strongest closes at #1

    start_frame = 0
    scenes = []
    for i, item in enumerate(chosen):
        aid = item['id']
        asset = ASSETS[aid]
        e = item['entry']
        best = item['best']
        frames = FRAME_DURATIONS[i]
        end_frame = start_frame + frames
        duration = frames / FPS
        source_duration = float(e.get('duration_seconds') or asset['duration_seconds'])
        source_start = float(best['start'])
        source_start = min(source_start, max(0.0, source_duration - 8.6 - 0.05))
        source_start = round(source_start, 3)
        scenes.append({
            'id': f"rank{7 - i}_{aid}",
            'rank': 7 - i,
            'title': asset['moment_label'],
            'moment_label': asset['moment_label'],
            'reaction_text': asset['reaction_text'],
            'emoji': asset['emoji'],
            'source_id': aid,
            'source_page': asset['source_page'],
            'license': asset['license'],
            'creator': asset['creator'],
            'local_filename': asset['local_filename'],
            'start_frame': start_frame,
            'end_frame': end_frame,
            'frames': frames,
            'start': round(start_frame / FPS, 6),
            'end': round(end_frame / FPS, 6),
            'duration': round(duration, 6),
            'source_start': source_start,
            'source_out': round(source_start + duration, 6),
            'focus_x': asset['focus_x'],
            'focus_y': asset['focus_y'],
            'zoom_start': 1.0,
            'zoom_end': 1.0,
            'payoff_at': SPEC['visual']['payoff_at'],
            'reaction_at': SPEC['visual']['reaction_at'],
            'label_reveal_at': SPEC['visual']['label_reveal_at'],
            'payoff_zoom': SPEC['visual']['payoff_zoom'],
            'audio_present': bool(e.get('audio_stream_present')),
            'audio_codec': e.get('audio_codec'),
            'runner_audio_rms_dbfs': best['rms_dbfs'],
            'runner_motion_score': best['motion_score'],
            'runner_window_score': best['score'],
            'runner_audio_visual_probe_passed': True,
            'runner_visual_motion_probe': True,
            'selected_from_runner_probe': True,
            'rights_cleared_social_origin_file_only': True,
            'no_unverified_reposts': True,
            'api_verification_required': True,
            'added_audio_layers': 0,
        })
        start_frame = end_frame
    if start_frame != 1800 or abs(scenes[-1]['end'] - 60.0) > 1e-9:
        raise RuntimeError('Selected timeline does not end at exactly 1800 frames / 60.0 seconds')

    flags = {
        'runner_probe_passed': True,
        'runner_audio_visual_probe_passed': True,
        'runner_visual_motion_probe': True,
        'contact_sheets_written': True,
        'source_review_recorded': True,
        'visual_lock_written': True,
        **false_guardrails(),
    }
    selected = {
        'edition': 'social_origin_v7',
        'duration': 60.0,
        'frame_count': 1800,
        'fps': FPS,
        'selected_count': 7,
        'rank_steps': [7, 6, 5, 4, 3, 2, 1],
        'scenes': scenes,
        'flags': flags,
        'probe_basis': 'Objective runner native-audio RMS and one-frame-per-second motion scores; exact windows locked for seven distinct rights-cleared social-origin Commons originals; no crop or zoom.',
        'source_order': [s['source_id'] for s in scenes],
        'runner_audio_visual_probe_passed': True,
        'runner_probe_passed': True,
        'runner_visual_motion_probe': True,
        'contact_sheets_written': True,
        'source_review_recorded': True,
        'visual_lock_written': True,
        'full_motion_review': False,
        'native_audio_listening': False,
        'human_approval': False,
        'sign_off': False,
        'audience_result_promise': False,
        'virality_guarantee': False,
    }
    (REVIEW / 'selected_windows.json').write_text(json.dumps(selected, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    lock = {
        'status': 'LOCKED_FOR_V7_RENDER',
        'edition': 'social_origin_v7',
        'source': 'Seven rights-cleared PD/CC BY Wikimedia Commons social-origin originals chosen by the runner audio/motion probe; no crop, no unverified reposts.',
        'review_basis': 'Objective runner audio/motion measurements and one-frame-per-second contact sheets; exact windows locked for seven selected moments only.',
        'flags': flags,
        'exact_timecodes': [{
            'rank': s['rank'], 'timeline_in': s['start'], 'timeline_out': s['end'],
            'source_id': s['source_id'], 'source_in': s['source_start'], 'source_out': s['source_out'],
            'frames': s['frames'], 'title': s['title'], 'moment_label': s['moment_label'],
            'reaction_text': s['reaction_text'],
            'emoji': s['emoji'], 'runner_audio_rms_dbfs': s['runner_audio_rms_dbfs'],
            'runner_motion_score': s['runner_motion_score'],
        } for s in scenes],
        'runner_probe_passed': True,
        'runner_audio_visual_probe_passed': True,
        'runner_visual_motion_probe': True,
        'contact_sheets_written': True,
        'source_review_recorded': True,
        'visual_lock_written': True,
        **false_guardrails(),
    }
    (REVIEW / 'visual_review_lock.json').write_text(json.dumps(lock, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Selected seven moments', selected['source_order'], flush=True)
    print('Exact frames', sum(FRAME_DURATIONS), 'duration', scenes[-1]['end'], flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
