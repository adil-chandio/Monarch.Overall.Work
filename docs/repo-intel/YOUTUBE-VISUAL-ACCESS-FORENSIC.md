# YouTube target-video visual access — forensic status

## Scope and evidence standard
This is a limited inspection of **nine public YouTube thumbnail candidates**, not playback and not a frame-by-frame analysis. Their exact source timestamps, whether each reflects the current video, and chronological ordering were **not verified**. Numbered filenames are identifiers, not proof of sequence or timing. The 120×90 images are too small to reliably identify fine details or motion. The generated thumbnail candidates are third-party material: do not reuse them in production without assessing rights and applicable YouTube terms.

The three YouTube IDs were already identified in our competitor research. GitHub Actions retrieved `1.jpg`, `2.jpg`, `3.jpg` for each from publicly served `i.ytimg.com` thumbnail URLs. Each JPEG was transferred for temporary inspection, and its SHA-256 was checked against the runner's independently saved metadata in `yt-public-thumbnail-probe.json`. No audiovisual video was received. The images were not added to this repository. Higher-quality `hqdefault.jpg` was retrieved by the runner, but **not visually inspected** in this review.

## What was actually visible

### DusanFC — POV: YOU ARE NEYMAR (`aWHX5Awe_TI`)
- [`1.jpg`](https://i.ytimg.com/vi/aWHX5Awe_TI/1.jpg): vertical image with a white headline band; a footballer in white/blue faces a light-blue opponent on a pitch.
- [`2.jpg`](https://i.ytimg.com/vi/aWHX5Awe_TI/2.jpg): vertical football goal/pitch view with a foreground limb, ball and dark-clad figure; white headline band. Fine identity and action cannot be established at this size.
- [`3.jpg`](https://i.ytimg.com/vi/aWHX5Awe_TI/3.jpg): vertical crowd/people scene beneath the same style of headline band.

**Implication, limited:** these look like live-action/photographic footage rather than proof of an animated character. This corrects any earlier assumption that this particular competitor clip was necessarily an animation reference. The stills alone cannot establish the full video structure, POV mechanics, editing rhythm, exact action or rights status.

### LV Animation — football animation (`8wtQAI_ZZlQ`)
- [`1.jpg`](https://i.ytimg.com/vi/8wtQAI_ZZlQ/1.jpg), [`2.jpg`](https://i.ytimg.com/vi/8wtQAI_ZZlQ/2.jpg), [`3.jpg`](https://i.ytimg.com/vi/8wtQAI_ZZlQ/3.jpg): all three show a football pitch/stadium-like setting with multiple football-clad figures seated or posed centrally, bright blue overhead lights, and darker enlarged side areas. The second candidate shows a red-clad figure in a more extended pose; the third shows a prominently colored ball-like object.
- **Limitation:** images have an edited/rendered appearance, but these low-resolution stills cannot establish whether the video uses 3D, compositing, AI-generated imagery, or how movement was made. No actual motion was observed.

### Stick Stuff Happens — stickman snooze (`GHT3RyE9wGI`)
- [`1.jpg`](https://i.ytimg.com/vi/GHT3RyE9wGI/1.jpg): simple flat bedroom composition: bed and figure, window, bedside table, clock/rooster-like graphic.
- [`2.jpg`](https://i.ytimg.com/vi/GHT3RyE9wGI/2.jpg): similar bedroom setup with changed small foreground poses/objects.
- [`3.jpg`](https://i.ytimg.com/vi/GHT3RyE9wGI/3.jpg): closer composition of a red-rimmed alarm clock and orange rooster-like figure above a bedside table.
- **Limitation:** visuals suggest a simple graphic style and a change of framing between candidates, but they cannot establish timing, whether a cut or camera zoom occurred, the frame holds, sound, or causation.

## Tests and results

1. **Official watch pages, automated Chromium:** all three returned `LOGIN_REQUIRED`, no advancing player time and no decoded video dimensions. See `yt-browser-probe.json` and `yt-preview-metadata-probe.json`. This is specific to the tested GitHub runner and does not mean a normal user's browser cannot play them.
2. **Public storyboard metadata:** none exposed on those watch responses. Numbered thumbnail candidates above are not equivalent to timeline storyboards or video playback.
3. **Official Google video-understanding API:** GitHub Actions tried all distinct configured Google/YouTube key slots. The only configured distinct key returned HTTP 403 `PERMISSION_DENIED`, reason `SERVICE_DISABLED`, from the models endpoint. No competitor video was sent for analysis after that check. See `yt-official-video-probe.json`. No credential values were printed or stored.
4. **Third-party repository research:** representative extractors depend on video access/download before FFmpeg/OpenCV processing; a different wrapper does not make the protected player playable. [Example](https://github.com/EnragedAntelope/youtube-screenshot-extractor).
5. **Creator-published mirrors:** search results for the exact IDs/title did not establish an authorized alternate full copy of the target clips. Similar-looking unrelated search hits were excluded.

## Next viable path and boundary
Google's [official video-understanding API](https://ai.google.dev/gemini-api/docs/video-understanding) documents public YouTube URL input and configurable static sampling. Google documents default 1 fps; [the generate-content API reference](https://ai.google.dev/api/generate-content) lists an fps range up to 24. This yields **model analysis of samples**, not an independently inspectable export of all source frames; service availability, model, quotas and behavior need testing. A 30/60 fps source cannot be assumed to have all frames processed at a 24 fps sampling cap. The current project requires its administrator to enable/authorize the appropriate Google service; a key or token must not be pasted into chat.

For demonstrably complete decoded-frame inspection, the input must be an original or otherwise authorized copy with frame timestamps, not metadata, still thumbnails or an unverified AI summary. Do not conflate a legitimate public preview with permission to extract or redistribute the whole YouTube audiovisual stream. In every route, separate model inference and actual observations, and never represent sparse samples as frame-by-frame coverage.
