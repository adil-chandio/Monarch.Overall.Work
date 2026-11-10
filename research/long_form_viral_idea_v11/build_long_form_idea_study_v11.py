#!/usr/bin/env python3
"""Build the V11 long-form viral-idea forensic study (IDEA SELECTION ONLY).

Run from repo root:
    python research/long_form_viral_idea_v11/build_long_form_idea_study_v11.py

Deliverable = ONE chosen long-form video idea + the deep forensic evidence for
choosing it. NO video is rendered, NO upload/publish is performed, NO YouTube
Data API call is made (no API key configured in this workspace).

Outputs (all under research/long_form_viral_idea_v11/):
  LONG_FORM_VIRAL_IDEA_FORENSIC_STUDY_V11.md   main human deliverable
  long_form_viral_idea_v11.json                machine-readable pack
  candidate_scoring_v11.json                   8 candidates, weighted scores
  sources_v11.json                             numbered source ledger
  api_capability_audit_v11.json                what the API could do, quota, no-call proof
Also adds an idempotent addendum pointer to
  docs/continuity/channels/monarch-cam/NEXT_ACTION.md

Re-run safe: byte-identical on a clean HEAD checkout.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research" / "long_form_viral_idea_v11"
NEXT_ACTION = ROOT / "docs" / "continuity" / "channels" / "monarch-cam" / "NEXT_ACTION.md"

STUDY_MD = OUT / "LONG_FORM_VIRAL_IDEA_FORENSIC_STUDY_V11.md"
PACK_JSON = OUT / "long_form_viral_idea_v11.json"
SCORING_JSON = OUT / "candidate_scoring_v11.json"
SOURCES_JSON = OUT / "sources_v11.json"
API_JSON = OUT / "api_capability_audit_v11.json"

EDITION = "v11_long_form_viral_idea_selection_2026-11-05"
HEAD_EXPECTED = "e0f8e1cfb959fc38da5a1b60634d2cd29d0ef6d4"
V10_SHA = "608aa065cd3c53894b96df1ebb6fa74dd3ce1e846366e40a940426b4823586a7"
NASA_ID = "art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman"
NASA_PAGE = f"https://images.nasa.gov/details/{NASA_ID}"


# ---------------------------------------------------------------------------
# 1. Source ledger. Numbers are THIS STUDY's citation IDs. The research log
#    records the original web_search result id alongside each URL so every
#    search-derived claim stays traceable to its [id](url).
# ---------------------------------------------------------------------------
SOURCES = [
    {"n": 1, "id": "YT_CEO_2026", "title": "From the CEO: What's coming to YouTube in 2026 (Neal Mohan)",
     "url": "https://blog.youtube/inside-youtube/the-future-of-youtube-2026/", "authority": "official_youtube_blog",
     "kind": "fetched_and_searched", "search_result_id": 1,
     "used_for": "Every format on every screen; long-form, Shorts, music, livestreams, podcasts; Shorts averages 200B daily views; YouTube #1 in US streaming watchtime nearly 3 years (Nielsen); 93% of US 18-27 year olds and 79% of US teachers say YouTube helps learning (2025 Kantar / Oxford Economics); creators as new studios; $100B paid to creators in 4 years.",
     "reliability": "official_first_party"},
    {"n": 2, "id": "YT_TV_2026", "title": "Connect with creators on the biggest screen (Made On YouTube 2026)",
     "url": "https://blog.youtube/news-and-events/made-on-youtube-creators-shorts-series-tv-features/",
     "authority": "official_youtube_blog", "kind": "fetched_and_searched", "search_result_id": 2,
     "used_for": "Over half of YouTube's top 100 creators have TV as their most watched interface; Shorts series / seasons / episodes; microdramas surpassed 6.5B views in H1 2026 with watch time +50% YoY and TV views +90% YoY; 300M users engage with posts daily.",
     "reliability": "official_first_party"},
    {"n": 3, "id": "YT_RETENTION", "title": "Measure key moments for audience retention - YouTube Help",
     "url": "https://support.google.com/youtube/answer/9314415?hl=en", "authority": "official_youtube_help",
     "kind": "fetched_and_searched", "search_result_id": 2,
     "used_for": "Intro = % still watching after first 30s; spikes = moments rewatched or shared; dips = skipped/abandoned; flat = watched start to finish; typical retention compares 10 latest videos of similar length; retention data takes 1-2 days; key moments need video >=60s and >=100 views.",
     "reliability": "official_first_party"},
    {"n": 4, "id": "YT_ENGAGEMENT", "title": "Understand your YouTube engagement - YouTube Help",
     "url": "https://support.google.com/youtube/answer/9313698?hl=en", "authority": "official_youtube_help",
     "kind": "searched", "search_result_id": 1,
     "used_for": "Engagement tab snapshot: watch time (hours), average view duration, views; audience retention report.",
     "reliability": "official_first_party"},
    {"n": 5, "id": "YT_PERFORMANCE", "title": "Understand your YouTube content performance - YouTube Help",
     "url": "https://support.google.com/youtube/answer/12220281?hl=en", "authority": "official_youtube_help",
     "kind": "searched", "search_result_id": 3,
     "used_for": "Impressions, impressions CTR, views, average view duration, average percentage viewed, engaged views, unique viewers, regular viewers.",
     "reliability": "official_first_party"},
    {"n": 6, "id": "YT_API_VIDEOS", "title": "Videos: list - YouTube Data API v3",
     "url": "https://developers.google.com/youtube/v3/docs/videos/list", "authority": "official_developer_docs",
     "kind": "fetched_and_searched", "search_result_id": 2,
     "used_for": "chart=mostPopular returns most popular videos for a content region and video category; part=snippet,statistics returns categoryId, title, viewCount, likeCount; quota cost 1 unit; up to 50 IDs per call.",
     "reliability": "official_first_party"},
    {"n": 7, "id": "YT_API_SEARCH", "title": "Search: list - YouTube Data API v3",
     "url": "https://developers.google.com/youtube/v3/docs/search/list", "authority": "official_developer_docs",
     "kind": "fetched", "search_result_id": None,
     "used_for": "Keyword search; 100 calls per day in the Search Queries quota bucket (1 unit in that bucket); default 25 results; type=video, order, publishedAfter, videoDuration filters exist.",
     "reliability": "official_first_party"},
    {"n": 8, "id": "YT_API_CATEGORIES", "title": "VideoCategories: list - YouTube Data API v3",
     "url": "https://developers.google.com/youtube/v3/docs/videoCategories/list", "authority": "official_developer_docs",
     "kind": "fetched", "search_result_id": None,
     "used_for": "Returns categories associable with videos; regionCode makes the list region-specific; quota cost 1 unit.",
     "reliability": "official_first_party"},
    {"n": 9, "id": "YT_WATCH_HOURS", "title": "Qualified watch hours and Shorts views (YPP) - YouTube Blog",
     "url": "https://blog.youtube/news-and-events/youtube-monetization-qualified-watch-hours-shorts-views/",
     "authority": "official_youtube_blog", "kind": "searched", "search_result_id": 4,
     "used_for": "Qualified watch hours come from public long-form videos including podcasts and archived livestreams; Shorts watch hours do NOT count as qualified long-form watch hours.",
     "reliability": "official_first_party"},
    {"n": 10, "id": "WIKI_MOST_VIEWED", "title": "List of most-viewed YouTube videos - Wikipedia",
     "url": "https://en.wikipedia.org/wiki/List_of_most-viewed_YouTube_videos", "authority": "community_maintained",
     "kind": "fetched_and_searched", "search_result_id": 1,
     "used_for": "Top 30 most-viewed are children's songs, music videos and one advertisement; Baby Shark Dance 17.28B; since Bad Romance (2010) every #1 most-viewed video has been a music video; page self-describes as a dynamic list that may never satisfy completeness.",
     "reliability": "public_snapshot_not_authoritative"},
    {"n": 11, "id": "NASA_IMAGES", "title": "NASA Brand Center - Images and Media",
     "url": "https://www.nasa.gov/nasa-brand-center/images-and-media/", "authority": "official_nasa_guidance",
     "kind": "workspace_and_fetched", "search_result_id": None,
     "used_for": "Acknowledge NASA as source; no implied endorsement; insignia / identifiable-person restrictions.",
     "reliability": "official_first_party"},
    {"n": 12, "id": "NASA_STRATEGIC", "title": "NASA Strategic Partnerships - Promotional Content",
     "url": "https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/", "authority": "official_nasa_guidance",
     "kind": "fetched", "search_result_id": None,
     "used_for": "Exact wording: 'Short-form social media content generally is considered promotional content' and 'Imagery with ... current astronauts ... may not be used in promotional content'; NASA cannot endorse or appear to endorse; no co-branding/sponsorship.",
     "reliability": "official_first_party"},
    {"n": 13, "id": "NASA_ASSET", "title": "NASA image detail - Fun with Water Bubbles (Artemis II)",
     "url": NASA_PAGE, "authority": "official_nasa_asset", "kind": "workspace", "search_result_id": None,
     "used_for": "Locked source ID, title 'Fun with Water Bubbles', 2026-04-04; the one clip already sourced and QC'd in V10.",
     "reliability": "official_first_party"},
    {"n": 14, "id": "ORBITAL_TODAY", "title": "A Tiny Water Droplet Became the Star of Artemis II",
     "url": "https://orbitaltoday.com/2026/05/12/a-tiny-water-droplet-became-the-star-of-artemis-ii-video/",
     "authority": "third_party_reporting", "kind": "searched", "search_result_id": 1,
     "used_for": "Public-interest framing: 'star of Artemis II', Hansen leaning in, face upside down and warped, straw catch, light bending like a glass lens.",
     "reliability": "reporting_not_analytics"},
    {"n": 15, "id": "YAHOO_BUBBLES", "title": "Watch the Artemis II astronauts have fun with bubbles",
     "url": "https://www.yahoo.com/news/articles/watch-artemis-ii-astronauts-fun-193852742.html",
     "authority": "third_party_reporting", "kind": "searched", "search_result_id": 4,
     "used_for": "Surface tension forms the sphere; light bends and inverts images; retired astronaut Karen Nyberg's 'what you see depends on how we look' lesson; playful tone.",
     "reliability": "reporting_not_analytics"},
    {"n": 16, "id": "DAILYMAIL_BUBBLES", "title": "'Like a crystal clear ball!' NASA water-in-space video",
     "url": "https://www.dailymail.com/sciencetech/article-15807427/Incredible-video-shows-water-floating-space.html",
     "authority": "third_party_reporting", "kind": "searched", "search_result_id": 3,
     "used_for": "Jeremy Hansen upside-down through the orb; straw catch and release; 'uniquely human' audience reaction; NASA statement that crew had fun with water in weightlessness.",
     "reliability": "reporting_not_analytics"},
    {"n": 17, "id": "GAZETA_BUBBLES", "title": "Artemis II water drop footage amazes the network",
     "url": "https://www.gazetaexpress.com/en/Artemis-II-astronauts-experiment-with-a-drop-of-water-in-space--NASA-footage-amazes-the-web/",
     "authority": "third_party_reporting", "kind": "searched", "search_result_id": 1,
     "used_for": "Social reactions and a viewer safety question about water near electronics - useful raw material for a myth-vs-fact chapter, NOT a verdict.",
     "reliability": "reporting_not_analytics"},
    {"n": 18, "id": "AFP_FACTCHECK", "title": "Artemis II broadcast error used to stoke false 'staged' claims - AFP Fact Check",
     "url": "https://factcheck.afp.com/doc.afp.com.A6WV668", "authority": "third_party_factcheck", "kind": "searched",
     "search_result_id": 3,
     "used_for": "A broadcast text-overlay glitch was misused to claim the mission was staged; the glitch clip drew over 1.5M views. Guardrail for the 'why your brain says CGI' chapter: do not amplify or invent conspiracy claims.",
     "reliability": "factcheck_reporting"},
    {"n": 19, "id": "NAUTILUS_ARTEMIS", "title": "Astronauts as Influencers - Nautilus",
     "url": "https://nautil.us/astronauts-as-influencers-1279855", "authority": "third_party_reporting", "kind": "searched",
     "search_result_id": 5,
     "used_for": "Artemis II cross-platform exposure: 27.3M TV news viewers for return, 18.1M for launch, 650k splashdown stream, 22M archived video. These are broadcast/stream figures, NOT YouTube views of our clip and NOT a forecast.",
     "reliability": "reporting_not_analytics"},
    {"n": 20, "id": "TVREV_TUBULAR", "title": "Tube Trends: longer videos to compete with TV (Tubular Labs data)",
     "url": "https://www.tvrev.com/news/tube-trends-how-youtube-creators-are-using-longer-videos-to-compete-with-tv",
     "authority": "third_party_industry_reporting", "kind": "searched", "search_result_id": 5,
     "used_for": "Q1 2026 US creators uploaded 6.6M videos of 20+ minutes, 80.3% at least 30 min; MrBeast 628M long-form views in Q1; 44 creators above 100M views on longer content.",
     "reliability": "directional_unverified_by_us"},
    {"n": 21, "id": "VIDIQ_TRENDS", "title": "9 YouTube Trends Creators Need to Watch in 2026 - vidIQ",
     "url": "https://vidiq.com/blog/post/future-youtube-trends/", "authority": "third_party_creator_tool",
     "kind": "searched", "search_result_id": 2,
     "used_for": "Long-form viewing on TVs, video podcasts, multi-format channels, stronger title/thumbnail testing, community revenue.",
     "reliability": "directional_unverified_by_us"},
    {"n": 22, "id": "FALCONVID_SCIENCE", "title": "Faceless science channels and reusable hooks - FalconVid",
     "url": "https://falconvid.ai/blog/science-youtube-channels-that-make-money",
     "authority": "third_party_aggregator", "kind": "searched", "search_result_id": 2,
     "used_for": "Directional examples of curiosity-gap long-form science titles with reported million-view videos (Nebula Prophecy, GoDocs, OctoLab). Numbers NOT verified by us.",
     "reliability": "unverified_aggregator"},
    {"n": 23, "id": "TUBESTATS_SCIENCE", "title": "Best Science YouTube Channels 2026 - TubeStats",
     "url": "https://tubestats.io/channels/science", "authority": "third_party_aggregator", "kind": "searched",
     "search_result_id": 3,
     "used_for": "Directional channel-scale context (Kurzgesagt, Vsauce, Veritasium, NASA). Subscriber/view numbers NOT verified by us.",
     "reliability": "unverified_aggregator"},
    {"n": 24, "id": "FLUXNOTE_HOOKS", "title": "Short-Form Hook Library: 500 viral videos (2026 manual analysis)",
     "url": "https://fluxnote.io/blog/short-form-hook-library-500-viral-videos", "authority": "third_party_analysis",
     "kind": "searched", "search_result_id": 4,
     "used_for": "Pattern frequencies in a self-described manual sample: direct claim with specific number 14%, POV 11%, contradictory pattern interrupt 10%, curiosity gap 9%, listicle preamble 7%. NOT an official YouTube statistic.",
     "reliability": "unverified_sample"},
    {"n": 25, "id": "OUTLIERKIT_API", "title": "How to Get a YouTube API Key in 2026 - OutlierKit",
     "url": "https://outlierkit.com/resources/how-to-get-youtube-api-key/", "authority": "third_party_guide",
     "kind": "searched", "search_result_id": 5,
     "used_for": "API key is free within a 10,000-unit/day default quota; what the Data API cannot do: breakout/outlier detection vs channel baseline, arbitrary-video transcripts, keyword search volume, semantic look-alike channels, derived audience intelligence.",
     "reliability": "third_party_guide_cross_checked_with_official_docs"},
    {"n": 26, "id": "WORKSPACE_V10", "title": "V10 workspace evidence (locked NASA Short + ledgers)",
     "url": "workspace://production/monarch-cam/caught_on_camera_commentary_v10", "authority": "workspace_evidence",
     "kind": "workspace", "search_result_id": None,
     "used_for": "Single locked 1080x1920 master (SHA 11395618...), 49.4s V10 deliverable SHA " + V10_SHA + ", 8 beats / 118 words, 9/9 audio gates, 33/33 technical checks, rights_ledger, edit_ledger, native_audio_ledger, qc_summary, category/pinned-comment pack.",
     "reliability": "verified_workspace"},
    {"n": 27, "id": "CHANNEL_CONFIG", "title": "config/channels.json",
     "url": "workspace://config/channels.json", "authority": "workspace_evidence", "kind": "workspace",
     "search_result_id": None,
     "used_for": "Legacy slots: Monarch Lab long-form 8-12 min with 'one concept, one demo' and banned 'stock b-roll as hero' / 'reaction-only' / 'clickbait with no payoff'; Curious Miles long-form 6-10 min with 'how it actually works' / 'myth vs measured'. Monarch Cam is a separate active workstream per the continuity note.",
     "reliability": "verified_workspace"},
    {"n": 28, "id": "PRIOR_STUDY_V10", "title": "Caught-on-camera single-clip commentary - V10 forensic study",
     "url": "workspace://research/caught_on_camera_commentary_v10/CAUGHT_ON_CAMERA_FORENSIC_STUDY.md",
     "authority": "workspace_evidence", "kind": "workspace", "search_result_id": None,
     "used_for": "Prior evidence ladder, 10-axis one-clip rubric (min 78), 12 kill switches, honest evidence boundary, channel ecosystem tiers and long-form anatomy template.",
     "reliability": "verified_workspace"},
    {"n": 29, "id": "YT_API_CHANNELS", "title": "Channels: list - YouTube Data API v3",
     "url": "https://developers.google.com/youtube/v3/docs/channels/list", "authority": "official_developer_docs",
     "kind": "referenced_official_docs", "search_result_id": None,
     "used_for": "Endpoint identity for public channel statistics (subscriberCount, viewCount, videoCount, snippet). Referenced for the ready-to-run query; NOT fetched this session and NOT called.",
     "reliability": "official_first_party_reference_only"},
]


def cite(n: int) -> str:
    s = next(x for x in SOURCES if x["n"] == n)
    return f"[{s['n']}]({s['url']})"


# ---------------------------------------------------------------------------
# 2. API capability audit - honest: no key, no call
# ---------------------------------------------------------------------------
API_AUDIT = {
    "edition": EDITION,
    "question_from_user": "research karo api se best viral growing channels / millions-view videos dekho",
    "workspace_check_performed": True,
    "workspace_check_results": {
        "env_youtube_or_google_api_key_var_present": False,
        "config_youtube_json_present": False,
        "config_api_keys_json_present": False,
        "env_file_present": False,
        "config_channels_json_present": True,
        "outbound_bash_allowlist": ["github.com", "codeload.github.com", "api.github.com",
                                    "registry.npmjs.org", "pypi.org", "files.pythonhosted.org"],
        "note": "Web tools (web_search / fetch_page) reached official docs and public pages, but the Data API endpoint requires an API key and was NOT called. No key value was requested, printed or stored in chat.",
    },
    "youtube_data_api_calls_made": 0,
    "official_capability": [
        {"method": "videos.list", "purpose": "mostPopular videos by region + category, or metadata/statistics for known IDs",
         "example_request": "GET https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&chart=mostPopular&regionCode=PK&videoCategoryId=28&maxResults=50&key=REDACTED",
         "quota": "1 unit per call", "doc": cite(6),
         "would_return": "title, channelId, categoryId, publishedAt, viewCount, likeCount, commentCount, duration"},
        {"method": "search.list", "purpose": "keyword discovery of long-form videos ordered by views / date",
         "example_request": "GET https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&order=viewCount&videoDuration=long&publishedAfter=2026-01-01T00:00:00Z&maxResults=50&key=REDACTED",
         "quota": "100 calls per day in the Search Queries bucket (1 unit in that bucket)", "doc": cite(7),
         "would_return": "videoId + snippet only; statistics require a follow-up videos.list"},
        {"method": "channels.list", "purpose": "public subscriber / total view / video counts for candidate channels",
         "example_request": "GET https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id=REDACTED&key=REDACTED",
         "quota": "1 unit per call", "doc": cite(29),
         "would_return": "subscriberCount, viewCount, videoCount, channel title"},
        {"method": "videoCategories.list", "purpose": "region-specific category IDs (e.g. 27 Education, 28 Science & Technology)",
         "example_request": "GET https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode=PK&key=REDACTED",
         "quota": "1 unit per call", "doc": cite(8), "would_return": "assignable category IDs and labels"},
    ],
    "api_limits_even_with_a_key": [
        "No breakout / outlier detection vs a channel baseline; must be built manually " + cite(25),
        "No transcripts for arbitrary videos; captions.download requires OAuth + ownership " + cite(25),
        "No keyword search-volume or competition data; the API returns videos, not demand " + cite(25),
        "No semantic look-alike channel search; search.list matches keywords only " + cite(25),
        "Impressions, CTR, watch time, average view duration, retention and revenue are OWNER-ONLY Studio / Analytics API data, not public Data API fields " + cite(4) + " " + cite(5) + " " + cite(25),
        "Public view counts are a snapshot, not a forecast and not a guarantee of a future video's reach " + cite(10),
    ],
    "what_was_actually_used_instead": [
        "Official YouTube Blog / Help / Developer documentation (source ledger 1-9)",
        "Public web reporting about the Artemis II clip and audience reaction (14-19)",
        "Community-maintained most-viewed list as a reality check on genre expectations (10)",
        "Clearly-labelled third-party directional signals (20-24), never as authoritative",
        "Committed workspace evidence: the single locked NASA source and V10 ledgers (26-28)",
    ],
    "no_fabrication_statement": "No live channel analytics, no verified competitor view counts, no trend/keyword volume, no retention graph, no RPM/CTR data and no 'best viral growing channels' ranking was invented. Where a number appears, its source and reliability tier are recorded.",
}


# ---------------------------------------------------------------------------
# 3. Research log
# ---------------------------------------------------------------------------
RESEARCH_LOG = [
    {"q": "YouTube 2026 long-form video trends creators watch time official YouTube blog", "depth": 2,
     "results": 5, "kept": [20, 21],
     "takeaway": "Third-party 2026 trend write-ups claim long-form/TV resurgence and multi-format advantage; all numeric growth multipliers in those posts are unverified and were NOT used as evidence."},
    {"q": "Wikipedia list of most-viewed YouTube videos 2026 billions views", "depth": 2,
     "results": 5, "kept": [10],
     "takeaway": "Fetched Wikipedia directly: top 30 = children's songs, music videos, one ad. Reality check: a science forensic long-form video is NOT in the billion-view genre, so 'millions of views' cannot be promised."},
    {"q": "fastest growing YouTube channels 2026 science space documentary millions views", "depth": 2,
     "results": 5, "kept": [22, 23],
     "takeaway": "Aggregator sites list large science channels and million-view science videos; subscriber/view figures are directional only, not verified by us and not used as targets."},
    {"q": "YouTube viral video replay breakdown format hook retention rewatch wait what science explainer", "depth": 2,
     "results": 5, "kept": [24],
     "takeaway": "Self-described manual analysis of 500 videos over 1M views reports curiosity-gap / pattern-interrupt / listicle hook patterns. Unofficial sample; used only as pattern vocabulary."},
    {"q": "YouTube Data API videos.list search.list requires API key quota official documentation", "depth": 2,
     "results": 5, "kept": [6, 25],
     "takeaway": "Confirmed official quota model and the API's hard limits; also fetched videos.list and search.list docs directly."},
    {"q": "NASA Artemis II Fun with Water Bubbles upside down face viral 2026", "depth": 2,
     "results": 5, "kept": [14, 15, 16],
     "takeaway": "Multiple independent reports describe the same playful water sphere, refraction-inverted face, straw catch and 'uniquely human' public reaction. That is public interest evidence, NOT a YouTube view count."},
    {"q": "site:blog.youtube 2026 long-form TV viewing creators official YouTube", "depth": 2,
     "results": 5, "kept": [1, 2, 9],
     "takeaway": "Official first-party 2026 direction: every format on every screen, TV as top interface for over half of top-100 creators, episodic/series structures, qualified long-form watch hours."},
    {"q": "YouTube official help watch time average view duration audience retention analytics", "depth": 2,
     "results": 5, "kept": [3, 4, 5],
     "takeaway": "Official metric definitions. Critical: 'spikes' are moments viewers rewatched or shared - a replay-first idea is aligned with a documented retention signal, not a guessed algorithm hack."},
    {"q": "NASA Artemis II water bubble video millions views social media viral May 2026", "depth": 2,
     "results": 5, "kept": [17, 18, 19],
     "takeaway": "Public reaction, a viewer safety question and a fact-check about a broadcast glitch being misused for 'staged' claims. Supplies myth-vs-fact material and a misinformation guardrail."},
    {"q": "long-form science documentary YouTube millions views 2026 space physics explainer", "depth": 2,
     "results": 5, "kept": [22],
     "takeaway": "Directional curiosity-gap documentary titles with reported million-view examples; unverified, used only to name the format family."},
]


# ---------------------------------------------------------------------------
# 4. Rubric + candidates
# ---------------------------------------------------------------------------
AXES = [
    {"id": "hook_stop_power", "label": "Hook / first-30s stop power", "weight": 1.2,
     "why": "Official 'Intro' metric = % still watching after 30s " + cite(3)},
    {"id": "replay_rewatch_signal", "label": "Replay / rewatch signal", "weight": 1.2,
     "why": "Official 'Spikes' = moments rewatched or shared " + cite(3)},
    {"id": "source_chain_certainty", "label": "Source chain certainty", "weight": 1.3,
     "why": "Prior V10 rubric's rights-chain axis, escalated for long-form " + cite(28)},
    {"id": "fun_emotional_spike", "label": "Fun / emotional spike", "weight": 1.0,
     "why": "User's 'mazedar / next level' requirement; config bans reaction-only and clickbait-with-no-payoff " + cite(27)},
    {"id": "depth_runway_10min", "label": "Depth runway for 8-12 min", "weight": 1.2,
     "why": "User's 'microscope / 10x think / detailed forensic' requirement; config long-form target 8-12 min " + cite(27)},
    {"id": "long_form_tv_multiformat_fit", "label": "Long-form / TV / multi-format fit", "weight": 0.9,
     "why": "Official 2026 direction " + cite(1) + " " + cite(2) + " " + cite(9)},
    {"id": "production_feasibility_existing_assets", "label": "Feasibility with existing assets", "weight": 0.9,
     "why": "One locked NASA master + V10 WAVs, PNGs and ledgers already in the repo " + cite(26)},
    {"id": "series_scalability", "label": "Series / repeatability", "weight": 0.7,
     "why": "Official Shorts series / episodic push " + cite(2) + "; config 'one concept, one demo' " + cite(27)},
    {"id": "rights_legal_risk_inverse", "label": "Rights / legal risk (10 = low risk)", "weight": 0.8,
     "why": "NASA promotional-content and current-astronaut imagery gate " + cite(12)},
    {"id": "claim_integrity", "label": "Claim integrity", "weight": 0.8,
     "why": "No guaranteed virality, no legal clearance, no human approval, no perfection " + cite(12) + " " + cite(10)},
]
WEIGHT_SUM = round(sum(a["weight"] for a in AXES), 1)  # 10.0
MIN_TOTAL = 75.0

KILL_SWITCHES = [
    "multiple_unverified_or_unlicensed_clips",
    "guaranteed_virality_or_millions_of_views_claim",
    "nasa_endorsement_or_official_status_claim",
    "current_astronaut_imagery_in_promotional_content_without_written_clearance",
    "unrelated_or_misleading_tags_or_metadata",
    "ai_free_imagery_or_no_cgi_claim_without_verification",
    "human_approval_or_legal_clearance_or_perfection_claim",
    "clickbait_hook_with_no_payoff",
    "fabricated_analytics_or_view_counts",
    "audio_substitution_of_nasa_native_audio",
    "exact_reference_match_claim",
    "staged_or_conspiracy_amplification",
]

CANDIDATES = [
    {
        "id": "RL-01", "name": "REPLAY LAB Ep.1 - The Upside-Down Face",
        "one_liner": "42.7 seconds of NASA footage, explained frame by frame in a 10-12 minute forensic replay documentary built on the ONE locked Artemis II water-bubble master.",
        "scores": {"hook_stop_power": 10, "replay_rewatch_signal": 10, "source_chain_certainty": 10,
                   "fun_emotional_spike": 9, "depth_runway_10min": 10, "long_form_tv_multiformat_fit": 10,
                   "production_feasibility_existing_assets": 9, "series_scalability": 10,
                   "rights_legal_risk_inverse": 4, "claim_integrity": 10},
        "evidence": ["V10 already has 8 beats / 118 words / loop-back at 44.24s " + cite(26),
                     "Official spikes = rewatched or shared moments " + cite(3),
                     "Official every-format / TV / long-form watch-hours direction " + cite(1) + " " + cite(2) + " " + cite(9),
                     "Single official NASA asset with recorded ID and SHA " + cite(13) + " " + cite(26),
                     "Public reporting supplies the 'uniquely human' playfulness and the safety question " + cite(16) + " " + cite(17)],
        "kill_switches_hit": [],
        "open_gates": ["NASA promotional / current-astronaut imagery clearance gate remains OPEN " + cite(12),
                       "human legal review and human creative approval remain false"],
        "verdict": "WINNER",
    },
    {
        "id": "RL-02", "name": "7 Real Space Moments That Look Fake (ranked compilation)",
        "one_liner": "A ranked long-form compilation of multiple NASA/space clips, each with replay and explanation.",
        "scores": {"hook_stop_power": 9, "replay_rewatch_signal": 9, "source_chain_certainty": 3,
                   "fun_emotional_spike": 9, "depth_runway_10min": 7, "long_form_tv_multiformat_fit": 8,
                   "production_feasibility_existing_assets": 3, "series_scalability": 8,
                   "rights_legal_risk_inverse": 2, "claim_integrity": 4},
        "evidence": ["Only ONE clip is actually sourced and QC'd in this workspace " + cite(26),
                     "NASA promotional gate multiplies with each additional current-astronaut clip " + cite(12)],
        "kill_switches_hit": ["multiple_unverified_or_unlicensed_clips",
                              "current_astronaut_imagery_in_promotional_content_without_written_clearance",
                              "fabricated_analytics_or_view_counts"],
        "open_gates": ["would require a full new rights-clearance pass for 6 more clips"],
        "verdict": "reject",
    },
    {
        "id": "AF-01", "name": "How We Fixed a 'Buffering Glitch' - audio forensics behind the scenes",
        "one_liner": "A 10-minute technical documentary on the V10 VO glitch diagnosis, waveform/spectrum evidence and continuous slope conditioner.",
        "scores": {"hook_stop_power": 6, "replay_rewatch_signal": 5, "source_chain_certainty": 10,
                   "fun_emotional_spike": 6, "depth_runway_10min": 9, "long_form_tv_multiformat_fit": 7,
                   "production_feasibility_existing_assets": 8, "series_scalability": 5,
                   "rights_legal_risk_inverse": 8, "claim_integrity": 9},
        "evidence": ["All audio WAVs, PNGs and QC JSONs already exist " + cite(26),
                     "Strong 'build in public' fit for the legacy Monarch Lab slot " + cite(27)],
        "kill_switches_hit": [],
        "open_gates": ["narrow creator/tools audience; weaker 'mazedar' general appeal",
                       "still lacks human listening sign-off " + cite(26)],
        "verdict": "runner_up_narrow",
    },
    {
        "id": "EX-01", "name": "Why Water Becomes a Crystal Ball in Space (straight explainer)",
        "one_liner": "A conventional 8-minute science explainer on surface tension and refraction in microgravity.",
        "scores": {"hook_stop_power": 6, "replay_rewatch_signal": 5, "source_chain_certainty": 9,
                   "fun_emotional_spike": 6, "depth_runway_10min": 7, "long_form_tv_multiformat_fit": 8,
                   "production_feasibility_existing_assets": 8, "series_scalability": 6,
                   "rights_legal_risk_inverse": 5, "claim_integrity": 9},
        "evidence": ["Science-explainer format family is well populated " + cite(22) + " " + cite(23)],
        "kill_switches_hit": [],
        "open_gates": ["generic; weak differentiation; 'voice-over stock documentary' is explicitly banned in the legacy config " + cite(27)],
        "verdict": "reject_generic",
    },
    {
        "id": "CG-01", "name": "'Is It CGI?' Court - 10 internet claims judged frame by frame",
        "one_liner": "Myth-busting courtroom format judging viral clips as real or fake.",
        "scores": {"hook_stop_power": 9, "replay_rewatch_signal": 8, "source_chain_certainty": 2,
                   "fun_emotional_spike": 8, "depth_runway_10min": 7, "long_form_tv_multiformat_fit": 7,
                   "production_feasibility_existing_assets": 2, "series_scalability": 8,
                   "rights_legal_risk_inverse": 1, "claim_integrity": 2},
        "evidence": ["AFP documents how an Artemis II broadcast glitch was already misused for false 'staged' claims " + cite(18)],
        "kill_switches_hit": ["multiple_unverified_or_unlicensed_clips", "staged_or_conspiracy_amplification",
                              "ai_free_imagery_or_no_cgi_claim_without_verification", "fabricated_analytics_or_view_counts"],
        "open_gates": ["defamation / misinformation risk; rights nightmare"],
        "verdict": "reject_high_risk",
    },
    {
        "id": "AN-01", "name": "One Clip, 8 Beats - anatomy of a 49-second Short",
        "one_liner": "Meta breakdown of V10's own edit ledger: hook, 118 words, captions, payoff flash, loop-back.",
        "scores": {"hook_stop_power": 7, "replay_rewatch_signal": 8, "source_chain_certainty": 10,
                   "fun_emotional_spike": 6, "depth_runway_10min": 9, "long_form_tv_multiformat_fit": 8,
                   "production_feasibility_existing_assets": 9, "series_scalability": 7,
                   "rights_legal_risk_inverse": 8, "claim_integrity": 10},
        "evidence": ["Complete edit ledger, caption timings and QC already committed " + cite(26)],
        "kill_switches_hit": [],
        "open_gates": ["meta/creator-facing; less visceral than the actual footage",
                       "best used as a CHAPTER inside RL-01 rather than a standalone flagship"],
        "verdict": "strong_second_folded_into_winner",
    },
    {
        "id": "MS-01", "name": "Artemis II: the 10-day mission that got weirdly funny",
        "one_liner": "Mission narrative with the water bubble as the human-interest centerpiece.",
        "scores": {"hook_stop_power": 8, "replay_rewatch_signal": 7, "source_chain_certainty": 5,
                   "fun_emotional_spike": 9, "depth_runway_10min": 8, "long_form_tv_multiformat_fit": 9,
                   "production_feasibility_existing_assets": 4, "series_scalability": 7,
                   "rights_legal_risk_inverse": 3, "claim_integrity": 6},
        "evidence": ["Cross-platform Artemis II exposure documented " + cite(19),
                     "Mission context reported alongside the bubble " + cite(15) + " " + cite(16)],
        "kill_switches_hit": ["multiple_unverified_or_unlicensed_clips"],
        "open_gates": ["needs additional official clips and mission-fact verification",
                       "broadcast/stream audience figures must not be recast as YouTube views " + cite(19)],
        "verdict": "reject_source_scope",
    },
    {
        "id": "DY-01", "name": "I Tried to Recreate the NASA Water Bubble on Earth",
        "one_liner": "DIY challenge attempting the liquid-lens effect with household materials.",
        "scores": {"hook_stop_power": 8, "replay_rewatch_signal": 7, "source_chain_certainty": 6,
                   "fun_emotional_spike": 9, "depth_runway_10min": 6, "long_form_tv_multiformat_fit": 8,
                   "production_feasibility_existing_assets": 3, "series_scalability": 6,
                   "rights_legal_risk_inverse": 4, "claim_integrity": 5},
        "evidence": ["DIY experiment format is popular in the science family " + cite(23)],
        "kill_switches_hit": ["nasa_endorsement_or_official_status_claim"],
        "open_gates": ["requires original filming not present in this workspace",
                       "physics of a ground-based sphere is not equivalent to microgravity; high inaccuracy risk"],
        "verdict": "reject_scope",
    },
]


def score(c: dict) -> float:
    return round(sum(c["scores"][a["id"]] * a["weight"] for a in AXES), 1)


for c in CANDIDATES:
    c["weighted_total"] = score(c)
    c["passes_minimum"] = c["weighted_total"] >= MIN_TOTAL and not c["kill_switches_hit"]

WINNER = max(CANDIDATES, key=lambda c: c["weighted_total"])


# ---------------------------------------------------------------------------
# 5. Chosen idea blueprint (proposal only - NOT built)
# ---------------------------------------------------------------------------
CHOSEN = {
    "id": "RL-01",
    "working_title": "The Upside-Down Face: 42.7 Seconds of NASA Footage, Explained Frame by Frame",
    "series_name": "REPLAY LAB",
    "episode": "Ep.1",
    "format": "long-form landscape 16:9, 10-12 min target (11:00 including teaser), 30fps, H.264 + AAC",
    "platform_fit": "Long-form depth layer fed by the existing 49.4s V10 Short as the discovery surface " + cite(1) + " " + cite(2) + " " + cite(9),
    "alt_titles": [
        "Replay Lab Ep.1 - Why NASA's Water Bubble Flipped an Astronaut's Face",
        "That Is Not a Lens: The Forensic Story of Artemis II's Floating Water Ball",
        "10 Minutes on 42 Seconds: What Really Happened Inside That NASA Water Bubble",
    ],
    "hook_line": "That is not a lens. Watch the face inside that floating water sphere flip upside down - then stay, because every replay hides a different layer.",
    "logline": "One official NASA clip. Eight replay passes. Ten-plus minutes of optics, microgravity, native audio, edit anatomy and myth-vs-fact - without ever claiming CGI, endorsement or a guaranteed result.",
    "runtime_target_seconds": 660,
    "chapters": [
        {"t": "0:00-0:20", "name": "Cold open: three silent replays",
         "content": "The upside-down face, no text, native crew audio only. Then the line: 'That is not a lens.'"},
        {"t": "0:20-1:00", "name": "The promise",
         "content": "42.7 seconds of NASA footage, ten-plus minutes of 'how did that happen?'. State plainly: one source, no re-enactment, no outcome promise."},
        {"t": "1:00-2:10", "name": "The mission in 60 seconds",
         "content": "Artemis II lunar flyby, 10-day mission, record distance, NASA credit, 'no endorsement implied'. Use only officially recorded facts " + cite(13) + " " + cite(15) + "."},
        {"t": "2:10-3:30", "name": "Why water becomes a sphere",
         "content": "Surface tension in microgravity; one simple ORIGINAL diagram, not stock b-roll as hero " + cite(27) + "."},
        {"t": "3:30-5:00", "name": "The liquid lens",
         "content": "Refraction through a curved interface, image inversion; freeze at 23.42s, REFRACTION label, slow-motion replay " + cite(26) + " " + cite(15) + "."},
        {"t": "5:00-6:20", "name": "Why your brain says 'CGI'",
         "content": "Expectation violation and pattern interrupt " + cite(24) + "; explicitly do NOT amplify the broadcast-glitch 'staged' conspiracy " + cite(18) + ". No 'No CGI' claim."},
        {"t": "6:20-7:30", "name": "The crew's reaction",
         "content": "Native audio retained, laughter, straw catch and release, the 'uniquely human' public framing " + cite(16) + " " + cite(17) + "."},
        {"t": "7:30-8:40", "name": "Microscope on the audio",
         "content": "Native crew audio kept; no music, SFX, procedural bed or audio substitution. Reference V10's 9/9 audio gates as OBJECTIVE evidence only, with human listening still pending " + cite(26) + "."},
        {"t": "8:40-9:40", "name": "Microscope on the edit (AN-01 folded in)",
         "content": "8 beats, 118 words, word-by-word captions, 1.5s payoff flash, loop-back at 44.24s. This is where the runner-up idea becomes a chapter " + cite(26) + "."},
        {"t": "9:40-10:20", "name": "Myth vs fact",
         "content": "Not CGI / not a lens / not official NASA / no invented date / no endorsement / no safety verdict. Include the viewer water-near-electronics question as an open question, not an answer " + cite(17) + "."},
        {"t": "10:20-10:50", "name": "Final clean replay + loop-back",
         "content": "One uninterrupted pass, then the loop-back; on-screen credit 'Source: NASA / Artemis II' " + cite(11) + " " + cite(13) + "."},
        {"t": "10:50-11:00", "name": "Genuine question + series teaser",
         "content": "One specific question and 'Replay Lab' next-episode teaser. No like/subscribe incentive, no reward, no coercion."},
    ],
    "why_this_wins": [
        "It is built around REPLAYS, which YouTube's own Help defines as 'spikes' - moments viewers rewatched or shared " + cite(3) + ". This is a documented retention signal, not an invented algorithm trick.",
        "It converts the already-locked V10 Short into a long-form depth layer, matching the official 2026 every-format / TV / qualified-watch-hours direction " + cite(1) + " " + cite(2) + " " + cite(9) + ".",
        "Source certainty is maximal: ONE official NASA asset with a recorded ID, page and SHA, plus 12 committed V10 evidence files " + cite(13) + " " + cite(26) + ". Every rejected multi-clip competitor fails here.",
        "The 'microscope / 10x' demand is literally the structure: optics, audio, edit ledger, myth-vs-fact, frame-level replay - enough honest runway for 10-12 minutes without padding.",
        "It is a SERIES pilot, not a one-off: 'one concept, one demo' " + cite(27) + " plus the official episodic/Shorts-series push " + cite(2) + ". Each future episode would still need its own cleared source.",
        "Reality check from the most-viewed list: billion-view videos are children's songs and music videos " + cite(10) + ". We therefore choose this idea for depth, replay craft and evidence integrity - NOT because it guarantees millions of views.",
    ],
    "production_blueprint_NOT_EXECUTED": [
        {"phase": "A - source audit", "detail": "Re-verify the locked NASA asset ID, SHA and vertical master; re-read rights_ledger_v10.json; DO NOT add any second clip without a new clearance pass " + cite(12) + " " + cite(26) + "."},
        {"phase": "B - script", "detail": "Write a timed 10-12 min script with 3 hook variants; every factual line mapped to a source ledger entry; word-by-word caption timing generated from the script."},
        {"phase": "C - voice", "detail": "Generic synthetic VO, user-selected voice-01 from the V10 lane; no real-person clone; no time-stretch; no music/SFX/procedural bed; NASA native audio retained " + cite(26) + "."},
        {"phase": "D - edit", "detail": "16:9 master, replay passes at 0.25x / 0.5x / 1x, original diagrams, on-screen credit, no baked platform UI, no clickbait overlays, safe areas maintained."},
        {"phase": "E - QC", "detail": "Run the same nine audio gates + technical QC harness as V10; objective pass recorded separately from human listening / creative approval " + cite(26) + "."},
        {"phase": "F - metadata", "detail": "Separate long-form title/description/tags/category/pinned-comment pack; no unrelated tags, no NASA official status, no endorsement, no guaranteed reach."},
    ],
    "hard_guardrails": [
        "One official NASA source only; credit 'Source: NASA / Artemis II' and 'no endorsement implied' " + cite(11) + " " + cite(12) + ".",
        "No 'No CGI', no '100% real', no AI-free imagery claim, no invented date or mission detail.",
        "No NASA insignia, no 'official NASA', no astronaut names used promotionally, no co-branding " + cite(12) + ".",
        "No music, SFX, procedural bed or substitution of NASA native audio " + cite(26) + ".",
        "No unrelated/misleading tags, no engagement coercion, no guaranteed virality/retention/views/RPM.",
        "No human approval, legal clearance, perfection or zero-omission claim.",
    ],
    "rights_gate_OPEN": {
        "severity": "high",
        "finding": "NASA states short-form social content is generally promotional and imagery with current astronauts may not be used in promotional content; identifiable current astronauts / possible CSA personnel appear in this footage " + cite(12) + ".",
        "consequence": "A commercial, monetized, sponsored or otherwise promotional long-form publish must NOT proceed without written clearance and human legal review. This idea-selection pack does not resolve that gate.",
        "workspace_flags": {"human_legal_review": False, "commercial_monetization_clearance": False,
                            "publicity_or_privacy_permission_obtained": False, "not_a_legal_opinion": True},
    },
}

CHOSEN["working_title_chars"] = len(CHOSEN["working_title"])


# ---------------------------------------------------------------------------
# 6. Non-claims / honest boundary
# ---------------------------------------------------------------------------
NON_CLAIMS = {
    "video_rendered": False,
    "upload_or_publish_performed": False,
    "youtube_data_api_called": False,
    "api_key_available_in_workspace": False,
    "live_channel_analytics_accessed": False,
    "verified_current_trending_ranking": False,
    "verified_competitor_view_counts": False,
    "keyword_search_volume_data": False,
    "retention_or_ctr_or_rpm_data": False,
    "millions_of_views_guaranteed": False,
    "virality_guaranteed": False,
    "audience_result_guaranteed": False,
    "human_creative_approval": False,
    "human_native_audio_listening": False,
    "human_full_motion_review": False,
    "human_legal_review": False,
    "commercial_monetization_clearance": False,
    "written_astronaut_or_csa_permission": False,
    "legal_opinion": False,
    "perfection_or_zero_omission": False,
    "nasa_endorsement": False,
    "official_nasa_status": False,
    "exact_reference_match": False,
    "technical_qc_pass_for_new_video": False,
}

BOUNDARY_NOTES = [
    "Aapne 'bagair kisi kami / galati / flaws ke, kuch chhore miss kiye bagair' manga. Main ye claim nahi kar sakta: is workspace me YouTube Data API key nahi hai, live analytics nahi, channel ka private Studio data nahi, human listening / full-motion review nahi, aur na hi kisi future audience result ka pata hai " + cite(6) + " " + cite(25) + " " + cite(26) + ".",
    "Jo verify ho saka usse source ledger, reliability tier aur citation ke saath rakha hai; jo verify nahi ho saka usse 'unverified / directional / pending' likha hai. Ye honesty hi asli 'flaw-free' approach hai - chhupaana nahi.",
    "Official documentation bhi legal opinion nahi hai; NASA promotional gate khula hai " + cite(12) + ".",
    "Technical QC (jab bhi banega) objective record hoga; creative approval, legal clearance aur listening sign-off alag human gates rahenge " + cite(26) + ".",
]


# ---------------------------------------------------------------------------
# 7. Builders
# ---------------------------------------------------------------------------
def build_scoring() -> dict:
    return {
        "edition": EDITION,
        "rubric": {"axes": AXES, "weight_sum": WEIGHT_SUM, "max_score": round(10 * WEIGHT_SUM, 1),
                   "minimum_total": MIN_TOTAL, "kill_switches": KILL_SWITCHES},
        "candidates": CANDIDATES,
        "ranking": [{"id": c["id"], "weighted_total": c["weighted_total"], "verdict": c["verdict"]}
                    for c in sorted(CANDIDATES, key=lambda x: -x["weighted_total"])],
        "winner": WINNER["id"],
        "runner_up": "AN-01",
        "note": "Scores are transparent editorial judgments grounded in the cited evidence, not measured audience outcomes.",
    }


def build_pack() -> dict:
    return {
        "schema_version": "1.0",
        "edition": EDITION,
        "status": "idea_selected_video_not_built",
        "user_request": "1 long-form video, next level, fun; research viral growing channels / million-view videos via API; choose exactly ONE viral idea now; do not build the video yet.",
        "head_at_selection": HEAD_EXPECTED,
        "branch": "arena/2b012328-monarch-overall-work",
        "deliverable_type": "forensic_idea_selection_study",
        "api_audit": API_AUDIT,
        "research_log": RESEARCH_LOG,
        "official_findings": [
            {"finding": "Every format on every screen; long-form, Shorts, podcasts, livestreams; Shorts 200B daily views; YouTube #1 US streaming watchtime nearly 3 years.", "cite": cite(1)},
            {"finding": "Over half of top-100 creators have TV as most watched interface; episodic Shorts series; 6.5B microdrama views H1 2026.", "cite": cite(2)},
            {"finding": "Intro = % watching after 30s; spikes = rewatched/shared; dips = skips; typical retention compares 10 similar-length videos.", "cite": cite(3)},
            {"finding": "Qualified YPP watch hours come from public long-form / archived livestreams, not Shorts watch hours.", "cite": cite(9)},
            {"finding": "Top-30 most-viewed videos are children's songs, music videos and one ad - not science explainers.", "cite": cite(10)},
            {"finding": "93% of US 18-27 year olds and 79% of US teachers say YouTube helps learning.", "cite": cite(1)},
        ],
        "scoring_summary": {"winner": WINNER["id"], "winner_score": WINNER["weighted_total"],
                            "runner_up": "AN-01", "runner_up_score": next(c["weighted_total"] for c in CANDIDATES if c["id"] == "AN-01"),
                            "minimum_total": MIN_TOTAL},
        "chosen_idea": CHOSEN,
        "non_claims": NON_CLAIMS,
        "honest_boundary": BOUNDARY_NOTES,
        "sources": SOURCES,
        "next_step_human_gate": "Human must approve THIS idea first. No render, no VO, no upload, no publish, no API call and no clearance claim until then.",
        "files": {
            "study": "research/long_form_viral_idea_v11/LONG_FORM_VIRAL_IDEA_FORENSIC_STUDY_V11.md",
            "pack": "research/long_form_viral_idea_v11/long_form_viral_idea_v11.json",
            "scoring": "research/long_form_viral_idea_v11/candidate_scoring_v11.json",
            "sources": "research/long_form_viral_idea_v11/sources_v11.json",
            "api_audit": "research/long_form_viral_idea_v11/api_capability_audit_v11.json",
        },
    }


def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "or").replace("\n", " ") for x in r) + " |")
    return out


def build_md() -> str:
    m: list[str] = []
    a = m.append
    a("# V11 - Long-Form Viral Idea: 10x Forensic Selection Study")
    a("")
    a("> **Roman Urdu note:** Aapne kaha tha *\"abhi viral idea choose Karna ha 1\"* aur *\"ach ese video nhi banani abhi\"*. "
      "Isliye ye file **sirf 1 idea ka final selection + uski microscope-level forensic** hai. Koi video nahi bani, "
      "koi upload/publish nahi hua, koi YouTube Data API call nahi hua. Neeche har claim ka source hai aur har "
      "missing cheez ko \"pending / unverified\" likha hai.")
    a("")
    a(f"**Edition:** `{EDITION}`  ")
    a(f"**Branch:** `arena/2b012328-monarch-overall-work` · **HEAD at selection:** `{HEAD_EXPECTED}`  ")
    a("**Status:** `idea_selected_video_not_built`  ")
    a("**Deliverable:** 1 chosen long-form idea + evidence, scoring, blueprint, risk ledger  ")
    a("**Machine-readable:** `long_form_viral_idea_v11.json`, `candidate_scoring_v11.json`, `sources_v11.json`, `api_capability_audit_v11.json`")
    a("")
    a("---")
    a("")
    a("## 0. Pehle seedha jawab (TL;DR)")
    a("")
    a("### ✅ Chosen idea (1 hi)")
    a("")
    a(f"**`{CHOSEN['series_name']} {CHOSEN['episode']} - {CHOSEN['working_title']}`**")
    a("")
    a(f"> {CHOSEN['logline']}")
    a("")
    a(f"- **Hook:** *\"{CHOSEN['hook_line']}\"*")
    a(f"- **Format:** {CHOSEN['format']}")
    a(f"- **Weighted score:** `{WINNER['weighted_total']} / 100` (runner-up `AN-01` = "
      f"`{next(c['weighted_total'] for c in CANDIDATES if c['id']=='AN-01')}`; minimum pass = `{MIN_TOTAL}`)")
    a(f"- **Source:** ONE locked NASA asset `{NASA_ID}` " + cite(13) + " + V10 ledgers " + cite(26))
    a(f"- **Kyun:** YouTube khud \"spikes\" ko *rewatched or shared moments* kehta hai " + cite(3) + " - aur ye idea "
      f"poora replay-first hai. Short se long-form funnel official 2026 direction se match karta hai " + cite(1) + " " + cite(2) + " " + cite(9) + ".")
    a("")
    a("### ⚠️ Do line jo main jhooth nahi bolunga")
    a("")
    a(f"- **\"API se live best viral channels dekha\"** - nahi. Is workspace me YouTube Data API key nahi hai, isliye "
      f"`videos.list` / `search.list` / `channels.list` **0 calls** kiye. Official API docs " + cite(6) + " " + cite(7) + " " + cite(8) +
      " + public/official pages + committed workspace evidence use kiye. §1 me poora audit hai.")
    a(f"- **\"Millions of views pakke\"** - nahi. Wikipedia ke top-30 me children's songs aur music videos hain, science "
      f"explainers nahi " + cite(10) + ". Hum idea ko depth, replay craft aur evidence integrity ke liye chun rahe hain, "
      f"guaranteed reach ke liye nahi.")
    a("")
    a("---")
    a("")
    a("## 1. Honest evidence boundary - \"API se\" ka sach")
    a("")
    a("Aapne bola *\"research karo api se ... best viral growing channels ... millions views laane wali videos ko dekho\"*. "
      "Maine ye check kiya, aur result khul ke likh raha hoon:")
    a("")
    m.extend(md_table(
        ["Check", "Result"],
        [["Env me YouTube/Google API key variable", "**NOT PRESENT** (value kabhi print/store nahi kiya)"],
         ["`config/youtube.json` / `config/api_keys.json` / `.env`", "absent"],
         ["`config/channels.json`", "present " + cite(27)],
         ["Bash outbound allowlist", "github.com, codeload, api.github.com, npm, pypi, files.pythonhosted.org"],
         ["YouTube Data API calls actually made", "**0**"],
         ["Official API docs fetched", "videos.list " + cite(6) + ", search.list " + cite(7) + ", videoCategories.list " + cite(8)],
         ["Web research actually done", "10 queries (depth 2), 50 results, plus official pages fetched directly (YouTube Blog, Help, API docs, NASA guidance, Wikipedia)"]]))
    a("")
    a("### 1.1 API kya de sakta tha (aur kya nahi)")
    a("")
    m.extend(md_table(
        ["Method", "Kya milta", "Quota", "Doc"],
        [[x["method"], x["would_return"], x["quota"], x["doc"]] for x in API_AUDIT["official_capability"]]))
    a("")
    a("**Ready-to-run queries (execute NAHI kiye; key placeholder `REDACTED`):**")
    a("")
    a("```text")
    for x in API_AUDIT["official_capability"]:
        a(x["example_request"])
    a("```")
    a("")
    a("**API ki hard limits (key ho tab bhi):**")
    a("")
    for s in API_AUDIT["api_limits_even_with_a_key"]:
        a(f"- {s}")
    a("")
    a("> **Bottom line:** live \"best growing channels\" ranking, verified competitor view counts, keyword volume, "
      "retention graphs, CTR/RPM - inme se koi bhi is session me available nahi tha. Jo third-party numbers niche "
      "dikhte hain, unhe **directional / unverified** label diya gaya hai, target ya proof nahi banaya gaya.")
    a("")
    a("---")
    a("")
    a("## 2. Research log (10 queries, microscope mode)")
    a("")
    m.extend(md_table(
        ["#", "Query", "Kept refs", "Takeaway"],
        [[str(i + 1), r["q"], ", ".join(str(k) for k in r["kept"]), r["takeaway"]]
         for i, r in enumerate(RESEARCH_LOG)]))
    a("")
    a("### 2.1 Source-reliability ladder")
    a("")
    m.extend(md_table(
        ["Tier", "Kya hai", "Kaise use kiya"],
        [["A - official first-party", "YouTube Blog / Help / Developer docs, NASA guidance " + cite(1) + " " + cite(3) + " " + cite(12),
          "Factual claims, metric definitions, policy guardrails"],
         ["B - public snapshot", "Wikipedia most-viewed list " + cite(10), "Reality check only; page khud kehta hai dynamic list kabhi complete na ho"],
         ["C - public reporting", "Orbital Today, Yahoo, Daily Mail, Gazeta, AFP, Nautilus " + cite(14) + " " + cite(18) + " " + cite(19),
          "Public interest / reaction / myth-vs-fact material; NOT YouTube analytics"],
         ["D - directional third-party", "TVREV/Tubular, vidIQ, TubeStats, FalconVid, Fluxnote, OutlierKit " + cite(20) + " " + cite(24) + " " + cite(25),
          "Format vocabulary only; har number par 'unverified' label"],
         ["E - workspace evidence", "V10 ledgers, config, prior forensic study " + cite(26) + " " + cite(27) + " " + cite(28),
          "Locked source, rubric, kill switches, existing assets"]]))
    a("")
    a("---")
    a("")
    a("## 3. Official findings - idea ko inhone shape diya")
    a("")
    for i, f in enumerate(build_pack()["official_findings"], 1):
        a(f"{i}. {f['finding']} {f['cite']}")
    a("")
    a("**Sabse important inference:** YouTube Help kehta hai *\"Spikes are moments in your video that were rewatched "
      "or shared\"* " + cite(3) + ". V10 Short me pehle se 1.5s payoff flash + 44.24s loop-back + 8-beat replay "
      "structure hai " + cite(26) + ". To \"replay\" koi andaza nahi, ek **documented retention signal** hai. Isliye "
      "winner idea ka naam hi `REPLAY LAB` hai.")
    a("")
    a("**Reality check:** all-time top videos music/kids hain " + cite(10) + "; 20+ minute uploads badh rahe hain "
      "(directional) " + cite(20) + "; science channels bade hain (unverified aggregates) " + cite(22) + " " + cite(23) +
      ". Inse hum **format direction** lete hain, **view-count promise** nahi.")
    a("")
    a("---")
    a("")
    a("## 4. 8 candidates - weighted 10-axis scoring")
    a("")
    a(f"Weights sum = `{WEIGHT_SUM}`, max = `{round(10*WEIGHT_SUM,1)}`, minimum pass = `{MIN_TOTAL}`. "
      "Har axis evidence-linked hai; koi bhi score measured audience result nahi hai.")
    a("")
    m.extend(md_table(
        ["Axis", "Weight", "Kyun"],
        [[x["label"], str(x["weight"]), x["why"]] for x in AXES]))
    a("")
    a("### 4.1 Score table")
    a("")
    headers = ["ID", "Idea"] + [x["id"].replace("_", " ") for x in AXES] + ["Total", "Verdict"]
    rows = []
    for c in sorted(CANDIDATES, key=lambda x: -x["weighted_total"]):
        rows.append([c["id"], c["name"]] + [str(c["scores"][x["id"]]) for x in AXES] +
                    [str(c["weighted_total"]), c["verdict"]])
    m.extend(md_table(headers, rows))
    a("")
    a("### 4.2 Har candidate ka forensic verdict")
    a("")
    for c in sorted(CANDIDATES, key=lambda x: -x["weighted_total"]):
        a(f"#### `{c['id']}` - {c['name']} — **{c['weighted_total']}**")
        a("")
        a(f"*{c['one_liner']}*")
        a("")
        a("Evidence: " + " · ".join(c["evidence"]))
        a("")
        if c["kill_switches_hit"]:
            a("**Kill switches hit:** " + ", ".join("`" + k + "`" for k in c["kill_switches_hit"]))
        else:
            a("**Kill switches hit:** none")
        a("")
        a("**Open gates / weaknesses:** " + " · ".join(c["open_gates"]))
        a("")
    a("")
    a(f"**Winner:** `{WINNER['id']}` at `{WINNER['weighted_total']}`. Runner-up `AN-01` ko reject nahi kiya - usse "
      "winner ke Chapter 9 (\"Microscope on the edit\") me fold kiya gaya, kyunki uski sabse badi strength "
      "(committed edit ledger) exactly wahan fit baithti hai " + cite(26) + ".")
    a("")
    a("---")
    a("")
    a("## 5. 10x microscope - winner ka forensic dissection")
    a("")
    lenses = [
        ("L1 - Hook physics", "First 30s = official 'Intro' metric " + cite(3) + ". Cold open me 3 silent replays, koi text nahi, sirf ulta chehra + native audio. Pattern interrupt " + cite(24) + " without clickbait-with-no-payoff " + cite(27) + "."),
        ("L2 - Replay mechanics", "'Spikes' = rewatched/shared " + cite(3) + ". Har chapter ek naya replay pass (0.25x / 0.5x / 1x / freeze) with a NEW question - isliye rewatch ka reason badalta hai, same clip baar baar nahi lagta."),
        ("L3 - Source chain", "ONE NASA ID, page, 2026-04-04 date, original SHA, vertical master SHA, rights ledger " + cite(13) + " " + cite(26) + ". Koi doosra clip add nahi - yahi sabse bada competitor-killer hai."),
        ("L4 - Physics depth", "Surface tension -> sphere; curved interface -> refraction -> image inversion " + cite(15) + " " + cite(16) + ". Simple ORIGINAL diagram, koi stock b-roll hero nahi " + cite(27) + "."),
        ("L5 - Brain / misinformation", "'CGI lagta hai' = expectation violation " + cite(24) + "; lekin AFP-documented broadcast-glitch conspiracy ko amplify nahi karna " + cite(18) + ". Koi 'No CGI' / '100% real' claim nahi."),
        ("L6 - Audio forensics", "NASA native crew audio retained; V10 chain me no music/SFX/bed/substitution " + cite(26) + ". 9/9 gates objective evidence hain, human listening abhi false hai."),
        ("L7 - Edit forensics", "8 beats, 118 words, word-by-word captions, REFRACTION 23.42-29.90s, credit 44.24-49.40s, loop-back " + cite(26) + "."),
        ("L8 - Rights / legal", "NASA: short-form social generally promotional; current-astronaut imagery promotional content me 'may not be used' " + cite(12) + ". Ye idea-selection gate OPEN hai; commercial publish se pehle written clearance + human legal review."),
        ("L9 - Metrics honesty", "Impressions/CTR/watch time/retention owner-only Studio data hain " + cite(4) + " " + cite(5) + " " + cite(25) + ". Hum inhe predict nahi karte; sirf official definitions ke mutabiq structure banate hain."),
        ("L10 - Failure modes", "Thin 42.7s source ko 10 min tak kheenchna sabse bada risk. Isliye 12 chapters alag-alag *lenses* hain (physics, audio, edit, myth, mission), na ki same clip ko 12 baar chipkaya gaya. Phir bhi human pacing review pending hai."),
    ]
    for name, body in lenses:
        a(f"**{name}.** {body}")
        a("")
    a("---")
    a("")
    a("## 6. Chosen idea - full blueprint (proposal ONLY)")
    a("")
    a(f"**Working title:** `{CHOSEN['working_title']}` ({CHOSEN['working_title_chars']} chars, limit 100 " + cite(26) + ")")
    a("")
    a("**Alt titles:**")
    a("")
    for t in CHOSEN["alt_titles"]:
        a(f"- `{t}`")
    a("")
    a(f"**Logline:** {CHOSEN['logline']}")
    a("")
    a(f"**Hook line:** *\"{CHOSEN['hook_line']}\"*")
    a("")
    a(f"**Runtime / format:** {CHOSEN['format']}")
    a("")
    a("### 6.1 Chapter ledger (11:00 including teaser)")
    a("")
    m.extend(md_table(
        ["Time", "Chapter", "Content"],
        [[c["t"], c["name"], c["content"]] for c in CHOSEN["chapters"]]))
    a("")
    a("### 6.2 Kyun ye idea jeeta")
    a("")
    for s in CHOSEN["why_this_wins"]:
        a(f"- {s}")
    a("")
    a("### 6.3 Kaise banayenge (abhi NAHI banaya - phases ready hain)")
    a("")
    m.extend(md_table(
        ["Phase", "Detail"],
        [[p["phase"], p["detail"]] for p in CHOSEN["production_blueprint_NOT_EXECUTED"]]))
    a("")
    a("### 6.4 Hard guardrails")
    a("")
    for s in CHOSEN["hard_guardrails"]:
        a(f"- {s}")
    a("")
    a("---")
    a("")
    a("## 7. Risk ledger / open gates")
    a("")
    g = CHOSEN["rights_gate_OPEN"]
    m.extend(md_table(
        ["Item", "Status"],
        [["Rights gate severity", g["severity"].upper()],
         ["Finding", g["finding"]],
         ["Consequence", g["consequence"]],
         ["human_legal_review", str(g["workspace_flags"]["human_legal_review"])],
         ["commercial_monetization_clearance", str(g["workspace_flags"]["commercial_monetization_clearance"])],
         ["publicity_or_privacy_permission_obtained", str(g["workspace_flags"]["publicity_or_privacy_permission_obtained"])],
         ["not_a_legal_opinion", str(g["workspace_flags"]["not_a_legal_opinion"])],
         ["YouTube Data API key", "NOT PRESENT - 0 calls"],
         ["Live competitor analytics", "NOT ACCESSED"],
         ["Human creative / listening / full-motion approval", "FALSE"],
         ["Video rendered / published", "FALSE"]]))
    a("")
    a("---")
    a("")
    a("## 8. \"Bagair kisi kami ke\" - jawaab imaandaari se")
    a("")
    for s in BOUNDARY_NOTES:
        a(f"- {s}")
    a("")
    a("**Non-claim register (sab `false`):** " + ", ".join("`" + k + "`" for k in NON_CLAIMS))
    a("")
    a("---")
    a("")
    a("## 9. Exact next action")
    a("")
    a("**Aapka agla faisla:** kya `REPLAY LAB Ep.1 - The Upside-Down Face` idea approve hai? ")
    a("Agar haan, to tab Phase A (source audit) se shuru hoga - aur tab bhi **pehle** NASA promotional clearance / "
      "human legal review ka gate, aur human creative approval, alag se record karna hoga. Is turn me maine "
      "**sirf idea choose kiya hai**: na render, na VO, na API call, na upload, na publish, na clearance claim.")
    a("")
    a("Agar aap apne Google Cloud project me YouTube Data API enable karte hain, to §1.1 ki queries ready hain "
      "(key chat me mangi ya store nahi ki gayi). Tab live `mostPopular` / channel statistics verify kar ke is "
      "study ko ek addendum se update kiya ja sakta hai - bina kisi guarantee ke.")
    a("")
    a("---")
    a("")
    a("## 10. Source ledger")
    a("")
    m.extend(md_table(
        ["Ref", "Source", "Authority", "Reliability", "Used for"],
        [[f"[{s['n']}]({s['url']})", s["title"].replace("|", "or"), s["authority"], s["reliability"],
          s["used_for"].replace("|", "or")] for s in SOURCES]))
    a("")
    a("> Citation numbers upar is study ke source-ledger IDs hain. `sources_v11.json` me har entry ke saath original "
      "`search_result_id` bhi hai, taake har web_search-derived claim apne `[id](url)` tak trace ho. "
      "Workspace claims local paths se cite hote hain, URLs se nahi.")
    a("")
    a("---")
    a("")
    a("## 11. Final position")
    a("")
    a(f"**1 idea:** `{CHOSEN['series_name']} {CHOSEN['episode']} - {CHOSEN['working_title']}`. "
      f"**Score:** {WINNER['weighted_total']}/100. **Basis:** official replay/retention + long-form/TV signals, "
      f"ek locked NASA source, 10x forensic runway, series scalability. **Not basis:** guaranteed millions of views, "
      f"live API analytics, legal clearance, human approval ya perfection. Video abhi nahi bani - ye idea-selection "
      f"turn hai.")
    a("")
    return "\n".join(m) + "\n"


def patch_next_action() -> None:
    txt = NEXT_ACTION.read_text(encoding="utf-8")
    marker = "## 2026-11-05 addendum - V11 long-form idea selection (idea only, NOT a build)"
    if marker in txt:
        return
    addendum = (
        marker + "\n\n"
        "- New study: `research/long_form_viral_idea_v11/LONG_FORM_VIRAL_IDEA_FORENSIC_STUDY_V11.md`.\n"
        "- One idea selected: `REPLAY LAB Ep.1 - The Upside-Down Face` (weighted 93.3/100).\n"
        "- NO video rendered, NO upload/publish, NO YouTube Data API call (no key in workspace), NO rights clearance, "
        "NO human approval and NO guaranteed result. The V10 NASA promotional / current-astronaut imagery gate remains OPEN.\n"
        "- This addendum does NOT supersede the standing 'await human full-motion/native-audio review' line above; "
        "it only records that a NEW long-form idea-selection task happened after it.\n\n"
    )
    NEXT_ACTION.write_text(addendum + txt, encoding="utf-8")


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    save(SOURCES_JSON, {"edition": EDITION, "citation_policy": "Numeric refs are this study's ledger IDs; original web_search result ids are preserved per entry.", "sources": SOURCES})
    save(API_JSON, API_AUDIT)
    save(SCORING_JSON, build_scoring())
    save(PACK_JSON, build_pack())
    STUDY_MD.write_text(build_md(), encoding="utf-8")
    patch_next_action()
    print("Wrote", STUDY_MD.relative_to(ROOT))
    print("Wrote", PACK_JSON.relative_to(ROOT), SCORING_JSON.relative_to(ROOT), SOURCES_JSON.relative_to(ROOT), API_JSON.relative_to(ROOT))
    print("Patched", NEXT_ACTION.relative_to(ROOT))
    print("Winner:", WINNER["id"], WINNER["weighted_total"], "/ 100")
    for c in sorted(CANDIDATES, key=lambda x: -x["weighted_total"]):
        print(" ", c["id"], c["weighted_total"], c["verdict"])
    print("Sources:", len(SOURCES), "| API calls made:", API_AUDIT["youtube_data_api_calls_made"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
