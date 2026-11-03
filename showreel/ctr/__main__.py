"""CLI: python -m showreel.ctr [--render] [--json out.json]"""
import json, sys, os
from . import thumb, title, hook, score

def main(argv):
    out = "public/showreel/ctr_report.json"
    # always re-render: it is deterministic, and scoring a stale JPEG is how you ship a
    # thumbnail that does not match the code (this happened once already)
    if "--no-render" not in argv:
        thumb.render_suite()
    report = {}
    imgs = {}
    from PIL import Image
    for name in thumb.ARCHETYPES:
        p = f"public/showreel/thumbs/{name}.jpg"
        report[name] = score.score_image(Image.open(p))
    report_titles = [r for _, r in title.rank_titles()]
    report_hooks = [hook.score_hook(s, o) for _, s, o in hook.hook_variants()]
    payload = {
        "thumbnails": report,
        "titles": report_titles,
        "hooks": report_hooks,
        "weights": score.WEIGHTS,
    }
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)
    print("THUMBNAILS")
    for k, v in sorted(report.items(), key=lambda kv: -kv[1]["score"]):
        print(f'  {v["score"]:5.1f} {v["grade"]}  {k:20} {"FAIL: " + "; ".join(v["hard_fails"]) if v["hard_fails"] else ""}')
    print("\nTITLES")
    for r in report_titles[:5]:
        print(f'  {r["score"]:5.1f} {r["grade"]}  {r["chars"]:3}c  {r["title"]}')
    print("\nHOOKS")
    for r, (name, _, _) in zip(report_hooks, hook.hook_variants()):
        print(f'  {r["score"]:5.1f} {r["grade"]}  {r["spoken_seconds"]:4.1f}s  {name}')
    print(f"\nwrote {out}")

if __name__ == "__main__":
    main(sys.argv[1:])
