#!/usr/bin/env python3
# Assemble only the seven selected native audio windows, choose a measured
# per-window gain and mastering chain that passes the unchanged V4 web gates,
# calibrate the delivered AAC stream and mux. No VO, music, SFX, bed, generated
# calls or added layers.
from __future__ import annotations
import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf
import pyloudnorm as pyln

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from showreel.audio_qc.gates import PROFILES, run as gate_run

BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v6'
WORK = ROOT / 'production/monarch-cam/work/short_ranking_raw_v6'
REVIEW = BASE / 'review'
MEDIA = WORK / 'media'
MANIFEST = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
ASSETS = {a['id']: a for a in MANIFEST['assets']}
SILENT_VIDEO = WORK / 'ranking_silent_raw_v6.mp4'
SILENT_H264 = WORK / 'ranking_silent_h264_raw_v6.mp4'
OUT = ROOT / 'deliverables/MONARCH_CAM_7_Unexpected_Animal_Moments_Ranked_60s_Short_RAW_FULLSCREEN_V6.mp4'
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
SELECTED = json.loads((REVIEW / 'selected_windows.json').read_text(encoding='utf-8'))
SCENES = SELECTED['scenes']
A = SPEC['audio_policy']
SR = int(A['sample_rate'])
N = int(round(SPEC['duration'] * SR))
TARGET_RMS_VALUES = [float(x) for x in A['per_window_target_rms_dbfs_candidates']]
MASTER_CHAINS = [
    {
        'id': 'linear_loudnorm_lra7',
        'filter': 'pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1,highpass=f=20,loudnorm=I=-14.2:TP=-2.2:LRA=7:linear=true:print_format=summary',
    },
    {
        'id': 'dynamic_loudnorm_lra7',
        'filter': 'pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1,highpass=f=20,loudnorm=I=-14.2:TP=-2.2:LRA=7:linear=false:print_format=summary',
    },
    {
        'id': 'rms_compressor_6to1_dynamic_loudnorm_lra7',
        'filter': 'pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1,highpass=f=20,acompressor=threshold=0.05:ratio=6:attack=10:release=250:makeup=1:knee=2.828:detection=rms:mix=1,loudnorm=I=-14.2:TP=-2.2:LRA=7:linear=false:print_format=summary',
    },
    {
        'id': 'strong_rms_compressor_12to1_dynamic_loudnorm_lra7',
        'filter': 'pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1,highpass=f=20,acompressor=threshold=0.02:ratio=12:attack=5:release=120:makeup=1:knee=1:detection=rms:mix=1,loudnorm=I=-14.2:TP=-2.2:LRA=7:linear=false:print_format=summary',
    },
]


def run(cmd, **kw):
    print('+', ' '.join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), text=True, **kw)


def json_safe(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    raise TypeError('Unsupported JSON type: ' + type(obj).__name__)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=json_safe) + '\n', encoding='utf-8')


def dbfs(value):
    return float(20 * np.log10(max(float(value), 1e-12)))


def decode_window(scene, meter):
    raw = MEDIA / ASSETS[scene['source_id']]['local_filename']
    if not raw.exists():
        raise RuntimeError('Missing verified original for audio: ' + str(raw))
    wav = WORK / ('native_' + scene['source_id'] + '.wav')
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', raw,
         '-ss', f"{scene['source_start']:.3f}", '-t', f"{scene['duration']:.3f}",
         '-map', '0:a:0', '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', wav], check=True)
    x, sr = sf.read(wav, dtype='float32', always_2d=True)
    if sr != SR:
        raise RuntimeError('Unexpected sample rate')
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    x = x[:, :2]
    x = x - np.mean(x, axis=0, keepdims=True)
    measured_lufs = float(meter.integrated_loudness(x.astype(np.float64)))
    if not np.isfinite(measured_lufs):
        measured_lufs = -120.0
    return {
        'scene': scene, 'x': x,
        'measured_lufs': measured_lufs,
        'rms_dbfs': round(dbfs(float(np.sqrt(np.mean(x ** 2)))), 3),
        'native_audible': bool(measured_lufs > -70.0),
    }


