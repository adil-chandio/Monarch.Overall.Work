"""Summarize exact-release diagnostics. No creative pass/fail is inferred.
Run: python production/extinct-life/review-v13/analyze_metrics.py
"""
import csv
import json
from pathlib import Path
from statistics import mean, median

BASE = Path(__file__).resolve().parent
frames = list(csv.DictReader((BASE / 'every-frame-metrics.csv').open()))
audio = list(csv.DictReader((BASE / 'audio-per-second.csv').open()))
schedule = json.loads((BASE.parent / 'film-v13-full-pov/schedule.json').read_text())
mae = [float(row['rgb_MAE_from_previous']) for row in frames]
stages = []
for stage in schedule['sequences']:
    values = mae[stage['start_frame'] + 1:stage['end_frame']]
    stages.append({
        'stage': stage['id'], 'world': stage['world'],
        'start': stage['start_frame'] / 30, 'end': stage['end_frame'] / 30,
        'duration': (stage['end_frame'] - stage['start_frame']) / 30,
        'mean_frame_MAE': mean(values), 'median_frame_MAE': median(values),
        'fraction_frame_MAE_below_0_1': mean(value < .1 for value in values),
    })
labs = {'extraction', 'controls', 'reference', 'branch', 'proxies', 'boundary', 'gaps', 'integration'}
lab_duration = sum(stage['duration'] for stage in stages if stage['world'] in labs)
summary = {
    'decoded_frames': len(frames),
    'near_black_over_98pct_frame_count': sum(float(row['near_black_fraction']) > .98 for row in frames),
    'exact_consecutive_160x90_rgb_duplicates': sum(value == 0 for value in mae[1:]),
    'later_lab_seconds': lab_duration,
    'later_lab_percent': lab_duration / (len(frames) / 30) * 100,
    'audio_rms_dbfs_min': min(float(row['rms_dbfs']) for row in audio),
    'audio_rms_dbfs_max': max(float(row['rms_dbfs']) for row in audio),
    'stereo_correlation_median': median(float(row['stereo_correlation']) for row in audio if row['stereo_correlation']),
    'warning': 'Metrics are diagnostics, not audience attention, speech intelligibility, ear comfort or frame-by-frame artistic validation.',
}
for name, value in [('stage-metrics.json', stages), ('MEASUREMENTS.json', summary)]:
    (BASE / name).write_text(json.dumps(value, indent=2) + '\n')
print(json.dumps(summary, indent=2))
