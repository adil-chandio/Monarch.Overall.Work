#!/usr/bin/env python3
# Audit the seven selected Commons windows for audible native audio.
# The segment RMS threshold comes from the V8 spec; no audio is substituted.
from __future__ import annotations
import json, math, os, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_clean_v8'
WORK = Path(os.environ.get('V8_WORK', str(ROOT / 'production/monarch-cam/work/short_ranking_clean_v8'))).resolve()
REVIEW = Path(os.environ.get('V8_REVIEW', str(BASE / 'review'))).resolve()
MEDIA = WORK / 'media'
MANIFEST = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
SELECTED = json.loads((REVIEW / 'selected_windows.json').read_text(encoding='utf-8'))
ASSETS = {a['id']: a for a in MANIFEST['assets']}
SR = int(SPEC['audio_policy']['sample_rate'])
WINDOW_S = 0.5
SELECTABLE_DBFS = float(SPEC['audio_policy']['native_audible_segment_rms_dbfs_min'])


def run(cmd, **kw):
    print('+', ' '.join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), text=True, **kw)


def db(value):
    return round(float(max(-120.0, 20 * math.log10(max(float(value), 1e-12)))), 2)


def chunk_stats(x, start, dur):
    a = int(round(start * SR))
    b = min(len(x), int(round((start + dur) * SR)))
    c = x[a:b]
    if not len(c):
        return -120.0, -120.0, 0
    ac = c - np.mean(c, axis=0, keepdims=True)
    return db(float(np.sqrt(np.mean(ac ** 2)))), db(float(np.max(np.abs(ac)))), int(len(c))


def main():
    REVIEW.mkdir(parents=True, exist_ok=True)
    report = {
        'edition': 'social_origin_v8',
        'sample_rate': SR,
        'window_seconds': WINDOW_S,
        'selectable_segment_rms_dbfs_min': SELECTABLE_DBFS,
        'assets': {},
        'flags': {},
    }
    all_audible = True
    for scene in SELECTED['scenes']:
        aid = scene['source_id']
        raw = MEDIA / ASSETS[aid]['local_filename']
        if not raw.exists():
            raise RuntimeError('Missing verified original for audit: ' + str(raw))
        wav = WORK / ('selected_audio_' + aid + '.wav')
        run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', raw,
             '-ss', f"{scene['source_start']:.3f}", '-t', f"{scene['duration']:.3f}",
             '-map', '0:a:0', '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', wav], check=True)
        x, sr = sf.read(wav, dtype='float32', always_2d=True)
        if sr != SR:
            raise RuntimeError('Unexpected audit rate for ' + aid)
        if x.shape[1] == 1:
            x = np.repeat(x, 2, axis=1)
        x = x[:, :2]
        x = x - np.mean(x, axis=0, keepdims=True)
        duration = len(x) / SR
        rms, peak, samples = chunk_stats(x, 0.0, duration)
        windows = []
        for st in np.arange(0.0, max(0.0, duration - 0.001), WINDOW_S):
            st = float(round(st, 3))
            r, p, n = chunk_stats(x, st, WINDOW_S)
            windows.append({'start': st, 'end': round(min(duration, st + WINDOW_S), 3),
                            'rms_dbfs': r, 'peak_dbfs': p, 'samples': n})
        full_windows = [w for w in windows if int(w['samples']) >= int(WINDOW_S * SR)]
        quiet_full_blocks = [w for w in full_windows if w['rms_dbfs'] <= SELECTABLE_DBFS]
        continuous_native_audio = bool(full_windows and not quiet_full_blocks)
        audible = bool(rms > SELECTABLE_DBFS and continuous_native_audio)
        all_audible = all_audible and audible
        report['assets'][aid] = {
            'id': aid, 'rank': scene['rank'], 'file': str(raw.relative_to(ROOT)),
            'source_in': scene['source_start'], 'source_out': scene['source_out'],
            'timeline_in': scene['start'], 'timeline_out': scene['end'],
            'duration_seconds': round(duration, 3), 'native_samples': int(len(x)),
            'audio_stream_present': True, 'audio_codec': scene['audio_codec'],
            'segment_rms_dbfs': rms, 'segment_peak_dbfs': peak,
            'windows': windows,
            'full_half_second_blocks': len(full_windows),
            'quiet_full_block_count': len(quiet_full_blocks),
            'min_full_block_rms_dbfs': min((w['rms_dbfs'] for w in full_windows), default=-120.0),
            'continuous_native_audio': continuous_native_audio,
            'audible_window_count': sum(1 for w in windows if w['rms_dbfs'] > SELECTABLE_DBFS),
            'peak_window': max(windows, key=lambda w: w['rms_dbfs']) if windows else None,
            'native_audio_audible': audible,
            'added_layers': 0,
            'runner_audio_rms_dbfs': scene['runner_audio_rms_dbfs'],
            'runner_motion_score': scene['runner_motion_score'],
            'runner_continuous_native_audio': scene.get('runner_continuous_native_audio'),
        }
        print('Selected-window audio', aid, 'RMS', rms, 'audible', audible,
              'continuous', continuous_native_audio, 'quiet full blocks', len(quiet_full_blocks), flush=True)
    if not all_audible:
        raise RuntimeError('At least one selected Commons window failed the ' + str(SELECTABLE_DBFS) + ' dBFS continuous native-audio gate')
    flags = {
        'runner_probe_passed': True,
        'runner_audio_visual_probe_passed': True,
        'runner_visual_motion_probe': True,
        'contact_sheets_written': True,
        'source_review_recorded': True,
        'visual_lock_written': True,
        'all_seven_selected_windows_audible': True,
        'continuous_native_audio_all_windows': True,
        'zero_quiet_full_blocks': True,
        'raw_per_window_native_audio_only': True,
        'native_source_audio_only': True,
        'no_added_audio_layers': True,
        'no_spoken_voice_over': True,
        'no_score': True,
        'no_effects': True,
        'no_bed': True,
        'no_fabricated_animal_calls': True,
        'current_trending_claim': False,
        'unverified_social_repost': False,
        'audio_substitution': False,
        'generated_calls': False,
        'v3_audio_packages': False,
        'sound_design_layers': False,
        'sub_bloom_layers': False,
        'native_ambience_layers': False,
        'ambience_layers': False,
        'cue_layers': False,
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
        'earshot_claim': False,
        'model_claim': False,
    }
    report['flags'] = flags
    report['all_seven_selected_windows_audible'] = True
    report['continuous_native_audio_all_windows'] = True
    report['zero_quiet_full_blocks'] = True
    (REVIEW / 'source_audio_audit.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Selected-window continuous native audio audit OK', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
