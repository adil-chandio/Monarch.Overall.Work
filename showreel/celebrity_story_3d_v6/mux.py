"""Score, ambience and foley synthesised from the measured cue layout.

Every sound here is generated with ffmpeg filters (sines, noise, envelopes) and
placed from the same cue table the picture uses, so hits land on cuts and never
drift.  There is no recorded foley and no stock music.
"""
from pathlib import Path
import json, math, re, subprocess, sys, tempfile
import imageio_ffmpeg

P = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 48000
DUR = 60.0


def run(args, **kw):
    return subprocess.run([FF, '-y', '-v', 'error'] + args, check=True, **kw)


def tone(freq, dur, amp=.2, fade=.02, wave='sine'):
    return (f"{wave}=f={freq}:d={dur:.3f},volume={amp},"
            f"afade=t=in:st=0:d={fade:.3f},afade=t=out:st={max(0, dur - fade):.3f}:d={fade:.3f}")


def pad_chain(notes, dur, amp=.10, trem=0.0):
    """A soft sustained chord bed: one oscillator per note, summed.

    Every source needs its own label and `tremolo` emits a second (control)
    output, so the pad is built as an explicit mix graph rather than a chain.
    """
    graph, labels = [], []
    for i, f in enumerate(notes):
        lvl = amp / max(1, len(notes) ** .5)
        vib = f',tremolo=f={trem:.2f}:d=0.35' if trem else ''
        graph.append(f"sine=f={f!r}:d={dur}[s{i}];"
                     f"[s{i}]volume={lvl:.4f},afade=t=in:st=0:d=0.600,"
                     f"afade=t=out:st={max(0, dur - .6):.3f}:d=0.600{vib}[n{i}]")
        labels.append(f'[n{i}]')
    graph.append(f"{''.join(labels)}amix=inputs={len(notes)}:normalize=0:duration=longest")
    return ';'.join(graph)


def build_score(out):
    """Warm minor bed that lifts at the carpet and thins out for the last act.

    Each section is written to its own file and joined, because a single
    filtergraph with three sinks would emit three streams into one file.
    """
    sections = [
        ([110.0, 164.81, 220.0, 277.18], 24.0, .13, .22),
        ([130.81, 196.0, 261.63, 329.63], 24.0, .15, .18),
        ([98.0, 146.83, 196.0, 233.08], 22.0, .10, .12),
    ]
    parts = []
    for i, (notes, dur, amp, trem) in enumerate(sections):
        label = f'[a{i}]'
        graph = pad_chain(notes, dur, amp=amp, trem=trem) + label
        path = out.with_name(f'score{i}.wav')
        run(['-filter_complex', graph, '-map', label, '-t', str(dur),
             '-ar', str(SR), str(path)])
        parts.append(path)
    m = out.with_name('score_list.txt')
    m.write_text(''.join(f"file '{p.name}'\n" for p in parts))
    tmp = out.with_name('score_raw.wav')
    run(['-f', 'concat', '-safe', '0', '-i', str(m),
         '-filter_complex', 'lowpass=f=2600,aecho=0.7:0.6:320|480:0.25|0.18,volume=0.9',
         '-t', str(DUR), '-ar', str(SR), str(tmp)])
    tmp.replace(out)


def build_bed(out, cues):
    """Room tone under the interiors, street wash once he is outside."""
    # interior: very low HVAC hum + faint high hiss
    run(['-filter_complex',
         f"sine=f=52:d=23,volume=0.035[h];"
         f"anoisesrc=d=23:c=pink:r={SR}:a=0.012,lowpass=f=900[n1];"
         f"[h][n1]amix=inputs=2:duration=first:normalize=0[int]",
         '-map', '[int]', '-ar', str(SR), str(out / 'bed_intro.wav')])
    run(['-filter_complex',
         f"anoisesrc=d=37:c=pink:r={SR}:a=0.05,lowpass=f=2200,highpass=f=120,"
         f"tremolo=f=0.18:d=0.25[st]",
         '-map', '[st]', '-ar', str(SR), str(out / 'bed_street.wav')])
    run(['-filter_complex',
         f"sine=f=44:d=14,volume=0.03[h2];"
         f"anoisesrc=d=14:c=pink:r={SR}:a=0.008,lowpass=f=700[n2];"
         f"[h2][n2]amix=inputs=2:duration=first:normalize=0[int2]",
         '-map', '[int2]', '-ar', str(SR), str(out / 'bed_final.wav')])


