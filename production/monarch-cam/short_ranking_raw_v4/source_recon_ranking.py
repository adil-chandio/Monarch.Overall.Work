#!/usr/bin/env python3
# Retrieve five verified CC0 animal clips, verify cached media, cut exact V4 windows,
# and rebuild compact V4 review sheets. No separate audio assets are downloaded.
from __future__ import annotations
import hashlib, json, math, os, re, shutil, subprocess, time
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v4'
OUT = Path(os.environ.get('V4_WORK', str(ROOT / 'production/monarch-cam/work/short_ranking_raw_v4'))).resolve()
REVIEW = Path(os.environ.get('V4_REVIEW', str(BASE / 'review'))).resolve()
SOURCE_MEDIA = Path(os.environ.get('V4_SOURCE_MEDIA', str(ROOT / 'production/monarch-cam/work/short_ranking_v3/media'))).resolve()
V3_REVIEW = ROOT / 'production/monarch-cam/short_ranking_v3/review'
LOCAL_MEDIA = OUT / 'media'
CLIPS = OUT / 'clips'
for p in (OUT, REVIEW, LOCAL_MEDIA, CLIPS):
    p.mkdir(parents=True, exist_ok=True)

MANIFEST = json.loads((BASE / 'source_manifest_ranking.json').read_text())
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text())
V3_LEDGER = {x['id']: x for x in json.loads((V3_REVIEW / 'source_video_ledger.json').read_text())}
HEADERS = {'User-Agent': 'MonarchCamRawV4/1.0 (+CC0 Wikimedia Commons review)'}


def run(cmd, **kw):
    print('+', ' '.join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), text=True, **kw)


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda: f.read(1024 * 1024), b''):
            h.update(c)
    return h.hexdigest()


def font(size):
    for c in [Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def get_raw(asset):
    name = asset['local_filename']
    dest = LOCAL_MEDIA / name
    expected = V3_LEDGER.get(asset['id'], {}).get('sha256')
    for src in [dest, SOURCE_MEDIA / name]:
        if src.exists() and src.stat().st_size >= 100000 and (not expected or sha256(src) == expected):
            if src != dest:
                shutil.copy2(src, dest)
            print('Using verified cached', asset['id'], dest.stat().st_size, flush=True)
            return dest
    last = None
    for url in asset['download_urls']:
        try:
            r = requests.get(url, headers=HEADERS, timeout=60, allow_redirects=True)
            r.raise_for_status()
            if len(r.content) < 100000:
                raise RuntimeError('short response')
            dest.write_bytes(r.content)
            if expected and sha256(dest) != expected:
                raise RuntimeError('sha256 mismatch')
            print('Retrieved', asset['id'], len(r.content), flush=True)
            return dest
        except Exception as e:
            last = e
            print('Candidate failed', asset['id'], url, repr(e), flush=True)
    raise RuntimeError('Could not retrieve ' + asset['id'] + ': ' + repr(last))


def probe(path, aid):
    p = run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path], capture_output=True, check=True)
    data = json.loads(p.stdout)
    (OUT / ('source_probe_' + aid + '.json')).write_text(json.dumps(data, indent=2), encoding='utf-8')
    return data


def cut_clip(asset, raw, scene):
    aid = asset['id']
    out = CLIPS / ('clip_' + aid + '.mp4')
    n = int(round(scene['duration'] * SPEC['fps']))
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', raw,
           '-ss', f"{scene['source_start']:.3f}", '-t', f"{scene['duration']:.3f}",
           '-map', '0:v:0', '-map', '0:a:0?', '-vf', f"fps={SPEC['fps']}",
           '-frames:v', str(n), '-c:v', 'libx264', '-crf', '18', '-preset', 'fast',
           '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out]
    run(cmd, check=True)
    q = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames,width,height,r_frame_rate', '-of', 'json', out], capture_output=True, check=True)
    info = json.loads(q.stdout)['streams'][0]
    if int(info['nb_frames']) != n:
        raise RuntimeError(f"Unexpected {aid} clip frames {info['nb_frames']} != {n}")
    return out, info


