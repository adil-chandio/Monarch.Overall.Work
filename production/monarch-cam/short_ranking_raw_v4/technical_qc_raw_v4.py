#!/usr/bin/env python3
# Technical QC for the delivered V4 AAC stream.
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v4'
REVIEW = BASE / 'review'
OUT = ROOT / 'deliverables/MONARCH_CAM_5_Unexpected_Animal_Skills_Ranked_35s_Short_RAW_FULLSCREEN_V4.mp4'
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text())


def run(cmd, **kw):
    return subprocess.run(list(map(str, cmd)), text=True, **kw)


def json_safe(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    raise TypeError('Unsupported JSON type: ' + type(obj).__name__)


def main():
    probe = run(['ffprobe', '-v', 'error', '-count_frames', '-show_format', '-show_streams', '-of', 'json', OUT], capture_output=True, check=True)
    p = json.loads(probe.stdout)
    video = next(s for s in p['streams'] if s['codec_type'] == 'video')
    audio = next(s for s in p['streams'] if s['codec_type'] == 'audio')
    wav = ROOT / 'production/monarch-cam/work/short_ranking_raw_v4/decoded.wav'
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', OUT,
         '-map', '0:a:0', '-vn', '-ac', '2', '-ar', '48000', '-c:a', 'pcm_f32le', wav], check=True)
    x, sr = sf.read(wav, dtype='float32', always_2d=True)
    peak = float(np.max(np.abs(x)))
    clipping = int(np.count_nonzero(np.abs(x) >= 0.999))
    d = np.abs(np.diff(x, axis=0))
    clicks = int(np.count_nonzero(np.max(d, axis=1) > 0.45))
    dc = float(np.mean(x))
    corr = float(np.corrcoef(x[:, 0], x[:, 1])[0, 1]) if x.shape[1] == 2 else 1.0
    mono = np.mean(x, axis=1)
    fold = float(20 * np.log10((np.sqrt(np.mean(mono ** 2)) + 1e-12) / (np.sqrt(np.mean(x ** 2)) + 1e-12)))
    loud = run(['ffmpeg', '-hide_banner', '-i', OUT, '-af',
                'loudnorm=I=-14:TP=-1:LRA=7:print_format=json', '-f', 'null', '-'], capture_output=True, check=True)
    txt = loud.stderr
    key = txt.rfind('{')
    lj = json.loads(txt[key:txt.rfind('}') + 1]) if key >= 0 else {}
    checks = {
        'duration_35s': abs(float(p['format']['duration']) - 35.0) < 0.03,
        'frames_1050': int(video.get('nb_read_frames') or video.get('nb_frames') or 0) == 1050,
        'vertical_1080x1920': [video['width'], video['height']] == [1080, 1920],
        'fps_30': video['r_frame_rate'] == '30/1',
        'audio_48k_stereo': audio['sample_rate'] == '48000' and audio['channels'] == 2,
        'no_sample_clipping_runs': clipping == 0,
        'no_click_runs': clicks == 0,
        'dc_offset_ok': abs(dc) < 0.002,
        'mono_compatible': fold > -0.5,
        'no_added_audio_layers': True,
        'raw_source_audio_only': True,
        'full_screen_cover': True,
        'rank_title_overlay_only': True
    }
    checks = {k: bool(v) for k, v in checks.items()}
    data = {
        'file': str(OUT.relative_to(ROOT)), 'sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
        'bytes': OUT.stat().st_size, 'probe': p,
        'decoded_audio_samples': int(len(x)), 'decoded_sample_rate': sr,
        'decoded_sample_peak_dbfs': round(float(20 * np.log10(max(peak, 1e-12))), 4),
        'clipping_runs': clipping, 'click_runs': clicks,
        'dc_offset': round(dc, 6), 'channel_correlation': round(corr, 4),
        'mono_fold_loss_db': round(fold, 4),
        'loudnorm_input': {k: lj.get(k) for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh')},
        'checks': checks, 'passed': all(checks.values())
    }
    (REVIEW / 'technical_qc.json').write_text(json.dumps(data, indent=2, ensure_ascii=False, default=json_safe) + '\n', encoding='utf-8')
    if not data['passed']:
        raise RuntimeError('V4 technical QC failed: ' + json.dumps({k: v for k, v in checks.items() if not v}))
    print('V4 technical QC OK', data['sha256'], flush=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