def hit(out, kind, dur=.5):
    """One-shot effects; every graph ends on a single labelled stream."""
    if kind == 'shutter':
        # two tight noise clicks a few milliseconds apart, like a mirror slap
        run(['-filter_complex',
             f"anoisesrc=d=0.050:c=white:r={SR}:a=0.5,highpass=f=1800,"
             f"afade=t=out:st=0.02:d=0.03[c1];"
             f"anoisesrc=d=0.050:c=white:r={SR}:a=0.3,highpass=f=2600,"
             f"afade=t=out:st=0.01:d=0.03[c2];"
             f"[c1]adelay=0[c1d];[c2]adelay=70[c2d];"
             f"[c1d][c2d]amix=inputs=2:normalize=0,volume=0.7[click]",
             '-map', '[click]', '-ar', str(SR), str(out)])
    elif kind == 'cork':
        run(['-filter_complex',
             f"sine=f=420:d=0.06,volume=0.22,afade=t=out:st=0.03:d=0.03[k1];"
             f"anoisesrc=d=0.080:c=pink:r={SR}:a=0.18,lowpass=f=1400,"
             f"afade=t=out:st=0.02:d=0.06[k2];"
             f"[k1][k2]amix=inputs=2:normalize=0[corked]",
             '-map', '[corked]', '-ar', str(SR), str(out)])
    elif kind == 'door':
        run(['-filter_complex',
             f"sine=f=120:d=0.30,volume=0.30,afade=t=out:st=0.05:d=0.25[d1];"
             f"anoisesrc=d=0.30:c=brown:r={SR}:a=0.16,lowpass=f=800,"
             f"afade=t=out:st=0.05:d=0.25[d2];"
             f"[d1][d2]amix=inputs=2:normalize=0[clunk]",
             '-map', '[clunk]', '-ar', str(SR), str(out)])
    elif kind == 'step':
        run(['-filter_complex',
             f"anoisesrc=d=0.10:c=brown:r={SR}:a=0.10,lowpass=f=600,highpass=f=70,"
             f"afade=t=out:st=0.02:d=0.08[step]",
             '-map', '[step]', '-ar', str(SR), str(out)])
    elif kind == 'swell':
        run(['-filter_complex',
             f"sine=f=196:d=2.6,volume=0.10,afade=t=in:st=0:d=1.600,"
             f"afade=t=out:st=1.8:d=0.8[w1];"
             f"sine=f=293.66:d=2.6,volume=0.07,afade=t=in:st=0:d=1.600,"
             f"afade=t=out:st=1.8:d=0.8[w2];"
             f"[w1][w2]amix=inputs=2:normalize=0[swelled]",
             '-map', '[swelled]', '-ar', str(SR), str(out)])


