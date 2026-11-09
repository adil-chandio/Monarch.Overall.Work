# Clean V8 — source credits and rights boundary

V8 is a separate, clean content-first rebuild made after the delivered V7 preview was rejected for
excessive overlays. It uses the same seven rights-cleared social-origin Wikimedia Commons originals
that V7 used. No clip from the user's linked YouTube/TikTok reference video is downloaded or reused.

The exact rights status of each selected title is re-verified in CI through the Commons API
(`extmetadata`), including the original SHA-1, licence short name, Credit, Categories, ImageDescription
and the capital `Restrictions` key. The generated ledger is
`review/verified_sources.json`; the per-title policy record is `review/social_origin_ledger.json`.

| Rank | Moment | Wikimedia Commons file page | Licence | Credit (from Commons) |
| --- | --- | --- | --- | --- |
| 7 | PARKING? NOPE | `File:Chicago Parallel Parking FAIL.webm` | CC BY 3.0 | Nathan Holth |
| 6 | SCARECROW JUMP | `File:Quaker Corn Bran scarecrow commercial 2 (1981).webm` | Public domain | Quaker |
| 5 | CAPTION CHAOS | `File:30, Caption fail.ogv` | CC BY 3.0 | DoubleTroubleisaikel |
| 4 | PLAYFUL FIGHT | `File:Funny Fight - JC vs Mark Webb.webm` | CC BY 3.0 | JC Pieri |
| 3 | NOSE WHEELIE | `File:Funny hang-5 - J.Vidarte & JC Pieri.webm` | CC BY 3.0 | JC Pieri |
| 2 | BOOK & DRIVE | `File:Eagan Police Catch Man Reading Novel Behind The Wheel.webm` | Public domain | CCTV / Eagan Police |
| 1 | CAKE HEIST | `File:Bear enters Californian home and allegedly eats chocolate cake (4 September 2022).webm` | Public domain | SVPD / SWNS |

Full URLs, licence URLs, attribution text, restrictions and original SHA-1 values are in
`review/verified_sources.json` and `review/social_origin_ledger.json`.

## Boundary

- These are older rights-cleared Commons mirrors of social-origin clips, **not** currently trending
  TikTok / Instagram / YouTube / Reddit / Dailymotion reposts. No current-trending claim is made.
- Unverified social reposts are not downloaded. CC BY 3.0 attribution is recorded where required.
- Commons metadata is a rights record, not a legal opinion; full legal compliance is not claimed.
- The user's reference Short was identified by metadata only (`onlymeamro` / `thatoneamro`,
  `08-ocSDpt7o`, 60s). Its frames were not playable/extractable in this environment, so V8 is a
  clean rebuild from the rejection, not a frame-by-frame reproduction of that video.
- No human full-motion/native-audio listening, creative approval, sign-off, perfection, retention,
  virality, likes/subscribes or audience result is claimed.