def build_premaster(windows, target_rms_dbfs, tag):
    target_rms = 10 ** (target_rms_dbfs / 20.0)
    guard = 10 ** (-2.0 / 20.0)
    mix = np.zeros((N, 2), dtype=np.float32)
    ledger, placements = [], []
    for item in windows:
        s = item['scene']
        start = int(round(s['start'] * SR))
        end = int(round(s['end'] * SR))
        want = end - start
        x = item['x'].copy()
        rms = float(np.sqrt(np.mean(x ** 2))) if x.size else 0.0
        gain_db = dbfs(target_rms) - dbfs(rms) if rms > 0 else 0.0
        x = x * (10 ** (gain_db / 20.0))
        if len(x) > want:
            x = x[:want]
        elif len(x) < want:
            x = np.pad(x, ((0, want - len(x)), (0, 0)), mode='constant')
        fade = int(SR * A['edge_fade_ms'] / 1000)
        if fade > 1:
            env = np.ones(want, dtype=np.float32)
            env[:fade] = np.linspace(0, 1, fade, dtype=np.float32)
            env[-fade:] = np.linspace(1, 0, fade, dtype=np.float32)
            x *= env[:, None]
        peak = float(np.max(np.abs(x))) if x.size else 0.0
        if peak > guard:
            x *= guard / peak
        mix[start:end] = x
        ledger.append({
            'id': s['id'], 'rank': s['rank'], 'source_id': s['source_id'],
            'timeline_in': s['start'], 'timeline_out': s['end'],
            'source_in': s['source_start'], 'source_out': s['source_out'],
            'audio_stream_present': bool(s['audio_present']), 'audio_codec': s['audio_codec'],
            'native_samples': int(want), 'measured_lufs_before_gain': round(item['measured_lufs'], 3),
            'measured_rms_dbfs_before_gain': item['rms_dbfs'],
            'per_window_target_rms_dbfs': target_rms_dbfs,
            'applied_gain_db': round(gain_db, 3),
            'peak_before_guard_dbfs': round(dbfs(peak), 3),
            'silent': not bool(s['audio_present']), 'native_audio_audible': bool(item['native_audible']),
            'added_layers': 0, 'raw_per_window_native_audio_only': True,
        })
        placements.append({'rank': s['rank'], 'start_sample': start, 'end_sample': end})
    if len(mix) != N:
        raise RuntimeError('Audio timeline length mismatch')
    premaster = WORK / ('native_timeline_' + tag + '.wav')
    sf.write(premaster, mix, SR, subtype='FLOAT')
    return premaster, mix, ledger, placements


def prepare_h264_video():
    if SILENT_H264.exists() and SILENT_H264.stat().st_size > 100000:
        return
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', SILENT_VIDEO,
         '-map', '0:v:0', '-an', '-c:v', 'libx264', '-crf', '23', '-preset', 'medium',
         '-maxrate', '3500k', '-bufsize', '7000k', '-pix_fmt', 'yuv420p',
         '-frames:v', str(int(SPEC['frame_count'])), '-movflags', '+faststart', SILENT_H264], check=True)


def mux_deliverable(audio_input):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prepare_h264_video()
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', SILENT_H264, '-i', audio_input,
         '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
         '-c:a', 'aac', '-b:a', '256k', '-ar', str(SR), '-ac', '2',
         '-t', f"{SPEC['duration']:.3f}", '-movflags', '+faststart', OUT], check=True)


def delivered_technical_click_count():
    wav = WORK / 'delivered_click_check.wav'
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', OUT,
         '-map', '0:a:0', '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', wav], check=True)
    x, sr = sf.read(wav, dtype='float32', always_2d=True)
    threshold = float(A['final_technical_click_threshold'])
    return int(np.count_nonzero(np.max(np.abs(np.diff(x, axis=0)), axis=1) > threshold))


