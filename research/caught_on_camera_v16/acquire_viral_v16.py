#!/usr/bin/env python3
"""V16 viral Commons acquisition: 20 NEW social-origin funny/shocking clips.

NOT V14 repeats. Live Commons API search with VIRAL FUNNY queries (fail, prank,
trick shot, instant karma, slip, viral, hilarious, unexpected, shocking) — NOT
animal-generic queries that produced low-energy V13 safe pass. Filters for
social origin (YouTube/TikTok/Dailymotion/Facebook/Instagram/Vimeo/viral/
FailArmy/AFV recorded in metadata) OR strong viral-funny terms. Hard-excludes
all 20 V14 titles. Licence gate PD/CC0/CC BY only. Safety gate blocks
graphic/tragic. Objective 10s hook window (motion + surprise). Writes
rights ledger + selection + contact sheet for validate_clips_v13.py.

No direct TikTok/Instagram/Reddit downloads. Commons video2commons mirrors
with recorded social origin are the rights-documented source. No legal opinion,
no monetisation claim, no upload/publish, no virality claim.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
BASE13 = ROOT / "research" / "caught_on_camera_v13"
BASE16 = ROOT / "research" / "caught_on_camera_v16"
sys.path.insert(0, str(BASE13))
sys.path.insert(0, str(ROOT))

from clip_safety_v13 import BLOCK_TERMS, GOOD_TERMS, EXCLUDE_TOKENS, ALLOWED_LICENSES, safety_gate  # noqa: E402

WORK = ROOT / "production" / "monarch-cam" / "work" / "caught_on_camera_viral_v16"
WINDOWS = BASE13 / "windows"
REVIEW = BASE13 / "review"
for p in (WORK, WINDOWS, REVIEW):
    p.mkdir(parents=True, exist_ok=True)

API = "https://commons.wikimedia.org/w/api.php"
UA = ("MonarchCamV16/1.0 (https://github.com/adil-chandio/Monarch.Overall.Work; "
      "viral social-origin caught-on-camera clip research)")
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept": "*/*"})

FF = "ffmpeg"
WINDOW_S = 10.0
SAMPLE_FPS = 4
MAX_CLIPS = 20

# VIRAL FUNNY queries — intitle: forces TITLE match (precise, avoids fuzzy
# description matches like "Fossil Lake" for "dog fail"). Bare "viral" removed
# (pulls medical "viral hepatitis"). Title on-brand + blocks reject leakage.
VIRAL_QUERIES = [
    'intitle:fail filetype:video',
    'intitle:prank filetype:video',
    'intitle:trick filetype:video',
    'intitle:karma filetype:video',
    'intitle:funny filetype:video',
    'intitle:hilarious filetype:video',
    'intitle:cat filetype:video',
    'intitle:dog filetype:video',
    'intitle:baby filetype:video',
    'intitle:slip filetype:video',
    'intitle:fall filetype:video',
    'intitle:scream filetype:video',
    'intitle:jump filetype:video',
    'intitle:dance filetype:video',
    'intitle:skate filetype:video',
    'intitle:parkour filetype:video',
    'intitle:sports filetype:video',
    'intitle:viral filetype:video',
    'intitle:caught filetype:video',
    'intitle:unexpected filetype:video',
    'intitle:surprise filetype:video',
    'intitle:amazing filetype:video',
    'intitle:incredible filetype:video',
    'intitle:smart filetype:video',
    'intitle:clever filetype:video',
    'intitle:rescue filetype:video',
    'intitle:cute filetype:video',
    'intitle:adorable filetype:video',
    'intitle:compilation filetype:video',
    'intitle:funniest filetype:video',
    'intitle:laugh filetype:video',
    'intitle:humor filetype:video',
    'intitle:comedy filetype:video',
    'intitle:joke filetype:video',
    'intitle:animal filetype:video',
    'intitle:monkey filetype:video',
    'intitle:bear filetype:video',
    'intitle:bird filetype:video',
    'intitle:squirrel filetype:video',
    'intitle:raccoon filetype:video',
    'intitle:puppy filetype:video',
    'intitle:kitten filetype:video',
    'intitle:elephant filetype:video',
    'intitle:horse filetype:video',
    'intitle:goat filetype:video',
    'intitle:rabbit filetype:video',
    'intitle:penguin filetype:video',
    'intitle:whale filetype:video',
    'intitle:dolphin filetype:video',
    'intitle:octopus filetype:video',
    'intitle:fox filetype:video',
    'intitle:deer filetype:video',
    'intitle:owl filetype:video',
    'intitle:pig filetype:video',
    'intitle:cow filetype:video',
    'intitle:parrot filetype:video',
    'intitle:skill filetype:video',
    'intitle:shock filetype:video',
    'intitle:unbelievable filetype:video',
    'fail compilation filetype:video',
    'funny fail filetype:video',
    'prank filetype:video',
    'trick shot filetype:video',
    'instant karma filetype:video',
    'hilarious fail filetype:video',
    'cat fail filetype:video',
    'dog fail filetype:video',
    'baby fail filetype:video',
    'funny animal fail filetype:video',
    'cute animal fail filetype:video',
    'caught on camera funny filetype:video',
    'FailArmy filetype:video',
    'America Funniest filetype:video',
]

# V14 20 titles — HARD EXCLUDE (owner rejected reuse). Lowercase substrings.
V14_EXCLUDE_SUBSTRINGS = [
    "dive mr bean",
    "horror bean",
    "ambulance bean",
    "japanese mascot fails",
    "baby monkey jumping fail",
    "ocicat on cat wheel",
    "animals workout mix",
    "baby elephant videos",
    "dance dance revolution",
    "april fools ai prank",
    "math professor fixes projector",
    "hunter's scary maze",
    "scary maze game prank",
    "cat behaviour - self-grooming",
    "flip the frog - funny face",
    "flip the frog - puddle pranks",
    "cat meowing into camera",
    "chicago_parallel_parking_fail",
    "chicago parallel parking",
    "greased_pigs",
    "greased pigs",
]
# Exact-title excludes for generic names (avoid over-blocking "comedy" substring).
V14_EXCLUDE_EXACT = {
    "file:comedy.webm",
}

# Social origin terms — at least one must appear in title/description/credit/categories
# OR strong viral-funny terms must appear in title. Bare "viral"/"shocking" removed:
# they match medical "viral hepatitis" and news. Use phrases "viral video" etc.
SOCIAL_TERMS = (
    "youtube", "tiktok", "dailymotion", "facebook", "instagram", "vimeo",
    "failarmy", "afv", "america's funniest", "americas funniest",
    "video2commons", "social media", "caught on camera", "instant karma",
    "trick shot", "prank", "fail compilation", "funny fail", "hilarious",
    "unexpected moment", "viral video", "viral moment", "viral clip",
    "went viral", "viral hit",
)
STRONG_FUNNY_TERMS = (
    "fail", "prank", "trick", "karma", "hilarious", "funny", "slip",
    "fall", "unexpected", "scream", "jump scare", "instant karma",
    "trick shot", "viral video", "viral moment", "caught on camera",
    "joke", "comedy", "laugh", "humor", "humour",
)

# Title MUST contain at least one on-brand term. Rejects HIV/COVID/police/
# protest/game/music/news titles (none contain funny/animal terms).
TITLE_ON_BRAND = (
    "fail", "prank", "trick", "karma", "hilarious", "funny", "slip",
    "fall", "cat", "dog", "puppy", "kitten", "baby", "animal",
    "monkey", "bear", "bird", "squirrel", "raccoon", "skate",
    "parkour", "sports", "dance", "jump", "scream", "viral video",
    "viral moment", "caught on camera", "unexpected", "cute",
    "adorable", "incredible", "amazing", "smart", "clever", "rescue",
    "compilation", "fails", "belly rub", "pig", "elephant", "horse",
    "goat", "cow", "rabbit", "parrot", "penguin", "whale", "dolphin",
    "octopus", "fox", "deer", "owl", "elk", "critter", "joke",
    "comedy", "laugh", "humor", "humour", "surprise", "skill",
    "shock", "unbelievable", "mind-blowing", "mind blowing",
)

# Medical / crime / news / volcano / farm / old-film / NASA / USDA / politics
# substring blocks. Catches "viral hepatitis", "protests" (plural bug),
# "police", "spraying", volcano compilations, USDA farm series, old films,
# NASA space, anime, press briefings, USDA ads, wildfires, tech tutorials.
V16_BLOCK_SUBSTRINGS = (
    "hiv", "aids", "covid", "vaccine", "vacine", "hepatitis", "epidemic",
    "pandemic", "unaids", "measles", "sarampo", "retroviral", "herpes",
    "rabies", "gag-protein", "alpharetroviral", "gene-expression",
    "police", "protest", "spray", "doordash", "kabila", "boris",
    "johnson", "keke", "palmer", "true jackson", "neffex", "multiversus",
    "victorious", "fenton", "pandemia", "epidemia", "relatório",
    "chefe da", "novo relatório", "ulli thiemann", "viralspot",
    "emmi win", "win ipad", "win iphone", "know your crew",
    "fails to", "hair fails", "agent smith", "fighter move",
    "modest", "mayor gordon", "campaign commercial", "dispose of waste",
    "grand canyon", "applegate river", "fossil lake", "borstar",
    "dps operations", "shelter medicine", "grape spritzer",
    "pumpkin curry", "phoebe chicks", "reading novel",
    "behind the wheel", "eagan police", "christmas tree",
    "campaign", "commercial, 1959", "interplay-between",
    "correlates-with", "stress-granules", "infection-induces",
    # Volcano / disaster (matched "compilation")
    "kapoho", "kīlauea", "kilauea", "fissure", "volcano", "eruption",
    "lava", "bay during", "conditions at",
    # USDA farm generic series (matched "animals")
    "fpac", "animals (20", "animals (19",
    # Old silent / chalk films (boring, static)
    "humorous phases", "unappreciated joke", "silent", "shortfilm",
    "kinetoscope", "chalk", "(1903)", "(1900", "(1910", "(1920",
    "cow island", "missouri", "river breaks",
    # NASA / space (matched trick/unexpected/cat/horse)
    "nasa", "lucy mission", "dinkinesh", "swift", "black hole",
    "snacking", "svs", "satellite", "telescope", "webb", "horsehead",
    "nebula", "cosmic cat", "hubble", "cat's eye", "cat eye",
    "orbit", "astronaut",
    # Old films / interviews (matched jump/laugh/comedy)
    "1911", "salchow", "ulrich", "stop! look", "smurthwaite",
    "(1921)", "(1925)", "cat and the canary", "monkey business",
    # Warm Springs horse roundup (matched horse)
    "warm springs", "horses and burros", "blm corral",
    "wild horse gather", "horse gather", "burros",
    "trained wild horses", "southern oregon",
    # Anime / cartoon (matched slip)
    "rwby", "chibi", "anime", "cartoon", "animation",
    # Politics / press (matched viral/baby/rescue)
    "sean spicer", "united airlines", "answers questions", "spicer",
    "joe biden", "biden", "american rescue plan", "explained",
    "press briefing", "white house",
    # USDA ads (matched animal/bird/pig)
    "usda", "defend the flock", "healthy harry", "bird market",
    "swine fever", "african swine", "animal and plant", "stop african",
    "遏制", "arrêtez", "frenemos", "peste porcine", "fiebre porcina",
    "inspection service", "kate bowers", "dvm", "veterinary medical",
    "biosecurity", "pack fun", "not pork", "protect your pigs",
    "deadly outbreak", "npip", "signs of illness", "learn npip",
    # Disaster / attack (matched rabbit/dog)
    "rabbit fire", "riverside county", "wildfire", "attacking",
    "stray dog", "denizli",
    # Tech / Wikipedia (matched smart/clever)
    "eset", "smart security", "download and install",
    "wikipedia", "being clever", "stepanakert", "wikiclub",
    # Science / military comedy (matched unexpected/laugh)
    "from-ugly-duckling", "cell-se", "identification-from",
    "charting", "exceptional", "heat of 2023", "brooding",
    "chilean-oyster", "ostrea-chilensis", "unexpected-comple",
    "afe comedy", "comedy tour", "shape, hq", "bring the laughs",
    # Science false positives (fail/trick/slip/unexpected in lab titles)
    "ccl2", "mesenchymal", "stem-cells", "fail-to-establish",
    "deficient", "cartilage", "phenotype", "cd4", "conditional-sos",
    "unexpected-cartilage", "construction-of-impossibility",
    "logic-based", "impossibility", "trics", "huntingtin",
    "aggregation", "elife00710", "three-dimensional", "paper-based",
    "slip-device", "one-step-point", "physical-sensing",
    "microswimmers", "surface-properties", "transformation-from",
    "plastic-flow", "deformation-mechani", "explanations-of",
    # Aquarium whales (static pool swimming, not funny)
    "kiska", "orcinu", "arctic cove", "delphinapterus",
    "marineland", "niagara",
    # Military TV spot / monastery (matched comedy/karma)
    "afn", "naples", "tv spot", "carney park", "brings laughs",
    "phodong", "karma thubten", "monastery", "chokhorling",
    # Dedup Theodore series (keep "rinses", block "oiled")
    "oiled wildlife",
    # Magic-talk head + autumn Fall false positives (fall=autumn, not slip)
    "perceptual-elements", "penn", "teller", "cups-and-balls",
    "fall overlook", "fall drive", "fall leaves",
    # Military rescue (not funny rescue)
    "undersea rescue", "submarine", "argentina",
    "firefighters conduct", "torii station", "rescue training",
)

BAD_LICENSE_TOKENS = ("by-sa", "by-nc", "sa 3.0", "sa 4.0", "fair use",
                      "license review needed", "review needed (video)", "all rights reserved")
VIDEO_EXT = (".webm", ".ogv", ".ogg", ".mp4", ".mov")
VIDEO_MIME = ("video/webm", "application/ogg", "video/ogg", "video/mp4",
              "video/quicktime", "video/x-matroska")


def log(*a):
    print(*a, flush=True)


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def api(params, tries=4):
    for i in range(tries):
        try:
            r = S.get(API, params=params, timeout=40)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            log("  api retry", i + 1, type(e).__name__)
            time.sleep(2 + 2 * i)
    return {}


def search(q):
    d = api({"action": "query", "format": "json", "formatversion": "2",
             "generator": "search", "gsrsearch": q, "gsrnamespace": 6,
             "gsrlimit": 50, "prop": "imageinfo",
             "iiprop": "url|size|mime|sha1|extmetadata|mediatype"})
    return d.get("query", {}).get("pages", []) or []


def clean_meta(m):
    def v(k):
        x = m.get(k, {})
        return (x.get("value") if isinstance(x, dict) else "") or ""
    return {
        "license_short_name": v("LicenseShortName"),
        "license_id": v("License"),
        "license_url": v("LicenseUrl"),
        "usage_terms": v("UsageTerms"),
        "artist": re.sub(r"<[^>]*>", "", v("Artist")).strip(),
        "credit": re.sub(r"<[^>]*>", "", v("Credit")).strip(),
        "attribution_required": v("AttributionRequired").lower() in ("true", "1", "yes"),
        "description": re.sub(r"<[^>]*>", "", v("ImageDescription")).strip()[:1200],
        "categories": v("Categories"),
        "copyrighted": v("Copyrighted"),
        "restrictions": v("Restrictions"),
        "permission_excerpt": re.sub(r"<[^>]*>", "", v("Permission")).strip()[:600],
    }


def is_v14_repeat(title):
    low = title.lower()
    if low in V14_EXCLUDE_EXACT:
        return True
    for sub in V14_EXCLUDE_SUBSTRINGS:
        if sub in low:
            return True
    return False


def has_social_origin(title, meta):
    blob = " ".join([title, meta.get("description", ""), meta.get("credit", ""),
                     meta.get("categories", ""), meta.get("artist", "")]).lower()
    if any(t in blob for t in SOCIAL_TERMS):
        return True
    # Fallback: strong funny terms in title (viral funny even without explicit platform tag)
    title_low = title.lower()
    if any(t in title_low for t in STRONG_FUNNY_TERMS):
        return True
    return False


def title_on_brand(title):
    low = title.lower()
    return any(t in low for t in TITLE_ON_BRAND)


def v16_blocked(title, meta):
    blob = " ".join([title, meta.get("description", ""), meta.get("categories", ""),
                     meta.get("credit", "")]).lower()
    for b in V16_BLOCK_SUBSTRINGS:
        if b in blob:
            return b
    return None


def acceptable(page, meta):
    title = page.get("title", "")
    low = title.lower()
    if not low.endswith(VIDEO_EXT):
        return False
    if any(t in low for t in EXCLUDE_TOKENS):
        return False
    if is_v14_repeat(title):
        return False
    if not title_on_brand(title):
        return False
    if v16_blocked(title, meta) is not None:
        return False
    blob = " ".join([title, meta.get("description", ""), meta.get("categories", ""),
                     meta.get("credit", "")])
    ok, blocked, _ = safety_gate(blob)
    if not ok:
        return False
    if not has_social_origin(title, meta):
        return False
    lic = (meta["license_short_name"] or meta["license_id"]).strip().lower()
    if lic and lic not in ALLOWED_LICENSES and not any(x in lic for x in ("public domain", "cc0", "cc by 3.0", "cc by 4.0")):
        if not any(x in lic for x in ("public domain", "cc0", "cc by 3.0", "cc by 4.0", "cc-by-3.0", "cc-by-4.0")):
            return False
    blob2 = (lic + " " + meta["permission_excerpt"] + " " + meta["usage_terms"]).lower()
    if any(b in blob2 for b in BAD_LICENSE_TOKENS):
        return False
    if not meta["license_short_name"] and not meta["license_id"]:
        return False
    return True


def derivatives(title):
    d = api({"action": "query", "format": "json", "formatversion": "2",
             "prop": "videoinfo", "titles": title, "viprop": "url|derivatives|size|mime"})
    pages = d.get("query", {}).get("pages", []) or []
    if not pages:
        return []
    vi = (pages[0].get("videoinfo") or [{}])[0]
    out = []
    for x in vi.get("derivatives", []) or []:
        src = x.get("src", "")
        if src.startswith("//"):
            src = "https:" + src
        if not src.startswith("https://"):
            continue
        out.append({"src": src, "type": x.get("type", ""),
                    "width": x.get("width", 0), "height": x.get("height", 0),
                    "key": x.get("transcodekey", "")})
    return out


def download(url, dest, cap_mb=90):
    try:
        with S.get(url, stream=True, timeout=180) as r:
            r.raise_for_status()
            n = 0
            with open(dest, "wb") as f:
                for c in r.iter_content(1 << 20):
                    if not c:
                        continue
                    f.write(c)
                    n += len(c)
                    if n > cap_mb * (1 << 20):
                        return False
        return dest.exists() and dest.stat().st_size > 20000
    except Exception as e:
        log("  download failed", type(e).__name__, str(e)[:140])
        return False


def probe_duration(path):
    r = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        return 0.0
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def has_audio(path):
    r = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    return "Audio:" in r.stderr


def hook_start(path, dur):
    try:
        r = subprocess.run(
            [FF, "-v", "error", "-i", str(path), "-vf",
             f"fps={SAMPLE_FPS},scale=160:90,format=gray", "-an",
             "-f", "rawvideo", "-"], capture_output=True, timeout=180)
        raw = r.stdout
        frames = len(raw) // (160 * 90)
        if frames < 12:
            return 0.0, {"status": "too_few_frames", "frames": frames}
        a = np.frombuffer(raw[:frames * 160 * 90], dtype=np.uint8).reshape(frames, 90, 160)
        d = np.abs(a[1:].astype(np.int16) - a[:-1].astype(np.int16)).mean(axis=(1, 2)).astype(float)
        w = max(4, int(WINDOW_S * SAMPLE_FPS))
        best, bi = -1.0, 0
        for i in range(0, max(1, len(d) - w)):
            seg = d[i:i + w]
            score = float(seg.mean()) + 0.55 * float(seg.max())
            if score > best:
                best, bi = score, i
        start = max(0.0, bi / SAMPLE_FPS)
        return start, {"status": "ok", "frames_scored": int(frames),
                       "window_frames": w, "motion_mean": round(float(d.mean()), 3),
                       "window_score": round(best, 3), "start_s": round(start, 2)}
    except Exception as e:
        return 0.0, {"status": "scoring_failed", "detail": type(e).__name__}


def encode_window(src, start, dest, native_audio):
    vf = ("scale=1152:648:force_original_aspect_ratio=decrease,"
          "pad=1152:648:(ow-iw)/2:(oh-ih)/2:black,setsar=1,"
          "crop=960:540:96:54,fps=30,format=yuv420p")
    common = [FF, "-y", "-v", "error", "-ss", f"{start:.3f}", "-t", str(WINDOW_S),
              "-i", str(src)]
    tail = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt",
            "yuv420p", "-r", "30", "-g", "60", "-c:a", "aac", "-b:a", "128k",
            "-ar", "48000", "-ac", "2", "-t", str(WINDOW_S), "-movflags",
            "+faststart", str(dest)]
    if native_audio:
        fc = ("[0:v]" + vf + ",setpts=PTS-STARTPTS[v];"
              "[0:a]atrim=0:" + str(WINDOW_S) + ",asetpts=PTS-STARTPTS,"
              "aresample=48000,aformat=channel_layouts=stereo[a]")
        cmd = common + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]"] + tail
    else:
        fc = ("[0:v]" + vf + ",setpts=PTS-STARTPTS[v];"
              "[1:a]atrim=0:" + str(WINDOW_S) + ",asetpts=PTS-STARTPTS[a]")
        cmd = common + ["-f", "lavfi", "-t", str(WINDOW_S), "-i",
                        "anullsrc=channel_layout=stereo:sample_rate=48000",
                        "-filter_complex", fc, "-map", "[v]", "-map", "[a]"] + tail
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        log("  encode failed", r.stderr[-300:])
    return r.returncode == 0 and dest.exists() and dest.stat().st_size > 10000


def frame(path, out):
    subprocess.run([FF, "-y", "-v", "error", "-ss", "2", "-i", str(path),
                    "-frames:v", "1", "-update", "1", str(out)], capture_output=True)


def contact(items):
    tw, th, cols = 320, 180, 4
    rows = (len(items) + cols - 1) // cols
    im = Image.new("RGB", (tw * cols, (th + 26) * rows), (10, 16, 26))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except Exception:
        f = ImageFont.load_default()
    for i, it in enumerate(items):
        p = REVIEW / f"curated_{it['id']:02d}.jpg"
        if not p.exists():
            continue
        tile = Image.open(p).convert("RGB").resize((tw, th))
        x, y = (i % cols) * tw, (i // cols) * (th + 26)
        im.paste(tile, (x, y))
        d.text((x + 5, y + th + 5), f"{it['id']:02d} {it['short'][:34]}",
               font=f, fill=(91, 214, 208))
    out = REVIEW / "curated_contact_sheet_v13.jpg"
    im.save(out, quality=88)
    log("contact sheet", out)


def main():
    # Clean stale windows (including failed social TikTok/Dailymotion licence-unknown files).
    for p in list(WINDOWS.glob("curated_*.mp4")) + list(REVIEW.glob("curated_*.jpg")):
        p.unlink(missing_ok=True)
    pool, seen, rejected = [], set(), 0
    for q in VIRAL_QUERIES:
        pages = search(q)
        log(f"search {q!r}: {len(pages)} hits")
        for pg in pages:
            title = pg.get("title", "")
            if title in seen:
                continue
            seen.add(title)
            ii = (pg.get("imageinfo") or [{}])[0]
            if not ii:
                continue
            meta = clean_meta(ii.get("extmetadata") or {})
            if not acceptable(pg, meta):
                rejected += 1
                continue
            mime = ii.get("mime", "")
            if mime and not any(m in mime for m in VIDEO_MIME) and not title.lower().endswith(VIDEO_EXT):
                continue
            dur = float(ii.get("duration") or 0)
            if dur and not (WINDOW_S + 0.5 <= dur <= 240.0):
                continue
            _, _, prio = safety_gate(" ".join([title, meta["description"], meta["categories"]]))
            # Social-origin boost: explicit platform mention ranks higher.
            blob = " ".join([title, meta["description"], meta["credit"], meta["categories"]]).lower()
            social_boost = sum(1 for t in ("youtube", "tiktok", "dailymotion", "facebook", "instagram", "viral video", "viral moment", "failarmy", "caught on camera") if t in blob)
            # Funny-title score: count strong funny terms in title (ranks prank/karma/fail first).
            title_low = title.lower()
            funny_score = sum(1 for t in STRONG_FUNNY_TERMS if t in title_low)
            pool.append({"title": title, "pageid": pg.get("pageid"),
                         "url": ii.get("url", ""), "size": ii.get("size", 0),
                         "mime": mime, "width": ii.get("width"), "height": ii.get("height"),
                         "duration": dur, "commons_sha1": ii.get("sha1", ""),
                         "descriptionurl": ii.get("descriptionurl", ""), "meta": meta,
                         "priority": prio, "social_boost": social_boost,
                         "funny_score": funny_score, "query": q})
        time.sleep(0.4)
    log(f"acceptable viral pool: {len(pool)} (rejected: {rejected})")
    save_json(REVIEW / "candidate_pool_v16.json", {"count": len(pool), "candidates": pool,
              "rejected_by_safety_or_licence_or_social": rejected})

    # Prefer funny titles first (karma/prank/trick/fail), then social-origin,
    # then on-brand, then small files. Funny-first puts Instant karma #1
    # (boost=0 but funny_score=2) ahead of boost=1 animal titles.
    pool.sort(key=lambda x: (-x["funny_score"], -x["social_boost"], -x["priority"], x["size"] or 1 << 30))
    accepted, failures = [], []
    seen_norm = set()
    for cand in pool:
        if len(accepted) >= MAX_CLIPS:
            break
        # Dedup near-duplicates (SD/HD, IDs, parenthetical numbers).
        norm = re.sub(r"\.(webm|mp4|ogv|ogg|mov)$", "", cand["title"].lower())
        norm = re.sub(r"\s+(hd|sd|1080p|720p|480p|360p|full hd|new)$", "", norm).strip()
        norm = re.sub(r"\([^)]*\d[^)]*\)", "", norm)  # strip (IDs/years)
        norm = re.sub(r"\d+", "", norm)  # strip remaining numbers
        norm = re.sub(r"\s+", " ", norm).strip()
        if norm in seen_norm:
            failures.append({"title": cand["title"], "reason": "duplicate_title"})
            continue
        seen_norm.add(norm)
        cid = len(accepted) + 1
        raw = WORK / f"raw_{cid:02d}.media"
        urls = [cand["url"]]
        if (cand["size"] or 0) > 30 * (1 << 20):
            urls = [d["src"] for d in derivatives(cand["title"])
                    if 360 <= d.get("width", 0) <= 720] + urls
        ok, used = False, None
        for u in urls[:4]:
            if not u.startswith("https://"):
                continue
            if download(u, raw):
                ok, used = True, u
                break
        if not ok:
            failures.append({"title": cand["title"], "reason": "download_failed"})
            continue
        dur = probe_duration(raw) or cand["duration"] or 0.0
        if dur < WINDOW_S + 0.5:
            failures.append({"title": cand["title"], "reason": "clip_too_short_for_10s_window",
                             "duration_s": round(dur, 2)})
            raw.unlink(missing_ok=True)
            continue
        st = max(0.0, dur - WINDOW_S - 0.2)
        start, score = hook_start(raw, dur)
        start = min(start, st)
        native = has_audio(raw)
        win = WINDOWS / f"curated_{cid:02d}.mp4"
        if not encode_window(raw, start, win, native):
            failures.append({"title": cand["title"], "reason": "encode_failed"})
            raw.unlink(missing_ok=True)
            continue
        frame(win, REVIEW / f"curated_{cid:02d}.jpg")
        short = cand["title"].replace("File:", "").replace(".webm", "").replace(".mp4", "").replace(".ogv", "")[:60]
        rec = {
            "id": cid, "title": cand["title"].replace("File:", ""), "short": short,
            "commons_page": cand["descriptionurl"], "commons_pageid": cand["pageid"],
            "license": cand["meta"]["license_short_name"],
            "license_id": cand["meta"]["license_id"],
            "license_url": cand["meta"]["license_url"],
            "usage_terms": cand["meta"]["usage_terms"],
            "artist": cand["meta"]["artist"], "credit": cand["meta"]["credit"],
            "attribution_required": cand["meta"]["attribution_required"],
            "categories": cand["meta"]["categories"][:600],
            "copyrighted": cand["meta"]["copyrighted"],
            "restrictions": cand["meta"]["restrictions"][:300],
            "origin_query": cand["query"],
            "commons_sha1": cand["commons_sha1"],
            "download_url": used,
            "source_duration_s": round(dur, 2),
            "source_bytes": cand["size"], "source_mime": cand["mime"],
            "window": {"start_s": round(start, 2), "duration_s": WINDOW_S,
                       "end_s": round(start + WINDOW_S, 2), "score": score},
            "local_window_file": f"windows/curated_{cid:02d}.mp4",
            "local_window_sha256": sha256(win),
            "local_window_bytes": win.stat().st_size,
            "native_audio_kept": native, "audio_added": (not native),
            "content_safety": {"keyword_gate": "passed", "positive_score": cand["priority"],
                               "social_boost": cand["social_boost"],
                               "blocked_terms": list(BLOCK_TERMS),
                               "human_watch_through_required": True,
                               "family_safe_claim": False},
            "human_legal_review": False, "not_a_legal_opinion": True,
        }
        accepted.append(rec)
        log(f"  [{cid:02d}] {rec['title'][:64]} | {rec['license']} | window {start:.1f}s | {rec['local_window_bytes']} B")
        raw.unlink(missing_ok=True)

    contact(accepted)
    ledger = {
        "project": "Monarch Cam V16 - NEW viral social-origin clips",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": "Live Commons API namespace-6 search with VIRAL FUNNY queries; social-origin filter; V14 20 hard-excluded; extmetadata licence gate PD/CC0/CC BY; objective motion/surprise hook-window scoring; native audio kept (silent AAC added where needed); 10s normalized MP4 windows committed.",
        "queries": VIRAL_QUERIES,
        "v14_excluded": V14_EXCLUDE_SUBSTRINGS + ["File:COMEDY.webm"],
        "candidate_pool_size": len(pool),
        "rejected_by_safety_or_licence_or_social": rejected,
        "content_safety_gate": {
            "hard_blocked_terms": list(BLOCK_TERMS),
            "positive_terms": list(GOOD_TERMS),
            "reason": "Viral funny/shocking-but-safe only. Graphic/tragic blocked. V14 20 hard-excluded.",
            "human_watch_through_required": True,
            "family_safe_guarantee": False,
        },
        "accepted_count": len(accepted),
        "failed_count": len(failures),
        "failures": failures,
        "boundary": ("Commons video2commons mirrors with recorded social origin (YouTube/TikTok/"
                     "Dailymotion/Facebook/Instagram/Vimeo/viral) are the rights-documented source. "
                     "No direct TikTok/Instagram/Reddit download. No legal opinion, no human legal review, "
                     "no upload/publish/monetisation, no virality or perfection claim."),
        "assets": accepted,
    }
    save_json(BASE13 / "rights_ledger_curated_v13.json", ledger)
    save_json(BASE13 / "hook_windows_curated_v13.json", {"accepted": accepted, "failures": failures})
    sel = {"selection_version": "v16-viral-20", "count": len(accepted),
           "note": "V16 20 NEW viral social-origin Commons clips. NOT V14 repeats.",
           "clips": [{"id": f"C{a['id']:02d}", "window_file": a["local_window_file"],
                      "ledger": "rights_ledger_curated_v13.json", "pool": "viral_v16",
                      "short": a["short"]} for a in accepted]}
    save_json(BASE13 / "selected_windows_v13.json", sel)
    log(f"DONE accepted={len(accepted)} failed={len(failures)}")
    if len(accepted) != MAX_CLIPS:
        log(f"WARNING: accepted {len(accepted)} != 20")
        sys.exit(1)


if __name__ == "__main__":
    main()
