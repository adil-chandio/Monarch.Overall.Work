#!/usr/bin/env python3
"""V17 transcript fallback: public captions only, no video/audio download.

The first V17 run recorded 12/12 yt-dlp transcript failures because YouTube's
datacenter bot-check demanded sign-in. This second pass tries:
  1. youtube-transcript-api (its own caption endpoint)
  2. yt-dlp with alternate player_client values

Only computed script/hook metrics and short excerpts are stored. No full
third-party transcript is reproduced. No causal virality claim, no private
analytics, no legal opinion, no upload/publish/monetisation claim.
"""
from __future__ import annotations
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from yt_intel import client, http, reverse  # noqa: E402

BASE = ROOT / "research" / "next_level_niche_v17"
OUT = BASE / "api_evidence"
TARGETS = json.loads((BASE / "transcript_targets_v17.json").read_text())["targets"]
VIDS = {r["id"]: r for r in json.loads((OUT / "video_details_v17.json").read_text())["videos"]}

def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def log(*a):
    print(*a, flush=True)

def yt_api_transcript(video_id):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        tr = api.fetch(video_id, languages=["en", "en-US", "en-GB"])
        raw = tr.to_raw_data()
        if raw and isinstance(raw[0], dict):
            text = " ".join(str(x.get("text", "")) for x in raw)
        else:
            text = " ".join(str(getattr(x, "text", "")) for x in raw)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return {"status": "error", "detail": "empty transcript text"}
        return {
            "status": "ok", "method": "youtube-transcript-api.fetch",
            "language": getattr(tr, "language_code", None) or getattr(tr, "language", None),
            "is_generated": getattr(tr, "is_generated", None),
            "text": text,
        }
    except Exception as e:
        return {"status": "error", "method": "youtube-transcript-api.fetch", "detail": f"{type(e).__name__}: {str(e)[:180]}"}

def yt_dlp_transcript(video_id):
    try:
        import yt_dlp
    except Exception as e:
        return {"status": "error", "method": "yt-dlp", "detail": f"import failed: {e}"}
    clients = ["android", "tv", "web_safari", "mweb", "ios"]
    for c in clients:
        opts = {
            "quiet": True, "no_warnings": True, "skip_download": True,
            "writesubtitles": True, "writeautomaticsub": True,
            "subtitleslangs": ["en", "en-US", "en-GB"], "subtitlesformat": "json3",
            "outtmpl": "/dev/null",
            "extractor_args": {"youtube": {"player_client": [c]}},
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            subs = info.get("subtitles") or {}
            auto = info.get("automatic_captions") or {}
            tracks = subs or auto
            lang = next((l for l in ("en", "en-US", "en-GB") if l in tracks), next(iter(tracks), None))
            if not lang:
                continue
            urls = [t.get("url") for t in tracks[lang] if t.get("ext") == "json3"] or [t.get("url") for t in tracks[lang]]
            if not urls:
                continue
            raw = http.get(urls[0], cache=True, ttl=86400 * 30)
            text, _ = client._json3_text(raw)
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                return {"status": "ok", "method": f"yt-dlp player_client={c}",
                        "language": lang, "is_generated": bool(auto and not subs), "text": text,
                        "chapters": info.get("chapters") or []}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:140]}"
            continue
    return {"status": "error", "method": "yt-dlp", "detail": f"all player_clients failed; last={locals().get('last', 'no detail')}"}

def fetch_transcript(video_id):
    a = yt_api_transcript(video_id)
    if a["status"] == "ok":
        return a
    b = yt_dlp_transcript(video_id)
    if b["status"] == "ok":
        return b
    return {"status": "error", "method": "both", "detail": f"api={a.get('detail')}; ytdlp={b.get('detail')}"}

