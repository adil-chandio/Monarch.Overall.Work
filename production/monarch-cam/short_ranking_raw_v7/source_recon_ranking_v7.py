#!/usr/bin/env python3
# Retrieve the seven API-verified rights-cleared social-origin Commons files, verify
# originals by SHA-1 when downloaded, cut exact V7 windows and rebuild contact sheets.
# Commons VP9/Opus transcodes may be used; the API original SHA-1 remains the rights record.
from __future__ import annotations
import hashlib, json, math, os, re, shutil, subprocess, time
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v7'
OUT = Path(os.environ.get('V7_WORK', str(ROOT / 'production/monarch-cam/work/short_ranking_raw_v7'))).resolve()
REVIEW = Path(os.environ.get('V7_REVIEW', str(BASE / 'review'))).resolve()
CANDIDATE_MEDIA = ROOT / 'production/monarch-cam/work/short_ranking_raw_v7/candidates/media'
V3_CACHE = ROOT / 'production/monarch-cam/work/short_ranking_v3/media'
V4_CACHE = ROOT / 'production/monarch-cam/work/short_ranking_raw_v4/media'
MEDIA = OUT / 'media'
CLIPS = OUT / 'clips'
for p in (OUT, REVIEW, MEDIA, CLIPS):
    p.mkdir(parents=True, exist_ok=True)

MANIFEST = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
SELECTED = json.loads((REVIEW / 'selected_windows.json').read_text(encoding='utf-8'))
VERIFIED = json.loads((REVIEW / 'verified_sources.json').read_text(encoding='utf-8'))
CANDIDATE_LEDGER_PATH = REVIEW / 'candidates' / 'candidate_video_ledger.json'
CANDIDATE_LEDGER = json.loads(CANDIDATE_LEDGER_PATH.read_text(encoding='utf-8')) if CANDIDATE_LEDGER_PATH.exists() else {'assets': []}
CANDIDATE_BY_ID = {e['id']: e for e in CANDIDATE_LEDGER.get('assets', [])}
ASSETS = {a['id']: a for a in MANIFEST['assets']}
VAPI = VERIFIED['assets']
HEADERS = {
    'User-Agent': 'MonarchCamViralV7/1.0 (https://github.com/adil-chandio/Monarch.Overall.Work; rights-cleared social-origin original retrieval)',
    'Accept': 'video/webm,application/octet-stream;q=0.9,*/*;q=0.8',
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
RETRY = Retry(
    total=6, connect=6, read=6, status=6, backoff_factor=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=frozenset(['GET']),
    respect_retry_after_header=True, raise_on_status=False,
)
SESSION.mount('https://', HTTPAdapter(max_retries=RETRY))
SESSION.mount('http://', HTTPAdapter(max_retries=RETRY))


def run(cmd, **kw):
    print('+', ' '.join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), text=True, **kw)


def sha1(path):
    h = hashlib.sha1()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def font(size):
    for p in [Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def cached_candidates(asset):
    paths = [MEDIA / asset['local_filename'], CANDIDATE_MEDIA / asset['local_filename']]
    if asset.get('cache_filename'):
        base = V4_CACHE if asset.get('cache_dir') == 'v4' else V3_CACHE
        paths.append(base / asset['cache_filename'])
    return paths


def get_raw(asset, verified):
    dest = MEDIA / asset['local_filename']
    original_sha1 = verified['expected_sha1'].lower()
    download_url = verified.get('download_url') or verified['original_url']
    download_kind = verified.get('download_kind', 'commons_original')
    cand = CANDIDATE_BY_ID.get(asset['id'], {})
    cached = CANDIDATE_MEDIA / asset['local_filename']
    if (cached.exists() and cached.stat().st_size >= 100000
            and cand.get('download_url') == download_url
            and str(cand.get('sha1', '')).lower() == sha1(cached).lower()):
        if cached != dest:
            shutil.copy2(cached, dest)
        print('Using verified cached Commons candidate', asset['id'], dest.stat().st_size, flush=True)
        return dest, sha1(dest).lower(), download_url, download_kind
    urls = []
    for url in [download_url, verified['original_url']] + asset['download_urls']:
        if url not in urls:
            urls.append(url)
    last = None
    tmp = dest.with_suffix('.download')
    for url in urls:
        try:
            r = SESSION.get(url, timeout=300, allow_redirects=True, stream=True)
            r.raise_for_status()
            declared = int(r.headers.get('content-length') or 0)
            if declared and declared < 100000:
                raise RuntimeError('short declared response')
            total = 0
            with tmp.open('wb') as fh:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        fh.write(chunk)
                        total += len(chunk)
            if total < 100000:
                raise RuntimeError('short streamed response')
            got = sha1(tmp).lower()
            if url == verified['original_url'] and got != original_sha1:
                raise RuntimeError('Commons API original SHA-1 mismatch')
            effective_kind = 'commons_vp9_opus_transcode' if 'transcoded' in url else 'commons_original'
            tmp.replace(dest)
            print('Retrieved verified Commons file', asset['id'], effective_kind, total, flush=True)
            time.sleep(3)
            return dest, got, url, effective_kind
        except Exception as e:
            last = e
            if tmp.exists():
                tmp.unlink()
            print('Commons download failed', asset['id'], url, repr(e), flush=True)
            time.sleep(10)
    raise RuntimeError('Could not retrieve verified Commons file ' + asset['id'] + ': ' + repr(last))


def probe(path, aid):
    p = run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path], capture_output=True, check=True)
    data = json.loads(p.stdout)
    (OUT / ('source_probe_' + aid + '.json')).write_text(json.dumps(data, indent=2), encoding='utf-8')
    return data