def main(clips_dir, out):
    clips = sorted(Path(clips_dir).glob('*.mp4'))
    if len(clips) < 9:
        raise SystemExit(f'expected at least 9 clips, found {len(clips)}')
    cues = json.loads((P / 'script.json').read_text())
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # concat picture
        lst = td / 'list.txt'
        lst.write_text(''.join(f"file '{c.resolve()}'\n" for c in clips))
        silent = td / 'silent.mp4'
        run(['-f', 'concat', '-safe', '0', '-i', str(lst),
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
             '-pix_fmt', 'yuv420p', '-r', '24', str(silent)])

        build_score(td / 'score.wav')
        build_bed(td, cues)
        # assemble the bed track at three spans
        run(['-filter_complex',
             f"[0:a]atrim=0:23,asetpts=PTS-STARTPTS[i];"
             f"[1:a]atrim=0:23.5,asetpts=PTS-STARTPTS,adelay=23000|23000[s];"
             f"[2:a]atrim=0:13.5,asetpts=PTS-STARTPTS,adelay=46500|46500[f];"
             f"[i][s][f]amix=inputs=3:duration=longest:normalize=0,volume=0.55[bed]",
             '-i', str(td / 'bed_intro.wav'), '-i', str(td / 'bed_street.wav'),
             '-i', str(td / 'bed_final.wav'), '-map', '[bed]', '-t', str(DUR),
             '-ar', str(SR), str(td / 'bed.wav')])

        # foley placement, driven by the cue times
        shutter, door, step, swell, cork = (td / 'shutter.wav'), (td / 'door.wav'), \
            (td / 'step.wav'), (td / 'swell.wav'), (td / 'cork.wav')
        hit(shutter, 'shutter'); hit(door, 'door'); hit(step, 'step')
        hit(swell, 'swell'); hit(cork, 'cork')
        events = []
        street = cues[3]['start']
        for i in range(14):
            events.append((shutter, street + .55 + i * .62 + (i % 3) * .11, .30))
        for i in range(10):
            events.append((shutter, cues[4]['start'] + .3 + i * .55, .34))
        for i in range(6):
            events.append((step, cues[3]['start'] + 3.4 + i * .52, .5))
        events.append((door, cues[4]['start'] - .15, .8))
        events.append((door, cues[8]['start'] + .9, .75))
        events.append((cork, cues[2]['start'] + .8, .5))
        events.append((swell, cues[6]['start'] + .2, .9))
        events.append((swell, cues[9]['start'] + .2, .8))
        inputs, chains, labels = [], [], []
        for k, (src, at, amp) in enumerate(events):
            inputs += ['-i', str(src)]
            chains.append(f"[{k}:a]volume={amp},adelay={int(at * 1000)}|{int(at * 1000)}[e{k}]")
            labels.append(f'[e{k}]')
        fc = ';'.join(chains) + f";{''.join(labels)}amix=inputs={len(events)}:normalize=0[foley]"
        run(['-filter_complex', fc, *inputs, '-map', '[foley]', '-t', str(DUR),
             '-ar', str(SR), str(td / 'foley.wav')])

        # narration: each trimmed take placed at its cue start
        n_inputs, n_chains, n_labels = [], [], []
        for i, c in enumerate(cues):
            n_inputs += ['-i', str(P / 'trimmed' / f'{i + 1:02d}.wav')]
            n_chains.append(f"[{i}:a]adelay={int(c['start'] * 1000)}|{int(c['start'] * 1000)}[n{i}]")
            n_labels.append(f'[n{i}]')
        fc = ';'.join(n_chains) + f";{''.join(n_labels)}amix=inputs={len(cues)}:normalize=0[vox]"
        run(['-filter_complex', fc, *n_inputs, '-map', '[vox]', '-t', str(DUR),
             '-ar', str(SR), str(td / 'vox.wav')])

        # final mix: voice forward, score tucked, foley for contact, loudness normalised
        run(['-filter_complex',
             "[0:a]volume=1.0[v];[1:a]volume=0.30[s];[2:a]volume=0.55[b];"
             "[3:a]volume=0.75[f];"
             "[v][s][b][f]amix=inputs=4:duration=longest:normalize=0,"
             "acompressor=threshold=0.12:ratio=2.4:attack=12:release=180,"
             "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[aout]",
             '-i', str(td / 'vox.wav'), '-i', str(td / 'score.wav'),
             '-i', str(td / 'bed.wav'), '-i', str(td / 'foley.wav'),
             '-map', '[aout]', '-t', str(DUR), '-ar', str(SR), str(td / 'mix.wav')])
        run(['-i', str(silent), '-i', str(td / 'mix.wav'), '-map', '0:v', '-map', '1:a',
             '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', str(out)])

    probe = subprocess.run([FF, '-i', str(out)], capture_output=True, text=True)
    print([l for l in probe.stderr.splitlines() if 'Duration' in l or 'Video' in l])
    print('OUTPUT', out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
