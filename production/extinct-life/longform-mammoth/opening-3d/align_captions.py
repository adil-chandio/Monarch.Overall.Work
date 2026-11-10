"""Align the known narration transcript to the unsped voice take.

PocketSphinx estimates word boundaries from the audio and known text. It is
not a substitute for a listening review; a custom pronunciation is provided
for Wrangel and genomes. Timeline creation adds the mix start offset.
"""
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg

B = Path(__file__).resolve().parent
SRC = B / 'source'
ff = imageio_ffmpeg.get_ffmpeg_exe()

SENTENCES = [
    "This mammoth may have had an extraordinary coat.",
    "Scientists found two mutations in a gene linked to hair development.",
    "They predicted a silky coat, but could not observe it directly.",
    "The animal lived on Wrangel Island, in the Arctic Ocean, a few thousand years ago.",
    "Now the strange part.",
    "A later study of ancient genomes found that the island population recovered after an extreme bottleneck.",
    "Yet the mammoths eventually disappeared.",
    "How can both things be true?",
    "Scientists have examined genetic damage, climate, and human arrival, but the final generations are missing from the genetic record.",
    "So which explanation holds up?",
    "We will take the evidence apart, and at the end, separate what is proven, what is plausible, and what is still missing from the file.",
]
CHUNKS = [
    ["This mammoth may have had", "an extraordinary coat."],
    ["Scientists found two mutations", "in a gene linked", "to hair development."],
    ["They predicted a silky coat,", "but could not observe it directly."],
    ["The animal lived on Wrangel Island,", "in the Arctic Ocean,", "a few thousand years ago."],
    ["Now the strange part."],
    ["A later study of ancient genomes", "found that the island population", "recovered after an extreme bottleneck."],
    ["Yet the mammoths eventually disappeared."],
    ["How can both things be true?"],
    ["Scientists have examined genetic damage,", "climate, and human arrival,", "but the final generations", "are missing from the genetic record."],
    ["So which explanation holds up?"],
    ["We will take the evidence apart,", "and at the end,", "separate what is proven,", "what is plausible,", "and what is still missing", "from the file."],
]


def main():
    # Align the actual take to the exact known transcript, not an invented ASR
    # transcript. PocketSphinx word boundaries are estimates and still require
    # editorial listening review, especially for names and soft syllables.
    import re
    from pocketsphinx import Decoder

    raw_path = B / 'source' / 'alignment-16k.raw'
    subprocess.run([ff, '-y', '-v', 'error', '-i', str(SRC / 'narration.mp3'),
                    '-ar', '16000', '-ac', '1', '-f', 's16le', str(raw_path)], check=True)
    raw = raw_path.read_bytes()
    raw_path.unlink()
    normalize = lambda s: re.sub(r"[^a-z ]", "", s.lower()).split()
    expected = normalize(' '.join(SENTENCES))
    d = Decoder(samprate=16000, loglevel='ERROR')
    d.add_word('wrangel', 'R AE NG G AH L', False)
    d.add_word('genomes', 'JH IY N OW M Z', False)
    unknown = sorted({w for w in expected if not d.lookup_word(w)})
    if unknown:
        raise ValueError('Missing alignment dictionary words: ' + ', '.join(unknown))
    d.set_align_text(' '.join(expected))
    d.start_utt()
    d.process_raw(raw, False, True)
    d.end_utt()
    segments = [x for x in d.seg() if not x.word.startswith('<')]
    actual = [re.sub(r'\(\d+\)$', '', x.word).lower() for x in segments]
    if actual != expected:
        raise ValueError('Forced alignment did not preserve the known transcript')

    cues = []
    i = 0
    for group in CHUNKS:
        for chunk in group:
            words = normalize(chunk)
            if expected[i:i + len(words)] != words:
                raise ValueError('Caption chunk does not match the transcript: ' + chunk)
            seg = segments[i:i + len(words)]
            cues.append({'start': round(seg[0].start_frame / 100, 3),
                         'end': round((seg[-1].end_frame + 1) / 100, 3), 'text': chunk})
            i += len(words)
    if i != len(expected):
        raise ValueError('Caption chunks do not cover transcript')
    audio_seconds = len(raw) / 2 / 16000
    meta = {
        'source': 'narration.mp3 (platform synthesised voice-04, unsped)',
        'audio_seconds': round(audio_seconds, 3),
        'sample_rate': 16000,
        'alignment_method': 'PocketSphinx 5.1.1 known-transcript word alignment',
        'alignment_caveat': 'Automatic forced alignment estimates word boundaries; it is not a human listening review.',
        'cue_count': len(cues),
        'cues': cues,
    }
    (B / 'caption-alignment.json').write_text(json.dumps(meta, indent=2) + '\n')
    print(json.dumps({k: v for k, v in meta.items() if k != 'cues'}, indent=2))
    for c in cues:
        print(f"{c['start']:6.2f} - {c['end']:6.2f}  {c['text']}")


if __name__ == '__main__':
    main()
