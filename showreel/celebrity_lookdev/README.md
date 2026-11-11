# Third-person 3D look-development (not a finished video)

The previous mannequin video did not meet the user's direction. This is an internal asset-integration experiment, **not a replacement deliverable**. It tests a skinned character with facial morphs and imported motion clips together with textured furniture under 3D lights. All visible elements in `scene.py` are geometry, not still-image backgrounds. No source footage is included.

Four discrete stills of `Phone_Rig` were rendered at frames 1, 100, 200 and 350; two were visually inspected. The character moves a hand near the ear, but there is **no phone prop or contact**, and the room and skyline still look sparse and artificial. The character's appearance is realistic game-like, not the source video's stylized design. No full animation, audio or finished video has been produced here. Do not describe this as the desired premium result.

Next production work must address: visual design consistent with the reference rather than a generic avatar; complete layered sets and physically plausible lighting; authored character actions, object grips/contact and continuity; shot-specific camera and editing; final audio; and visual/audio review of the resulting video. A better asset does not solve those requirements by itself.

## Assets

`assets.json` pins each external GLB by Git blob and SHA-256; `fetch_assets.py` downloads only those exact files via the GitHub CLI to a directory outside the repo. No weight/model blobs are committed. The character is from `memoriesrohit/avatar-studio`, based on Microsoft Rocketbox under MIT. It is generic and is not a likeness or endorsement. The furniture models are Poly Haven CC0 as documented by `Sanikaa205/INTERIO/public/assets/furniture/LICENSES.md`; the adapted copies have reduced textures and renamed materials. The full MIT notice is in `ROCKETBOX-MIT.txt`. The code here is original to this repo.

## Reproduce still experiment

Requires Python 3.11, bpy 4.2.23, its system libraries, GitHub CLI, and Pillow/NumPy as appropriate for further processing. It is a Blender Cycles test, not a complete animation pipeline.

```sh
python showreel/celebrity_lookdev/fetch_assets.py /path/to/assets
python showreel/celebrity_lookdev/scene.py --assets /path/to/assets --output /path/to/stills --samples 8
python -m unittest discover -s showreel/celebrity_lookdev/tests -v
```
