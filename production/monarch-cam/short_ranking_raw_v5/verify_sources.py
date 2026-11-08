#!/usr/bin/env python3
# Verify the selected CC0 1.0 Commons originals through the Commons API.
# Extmetadata licence fields and the API SHA-1 are used by source retrieval.
from __future__ import annotations
import json, re, time
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v5'
REVIEW = BASE / 'review'
REVIEW.mkdir(parents=True, exist_ok=True)
MANIFEST = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
SELECTED = json.loads((REVIEW / 'selected_windows.json').read_text(encoding='utf-8'))
ASSETS = {a['id']: a for a in MANIFEST['assets']}
API = 'https://commons.wikimedia.org/w/api.php'
HEADERS = {
    'User-Agent': 'MonarchCamRawV5/1.0 (https://github.com/adil-chandio/Monarch.Overall.Work; CC0 source verification)',
    'Accept': 'application/json',
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


def strip_html(value):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(value or ''))).strip()


def ext_value(ext, name):
    item = ext.get(name, {})
    if isinstance(item, dict):
        return strip_html(item.get('value', ''))
    return strip_html(item)


def verify(asset):
    params = {
        'action': 'query', 'format': 'json', 'formatversion': '2',
        'prop': 'imageinfo', 'titles': asset['commons_title'],
        'iiprop': 'url|size|sha1|mime|metadata|extmetadata',
        'iiextmetadatafilter': 'LicenseShortName|UsageTerms|LicenseUrl|AttributionRequired|Artist|ImageDescription',
    }
    r = SESSION.get(API, params=params, timeout=90)
    r.raise_for_status()
    data = r.json()
    pages = data.get('query', {}).get('pages', [])
    if not pages:
        raise RuntimeError('No Commons API page for ' + asset['id'])
    page = pages[0]
    if page.get('missing') or 'imageinfo' not in page:
        raise RuntimeError('Commons API page missing imageinfo for ' + asset['id'])
    info = page['imageinfo'][0]
    ext = info.get('extmetadata', {})
    short = ext_value(ext, 'LicenseShortName')
    usage = ext_value(ext, 'UsageTerms')
    license_url = ext_value(ext, 'LicenseUrl')
    attribution = ext_value(ext, 'AttributionRequired').lower()
    if 'cc0' not in short.lower() and 'cc0' not in usage.lower():
        raise RuntimeError('CC0 licence not confirmed for ' + asset['id'] + ': ' + repr({'short': short, 'usage': usage}))
    if '/publicdomain/zero/1.0' not in license_url:
        raise RuntimeError('CC0 1.0 licence URL not confirmed for ' + asset['id'] + ': ' + repr(license_url))
    if attribution in ('true', '1', 'yes'):
        raise RuntimeError('Attribution required for ' + asset['id'])
    if not info.get('sha1') or not info.get('url') or not info.get('size'):
        raise RuntimeError('Missing original URL, SHA-1 or size for ' + asset['id'])
    return {
        'id': asset['id'],
        'commons_title': asset['commons_title'],
        'source_page': asset['source_page'],
        'pageid': page.get('pageid'),
        'creator': asset['creator'],
        'api_artist': ext_value(ext, 'Artist'),
        'api_description': ext_value(ext, 'ImageDescription'),
        'license_short_name': short,
        'usage_terms': usage,
        'license_url': license_url,
        'attribution_required': attribution,
        'expected_bytes': int(info['size']),
        'expected_sha1': str(info['sha1']).lower(),
        'original_url': info['url'],
        'mime': info.get('mime'),
        'api_metadata': info.get('metadata', []),
        'api_extmetadata': ext,
        'api_license_verified': True,
        'original_cc0_file_only': True,
        'no_transcodes': True,
    }


def main():
    selected_ids = [s['source_id'] for s in SELECTED['scenes']]
    if len(selected_ids) != 7 or len(set(selected_ids)) != 7:
        raise RuntimeError('Expected seven distinct selected sources')
    verified = {}
    for aid in selected_ids:
        asset = ASSETS[aid]
        entry = verify(asset)
        verified[aid] = entry
        print('Commons API CC0 OK', aid, entry['license_short_name'], entry['expected_sha1'], entry['expected_bytes'], flush=True)
        time.sleep(2.5)
    flags = {
        'runner_probe_passed': bool(SELECTED.get('runner_probe_passed')),
        'runner_audio_visual_probe_passed': bool(SELECTED.get('runner_audio_visual_probe_passed')),
        'runner_visual_motion_probe': bool(SELECTED.get('runner_visual_motion_probe')),
        'contact_sheets_written': bool(SELECTED.get('contact_sheets_written')),
        'source_review_recorded': bool(SELECTED.get('source_review_recorded')),
        'visual_lock_written': bool(SELECTED.get('visual_lock_written')),
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
    if not all([flags['runner_probe_passed'], flags['runner_audio_visual_probe_passed'], flags['runner_visual_motion_probe'], flags['contact_sheets_written'], flags['source_review_recorded'], flags['visual_lock_written']]):
        raise RuntimeError('Runner probe records are incomplete before Commons verification')
    report = {
        'edition': 'raw_fullscreen_v5',
        'checked_on': MANIFEST['checked_on'],
        'policy': MANIFEST['policy'],
        'selected_ids': selected_ids,
        'assets': verified,
        'flags': flags,
        'note': 'Commons API extmetadata confirms CC0 1.0 and the original SHA-1 for each selected source. Runner audio and motion probe records are carried through; no full-motion viewing, listening session, sign-off, or outcome claim.',
    }
    (REVIEW / 'verified_sources.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Verified sources written', len(verified), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