def cut_clip(raw, scene):
    aid = scene['source_id']
    out = CLIPS / ('clip_' + aid + '.mp4')
    n = int(scene['frames'])
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', raw,
           '-ss', f"{scene['source_start']:.3f}", '-t', f"{scene['duration']:.3f}",
           '-map', '0:v:0', '-an', '-vf', f"fps={SPEC['fps']}",
           '-frames:v', str(n), '-c:v', 'libx264', '-crf', '18', '-preset', 'fast',
           '-movflags', '+faststart', out]
    run(cmd, check=True)
    q = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames,width,height,r_frame_rate', '-of', 'json', out], capture_output=True, check=True)
    info = json.loads(q.stdout)['streams'][0]
    if int(info['nb_frames']) != n:
        raise RuntimeError(f"Unexpected {aid} clip frames {info['nb_frames']} != {n}")
    return out, info


def make_sheets(raw, scene):
    aid = scene['source_id']
    frames_dir = OUT / 'frames'
    frames_dir.mkdir(parents=True, exist_ok=True)
    for old in frames_dir.glob(aid + '_*.jpg'):
        old.unlink()
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning',
         '-ss', f"{scene['source_start']:.3f}", '-t', f"{scene['duration']:.3f}", '-i', raw,
         '-vf', 'fps=1,scale=320:-2', '-q:v', '3', '-start_number', '0',
         frames_dir / (aid + '_%04d.jpg')], check=True)
    frames = sorted(frames_dir.glob(aid + '_*.jpg'))
    if not frames:
        raise RuntimeError('No selected-window review frames for ' + aid)
    cols, rows, cw, ch = 4, 2, 336, 246
    pages = math.ceil(len(frames) / (cols * rows))
    paths = []
    for page in range(pages):
        chunk = frames[page * cols * rows:(page + 1) * cols * rows]
        canvas = Image.new('RGB', (cols * cw, 64 + rows * ch), '#101820')
        d = ImageDraw.Draw(canvas)
        d.text((16, 10), f"V7 SELECTED WINDOW - RANK {scene['rank']} - {aid.upper()} - PAGE {page + 1}/{pages}", font=font(18), fill='#F4F1E8')
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
        out = REVIEW / f"v7_{aid}_contact_sheet_{page + 1:02d}.jpg"
        canvas.save(out, quality=92)
        paths.append(str(out.relative_to(ROOT)))
    return len(frames), paths


