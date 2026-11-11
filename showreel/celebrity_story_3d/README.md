# A Day in the Spotlight — third-person 3D video

A 60-second fictional celebrity day, told in third person, not a portrait of a real celebrity or a factual account. All visible environments, characters, props and cameras are 3D geometry rendered with Blender Cycles; no reference frames, still plates or stock footage are used. The opening includes a phone call and a coffee, followed by a walk, an event, a studio appearance, a fan greeting, and a return home.

## Important limitations

This is **not a perfect match** for the supplied reference, nor a premium finished film: the visual style is more game-like and realistic than the reference's illustrated round-faced characters. The rooms and crowds remain sparse; generic mocap actions are reused and some shots hold. The wrist-attached phone and cup are approximated, not dynamically gripped or collision-simulated. There is no realistic physical interaction between the two people. Lighting is approximate and the video is 480×270 at 18 fps. It therefore falls short of the user's requested quality and detail. The final audio has not been human-listened to. No guarantee of reference-derived public-publishing rights is made.

## Assets and audio

Character models and animations: Microsoft Rocketbox Avatar Library, MIT, Copyright (c) 2020 Microsoft, via `memoriesrohit/avatar-studio`; full notice `../celebrity_lookdev/ROCKETBOX-MIT.txt`. Furniture: Poly Haven CC0 models prepared by `Sanikaa205/INTERIO`. Exact sources, blob IDs and SHA-256 hashes are pinned in `../celebrity_lookdev/assets.json`. Original geometry includes the city, sets, foliage and props.

The original fictional English narration was synthesized with Piper Amy; music and shutter accents were synthesized in `mux.py`. Amy's model card points to Mycroft Mimic 3 voice data; a third-party description reports CC BY-SA 4.0 for that data. The exact rights and conditions for model/audio have not been independently resolved. Verify voice-model and reference-related rights before publishing.

- https://huggingface.co/rhasspy/piper-voices/blob/v1.0.0/en/en_US/amy/medium/MODEL_CARD
- https://huggingface.co/qualcomm/PiperTTS-EN-Amy
- https://github.com/memoriesrohit/avatar-studio/blob/main/THIRD_PARTY_NOTICES.md
- https://github.com/Sanikaa205/INTERIO/blob/main/public/assets/furniture/LICENSES.md

## Render

Requires Python 3.11, bpy 4.2.23, NumPy, Pillow, imageio-ffmpeg and Blender system libraries. Generated narration WAVs are included. Character and furniture files are fetched and checksum-verified outside the repository:

```sh
python showreel/celebrity_lookdev/fetch_assets.py /path/to/assets
python -m unittest discover -s showreel/celebrity_story_3d/tests -v
python showreel/celebrity_story_3d/render.py --assets /path/to/assets --output /path/to/silent.mp4
python showreel/celebrity_story_3d/mux.py /path/to/silent.mp4 deliverables/celebrity-story-third-person-3d.mp4
```

## QC

FFmpeg decoded all 1,080 video frames and audio. Thirty samples per 30-second contact sheet were inspected at 1 fps, plus roughly 3 fps samples from the coffee and carpet segments; not all frames were viewed. Sample mean/max levels were -16.7/-1.3 dBFS; these are not true-peak or listening quality checks. One narration-cue fit test and an asset-manifest pin test passed; these do not prove quality, physical accuracy or reference fidelity. SHA-256: `b0b7f7dbe813f4fac008ef251ffc32c1d82dea30030850aa02e705c7f24ebcc6`.
