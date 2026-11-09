# V7 source credits and rights ledger

The workflow selects seven of the ten rights-cleared social-origin candidates below using objective runner audio/motion measurements. The exact selected subset, API extmetadata, original SHA-1, downloaded transcode hash and attribution are written to `review/verified_sources.json`, `review/social_origin_ledger.json` and `review/source_video_ledger.json` during CI.

All sources are **original Wikimedia Commons file pages** whose Commons metadata records a YouTube, Vimeo, SWNS/Instagram or police/social-video origin. No unverified trending TikTok/Instagram/Reddit/Dailymotion/YouTube reposts are downloaded. Commons-generated VP9/Opus transcodes may be used for large originals; the original Commons API SHA-1 remains the rights record.

## Candidate credits

1. **How To Drop In At Your Local Pro Shop** — Warrior Custom Golf — Public domain — [Commons file](https://commons.wikimedia.org/wiki/File:How_To_Drop_In_At_Your_Local_Pro_Shop-vKdfnsXiO94.webm) — YouTube / 2014 viral-video and internet-meme categories. Commons restrictions: personality, trademarked. Attribution not required.
2. **Chicago Parallel Parking FAIL** — Nathan Holth — [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) — [Commons file](https://commons.wikimedia.org/wiki/File:Chicago_Parallel_Parking_FAIL.webm) — YouTube. **Attribution required.**
3. **Floridian cop caught on camera running from a rat** — St. Petersburg P.D. — Public domain (PD Florida) — [Commons file](https://commons.wikimedia.org/wiki/File:Floridian_cop_caught_on_camera_running_from_a_rat.webm) — YouTube. Attribution not required.
4. **Funny hang-5 - J.Vidarte & JC Pieri** — JC Pieri — [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) — [Commons file](https://commons.wikimedia.org/wiki/File:Funny_hang-5_-_J.Vidarte_%26_JC_Pieri.webm) — Vimeo. **Attribution required.**
5. **Funny Fight - JC vs Mark Webb** — JC Pieri — [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) — [Commons file](https://commons.wikimedia.org/wiki/File:Funny_Fight_-_JC_vs_Mark_Webb.webm) — Vimeo. **Attribution required.**
6. **Bear enters Californian home and allegedly eats chocolate cake (4 September 2022)** — SVPD / SWNS — Public domain (PD California) — [Commons file](https://commons.wikimedia.org/wiki/File:Bear_enters_Californian_home_and_allegedly_eats_chocolate_cake_(4_September_2022).webm) — YouTube / SWNS / Instagram. Attribution not required.
7. **Eagan Police Catch Man Reading Novel Behind The Wheel** — CCTV / Eagan Police — Public domain — [Commons file](https://commons.wikimedia.org/wiki/File:Eagan_Police_Catch_Man_Reading_Novel_Behind_The_Wheel.webm) — YouTube / PoliceActivity. Attribution not required. The source description notes the behaviour is dangerous; V7 does not endorse it.
8. **30, Caption fail** — DoubleTroubleisaikel — [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) — [Commons file](https://commons.wikimedia.org/wiki/File:30,_Caption_fail.ogv) — YouTube. **Attribution required.**
9. **Amazon delivery driver THROWS parcel as shocked dad watches live on CCTV - SWNS TV** — SWNS — Public domain — [Commons file](https://commons.wikimedia.org/wiki/File:Amazon_delivery_driver_THROWS_parcel_as_shocked_dad_watches_live_on_CCTV_-_SWNS_TV.webm) — YouTube / SWNS / Instagram. Attribution not required.
10. **Quaker Corn Bran scarecrow commercial 2 (1981)** — Quaker — Public domain (US no notice) — [Commons file](https://commons.wikimedia.org/wiki/File:Quaker_Corn_Bran_scarecrow_commercial_2_(1981).webm) — YouTube. Attribution not required.

## Excluded candidates

Two CC BY 3.0 YouTube comedy candidates (`Street Quiz -- Who is Barack Obama...` and `AFRICAN COMEDY - WHEN SNEAK INTO YOUR FATHER'S HOUSE...`) were removed from the pool because their Commons descriptions contain third-party copyright language. They are not downloaded or used.

## Reuse conditions

- Public-domain and CC0 sources: no attribution requirement; credit is recorded voluntarily.
- CC BY 3.0 sources: title, creator, licence, licence URL and source link are recorded here and in the upload metadata; the description must retain this credit.
- No CC BY-SA, CC BY-NC, fair-use-only, Section 107 substitute, `license review needed (video)`, or unverified social-platform repost is used.
- No currently trending claim, audience result, virality guarantee, human full-motion listening, sign-off or creative approval is claimed.