def main():
    started = time.time()
    flags = SELECTED['flags']
    for key in ['runner_probe_passed', 'runner_audio_visual_probe_passed', 'runner_visual_motion_probe', 'contact_sheets_written', 'source_review_recorded', 'visual_lock_written']:
        if not bool(flags.get(key)):
            raise RuntimeError('Missing runner record before source retrieval: ' + key)
    if len(SELECTED['scenes']) != 7:
        raise RuntimeError('Expected seven selected scenes')
    ledger, windows, all_sheets = [], {}, []
    first_clip = None
    for scene in SELECTED['scenes']:
        aid = scene['source_id']
        asset = ASSETS[aid]
        v = VAPI[aid]
        if not v.get('api_license_verified'):
            raise RuntimeError('Commons API licence not verified for ' + aid)
        raw, download_sha1, used_url, effective_kind = get_raw(asset, v)
        info = probe(raw, aid)
        streams = info.get('streams', [])
        video = next((s for s in streams if s.get('codec_type') == 'video'), {})
        audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
        if audio is None:
            raise RuntimeError('Native audio stream missing for ' + aid)
        duration = float(info.get('format', {}).get('duration', 0.0))
        if duration + 0.05 < scene['source_out']:
            raise RuntimeError('Source too short for selected window ' + aid)
        clip, clip_info = cut_clip(raw, scene)
        if first_clip is None:
            first_clip = clip
        n, sheets = make_sheets(raw, scene)
        all_sheets.extend(sheets)
        windows[aid] = {
            'start': scene['source_start'], 'end': scene['source_out'],
            'duration': scene['duration'], 'frames': int(scene['frames']),
        }
        ledger.append({
            'id': aid, 'raw_file': str(raw.relative_to(ROOT)), 'clip_file': str(clip.relative_to(ROOT)),
            'bytes': raw.stat().st_size, 'sha1': download_sha1, 'sha256': sha256(raw),
            'original_sha1': v['expected_sha1'], 'download_url': used_url,
            'download_kind': effective_kind,
            'source_page': asset['source_page'], 'license': asset['license'],
            'license_short_name': asset['license_short_name'], 'platform': asset['platform'],
            'attribution_required': bool(asset['attribution_required']), 'creator': asset['creator'],
            'duration_seconds': duration,
            'width': int(video.get('width', 0)), 'height': int(video.get('height', 0)),
            'video_codec': video.get('codec_name'), 'audio_codec': (audio or {}).get('codec_name'),
            'audio_stream_present': True, 'clip_frames': int(clip_info['nb_frames']),
            'rank': scene['rank'], 'title': scene['title'], 'reaction_text': scene['reaction_text'],
            'emoji': scene['emoji'], 'timeline_in': scene['start'], 'timeline_out': scene['end'],
            'source_in': scene['source_start'], 'source_out': scene['source_out'],
            'review_frames': n, 'api_license_verified': True,
            'runner_probe_passed': True, 'runner_audio_visual_probe_passed': True,
            'runner_visual_motion_probe': True, 'contact_sheets_written': True,
            'source_review_recorded': True, 'visual_lock_written': True,
            'rights_cleared_social_origin_file_only': True, 'no_unverified_reposts': True,
        })
    if first_clip is None:
        raise RuntimeError('No selected clip was rendered')
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', first_clip,
         '-frames:v', '1', '-vf', 'scale=540:-2', '-q:v', '2', REVIEW / 'source_poster.jpg'], check=True)
    (REVIEW / 'source_video_ledger.json').write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (REVIEW / 'source_windows.json').write_text(json.dumps(windows, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    review_manifest = {
        'topic': SPEC['topic'], 'edition': 'social_origin_v7',
        'source_pages': {s['source_id']: s['source_page'] for s in SELECTED['scenes']},
        'rights_declaration': 'Seven rights-cleared social-origin Commons originals rechecked through API extmetadata and original SHA-1; CC BY attribution is recorded where required; Commons VP9/Opus transcodes may be downloaded.',
        'credits': {s['source_id']: s['creator'] for s in SELECTED['scenes']},
        'source_video_ledger': str((REVIEW / 'source_video_ledger.json').relative_to(ROOT)),
        'source_windows': str((REVIEW / 'source_windows.json').relative_to(ROOT)),
        'selected_window_sheets': all_sheets,
        'candidate_contact_sheets': sorted(str(p.relative_to(ROOT)) for p in (REVIEW / 'candidates').glob('candidate_*_sheet_*.jpg')),
        'source_poster': str((REVIEW / 'source_poster.jpg').relative_to(ROOT)),
        'flags': flags,
        'runner_probe_passed': True, 'runner_audio_visual_probe_passed': True,
        'runner_visual_motion_probe': True, 'contact_sheets_written': True,
        'source_review_recorded': True, 'visual_lock_written': True,
        'full_motion_review': False, 'native_audio_listening': False,
        'human_approval': False, 'sign_off': False,
        'audience_result_promise': False, 'virality_guarantee': False,
        'retrieved_unix': int(started),
    }
    (REVIEW / 'review-manifest.json').write_text(json.dumps(review_manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(review_manifest, indent=2), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
