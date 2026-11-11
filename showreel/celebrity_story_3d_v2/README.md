# A Day in the Spotlight — 3D revision

A 60-second fictional celebrity day, rendered in third person. No named celebrity is depicted, and it is not a factual biography or endorsement. The sets, characters, objects, lights and cameras are 3D; no source-video frames, still-image background plates or stock footage are used.

## Revision

Compared with `../celebrity_story_3d`, this version renders natively at **640×360 and 24 fps**, with two Cycles samples per frame and denoising. It adds a formal outfit for the public appearances, simple face-shape smiles and blinks, cooler twilight in the final room, room dressing and more complete photographers. The walk cycle's baked root translation is compensated at loop boundaries, using measured displacement from the imported rig; a test evaluates the hip position at the boundary. These are improvements, not a claim of physically exact motion or perfect facial performance.

## Limits

The visual remains game-like and differs from the original illustrated reference. Sets, crowd detail, some holds, body dynamics and person-to-person interaction remain simplified; the phone and cup use approximate wrist attachments, not physically simulated grips. Formal clothes switch at a cut rather than being physically changed. The score and narration are the same original synthetic tracks as the earlier version; the final mix has not been human-listened to. Do not describe the film as flawless, photoreal, a full physics simulation or an exact reference recreation. Verify all rights before public or commercial release.

## Assets and audio

The rigged character models and animation derive from the Microsoft Rocketbox Avatar Library, MIT, copyright © 2020 Microsoft, via `memoriesrohit/avatar-studio`; the full notice is `../celebrity_lookdev/ROCKETBOX-MIT.txt`. Furniture models are Poly Haven CC0, prepared by `Sanikaa205/INTERIO`. Sources and pinned hashes are in `../celebrity_lookdev/assets.json`. City, sets, foliage and other props are independently modeled geometry.

The fictional English narration uses Piper Amy. Its model card points to Mycroft Mimic 3 voice data; one third-party description reports CC BY-SA 4.0 for that data. Exact model/output rights have not been independently resolved. Music and effects are original procedural synthesis in `mux.py`.

- https://github.com/memoriesrohit/avatar-studio/blob/main/THIRD_PARTY_NOTICES.md
- https://github.com/Sanikaa205/INTERIO/blob/main/public/assets/furniture/LICENSES.md
- https://huggingface.co/rhasspy/piper-voices/blob/v1.0.0/en/en_US/amy/medium/MODEL_CARD
- https://huggingface.co/qualcomm/PiperTTS-EN-Amy

## Reproduce

Requires Python 3.11, bpy 4.2.23, Pillow, NumPy, imageio-ffmpeg and Blender's system graphics libraries. Download the pinned assets outside the repository; voice WAV files are included.

```sh
python showreel/celebrity_lookdev/fetch_assets.py /path/to/assets
python -m unittest discover -s showreel/celebrity_story_3d_v2/tests -v
python showreel/celebrity_story_3d_v2/render.py --assets /path/to/assets --width 640 --fps 24 --samples 2 --output /path/to/silent.mp4
python showreel/celebrity_story_3d_v2/mux.py /path/to/silent.mp4 deliverables/celebrity-story-third-person-3d-v2.mp4
```

The film was rendered in twelve five-second shards on GitHub Actions and assembled; `assemble.py` also accepts the downloaded shard directories. Artifact retention is limited, so the complete render command above is the durable path.

## QC

FFmpeg decoded all **1,440 frames and audio**, 60 seconds. Visual review covered all 60 seconds at approximately 1 fps, plus selected walking and waving windows at 6 fps—not every frame. Four tests passed, covering cue lengths, facial-blink bounds, loop-offset arithmetic and evaluated hip continuity at the imported walk-loop seam. They do not certify visual quality, foot contact or audio. Mean/max sample audio levels were -16.7/-1.3 dBFS, not true-peak or listening checks. SHA-256: `9d81a4933ddcbea07cccbd28e54e9ba812c9e36b128f51e7218008d7a6afc0ab`.
