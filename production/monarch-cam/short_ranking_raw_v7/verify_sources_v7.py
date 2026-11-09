#!/usr/bin/env python3
# Verify seven selected rights-cleared social-origin Commons originals through
# the Commons API, then choose a Commons VP9/Opus transcode for large originals.
from __future__ import annotations
import json, re, time
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v7'
REVIEW = BASE / 'review'
REVIEW.mkdir(parents=True, exist_ok=True)
MANIFEST = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
SELECTED = json.loads((REVIEW / 'selected_windows.json').read_text(encoding='utf-8'))
ASSETS = {a['id']: a for a in MANIFEST['assets']}
API = 'https://commons.wikimedia.org/w/api.php'
HEADERS = {
    'User-Agent': 'MonarchCamViralV7/1.0 (https://github.com/adil-chandio/Monarch.Overall.Work; rights-cleared social-origin verification)',
    'Accept': 'application/json',
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
RETRY = Retry(total=6, connect=6, read=6, status=6, backoff_factor=3,
              status_forcelist=[429, 500, 502, 503, 504],
              allowed_methods=frozenset(['GET']), respect_retry_after_header=True,
              raise_on_status=False)
SESSION.mount('https://', HTTPAdapter(max_retries=RETRY))
SESSION.mount('http://', HTTPAdapter(max_retries=RETRY))


def strip_html(value):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(value or ''))).strip()


def ext_value(ext, name):
    item = ext.get(name, {})
    if isinstance(item, dict):
        return strip_html(item.get('value', ''))
    return strip_html(item)


def api_get(params):
    r = SESSION.get(API, params=params, timeout=90)
    r.raise_for_status()
    return r.json()


def choose_download(title, original_url):
    params = {
        'action': 'query', 'format': 'json', 'formatversion': '2',
        'prop': 'videoinfo', 'titles': title,
        'viprop': 'url|derivatives|size',
    }
    try:
        data = api_get(params)
        pages = data.get('query', {}).get('pages', [])
        if pages and 'videoinfo' in pages[0]:
            vi = pages[0]['videoinfo'][0]
            derivs = vi.get('derivatives', []) or []
            preferred = [d for d in derivs if d.get('transcodekey') == '480p.vp9.webm' and 'opus' in d.get('type', '')]
            fallback = [d for d in derivs if d.get('transcodekey') == '240p.vp9.webm' and 'opus' in d.get('type', '')]
            chosen = (preferred or fallback or [None])[0]
            if chosen and str(chosen.get('src', '')).startswith('https://upload.wikimedia.org/wikipedia/commons/transcoded/'):
                return chosen['src'], 'commons_vp9_opus_transcode'
    except Exception as e:
        print('Derivative lookup fell back to original for', title, repr(e), flush=True)
    return original_url, 'commons_original'


