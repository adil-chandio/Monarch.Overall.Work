#!/usr/bin/env python3
# Audit native source audio across each CC0 clip to locate audible windows.
from __future__ import annotations
import json, math, os, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v4'
WORK = Path(os.environ.get('V4_WORK', str(ROOT / 'production/monarch-cam/work/short_ranking_raw_v4'))).resolve()
REVIEW = Path(os.environ.get('V4_REVIEW', str(BASE / 'review'))).resolve()
SOURCE_MEDIA = Path(os.environ.get('V4_SOURCE_MEDIA', str(ROOT / 'production/monarch-cam/work/short_ranking_v3/media'))).resolve()
MEDIA = WORK / 'media'
if not MEDIA.exists() or not any(MEDIA.iterdir()):
    MEDIA = SOURCE_MEDIA
REVIEW.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)
MANIFEST = json.loads((BASE / 'source_manifest_ranking.json').read_text())
SR = 48000
WIN = 0.5
SEG = 8.0


def run(cmd, **kw):
    print('+', ' '.join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), text=True, **kw)


def probe(path):
    p = run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path], capture_output=True, check=True)
    return json.loads(p.stdout)


def db(v):
    return round(float(max(-120.0, 20 * math.log10(max(float(v), 1e-9)))), 2)


def chunk_stats(x, sr, start, dur):
    a = int(round(start * sr))
    b = min(len(x), int(round((start + dur) * sr)))
    c = x[a:b]
    if not len(c):
        return -120.0, -120.0, 0
    ac = c - np.mean(c, axis=0, keepdims=True)
    rms = float(np.sqrt(np.mean(ac ** 2)))
    peak = float(np.max(np.abs(ac)))
    return db(rms), db(peak), int(len(c))


def main():
    report = {'edition': 'raw_fullscreen_v4', 'sample_rate': SR, 'window_seconds': WIN, 'segment_seconds': SEG, 'assets': {}}
    for asset in MANIFEST['assets']:
        aid = asset['id']
        raw = MEDIA / asset['local_filename']
        if not raw.exists():
            raise RuntimeError('Missing raw source for audit: ' + str(raw))
        info = probe(raw)
        streams = info.get('streams', [])
        audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
        duration = float(info.get('format', {}).get('duration', 0.0))
        entry = {
            'id': aid, 'file': str(raw.relative_to(ROOT)), 'duration_seconds': round(duration, 3),
            'audio_stream_present': audio is not None, 'audio_codec': (audio or {}).get('codec_name'),
            'windows': [], 'top_8s_windows': []
        }
        if audio is not None:
            wav = WORK / ('audio_audit_' + aid + '.wav')
            run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', raw,
                 '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', wav], check=True)
            x, sr = sf.read(wav, dtype='float32', always_2d=True)
            if sr != SR:
                raise RuntimeError('Unexpected audit rate')
            if x.shape[1] == 1:
                x = np.repeat(x, 2, axis=1)
            x = x[:, :2]
            duration = len(x) / SR
            entry['duration_seconds'] = round(duration, 3)
            starts = np.arange(0.0, max(0.0, duration - 0.001), WIN)
            for st in starts:
                st = float(round(st, 3))
                rms, peak, n = chunk_stats(x, SR, st, WIN)
                entry['windows'].append({'start': st, 'end': round(min(duration, st + WIN), 3), 'rms_dbfs': rms, 'peak_dbfs': peak, 'samples': n})
            segs = []
            for st in np.arange(0.0, max(0.0, duration - SEG + 0.001), 0.5):
                st = float(round(st, 3))
                rms, peak, n = chunk_stats(x, SR, st, min(SEG, duration - st))
                segs.append({'start': st, 'end': round(min(duration, st + SEG), 3), 'rms_dbfs': rms, 'peak_dbfs': peak, 'samples': n})
            segs.sort(key=lambda z: z['rms_dbfs'], reverse=True)
            entry['top_8s_windows'] = segs[:12]
            entry['audible_window_count'] = sum(1 for w in entry['windows'] if w['rms_dbfs'] > -55.0)
            entry['peak_window'] = max(entry['windows'], key=lambda z: z['rms_dbfs']) if entry['windows'] else None
        else:
            entry['audible_window_count'] = 0
            entry['peak_window'] = None
        report['assets'][aid] = entry
        print(aid, 'audio', entry['audio_stream_present'], 'audible windows', entry['audible_window_count'],
              'best', (entry['peak_window'] or {}).get('rms_dbfs', -120), flush=True)
    out = REVIEW / 'source_audio_audit.json'
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Audio audit written', out, flush=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