def build_teardown(target, transcript):
    meta = VIDS.get(target["id"], {})
    dur = meta.get("duration_seconds")
    text = transcript["text"]
    words = text.split()
    wpm = round(len(words) / (dur / 60), 1) if dur else None
    grade = reverse.reading_grade(text)
    ctas = [m.group(0).lower() for m in reverse.CTA.finditer(text)]
    first_sentence = re.split(r"(?<=[.!?])\s", text.strip())[0][:240] if text.strip() else ""
    hook = {
        "first_3s_words": " ".join(reverse.hook_window(words)),
        "first_sentence": first_sentence,
        "opens_with_number": bool(reverse.NUMBER_WORD.search(" ".join(words[:12]))),
        "opens_with_question": "?" in " ".join(words[:14]),
        "opens_with_you": bool(re.search(r"\byou\b", " ".join(words[:12]), re.I)),
        "claim_type": reverse._claim_type(" ".join(words[:40])),
    }
    script = {
        "words": len(words), "wpm": wpm,
        "filler_rate": round(sum(1 for w in words if w.lower().strip(".,") in reverse.FILLER) / max(1, len(words)), 4),
        "cta_count": len(ctas), "cta_examples": ctas[:5],
        "numbers_per_100w": round(len(reverse.NUMBER_WORD.findall(text)) / max(1, len(words)) * 100, 2),
        "reading_grade": grade, "first_30_words": " ".join(words[:30]),
        "reading": reverse._script_reading(len(words), wpm, grade),
    }
    t = {"receipt": {"age_days": meta.get("age_days"), "views": meta.get("views")},
         "hook": hook, "script": script}
    return {
        "id": target["id"], "lane": target["lane"], "title": meta.get("title") or target["title"],
        "channel": meta.get("channel"), "views": meta.get("views"), "duration_seconds": dur,
        "age_days": meta.get("age_days"),
        "transcript_status": {k: transcript.get(k) for k in ("status", "method", "language", "is_generated")},
        "script": script, "hook": hook,
        "structure": reverse.section_map(text, dur, transcript.get("chapters") or []),
        "psychology": reverse._psych(hook, meta.get("title") or target["title"]),
        "replication": reverse._replication(t),
        "boundary": "Descriptive co-occurrence only; no causal claim, no full transcript stored.",
    }

def esc(s, n=90):
    return re.sub(r"\s+", " ", str(s or "")).strip().replace("|", "\\|")[:n]

