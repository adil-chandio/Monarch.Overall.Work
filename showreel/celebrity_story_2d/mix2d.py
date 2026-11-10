"""Sound for the 2D cut: narration, score, room tone, street wash and foley.

Every element is placed from the same cue table the picture is cut to, so a
shutter lands on the flash and the door thud lands on the cut. Nothing here is
recorded or licensed: the score and effects are synthesised with ffmpeg filters.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg

P = Path(__file__).resolve().parent
V6 = P.parent / 'celebrity_story_3d_v6'
FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 48000
DUR = 60.0

CUE_DAWN, CUE_CALLS, CUE_KITCHEN, CUE_STREET, CUE_PRESS, CUE_FLASH, CUE_BARRIER, CUE_REACH, CUE_CAR, CUE_NIGHT = \
    [0.26, 7.14, 11.91, 17.24, 22.95, 29.81, 34.79, 40.12, 46.31, 50.54]


def run(args, **kw):
    return subprocess.run([FF, '-y', '-v', 'error'] + args, check=True, **kw)


def pad_section(notes, dur, amp, trem, out):
    """A slow stacked pad: one sine per note, tremolo, then a shared bend."""
    chains, labels = [], []
    for i, f in enumerate(notes):
        chains.append(f"sine=f={f}:d={dur}:r={SR},volume={amp}[p{i}]")
        labels.append(f'[p{i}]')
        # octave shadow, very quiet
        chains.append(f"sine=f={f * 2 if f > 130 else f / 2}:d={dur}:r={SR},volume={amp * .22}[q{i}]")
        labels.append(f'[q{i}]')
    tail = 'lowpass=f=2400,volume=0.9'
    if trem:
        tail += (f',tremolo=f={trem:.2f}:d=0.4,afade=t=in:d=1.6,'
                 f'afade=t=out:st={dur - 1.8:.2f}:d=1.8')
    fc = ';'.join(chains) + ';' + ''.join(labels) + \
        f"amix=inputs={len(labels)}:duration=first:normalize=0,{tail}[out]"
    run(['-filter_complex', fc, '-map', '[out]', '-t', f'{dur:.2f}', '-ar', str(SR), str(out)])


def build_score(out):
    sections = [
        ([110.00, 164.81, 220.00, 277.18], 24.0, .085, .17),   # dawn, morning minor
        ([130.81, 196.00, 261.63, 329.63], 24.0, .095, .15),   # street, lifted
        ([98.00, 146.83, 196.00, 233.08], 22.0, .070, .10),    # night, settles
    ]
    parts = []
    for i, (notes, dur, amp, trem) in enumerate(sections):
        path = out.with_name(f'sc{i}.wav')
        pad_section(notes, dur, amp, trem, path)
        parts.append(path)
    lst = out.with_name('sc_list.txt')
    lst.write_text(''.join(f"file '{p.name}'\n" for p in parts))
    raw = out.with_name('sc_raw.wav')
    run(['-f', 'concat', '-safe', '0', '-i', str(lst), '-t', str(DUR), '-ar', str(SR), str(raw)])
    raw.replace(out)


def build_room(out):
    """Interior room tone for the dawn act, cut to the door line."""
    run(['-filter_complex',
         f"sine=f=48:d=18,volume=0.05[h];"
         f"anoisesrc=d=18:c=pink:r={SR}:a=0.010,lowpass=f=800[n];"
         f"[h][n]amix=inputs=2:duration=first:normalize=0,"
         f"tremolo=f=0.12:d=0.3[out]",
         '-map', '[out]', '-t', '18', '-ar', str(SR), str(out)])


def build_street(out):
    """Exterior wash: wind + traffic hiss, with the press scrum layered in."""
    run(['-filter_complex',
         f"anoisesrc=d=40:c=pink:r={SR}:a=0.055,lowpass=f=2000,highpass=f=90[s1];"
         f"anoisesrc=d=40:c=brown:r={SR}:a=0.045,lowpass=f=500[s2];"
         f"sine=f=64:d=40,volume=0.02[s3];"
         f"[s1][s2][s3]amix=inputs=3:duration=first:normalize=0,"
         f"tremolo=f=0.21:d=0.22[out]",
         '-map', '[out]', '-t', '40', '-ar', str(SR), str(out)])


def build_crowd(out):
    """A murmur that swells for the press line: filtered noise with slow wobble."""
    run(['-filter_complex',
         f"anoisesrc=d=30:c=pink:r={SR}:a=0.05,bandpass=f=1200:width_type=o:w=2.4[c1];"
         f"anoisesrc=d=30:c=pink:r={SR}:a=0.04,bandpass=f=600:width_type=o:w=2.0[c2];"
         f"[c1][c2]amix=inputs=2:duration=first:normalize=0,"
         f"tremolo=f=2.7:d=0.7,volume=0.7[out]",
         '-map', '[out]', '-t', '30', '-ar', str(SR), str(out)])


def one_shot(kind, out, dur=.5):
    d = f'{dur:.3f}'
    if kind == 'shutter':
        run(['-filter_complex',
             f"anoisesrc=d={d}:c=white:r={SR}:a=0.9,highpass=f=1800,"
             f"afade=t=in:d=0.004,afade=t=out:st=0.02:d=0.10[s1];"
             f"anoisesrc=d={d}:c=white:r={SR}:a=0.5,highpass=f=900,"
             f"afade=t=in:d=0.004,afade=t=out:st=0.05:d=0.09[s2];"
             f"[s1][s2]amix=inputs=2:duration=first:normalize=0[out]",
             '-map', '[out]', '-ar', str(SR), str(out)])
    elif kind == 'door':
        run(['-filter_complex',
             f"sine=f=72:d={d}:r={SR},volume=0.7,afade=t=out:st=0.02:d=0.42[t];"
             f"anoisesrc=d={d}:c=brown:r={SR}:a=0.7,lowpass=f=420,"
             f"afade=t=in:d=0.004,afade=t=out:st=0.03:d=0.30[n];"
             f"[t][n]amix=inputs=2:duration=first:normalize=0[out]",
             '-map', '[out]', '-ar', str(SR), str(out)])
    elif kind == 'step':
        run(['-filter_complex',
             f"anoisesrc=d={d}:c=brown:r={SR}:a=0.55,lowpass=f=700,"
             f"afade=t=in:d=0.006,afade=t=out:st=0.01:d=0.20[n];"
             f"sine=f=96:d={d}:r={SR},volume=0.25,afade=t=out:st=0.0:d=0.16[t];"
             f"[n][t]amix=inputs=2:duration=first:normalize=0[out]",
             '-map', '[out]', '-ar', str(SR), str(out)])
    elif kind == 'pour':
        run(['-filter_complex',
             f"anoisesrc=d={d}:c=pink:r={SR}:a=0.30,bandpass=f=2600:width_type=o:w=1.6,"
             f"tremolo=f=13:d=0.6,afade=t=in:d=0.10,afade=t=out:st={dur - .20:.2f}:d=0.18[out]",
             '-map', '[out]', '-ar', str(SR), str(out)])
    elif kind == 'swell':
        run(['-filter_complex',
             f"sine=f=196:d={d}:r={SR},volume=0.05,"
             f"afade=t=in:d={dur * .5:.2f},afade=t=out:st={dur * .55:.2f}:d={dur * .45:.2f}[t];"
             f"anoisesrc=d={d}:c=pink:r={SR}:a=0.10,highpass=f=2200,"
             f"afade=t=in:d={dur * .55:.2f},afade=t=out:st={dur * .6:.2f}:d={dur * .4:.2f}[n];"
             f"[t][n]amix=inputs=2:duration=first:normalize=0[out]",
             '-map', '[out]', '-ar', str(SR), str(out)])
    else:
        raise ValueError(kind)


def place_many(events, out):
    """Stack one-shots at absolute times. adelay is single-input: one per event."""
    inputs, chains, labels = [], [], []
    for k, (src, at, amp) in enumerate(events):
        inputs += ['-i', str(src)]
        chains.append(f"[{k}:a]volume={amp},adelay={int(at * 1000)}|{int(at * 1000)}[e{k}]")
        labels.append(f'[e{k}]')
    fc = ';'.join(chains) + f";{''.join(labels)}amix=inputs={len(labels)}:normalize=0[out]"
    run(['-filter_complex', fc, *inputs, '-map', '[out]', '-t', str(DUR),
         '-ar', str(SR), str(out)])


def main(silent_mp4, out_mp4):
    cues = json.loads((P / 'script.json').read_text())
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        # ---- clock
        build_score(td / 'score.wav')
        build_room(td / 'room.wav')
        build_street(td / 'street.wav')
        build_crowd(td / 'crowd.wav')

        # room tone: dawn interior, hands to the street at the window line
        run(['-filter_complex',
             "[0:a]atrim=0:18,asetpts=PTS-STARTPTS,afade=t=out:st=16:d=2[r];"
             "[1:a]atrim=0:40,asetpts=PTS-STARTPTS,afade=t=in:d=2.5,afade=t=out:st=37.5:d=2.5,"
             "adelay=17000|17000[s];"
             "[2:a]atrim=0:30,asetpts=PTS-STARTPTS,afade=t=in:d=4,afade=t=out:st=26:d=4,"
             "adelay=22000|22000[c];"
             "[r][s][c]amix=inputs=3:duration=longest:normalize=0,volume=0.55[bed]",
             '-i', str(td / 'room.wav'), '-i', str(td / 'street.wav'),
             '-i', str(td / 'crowd.wav'), '-map', '[bed]', '-t', str(DUR),
             '-ar', str(SR), str(td / 'bed.wav')])

        # ---- foley: every hit is tied to a picture event
        for kind, name in (('shutter', 'shutter'), ('door', 'door'), ('step', 'step'),
                           ('pour', 'pour'), ('swell', 'swell')):
            one_shot(kind, td / f'{name}.wav', dur={'shutter': .30, 'door': .60,
                                                   'step': .30, 'pour': 1.2, 'swell': 2.4}[kind])
        ev = []
        # phone buzzing on the nightstand, then his alarm-level missed calls
        for i in range(3):
            ev.append((td / 'step.wav', CUE_DAWN + 1.2 + i * 1.9, .18))
        # coffee poured at the kitchen line
        ev.append((td / 'pour.wav', CUE_KITCHEN + 2.1, .55))
        # walk to the door and out
        for i in range(9):
            ev.append((td / 'step.wav', CUE_STREET - 1.6 + i * .52, .42))
        ev.append((td / 'door.wav', CUE_STREET - .30, .55))
        # shutters across the street and press beats
        for i in range(13):
            ev.append((td / 'shutter.wav', CUE_STREET + .55 + i * .62 + (i % 3) * .11, .26))
        for i in range(11):
            ev.append((td / 'shutter.wav', CUE_PRESS + .25 + i * .48 + (i % 4) * .07, .30))
        # the pause at the barrier, then the reach
        ev.append((td / 'swell.wav', CUE_BARRIER + .20, .80))
        ev.append((td / 'swell.wav', CUE_REACH + .30, .65))
        # car door
        ev.append((td / 'door.wav', CUE_CAR + .95, .70))
        # night: one soft step, then nothing
        ev.append((td / 'step.wav', CUE_NIGHT + 3.4, .22))
        place_many(ev, td / 'foley.wav')

        # ---- narration, each take at its cue
        take_dir = V6 / 'trimmed'
        n_in, n_ch, n_lab = [], [], []
        for i, c in enumerate(cues):
            n_in += ['-i', str(take_dir / f'{i + 1:02d}.wav')]
            n_ch.append(f"[{i}:a]adelay={int(c['start'] * 1000)}|{int(c['start'] * 1000)}[n{i}]")
            n_lab.append(f'[n{i}]')
        fc = ';'.join(n_ch) + f";{''.join(n_lab)}amix=inputs={len(cues)}:normalize=0[vox]"
        run(['-filter_complex', fc, *n_in, '-map', '[vox]', '-t', str(DUR),
             '-ar', str(SR), str(td / 'vox.wav')])

        # ---- mix: voice forward, score tucked under, effects for contact
        run(['-filter_complex',
             "[0:a]volume=1.0[v];[1:a]volume=0.34[s];[2:a]volume=0.60[b];[3:a]volume=0.80[f];"
             "[v][s][b][f]amix=inputs=4:duration=longest:normalize=0,"
             "acompressor=threshold=0.14:ratio=2.2:attack=14:release=200,"
             "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[aout]",
             '-i', str(td / 'vox.wav'), '-i', str(td / 'score.wav'),
             '-i', str(td / 'bed.wav'), '-i', str(td / 'foley.wav'),
             '-map', '[aout]', '-t', str(DUR), '-ar', str(SR), str(td / 'mix.wav')])

        run(['-i', str(silent_mp4), '-i', str(td / 'mix.wav'),
             '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
             '-c:a', 'aac', '-b:a', '192k', '-shortest', str(out_mp4)])

    probe = subprocess.run([FF, '-i', str(out_mp4)], capture_output=True, text=True)
    for line in probe.stderr.splitlines():
        if 'Duration' in line or 'Stream' in line:
            print(line.strip())
    print('OUTPUT', out_mp4)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