def make_sheets(aid, clip, scene):
    frames_dir = OUT / 'frames'
    frames_dir.mkdir(parents=True, exist_ok=True)
    for old in frames_dir.glob(aid + '_*.jpg'):
        old.unlink()
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', clip,
         '-vf', 'fps=1,scale=320:-2', '-q:v', '3', '-start_number', '0',
         frames_dir / (aid + '_%04d.jpg')], check=True)
    frames = sorted(frames_dir.glob(aid + '_*.jpg'))
    if not frames:
        raise RuntimeError('No review frames for ' + aid)
    cols, rows, cw, ch = 4, 2, 336, 246
    pages = math.ceil(len(frames) / (cols * rows))
    paths = []
    for page in range(pages):
        chunk = frames[page * cols * rows:(page + 1) * cols * rows]
        canvas = Image.new('RGB', (cols * cw, 64 + rows * ch), '#101820')
        d = ImageDraw.Draw(canvas)
        d.text((16, 10), f"V4 FULL-SCREEN BEST MOMENT - {aid.upper()} - PAGE {page + 1}/{pages}", font=font(18), fill='#F4F1E8')
        d.text((16, 36), 'One frame every 1s - labels are source timestamps', font=font(14), fill='#A9B8C4')
        for i, fp in enumerate(chunk):
            m = re.search(r'_(\d+)\.jpg$', fp.name)
            t = scene['source_start'] + (int(m.group(1)) if m else i)
            im = Image.open(fp).convert('RGB')
            im.thumbnail((320, 202), Image.Resampling.LANCZOS)
            tile = Image.new('RGB', (320, 202), '#05080B')
            tile.paste(im, ((320 - im.width) // 2, (202 - im.height) // 2))
            x = (i % cols) * cw + 8
            y = 64 + (i // cols) * ch
            canvas.paste(tile, (x, y))
            d.text((x + 4, y + 207), f"{int(t)//60:02d}:{t%60:04.1f}", font=font(19), fill='#63D7C8')
        out = REVIEW / f"v4_{aid}_contact_sheet_{page + 1:02d}.jpg"
        canvas.save(out, quality=92)
        paths.append(str(out.relative_to(ROOT)))
    return len(frames), paths


def copy_v3_sheets():
    copied = []
    for p in sorted(V3_REVIEW.glob('coarse_*_contact_sheet_*.jpg')) + sorted(V3_REVIEW.glob('fine_*_contact_sheet_*.jpg')):
        q = REVIEW / ('source_' + p.name)
        shutil.copy2(p, q)
        copied.append(str(q.relative_to(ROOT)))
    for name in ['source_poster.jpg', 'source_poster_starfish.jpg']:
        p = V3_REVIEW / name
        if p.exists():
            q = REVIEW / name
            shutil.copy2(p, q)
    return copied


def main():
    started = time.time()
    ledger, windows, sheets = [], {}, []
    for asset in MANIFEST['assets']:
        aid = asset['id']
        scene = next(s for s in SPEC['scenes'] if s['source_id'] == aid)
        raw = get_raw(asset)
        info = probe(raw, aid)
        streams = info.get('streams', [])
        video = next((s for s in streams if s.get('codec_type') == 'video'), {})
        audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
        if [int(video.get('width', 0)), int(video.get('height', 0))] != [asset['width'], asset['height']]:
            raise RuntimeError('Unexpected geometry ' + aid)
        clip, clip_info = cut_clip(asset, raw, scene)
        n, paths = make_sheets(aid, clip, scene)
        sheets.extend(paths)
        windows[aid] = {'start': scene['source_start'], 'end': scene['source_start'] + scene['duration'], 'duration': scene['duration']}
        ledger.append({
            'id': aid, 'raw_file': str(raw.relative_to(ROOT)), 'clip_file': str(clip.relative_to(ROOT)),
            'bytes': raw.stat().st_size, 'sha256': sha256(raw),
            'source_page': asset['source_page'], 'license': asset['license'], 'creator': asset['creator'],
            'duration_seconds': float(info.get('format', {}).get('duration', 0.0)),
            'width': int(video.get('width', 0)), 'height': int(video.get('height', 0)),
            'video_codec': video.get('codec_name'), 'audio_codec': (audio or {}).get('codec_name'),
            'audio_stream_present': audio is not None, 'clip_frames': int(clip_info['nb_frames']),
            'rank': scene['rank'], 'title': scene['title'], 'timeline_in': scene['start'], 'timeline_out': scene['end'],
            'source_in': scene['source_start'], 'source_out': scene['source_start'] + scene['duration'],
            'review_frames': n
        })
    copied = copy_v3_sheets()
    (REVIEW / 'source_video_ledger.json').write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (REVIEW / 'source_windows.json').write_text(json.dumps(windows, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    review_manifest = {
        'topic': SPEC['topic'], 'edition': 'raw_fullscreen_v4',
        'source_pages': {a['id']: a['source_page'] for a in MANIFEST['assets']},
        'rights_declaration': 'All five picture sources are CC0 1.0 via Wikimedia Commons; attribution is given voluntarily.',
        'credits': {a['id']: a['creator'] for a in MANIFEST['assets']},
        'source_video_ledger': str((REVIEW / 'source_video_ledger.json').relative_to(ROOT)),
        'source_windows': str((REVIEW / 'source_windows.json').relative_to(ROOT)),
        'v4_selected_window_sheets': sheets,
        'source_contact_sheets': copied,
        'source_poster': str((REVIEW / 'source_poster.jpg').relative_to(ROOT)),
        'visual_timestamp_approval': 'LOCKED_AFTER_CONTACT_SHEET_REVIEW',
        'full_motion_review': False, 'native_audio_listening': False,
        'retrieved_unix': int(started)
    }
    (REVIEW / 'review-manifest.json').write_text(json.dumps(review_manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(review_manifest, indent=2), flush=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
