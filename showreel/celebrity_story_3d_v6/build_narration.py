"""Trim the recorded takes, fit them to the 60 s cut, and write script.json.

The takes are trimmed to speech (RMS gate), then a single global tempo factor
packs them into the target, so the voice keeps one constant speed instead of
each line being squeezed differently.
"""
from pathlib import Path
import json, subprocess, sys, wave, audioop
import imageio_ffmpeg

P = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TEXT = [
    "At five forty in the morning, the city is still asleep. His phone is already awake.",
    "Three missed calls. Two shoot days. One hour before the car arrives.",
    "So he does what he always does. Coffee first. Everything else can wait a minute.",
    "By eight, the street outside his building has changed. They know the car. They know the windows.",
    "The door opens, and the noise hits him all at once. His name, from every direction.",
    "Then the flashes start, and the smile is not fake. It is just practiced.",
    "One girl at the barrier is not holding a phone. She is shaking. He stops walking.",
    "He reaches over the barrier, and for a second he is not a headline. He is just someone who listened.",
    "Then the car door closes, and the street goes quiet again.",
    "Hours later, the apartment is dark. He sits on the floor, back against the sofa. Nobody is watching.",
]


def convert(src, dst, tempo=None):
    cmd = [FF, '-y', '-v', 'error', '-i', str(src)]
    if tempo:
        cmd += ['-filter:a', f'atempo={tempo:.5f}']
    cmd += ['-ac', '1', '-ar', '24000', str(dst)]
    subprocess.run(cmd, check=True)


def trim_speech(path, pad_head=.02, pad_tail=.06):
    with wave.open(str(path)) as w:
        rate = w.getframerate()
        raw = w.readframes(w.getnframes())
    frame = rate // 100
    marks = []
    for i in range(0, len(raw) - frame, frame):
        if audioop.rms(raw[i:i + frame], 2) > 240:
            marks.append(i / (2 * rate))
    if not marks:
        return 0.0, len(raw) / (2 * rate)
    a = max(0.0, marks[0] - pad_head)
    b = min(len(raw) / (2 * rate), marks[-1] + pad_tail)
    return a, b


def main():
    takes = sorted((P / 'audio').glob('*.wav'))
    if len(takes) != len(TEXT):
        raise SystemExit(f'expected {len(TEXT)} takes, found {len(takes)}')
    trim_dir = P / 'trimmed'
    trim_dir.mkdir(exist_ok=True)
    spans = []
    for i, src in enumerate(takes, 1):
        tmp = trim_dir / f'raw{i:02d}.wav'
        convert(src, tmp)
        a, b = trim_speech(tmp)
        spans.append((tmp, a, b))
    gap = .16
    gross = sum(b - a for _, a, b in spans)
    lead = .26
    total = lead + gross + gap * (len(spans) - 1)
    tempo = max(1.0, total / 59.2)
    print('gross', round(gross, 3), 'total', round(total, 3), 'tempo', round(tempo, 4))
    cues = []
    cursor = lead
    for i, (tmp, a, b) in enumerate(spans, 1):
        out = trim_dir / f'{i:02d}.wav'
        subprocess.run([FF, '-y', '-v', 'error', '-ss', f'{a:.3f}', '-to', f'{b:.3f}',
                        '-i', str(tmp), '-filter:a', f'atempo={tempo:.5f}',
                        '-ac', '1', '-ar', '24000', str(out)], check=True)
        with wave.open(str(out)) as w:
            dur = w.getnframes() / w.getframerate()
        cues.append({'start': round(cursor, 3), 'duration': round(dur, 3), 'text': TEXT[i - 1]})
        cursor += dur + gap * (1 / tempo)
    (P / 'script.json').write_text(json.dumps(cues, indent=1) + '\n')
    print('speech ends', round(cues[-1]['start'] + cues[-1]['duration'], 3))


if __name__ == '__main__':
    main()
