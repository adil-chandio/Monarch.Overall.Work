#!/usr/bin/env python3
# Assemble only the native source audio from each selected V4 window, then mux.
from __future__ import annotations
import hashlib, json, os, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
import pyloudnorm as pyln

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v4'
WORK = ROOT / 'production/monarch-cam/work/short_ranking_raw_v4'
REVIEW = BASE / 'review'
CLIPS = WORK / 'clips'
MEDIA = WORK / 'media'
MANIFEST = json.loads((BASE / 'source_manifest_ranking.json').read_text())
ASSETS = {a['id']: a for a in MANIFEST['assets']}
SILENT_VIDEO = WORK / 'ranking_silent_raw_v4.mp4'
OUT = ROOT / 'deliverables/MONARCH_CAM_5_Unexpected_Animal_Skills_Ranked_35s_Short_RAW_FULLSCREEN_V4.mp4'
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text())
A = SPEC['audio_policy']
SR = A['sample_rate']
N = int(round(SPEC['duration'] * SR))
mix = np.zeros((N, 2), dtype=np.float32)


def run(cmd, **kw):
    print('+', ' '.join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), text=True, **kw)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def decode_window(scene):
    raw = MEDIA / ASSETS[scene['source_id']]['local_filename']
    if not raw.exists():
        raw = Path(os.environ.get('V4_SOURCE_MEDIA', str(ROOT / 'production/monarch-cam/work/short_ranking_v3/media'))) / ASSETS[scene['source_id']]['local_filename']
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
    return x


def main():
    meter = pyln.Meter(SR)
    ledger, placements = [], []
    for s in SPEC['scenes']:
        start = int(round(s['start'] * SR))
        end = int(round(s['end'] * SR))
        want = end - start
        native_audible = False
        if s['audio_present']:
            x = decode_window(s)
            measured = float(meter.integrated_loudness(x.astype(np.float64)))
            if np.isfinite(measured) and measured > -70.0:
                native_audible = True
                gain_db = A['target_integrated_lufs'] - measured
                x = x * (10 ** (gain_db / 20.0))
            else:
                gain_db = 0.0
        else:
            x = np.zeros((want, 2), dtype=np.float32)
            measured = -120.0
            gain_db = 0.0
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
        guard = 10 ** (-2.0 / 20.0)
        if peak > guard:
            x *= guard / peak
        mix[start:end] = x
        ledger.append({
            'id': s['id'], 'rank': s['rank'], 'source_id': s['source_id'],
            'timeline_in': s['start'], 'timeline_out': s['end'],
            'source_in': s['source_start'], 'source_out': s['source_start'] + s['duration'],
            'audio_stream_present': s['audio_present'], 'audio_codec': s['audio_codec'],
            'native_samples': int(want), 'measured_lufs_before_gain': round(measured, 3),
            'applied_gain_db': round(gain_db, 3), 'peak_before_guard_dbfs': round(20 * np.log10(max(peak, 1e-12)), 3),
            'silent': not s['audio_present'], 'native_audio_audible': native_audible, 'added_layers': 0
        })
        placements.append({'rank': s['rank'], 'start_sample': start, 'end_sample': end})
    if len(mix) != N:
        raise RuntimeError('Audio timeline length mismatch')
    premaster = WORK / 'native_timeline.wav'
    sf.write(premaster, mix, SR, subtype='FLOAT')
    mastered = WORK / 'native_timeline_mastered.wav'
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', premaster,
         '-af', f"highpass=f=20,loudnorm=I={A['target_integrated_lufs']}:TP={A['true_peak_target_dbtp']}:LRA=7:linear=true:print_format=summary",
         '-ar', str(SR), '-ac', '2', '-c:a', 'pcm_f32le', mastered], check=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', SILENT_VIDEO, '-i', mastered,
         '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
         '-ar', str(SR), '-ac', '2', '-t', f"{SPEC['duration']:.3f}", '-movflags', '+faststart', OUT], check=True)
    save_json(REVIEW / 'native_audio_ledger.json', {
        'edition': 'raw_fullscreen_v4', 'policy': A, 'segments': ledger, 'placements': placements,
        'no_spoken_voice_over': True, 'no_score': True, 'no_effects': True,
        'no_added_layers': True, 'no_fabricated_animal_calls': True,
        'native_source_audio_only': True,
        'source_audio_present_segments': sum(1 for item in ledger if item['audio_stream_present']),
        'silent_segments': sum(1 for item in ledger if item['silent']),
        'all_five_native_audio_audible': all(item['native_audio_audible'] for item in ledger),
        'premaster': str(premaster.relative_to(ROOT)), 'mastered': str(mastered.relative_to(ROOT)),
        'deliverable_sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
        'deliverable_bytes': OUT.stat().st_size
    })
    print('V4 native-audio MP4 written', OUT, OUT.stat().st_size, flush=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
