# Extinct Life V14 — selected YouTube launch kit

## Use this pairing

**Title:** A Lost World Hidden in Greenland’s Dirt  
**Thumbnail:** `thumbnails/thumbnail-B.jpg` (3840×2160; 1.14 MB)  
**Compatibility export:** `thumbnails/thumbnail-B-1280.jpg` (1280×720; 0.23 MB)

The user selected B artwork option 1. Both A options were declined, so no A image is presented as approved. B’s typography reads **2 MILLION YEARS**. These are hypotheses for audience testing, not guaranteed million-view packaging. The image is an AI-generated editorial illustration, not film footage; the small illustration label and description make that explicit.

## Ready to paste / upload

- `DESCRIPTION.txt`: full description, eight timed chapters, primary study and both required music credits.
- `TAGS.txt`: modest relevant tags and alternative spellings.
- `PINNED-COMMENT.txt`: honest discussion prompt.
- `English.srt`: byte-identical captions copied from the approved full English master.
- `UPLOAD-METADATA.json`: selected title, description, category/language recommendations, captions, community post, upload checks and selected thumbnail paths.
- `TITLE-OPTIONS.md` / `.json`: fifteen options with length and trade-offs. Search challenger: **2-Million-Year-Old DNA Revealed Greenland’s Lost World**.

## Research and evidence

- `RESEARCH-AND-LAUNCH-PLAN.md`: full twenty-video audit, visual observations, click-mechanism hypotheses, scientific boundaries and native-test plan.
- `RESEARCH-CORPUS.json` / `.csv`: twenty successful public-page metadata audits; fifteen fetched million-plus videos. Public snapshots may be cached. Not authenticated Data API/private Studio metrics.
- `VISUAL-REFERENCE-LOG.json`: six usable indexed visual references; two returned images unusable. Not twenty original historical thumbnails or twenty complete-video watches.
- `THUMBNAIL-PROVENANCE.json`: actual artwork selection, source/exports hashes, crop, typography and fidelity limitations.
- `PACKAGE-VALIDATION.json`: metadata/export contract checks, not a virality certificate.
- `EXPERIMENT-LOG.csv`: intentionally empty results template. Current actionable experiment is title-only B versus A versus C with selected B image held fixed. A/B thumbnail testing requires another approved artwork.

## Reproduce in the repository

```sh
.venv/bin/python production/extinct-life/youtube-v14/render_thumbnail.py
.venv/bin/python production/extinct-life/youtube-v14/validate_package.py --require-thumbnails
```

Rendering uses Pillow and the repository’s Anton/Manrope font files. The ZIP contains final files and source artwork; rerendering scripts assume the repository layout. The standalone `START-HERE.html` presents the selected thumbnail, copy buttons, title options and full research report without network dependencies for its core display.

Fonts: Anton and Manrope, SIL Open Font License; texts retained in `licenses/`. Rendered thumbnail lettering does not imply exclusive ownership of the fonts. Competitor reference images are not redistributed or embedded in the final artwork.

No YouTube upload, scheduled publication, private channel access or live audience test was performed. Owner must confirm audience/disclosure settings and review music/rights checks in actual Studio. The film and V13 are unchanged by this packaging work.
