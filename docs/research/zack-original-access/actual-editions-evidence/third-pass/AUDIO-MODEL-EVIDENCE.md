# Actual soundtrack model evidence — NOT verified listening

Source-verified actual soundtracks analyzed: **10/10**. ASR words: **867**. Overlapping audio-event windows: **69**.

Models: `Systran/faster-whisper-base.en` and `MIT/ast-finetuned-audioset-10-10-0.4593`. Speech-to-text and broad AudioSet labels are model-derived aids, not perceptual listening, isolated stems, precise SFX timing or verified music identification.

| Case | Seconds | ASR words | ASR words/full-clip minute | Word scores <0.8 | Event windows |
|---|---:|---:|---:|---:|---:|
| 01-hearts | 28.139 | 66 | 140.7 | 0 | 6 |
| 02-stomach | 26.752 | 69 | 154.8 | 3 | 6 |
| 03-splinter | 24.404 | 69 | 169.6 | 0 | 5 |
| 04-balloon | 34.760 | 97 | 167.4 | 4 | 7 |
| 05-surfer | 31.556 | 82 | 155.9 | 7 | 7 |
| 06-concert | 27.283 | 80 | 175.9 | 3 | 6 |
| 07-balcony | 32.213 | 85 | 158.3 | 5 | 7 |
| 08-ai | 54.010 | 128 | 142.2 | 10 | 11 |
| 09-fight | 28.189 | 85 | 180.9 | 3 | 6 |
| 10-jerboa | 38.551 | 106 | 165.0 | 9 | 8 |

## 01-hearts
Status: `model_analysis_complete`; source audio verified: `True`; method: `exact_encoded_audio_packet_hash`; direct remote encoded-audio comparison: `True`.
Model first-word start: 0.0s; last-word end: 27.52s. Timestamp-review indices: [].

Broad candidate labels (top five labels per overlapping window; scores not calibrated truth):
- Speech: peak model score 0.8486; appears in 6 top-five windows. This does not establish an audible event at an exact timestamp.
- Music: peak model score 0.8235; appears in 6 top-five windows. This does not establish an audible event at an exact timestamp.
- Heart sounds, heartbeat: peak model score 0.6773; appears in 3 top-five windows. This does not establish an audible event at an exact timestamp.
- Throbbing: peak model score 0.2734; appears in 3 top-five windows. This does not establish an audible event at an exact timestamp.
- Hum: peak model score 0.2403; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.
- Heart murmur: peak model score 0.1325; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.

## 02-stomach
Status: `model_analysis_complete`; source audio verified: `True`; method: `authenticated_local_PCM_transfer`; direct remote encoded-audio comparison: `None`.
Model first-word start: 0.0s; last-word end: 26.02s. Timestamp-review indices: [].

Broad candidate labels (top five labels per overlapping window; scores not calibrated truth):
- Music: peak model score 0.7883; appears in 6 top-five windows. This does not establish an audible event at an exact timestamp.
- Speech: peak model score 0.7661; appears in 6 top-five windows. This does not establish an audible event at an exact timestamp.
- Crumpling, crinkling: peak model score 0.3863; appears in 6 top-five windows. This does not establish an audible event at an exact timestamp.
- Crack: peak model score 0.2105; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.
- Crunch: peak model score 0.0897; appears in 4 top-five windows. This does not establish an audible event at an exact timestamp.
- Spray: peak model score 0.0750; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.

## 03-splinter
Status: `model_analysis_complete`; source audio verified: `True`; method: `exact_encoded_audio_packet_hash`; direct remote encoded-audio comparison: `True`.
Model first-word start: 0.0s; last-word end: 23.76s. Timestamp-review indices: [].

Broad candidate labels (top five labels per overlapping window; scores not calibrated truth):
- Speech: peak model score 0.9390; appears in 5 top-five windows. This does not establish an audible event at an exact timestamp.
- Music: peak model score 0.7439; appears in 5 top-five windows. This does not establish an audible event at an exact timestamp.
- Single-lens reflex camera: peak model score 0.3527; appears in 3 top-five windows. This does not establish an audible event at an exact timestamp.
- Spray: peak model score 0.2357; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.
- Speech synthesizer: peak model score 0.1345; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.
- Crack: peak model score 0.1007; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.

## 04-balloon
Status: `model_analysis_complete`; source audio verified: `True`; method: `exact_encoded_audio_packet_hash`; direct remote encoded-audio comparison: `True`.
Model first-word start: 0.0s; last-word end: 33.94s. Timestamp-review indices: [].

Broad candidate labels (top five labels per overlapping window; scores not calibrated truth):
- Speech: peak model score 0.8105; appears in 7 top-five windows. This does not establish an audible event at an exact timestamp.
- Music: peak model score 0.7647; appears in 7 top-five windows. This does not establish an audible event at an exact timestamp.
- Explosion: peak model score 0.3045; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.
- Spray: peak model score 0.2371; appears in 4 top-five windows. This does not establish an audible event at an exact timestamp.
- Burst, pop: peak model score 0.1561; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.
- Hiss: peak model score 0.1255; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.

## 05-surfer
Status: `model_analysis_complete`; source audio verified: `True`; method: `exact_encoded_audio_packet_hash`; direct remote encoded-audio comparison: `True`.
Model first-word start: 0.0s; last-word end: 30.84s. Timestamp-review indices: [].

