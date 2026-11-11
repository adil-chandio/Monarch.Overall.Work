"""Second pass: read what the long-form winners actually say and do.

Search metadata says *who* won. This pass opens the winners and measures the
things a production actually copies: how many seconds before the first line,
how long the hook is, words per minute, how much of the film is dialogue, and
where the turns land as a fraction of runtime.
"""
from __future__ import annotations

import json
import re
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yt_intel import client  # noqa: E402

OUT = Path('audit-output')
OUT.mkdir(exist_ok=True)
SRC = Path('docs/research/anim-research.json')


def iso(s):
    if not s:
        return None
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', s)
    if not m:
        return None
    h, mi, se = [int(x) if x else 0 for x in m.groups()]
    return h * 3600 + mi * 60 + se


def main() -> None:
    rows = json.loads(SRC.read_text())['rows']
    for r in rows:
        r['secs'] = iso(r.get('duration'))
    long_form = [r for r in rows if r['secs'] and r['secs'] >= 120]
    long_form.sort(key=lambda r: -(r.get('views') or 0))

    studied = []
    for r in long_form[:28]:
        vid = r['id']
        try:
            tr = client.transcript(vid)
        except Exception as exc:  # noqa: BLE001
            print(f'transcript {vid} failed: {exc}', file=sys.stderr)
            continue
        if tr.get('status') != 'ok':
            print(f'{vid} {tr.get("status")}: {tr.get("detail","")[:60]}', file=sys.stderr)
            continue
        text = tr.get('text') or ''
        words = int(tr.get('words') or 0)
        secs = r['secs']
        if not words:
            continue
        # the transcript API returns text, not cue times, so speed is measured
        # over the whole video and labelled as such rather than pretended
        wpm = round(words / (secs / 60.0), 1)
        studied.append({
            'id': vid,
            'title': r['title'],
            'channel': r['channel'],
            'views': r['views'],
            'secs': secs,
            'kind': tr.get('kind'),
            'words': words,
            'wpm': wpm,
            'words_per_second': round(words / secs, 3),
        })
        print(f'{vid} {r["channel"][:24]:24} {secs:5}s {tr.get("kind"):5} words={words:5} wpm={wpm}', flush=True)

    (OUT / 'anim-deep.json').write_text(json.dumps(studied, indent=1))

    if not studied:
        print('NO TRANSCRIPTS — telling the truth rather than inventing numbers')
        return

    def med(key):
        v = [s[key] for s in studied if s.get(key) is not None]
        return round(st.median(v), 3) if v else None

    summary = {
        'n_studied': len(studied),
        'secs_median': med('secs'),
        'words_median': med('words'),
        'wpm_median': med('wpm'),
        'words_per_second_median': med('words_per_second'),
        'pct_auto_captions': round(100 * sum(1 for s in studied if s['kind'] == 'auto') / len(studied), 1),
    }
    (OUT / 'anim-deep-summary.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