def verify(asset):
    params = {
        'action': 'query', 'format': 'json', 'formatversion': '2',
        'prop': 'imageinfo', 'titles': asset['commons_title'],
        'iiprop': 'url|size|sha1|mime|metadata|extmetadata',
        'iiextmetadatafilter': 'LicenseShortName|UsageTerms|LicenseUrl|AttributionRequired|Artist|ImageDescription|Credit|DateTimeOriginal|Categories|Restrictions|Copyrighted',
    }
    data = api_get(params)
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
    credit = ext_value(ext, 'Credit')
    categories = ext_value(ext, 'Categories')
    artist = ext_value(ext, 'Artist')
    restrictions = ext_value(ext, 'Restrictions')
    restrictions_present = 'Restrictions' in ext
    restrictions_status = 'reported' if restrictions else 'none_reported_in_extmetadata'
    allowed = {'cc0', 'public domain', 'cc by 3.0'}
    if short.lower() not in allowed and usage.lower() not in allowed:
        raise RuntimeError('Allowed licence not confirmed for ' + asset['id'] + ': ' + repr({'short': short, 'usage': usage}))
    if short.lower() == 'cc by 3.0' and '/licenses/by/3.0' not in license_url:
        raise RuntimeError('CC BY 3.0 licence URL not confirmed for ' + asset['id'] + ': ' + repr(license_url))
    if 'license review needed (video)' in categories.lower():
        raise RuntimeError('Commons licence review needed for ' + asset['id'])
    want_attr = bool(asset['attribution_required'])
    got_attr = attribution in ('true', '1', 'yes')
    if want_attr != got_attr:
        raise RuntimeError('Attribution requirement mismatch for ' + asset['id'] + ': ' + repr({'manifest': want_attr, 'api': attribution}))
    if asset['license'] not in MANIFEST['policy']['allowed_license_ids']:
        raise RuntimeError('Manifest licence not allowed for ' + asset['id'])
    description = ext_value(ext, 'ImageDescription')
    origin_text = ' '.join([credit, categories, description]).lower()
    credit_ok = any(str(tok).lower() in origin_text for tok in asset['platform_tokens'])
    if not credit_ok:
        raise RuntimeError('Social origin not confirmed in Commons Credit/Categories for ' + asset['id'] + ': ' + repr({'credit': credit, 'categories': categories}))
    if not str(asset['source_page']).startswith('https://commons.wikimedia.org/wiki/File:'):
        raise RuntimeError('Source page is not an original Commons file page for ' + asset['id'])
    if not info.get('sha1') or not info.get('url') or not info.get('size'):
        raise RuntimeError('Missing original URL, SHA-1 or size for ' + asset['id'])
    original_url = info['url']
    download_url, download_kind = choose_download(asset['commons_title'], original_url)
    if not (download_url.startswith('https://upload.wikimedia.org/') or download_url.startswith('https://commons.wikimedia.org/')):
        raise RuntimeError('Download URL is not a Wikimedia Commons URL for ' + asset['id'])
    attribution_text = ''
    if want_attr:
        attribution_text = f"{asset['title']} — {asset['creator']} — {short} — {license_url} — {asset['source_page']}"
    return {
        'id': asset['id'], 'commons_title': asset['commons_title'],
        'source_page': asset['source_page'], 'pageid': page.get('pageid'),
        'creator': asset['creator'], 'api_artist': artist,
        'api_description': description,
        'api_credit': credit, 'api_categories': categories,
        'platform': asset['platform'], 'platform_tokens': asset['platform_tokens'],
        'license': asset['license'], 'license_short_name': short,
        'usage_terms': usage, 'license_url': license_url,
        'attribution_required': want_attr, 'attribution_text': attribution_text,
        'restrictions': restrictions,
        'restrictions_status': restrictions_status,
        'expected_bytes': int(info['size']), 'expected_sha1': str(info['sha1']).lower(),
        'original_url': original_url, 'download_url': download_url,
        'download_kind': download_kind, 'mime': info.get('mime'),
        'api_metadata': info.get('metadata', []), 'api_extmetadata': ext,
        'api_license_verified': True, 'social_origin_verified': True,
        'api_restrictions_recorded': restrictions_present,
        'rights_not_legal_opinion': True,
        'original_commons_page': True, 'original_sha1_verified': True,
        'no_unverified_repost': True,
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
        print('Commons API OK', aid, entry['license_short_name'], entry['download_kind'], entry['expected_sha1'], flush=True)
        time.sleep(2.0)
    flags = dict(SELECTED.get('flags', {}))
    flags.update({
        'full_motion_review': False, 'native_audio_listening': False,
        'human_approval': False, 'sign_off': False,
        'audience_result_promise': False, 'virality_guarantee': False,
        'current_trending_claim': False, 'unverified_social_repost': False,
    })
    report = {
        'edition': 'social_origin_v7', 'checked_on': MANIFEST['checked_on'],
        'policy': MANIFEST['policy'], 'selected_ids': selected_ids,
        'assets': verified, 'flags': flags,
        'note': 'Commons API extmetadata confirms an allowed PD/CC0/CC BY 3.0 licence, social-origin Credit/Categories and the original SHA-1 for each selected source. Commons VP9/Opus transcodes may be downloaded for large originals; the original API SHA-1 remains the rights record. No full-motion viewing, listening session, sign-off or outcome claim.',
    }
    (REVIEW / 'verified_sources.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    social = {
        'edition': 'social_origin_v7',
        'policy': 'Per-title Commons API extmetadata verification; PD/CC0/CC BY 3.0 only; original Commons file pages; social-origin Credit/Categories; no unverified trending reposts; CC BY attribution recorded.',
        'selected_ids': selected_ids,
        'assets': {
            aid: {
                'source_page': e['source_page'], 'commons_title': e['commons_title'],
                'platform': e['platform'], 'api_credit': e['api_credit'],
                'license': e['license'], 'license_short_name': e['license_short_name'],
                'license_url': e['license_url'], 'attribution_required': e['attribution_required'],
                'attribution_text': e['attribution_text'],
                'expected_sha1': e['expected_sha1'], 'expected_bytes': e['expected_bytes'],
                'download_url': e['download_url'], 'download_kind': e['download_kind'],
                'api_license_verified': True, 'social_origin_verified': True,
                'original_commons_page': True, 'original_sha1_verified': True,
                'no_unverified_repost': True,
            } for aid, e in verified.items()
        },
        'all_api_license_verified': all(e['api_license_verified'] for e in verified.values()),
        'all_social_origin_verified': all(e['social_origin_verified'] for e in verified.values()),
        'all_original_commons_pages': all(e['original_commons_page'] for e in verified.values()),
        'all_original_sha1_verified': all(e['original_sha1_verified'] for e in verified.values()),
        'no_unverified_reposts': all(e['no_unverified_repost'] for e in verified.values()),
        'api_restrictions_recorded': all(e['api_restrictions_recorded'] for e in verified.values()),
        'rights_not_legal_opinion': all(e['rights_not_legal_opinion'] for e in verified.values()),
        'cc_by_attribution_recorded': all(bool(e['attribution_text']) for e in verified.values() if e['attribution_required']),
        'flags': {
            'full_motion_review': False, 'native_audio_listening': False,
            'human_approval': False, 'sign_off': False,
            'audience_result_promise': False, 'virality_guarantee': False,
            'current_trending_claim': False, 'unverified_social_repost': False,
        },
    }
    (REVIEW / 'social_origin_ledger.json').write_text(json.dumps(social, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if not all([social['all_api_license_verified'], social['all_social_origin_verified'], social['all_original_commons_pages'], social['all_original_sha1_verified'], social['no_unverified_reposts'], social['api_restrictions_recorded'], social['rights_not_legal_opinion'], social['cc_by_attribution_recorded']]):
        raise RuntimeError('V7 social-origin/rights ledger failed')
    print('Verified sources and social-origin ledger written', len(verified), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