Broad candidate labels (top five labels per overlapping window; scores not calibrated truth):
- Speech: peak model score 0.7773; appears in 7 top-five windows. This does not establish an audible event at an exact timestamp.
- Music: peak model score 0.6765; appears in 7 top-five windows. This does not establish an audible event at an exact timestamp.
- Police car (siren): peak model score 0.6711; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.
- Emergency vehicle: peak model score 0.3593; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.
- Pink noise: peak model score 0.3553; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.
- Siren: peak model score 0.2867; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.

## 06-concert
Status: `model_analysis_complete`; source audio verified: `True`; method: `exact_encoded_audio_packet_hash`; direct remote encoded-audio comparison: `True`.
Model first-word start: 0.0s; last-word end: 26.7s. Timestamp-review indices: [].

Broad candidate labels (top five labels per overlapping window; scores not calibrated truth):
- Speech: peak model score 0.9550; appears in 6 top-five windows. This does not establish an audible event at an exact timestamp.
- Music: peak model score 0.9088; appears in 5 top-five windows. This does not establish an audible event at an exact timestamp.
- Police car (siren): peak model score 0.3673; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.
- Emergency vehicle: peak model score 0.3575; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.
- Siren: peak model score 0.2916; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.
- Ambulance (siren): peak model score 0.2846; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.

## 07-balcony
Status: `model_analysis_complete`; source audio verified: `True`; method: `exact_encoded_audio_packet_hash`; direct remote encoded-audio comparison: `True`.
Model first-word start: 0.0s; last-word end: 31.74s. Timestamp-review indices: [].

Broad candidate labels (top five labels per overlapping window; scores not calibrated truth):
- Speech: peak model score 0.8915; appears in 7 top-five windows. This does not establish an audible event at an exact timestamp.
- Music: peak model score 0.8519; appears in 7 top-five windows. This does not establish an audible event at an exact timestamp.
- Neigh, whinny: peak model score 0.7137; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.
- Horse: peak model score 0.7060; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.
- Animal: peak model score 0.5439; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.
- Single-lens reflex camera: peak model score 0.1836; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.

## 08-ai
Status: `model_analysis_complete`; source audio verified: `True`; method: `authenticated_local_PCM_transfer`; direct remote encoded-audio comparison: `None`.
Model first-word start: 0.0s; last-word end: 51.24s. Timestamp-review indices: [].

Broad candidate labels (top five labels per overlapping window; scores not calibrated truth):
- Speech: peak model score 0.7522; appears in 11 top-five windows. This does not establish an audible event at an exact timestamp.
- Music: peak model score 0.6646; appears in 11 top-five windows. This does not establish an audible event at an exact timestamp.
- Shatter: peak model score 0.2630; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.
- Speech synthesizer: peak model score 0.1943; appears in 4 top-five windows. This does not establish an audible event at an exact timestamp.
- Keys jangling: peak model score 0.1214; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.
- Chink, clink: peak model score 0.0897; appears in 5 top-five windows. This does not establish an audible event at an exact timestamp.

## 09-fight
Status: `model_analysis_complete`; source audio verified: `True`; method: `exact_encoded_audio_packet_hash`; direct remote encoded-audio comparison: `True`.
Model first-word start: 0.0s; last-word end: 27.32s. Timestamp-review indices: [].

Broad candidate labels (top five labels per overlapping window; scores not calibrated truth):
- Speech: peak model score 0.9582; appears in 6 top-five windows. This does not establish an audible event at an exact timestamp.
- Music: peak model score 0.9051; appears in 6 top-five windows. This does not establish an audible event at an exact timestamp.
- Chop: peak model score 0.1217; appears in 3 top-five windows. This does not establish an audible event at an exact timestamp.
- Smash, crash: peak model score 0.0978; appears in 4 top-five windows. This does not establish an audible event at an exact timestamp.
- Artillery fire: peak model score 0.0647; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.
- Gunshot, gunfire: peak model score 0.0535; appears in 1 top-five windows. This does not establish an audible event at an exact timestamp.

## 10-jerboa
Status: `model_analysis_complete`; source audio verified: `True`; method: `exact_encoded_audio_packet_hash`; direct remote encoded-audio comparison: `True`.
Model first-word start: 0.0s; last-word end: 37.76s. Timestamp-review indices: [].

Broad candidate labels (top five labels per overlapping window; scores not calibrated truth):
- Speech: peak model score 0.8549; appears in 8 top-five windows. This does not establish an audible event at an exact timestamp.
- Music: peak model score 0.6968; appears in 8 top-five windows. This does not establish an audible event at an exact timestamp.
- Speech synthesizer: peak model score 0.2449; appears in 4 top-five windows. This does not establish an audible event at an exact timestamp.
- Mouse: peak model score 0.1912; appears in 3 top-five windows. This does not establish an audible event at an exact timestamp.
- Zipper (clothing): peak model score 0.1740; appears in 2 top-five windows. This does not establish an audible event at an exact timestamp.
- Animal: peak model score 0.1714; appears in 6 top-five windows. This does not establish an audible event at an exact timestamp.

## Required verification

- ASR word/window times relative to decoded mono 16kHz WAV, not human-corrected or guaranteed frame-accurate. Container start times recorded for review.
- Multi-label model scores are not calibrated confidence, source stems or exact event timings; coarse overlapping windows, possible false positives/negatives.
- ASR may mistranscribe names, terms, punctuation and boundaries; model score is not calibrated correctness probability
- Event windows overlap. Count is not a count of discrete sound effects; labels are not verified stems or music identities
- No full verbatim source transcripts published; raw model outputs and word ledgers remain private/ignored

Raw narration word timing and event-window outputs remain private for correction against source captions and an actual listening-capable review. Do not claim this model pass completes the requested ten-video forensic study. No production was performed.