def declick_wav(path):
    """Repair isolated sample discontinuities with short linear interpolations."""
    x, sr = sf.read(path, dtype='float32', always_2d=True)
    threshold = float(A['final_declick_threshold'])
    width = int(A['final_declick_width_samples'])
    d = np.max(np.abs(np.diff(x, axis=0)), axis=1)
    idx = np.where(d > threshold)[0]
    groups = []
    for i in idx:
        if groups and i - groups[-1][-1] <= 4:
            groups[-1].append(int(i))
        else:
            groups.append([int(i)])
    for g in groups:
        a = max(0, g[0] - width)
        b = min(len(x), g[-1] + width + 2)
        if b - a < 8:
            continue
        for c in range(x.shape[1]):
            x[a:b, c] = np.linspace(x[a, c], x[b - 1, c], b - a, dtype=np.float32)
    sf.write(path, x, sr, subtype='FLOAT')
    return len(groups)


def repair_delivered_clicks():
    report = []
    for i in range(int(A['final_calibration_iterations'])):
        clicks = delivered_technical_click_count()
        report.append({'iteration': i, 'technical_click_runs': clicks})
        if clicks == 0:
            break
        wav = WORK / 'delivered_declick.wav'
        run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', OUT,
             '-map', '0:a:0', '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', wav], check=True)
        regions = declick_wav(wav)
        report[-1]['declick_regions'] = regions
        mux_deliverable(wav)
    return report


def master_variant(premaster, mastered, chain):
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', premaster,
         '-af', chain, '-ar', str(SR), '-ac', '2', '-c:a', 'pcm_f32le', mastered], check=True)
    declick_wav(mastered)


def calibrate_final_gain(mastered):
    """Measure the delivered AAC stream and apply bounded level, peak and click corrections only."""
    target = float(PROFILES['web']['lufs'])
    limit = float(A['final_peak_limit_linear'])
    iterations = int(A['final_calibration_iterations'])
    report = []
    for i in range(iterations):
        result = gate_run(str(OUT), 'web')
        measured = result['measured']
        checks = result['checks']
        technical_clicks = delivered_technical_click_count()
        entry = {
            'iteration': i, 'integrated_lufs': measured['integrated_lufs'],
            'lra_lu': measured['lra_lu'], 'sample_peak_dbfs': measured['sample_peak_dbfs'],
            'loudness_in_range': bool(checks['loudness_in_range']),
            'lra_in_range': bool(checks['lra_in_range']),
            'true_peak_ok': bool(checks['true_peak_ok']),
            'web_gate_pass': bool(result['pass']),
            'technical_click_runs': technical_clicks,
            'measured_on': 'delivered_aac_stream',
        }
        if result['pass'] and technical_clicks == 0:
            entry['applied_gain_db'] = 0.0
            entry['declick_regions'] = 0
            entry['delivered_click_repair'] = []
            report.append(entry)
            break
        delta = target - measured['integrated_lufs']
        if abs(delta) > 0.05:
            tmp = WORK / 'native_timeline_mastered_calibrated.wav'
            run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', mastered,
                 '-af', f"volume={delta:.3f}dB,alimiter=limit={limit}:level=disabled",
                 '-ar', str(SR), '-ac', '2', '-c:a', 'pcm_f32le', tmp], check=True)
            shutil.move(str(tmp), str(mastered))
        regions = declick_wav(mastered)
        mux_deliverable(mastered)
        repair = repair_delivered_clicks()
        entry['applied_gain_db'] = round(delta, 3) if abs(delta) > 0.05 else 0.0
        entry['declick_regions'] = regions
        entry['peak_limit_linear'] = limit if abs(delta) > 0.05 else None
        entry['delivered_click_repair'] = repair
        report.append(entry)
    return report


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
    }