def main():
    results, errors = [], []
    for i, t in enumerate(TARGETS, 1):
        tr = fetch_transcript(t["id"])
        if tr["status"] == "ok":
            results.append(build_teardown(t, tr))
            log(f"[{i:02d}/{len(TARGETS)}] OK {t['id']} via {tr.get('method')} words={len(tr['text'].split())}")
        else:
            errors.append({"id": t["id"], "lane": t["lane"], "title": t["title"], "detail": tr.get("detail")})
            log(f"[{i:02d}/{len(TARGETS)}] FAIL {t['id']} {tr.get('detail')[:120]}")
        time.sleep(0.4)
    save("transcript_teardowns_v17.json", {"count": len(results), "errors": errors, "items": results})
    run = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "targets": len(TARGETS), "usable_transcripts": len(results), "errors": len(errors),
        "methods": [r["transcript_status"].get("method") for r in results],
        "boundary": "Public captions only; no video/audio download, no invented transcript, no causal claim.",
    }
    save("transcript_fallback_run_v17.json", run)
    log("fallback run", json.dumps(run, indent=2))

    L = []
    A = L.append
    A("# V17 transcript / script / hook fallback forensics")
    A("")
    A(f"Generated UTC: `{run['generated_utc']}`. Targets: `{run['targets']}`. Usable public captions: `{run['usable_transcripts']}`. Errors: `{run['errors']}`.")
    A("")
    A("The first V17 pass used `yt_intel.reverse.teardown` with default `yt-dlp`; all 12 attempts hit YouTube's datacenter sign-in bot-check. This second pass tried `youtube-transcript-api` and alternate `yt-dlp` player clients. Only public captions are used. No full transcript is reproduced, no video/audio is downloaded, and no causal virality claim is made.")
    A("")
    if results:
        rows = []
        for r in results:
            s, h, rp = r["script"], r["hook"], r["replication"]
            rows.append([esc(r["title"], 62), r["id"], esc(r["transcript_status"].get("method"), 28),
                         s["words"], s["wpm"], s["reading_grade"], s["cta_count"],
                         esc(s["first_30_words"], 70), h["claim_type"],
                         "Y" if h["opens_with_you"] else "N", "Y" if h["opens_with_number"] else "N",
                         esc("; ".join(rp.get("keep", [])[:2]), 46)])
        L.extend(["| " + " | ".join(["Title", "ID", "Method", "Words", "WPM", "Grade", "CTAs", "First 30 words", "Claim", "You", "Num", "Keep"]) + " |",
                  "| " + " | ".join(["---"] * 12) + " |"] + ["| " + " | ".join(str(x) for x in row) + " |" for row in rows])
        A("")
        for r in results:
            A(f"## `{r['id']}` — {esc(r['title'], 100)}")
            A("")
            A(f"- Receipt: {r['views']:,} views · {r['duration_seconds']} s · {r['age_days']} days old · {r['channel']}.")
            A(f"- Method: `{r['transcript_status'].get('method')}` · language `{r['transcript_status'].get('language')}` · generated `{r['transcript_status'].get('is_generated')}`.")
            A(f"- Script: {r['script']['reading']} · CTAs {r['script']['cta_count']} · numbers/100w {r['script']['numbers_per_100w']}.")
            A(f"- Hook first sentence: `{esc(r['hook']['first_sentence'], 220)}`")
            A(f"- First 3s proxy: `{esc(r['hook']['first_3s_words'], 120)}`")
            A("- Structure: " + "; ".join(f"{s.get('at')} {s.get('title')}" for s in r["structure"][:8]))
            A("- Psychology drivers: " + "; ".join(d.get("driver", "") for d in r["psychology"].get("drivers", [])))
            A("- Replication keep: " + "; ".join(r["replication"].get("keep", [])))
            A("- Replication change: " + "; ".join(r["replication"].get("change", [])))
            A("- Replication beat: " + "; ".join(r["replication"].get("beat", [])))
            A("")
    else:
        A("No public transcript could be retrieved for any target. This is an access result, not a gap filled with invented script text.")
    A("")
    A("## Failed targets (honest access log)")
    A("")
    A("| ID | Lane | Title | Detail |")
    A("| --- | --- | --- | --- |")
    for e in errors:
        A(f"| `{e['id']}` | {e['lane']} | {esc(e['title'], 70)} | {esc(e['detail'], 160)} |")
    A("")
    A("---")
    A("")
    A("**NOT claimed:** competitor video-frame editing analysis, private retention/CTR/RPM, invented transcripts, verified growth ranking, legal clearance, human approval, upload/publish/monetisation, guaranteed views, virality, perfection.")
    (BASE / "TRANSCRIPT_FORENSICS_V17.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # Append a short pointer to the main data appendix so it is not stale.
    rp = BASE / "FORENSIC_REPORT_V17.md"
    txt = rp.read_text(encoding="utf-8")
    marker = "## Transcript fallback pointer"
    if marker not in txt:
        txt += ("\n" + marker + "\n\n"
                "The default `yt-dlp` teardowns in this report all returned a YouTube sign-in bot-check. "
                "A second pass with `youtube-transcript-api` + alternate `yt-dlp` clients is recorded in "
                "`TRANSCRIPT_FORENSICS_V17.md` and `api_evidence/transcript_teardowns_v17.json`. "
                f"Usable public captions: {run['usable_transcripts']}/{run['targets']}. "
                "No transcript was invented and no full third-party transcript is reproduced.\n")
        rp.write_text(txt, encoding="utf-8")
    log("DONE", run["usable_transcripts"], "usable transcripts")

if __name__ == "__main__":
    main()
