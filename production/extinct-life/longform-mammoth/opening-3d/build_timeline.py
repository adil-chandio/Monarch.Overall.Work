"""Build the single timeline source for the 3D opening (shots + caption cues)."""
import json
from pathlib import Path

B = Path(__file__).resolve().parent
DURATION = 60.0
FPS = 30
WIDTH, HEIGHT = 1920, 1080

# Each shot: kind drives the 3D behaviour in scene.mjs.
SHOTS = [
    dict(id='wide-floe', kind='wide', start=0.0, end=4.35),
    dict(id='shoulder-wool', kind='shoulder', start=4.35, end=13.65),
    dict(id='island-rise', kind='island', start=13.65, end=18.95),
    dict(id='strange-part', kind='strange', start=18.95, end=20.35),
    dict(id='genome-record', kind='genome', start=20.35, end=27.0),
    dict(id='two-truths', kind='truths', start=27.0, end=31.1),
    dict(id='four-witnesses', kind='witnesses', start=31.1, end=35.9),
    dict(id='empty-slot', kind='empty', start=35.9, end=40.7),
    dict(id='four-arcs', kind='arcs', start=40.7, end=44.0),
    dict(id='promise', kind='promise', start=44.0, end=50.6),
    dict(id='resolve', kind='resolve', start=50.6, end=60.0),
]

# Screen-space overlays: absolute seconds, 3D animated, attached to the camera.
# The "NO FINAL WITNESS" headline is not here: it is built into the 3D empty-slot
# frame itself, so the line and the thing it describes occupy the same object.
OVERLAYS = [
    dict(id='promise-1', start=44.4, end=50.5, text='PROVEN', sub='what the evidence supports', fx=.22, fy=.235, size=.28, accent='#9fe8c6'),
    dict(id='promise-2', start=44.4, end=50.5, text='PLAUSIBLE', sub='what it cannot rule out', fx=.50, fy=.235, size=.28, accent='#8fd6ff'),
    dict(id='promise-3', start=44.4, end=50.5, text='NOT IN THE FILE', sub='what nobody has evidence for', fx=.78, fy=.235, size=.28, accent='#ffb27a'),
    dict(id='title', start=52.6, end=59.6, text='THE LAST MAMMOTHS RECOVERED.', sub='THEN THEY VANISHED.', fx=.5, fy=.145, size=.40, accent='#e9dcc4', plate=True),
]


def main():
    alignment = json.loads((B / 'caption-alignment.json').read_text())
    captions = alignment['cues']
    for c in captions:
        c['start'] = round(c['start'] + 0.55, 3)
        c['end'] = round(c['end'] + 0.55, 3)
    shots = []
    for s in SHOTS:
        s = dict(s)
        s['start_frame'] = int(round(s['start'] * FPS))
        s['end_frame'] = int(round(s['end'] * FPS))
        shots.append(s)
    assert shots[0]['start'] == 0
    assert abs(shots[-1]['end'] - DURATION) < 1e-6
    for a, b in zip(shots, shots[1:]):
        assert abs(a['end'] - b['start']) < 1e-9, (a['id'], b['id'])

    timeline = {
        'width': WIDTH,
        'height': HEIGHT,
        'fps': FPS,
        'duration': DURATION,
        'total_frames': int(DURATION * FPS),
        'title': 'The Last Mammoths Recovered. Then They Vanished.',
        'segment': 'Opening 01 — 3D, first 60 seconds',
        'voice_id': 'voice-04',
        'narration': 'source/narration.mp3 (unsped)',
        'alignment': {
            'method': alignment['alignment_method'],
            'caveat': alignment['alignment_caveat'],
        },
        'shots': shots,
        'overlays': OVERLAYS,
        'captions': captions,
        'reconstruction_note': 'All mammoth, island and case-board imagery is original 3D reconstruction built for this film; it is an illustration, not a photograph, a scan or laboratory footage.',
    }
    (B / 'timeline.json').write_text(json.dumps(timeline, indent=2) + '\n')
    print(f"shots={len(shots)} overlays={len(OVERLAYS)} captions={len(captions)} frames={timeline['total_frames']}")
    print('caption coverage', round(sum(c['end'] - c['start'] for c in captions), 2), 's of', DURATION)


if __name__ == '__main__':
    main()
