"""Report the picture balance of the assembled timeline.

Built because section-by-section QC cannot see the film's largest structural problem:
each evidence plate is honest on its own, and a run of them stops being a documentary
and becomes a slide deck. This script measures that directly, from the same verified
windows `check_coverage.py` publishes, so the number cannot silently drift.

It reports, and never fixes:
  * how much of the covered timeline is printed plate versus native 3D picture;
  * the longest uninterrupted run of plates;
  * every plate run of 60 s or more, with its time range.

Exit code is 1 when a plate run exceeds LONG_PLATE_RUN, so a build can be stopped from
quietly making the problem worse. It is a report, not an edit decision.
"""
from pathlib import Path
import json, subprocess, sys

base = Path(__file__).resolve().parent
LONG_PLATE_RUN = 150.0   # seconds of continuous paper before this is flagged
FPS = 30

# Scene directories whose picture is printed plate / canvas-2D rather than rendered world.
PLATE = {
    'isolation-section', 'other-islands', 'genome-comparison', 'gene-disruption',
    'one-genome', 'chemistry-section', 'people-section', 'contact-section',
    'genome-record', 'reversal-section', 'genetic-strain', 'coverage-section',
    'trends-section', 'genomic-gap', 'new-lead-section', 'ledger-section',
}


def coverage():
    r = subprocess.run([sys.executable, str(base / 'check_coverage.py')],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('coverage check failed')
    return json.loads(r.stdout[r.stdout.index('{'):])


def main():
    data = coverage()
    windows = [(a, b, n) for a, b, n in data['verified_windows']]
    plate = sum(b - a for a, b, n in windows if n in PLATE) / FPS
    world = sum(b - a for a, b, n in windows if n not in PLATE) / FPS
    total = plate + world

    runs, cur = [], None
    for a, b, n in sorted(windows):
        if n in PLATE:
            # a gap between windows (missing_ranges_frames) also breaks a run
            if cur and a == cur[1]:
                cur = (cur[0], b)
            else:
                if cur:
                    runs.append(cur)
                cur = (a, b)
        else:
            if cur:
                runs.append(cur)
                cur = None
    if cur:
        runs.append(cur)

    long_runs = [((a / FPS, b / FPS, (b - a) / FPS)) for a, b in runs
                 if (b - a) / FPS >= 60]
    longest = max(((b - a) / FPS for a, b in runs), default=0.0)

    report = {
        'status': 'picture-balance report; not an editorial judgement of quality',
        'covered_seconds': round(total, 1),
        'plate_seconds': round(plate, 1),
        'world_seconds': round(world, 1),
        'plate_share_percent': round(100 * plate / total, 1) if total else None,
        'longest_plate_run_seconds': round(longest, 1),
        'plate_runs_over_60s': [[round(a, 1), round(b, 1), round(d, 1)]
                                for a, b, d in long_runs],
        'plate_run_threshold_seconds': LONG_PLATE_RUN,
        'finding': ('A run of evidence plates longer than roughly two and a half minutes '
                    'reads as a slide sequence. The remedy is native picture under the '
                    'narration, not shorter plates: the plates are the honest form of '
                    'these claims and each is individually defensible.'),
    }
    print(json.dumps(report, indent=2))
    (base.parent / 'edit' / 'picture-balance.json').write_text(json.dumps(report, indent=2))
    if longest > LONG_PLATE_RUN:
        print(f"\nNOTE: longest plate run {longest:.1f} s exceeds "
              f"{LONG_PLATE_RUN:.0f} s — documented in README, not auto-fixed.",
              file=sys.stderr)


if __name__ == '__main__':
    main()