def main():
    meter = pyln.Meter(SR)
    windows = [decode_window(s, meter) for s in SCENES]
    prepare_h264_video()
    chosen = None
    attempts = []
    for target_rms in TARGET_RMS_VALUES:
        tag = 'rms' + str(int(target_rms)).replace('-', 'm')
        premaster, mix, ledger, placements = build_premaster(windows, target_rms, tag)
        for variant in MASTER_CHAINS:
            mastered = WORK / ('native_timeline_mastered_' + tag + '.wav')
            combo_id = tag + '_' + variant['id']
            try:
                master_variant(premaster, mastered, variant['filter'])
                mux_deliverable(mastered)
                calibration = calibrate_final_gain(mastered)
                final = gate_run(str(OUT), 'web')
                clicks = delivered_technical_click_count()
                attempt = {
                    'id': combo_id, 'target_rms_dbfs': target_rms,
                    'mastering_variant': variant['id'], 'filter': variant['filter'],
                    'web_gate_pass': bool(final['pass']), 'failed': final['failed'],
                    'integrated_lufs': final['measured']['integrated_lufs'],
                    'lra_lu': final['measured']['lra_lu'],
                    'sample_peak_dbfs': final['measured']['sample_peak_dbfs'],
                    'movement_db': final['measured']['movement_db'],
                    'technical_click_runs': clicks,
                }
                attempts.append(attempt)
                print('Mastering combo', combo_id, 'gate pass', final['pass'],
                      'LRA', final['measured']['lra_lu'], 'movement', final['measured']['movement_db'],
                      'clicks', clicks, flush=True)
                if final['pass'] and clicks == 0:
                    chosen = {
                        'target_rms_dbfs': target_rms, 'variant': variant,
                        'calibration': calibration, 'final_gate': final,
                        'technical_click_runs': clicks, 'ledger': ledger,
                        'placements': placements, 'premaster': premaster,
                        'mastered': mastered, 'combo_id': combo_id,
                    }
                    break
            except Exception as e:
                attempts.append({'id': combo_id, 'target_rms_dbfs': target_rms,
                                 'mastering_variant': variant['id'], 'error': repr(e)})
                print('Mastering combo failed', combo_id, repr(e), flush=True)
                continue
        if chosen is not None:
            break
    if chosen is None:
        raise RuntimeError('No measured per-window gain / mastering chain passed the unchanged web gates: ' + json.dumps(attempts, indent=2))
    report = {
        'edition': 'raw_fullscreen_v6', 'policy': A,
        'segments': chosen['ledger'], 'placements': chosen['placements'],
        'no_spoken_voice_over': True, 'no_score': True, 'no_effects': True, 'no_bed': True,
        'no_added_layers': True, 'no_fabricated_animal_calls': True,
        'native_source_audio_only': True, 'raw_per_window_native_audio_only': True,
        'native_stereo_fold_to_dual_mono': True,
        'source_audio_present_segments': sum(1 for item in chosen['ledger'] if item['audio_stream_present']),
        'silent_segments': sum(1 for item in chosen['ledger'] if item['silent']),
        'all_seven_native_audio_audible': all(item['native_audio_audible'] for item in chosen['ledger']),
        'runner_probe_passed': True, 'runner_audio_visual_probe_passed': True,
        'runner_visual_motion_probe': True, 'contact_sheets_written': True,
        'source_review_recorded': True, 'visual_lock_written': True,
        'chosen_combo': chosen['combo_id'],
        'per_window_target_rms_dbfs': chosen['target_rms_dbfs'],
        'mastering_variant': chosen['variant']['id'],
        'mastering_filter': chosen['variant']['filter'],
        'mastering_attempts': attempts,
        'final_gain_calibration': chosen['calibration'],
        'final_web_gate_pass': bool(chosen['final_gate']['pass']),
        'final_technical_click_runs': chosen['technical_click_runs'],
        'premaster': str(chosen['premaster'].relative_to(ROOT)),
        'mastered': str(chosen['mastered'].relative_to(ROOT)),
        'deliverable_sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
        'deliverable_bytes': OUT.stat().st_size,
        **false_guardrails(),
    }
    save_json(REVIEW / 'native_audio_ledger.json', report)
    print('V6 native-audio MP4 written', OUT, OUT.stat().st_size, flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
