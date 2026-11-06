#!/usr/bin/env python3
"""Build an auditable register from original, manually authored script analyses.

Never fetches or stores competitor scripts. Numbered analytical beats are NOT
caption alignment, observed cuts, measured retention, or independent science.
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/research/extinct-script-forensics/expanded'
DATA = ROOT / 'docs/research/data/extinct-expanded-study'
MODERN_IDS = ['nAWpLtG-kNs', 'SDs41Ke3v4Q', 'qrfhhZ-Wvmk', 'eWu92oXtxsw',
              'fKizW6NlnoA', 'G2qpBEmUOYk', '5QExdZCvdgE', 'B5Lmnh_BHOU']
PBS_KEYS = ['dodo', 'sponges', 'cousins', 'neandertals', 'rainforests', 'oxygen',
            'pangea-formation', 'pangea-herbivores', 'pangea-reef', 'pangea-dying',
            'pangea-survivors']

def build():
    api = json.loads((DATA / 'api-snapshot.json').read_text())
    captions = json.loads((DATA / 'publisher-captions.json').read_text())
    videos = {v['id']: v for v in api['videos']}
    publisher = {v['key']: v for v in captions['cases']}
    cases = []
    for filename in ['MODERN-MICROSCOPES.md', 'PUBLISHER-MICROSCOPES.md']:
        text = (OUT / filename).read_text()
        for match in re.finditer(r'^## ([MP]\d\d) — ([^\n]+)\n(.*?)(?=^## [MP]\d\d — |\Z)', text, re.M | re.S):
            key, title, body = match.groups()
            url = re.search(r'^Source: (\S+)', body, re.M).group(1)
            beats = [m.group(1) for m in re.finditer(r'^\d+\. (.+)$', body, re.M)
                     if 'Uninspected middle' not in m.group(1)]
            status = ('partial-middle-missing' if key == 'M08' else
                      'main-narrative-final-sentence-clipped' if key == 'P04' else
                      'complete-public-text-read')
            item = {'case': key, 'title': title, 'source_url': url,
                    'coverage_status': status, 'manual_analytical_beats': len(beats),
                    'timing_of_manual_beats': 'source order only; no cut/onset alignment',
                    'playback_reviewed': False, 'private_retention_available': False,
                    'analysis_file': f'{key}.md'}
            n = int(key[1:]) - 1
            if key.startswith('M'):
                vid = videos[MODERN_IDS[n]]
                item['api_video'] = {k: vid[k] for k in ['id', 'views', 'duration', 'channel', 'published']}
                item['million_view_exact_video'] = vid['views'] >= 1_000_000
                item['script_timing'] = 'untimed public prose'
            else:
                cap = publisher[PBS_KEYS[n]]
                item['publisher_caption'] = {k: cap[k] for k in ['key', 'cue_count', 'publisher_duration_seconds', 'caption_sha256', 'status']}
                item['million_view_exact_video'] = None
                item['script_timing'] = 'separate publisher caption timing available; manually coded beats not aligned'
            (OUT / f'{key}.md').write_text(f'# {key} — {title}\n\n' + body.strip() + '\n')
            item['analysis_word_count'] = len(body.split())
            item['ordered_original_analysis'] = beats
            cases.append(item)
    result = {'scope': '19 new actual-text analyses, not 252 scripts; previous four reference cases are not counted as new',
              'api_checked_at': api['checked_at'], 'api_video_records': len(api['videos']),
              'api_channel_records': len(api['channels']), 'api_errors': api['errors'],
              'publisher_cases': len(captions['cases']),
              'publisher_cue_derivatives': sum(c['cue_count'] for c in captions['cases']),
              'publisher_duration_seconds': sum(c['publisher_duration_seconds'] for c in captions['cases']),
              'complete_new_public_text_cases': sum(c['coverage_status'] == 'complete-public-text-read' for c in cases),
              'partial_new_cases': sum(c['coverage_status'] != 'complete-public-text-read' for c in cases),
              'new_manual_analytical_beats': sum(c['manual_analytical_beats'] for c in cases),
              'raw_competitor_scripts_published': False, 'causal_retention_claim': False,
              'cases': cases}
    (OUT / 'register.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    with (OUT / 'register.csv').open('w', newline='') as f:
        fields = ['case', 'title', 'source_url', 'coverage_status', 'manual_analytical_beats', 'analysis_word_count', 'analysis_file']
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader(); w.writerows(cases)
    print(json.dumps({k: v for k, v in result.items() if k != 'cases'}, indent=2))
    return result

if __name__ == '__main__':
    build()
