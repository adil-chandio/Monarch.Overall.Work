"""Offline derivative measurements from an existing decoded reference (no production).
Frame PTS come from the existing full decode, never proportional transcript timings.
Audio-window RMS describes the mixed decoded PCM, not isolated SFX/voice/music.
"""
import argparse,csv,hashlib,json,math
from pathlib import Path
import numpy as np

def write_csv(path,rows):
 with path.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--analysis-dir',required=True,type=Path);ap.add_argument('--video',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);args=ap.parse_args()
 info=json.loads((args.analysis_dir/'analysis.json').read_text())
 digest=hashlib.file_digest(args.video.open('rb'),'sha256').hexdigest()
 if digest!=info['sha256']:raise ValueError('Reference checksum mismatch')
 with (args.analysis_dir/'frame-metrics.csv').open() as f:source=list(csv.DictReader(f))
 if len(source)!=info['decoded_frames']:raise ValueError('Decoded frame coverage mismatch')
 times=np.array([float(x['time']) for x in source]);
 if not np.all(np.diff(times)>0):raise ValueError('Frame PTS not strictly increasing')
 audio=np.fromfile(args.analysis_dir/'audio.f32',dtype='<f4').reshape(-1,2)
 if not np.isfinite(audio).all():raise ValueError('Nonfinite PCM')
 sr=48000;end=info['video_duration_seconds'];args.out.mkdir(parents=True,exist_ok=True)
 rows=[]
 for i,x in enumerate(source):
  stop=times[i+1] if i+1<len(times) else end
  segment=audio[round(times[i]*sr):min(len(audio),round(stop*sr))].astype(np.float64)
  rms=float(np.sqrt(np.mean(segment*segment))) if len(segment) else None
  rows.append(dict(frame=i,source_pts_seconds=float(times[i]),next_pts_or_video_end=float(stop),
    mean_rgb_difference=float(x['mean_rgb_difference']),changed_pixel_fraction_threshold20=float(x['changed_pixel_fraction_threshold20']),
    mixed_audio_window_rms=rms,mixed_audio_window_rms_dbfs=20*math.log10(max(rms,1e-12)) if rms is not None else None))
 write_csv(args.out/'all-1372-frame-measurements.csv',rows)
 seconds=[]
 for second in range(math.ceil(end)):
  stop=min(second+1,end);selected=[r for r in rows if second<=r['source_pts_seconds']<stop]
  segment=audio[round(second*sr):round(stop*sr)].astype(np.float64)
  seconds.append(dict(start_seconds=second,end_seconds=stop,first_frame=selected[0]['frame'],last_frame=selected[-1]['frame'],frame_count=len(selected),
   mean_frame_difference=float(np.mean([r['mean_rgb_difference'] for r in selected])),
   max_frame_difference=max(r['mean_rgb_difference'] for r in selected),
   mixed_audio_rms_dbfs=20*math.log10(max(float(np.sqrt(np.mean(segment*segment))),1e-12)),
   mixed_audio_sample_peak_dbfs=20*math.log10(max(float(np.max(np.abs(segment))),1e-12))))
 write_csv(args.out/'second-by-second-measurements.csv',seconds)
 metadata=dict(source_sha256=digest,decoded_frame_records=len(rows),second_intervals=len(seconds),
   source_video_seconds=end,decoded_pcm_seconds=len(audio)/sr,
   prior_visual_metric_definition='Decoded source frames downsampled to 90x160, RGB MAE and changed pixels >20/255; not a verified cut detector',
   audio_window_definition='48kHz stereo f32 decode, mean-square across both channels; normalized timeline starts at decoded PCM sample zero',
   limitations=['RMS windows do not establish source-edit sync or speech alignment','No semantic sound attribution from mixed energy',
    'No new perceptual listening','Visual metrics inherited from source decode, not project/render settings',
    'No claim that every frame has been visually inspected at native size'],production_hold=True)
 (args.out/'measurement-provenance.json').write_text(json.dumps(metadata,indent=2)+'\n')
 print(json.dumps(metadata,indent=2))
if __name__=='__main__':main()
