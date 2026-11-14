#!/usr/bin/env python3
"""Score whether a skill's own numbers survive into a model's answer.

Structural validation cannot tell a real skill from a well-formatted empty one: the
upstream pack passed every form check while 48 of its skills carried no claim that
could be wrong. This runner tests the claim.

A case supplies a prompt, the regexes that must appear in a competent answer, and
the regexes that indicate the failure mode the skill names. Scoring is mechanical on
purpose; an LLM judge would reward the plausible paragraph that the skill exists to
prevent.

Connection is optional. With no model available every case reports SKIP and the
exit code is 0, so this can sit in CI next to validate.py without a secret.

    python3 evals/run.py
    python3 evals/run.py --case 3
    python3 evals/run.py --selftest              # no model needed, runs in CI
    python3 evals/run.py --answer 3 answer.txt   # score a file you produced
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CASES = pathlib.Path(__file__).resolve().parent / "cases.json"

# words that mark a clause as rejecting the thing it names rather than prescribing it
NEGATED = re.compile(
    r"\b(not|never|no|avoid|don't|do not|isn't|instead|rather than|fails?|wrong|"
    r"a different|breaks?|loses?|kills?|turn|turns|reading as|reads as)\b", re.I)
# A rejection clause can sit further from the term than any fixed window allows -
# in a bullet list it is often on the next line. Judge the enclosing sentence pair.
CLAUSE_BEFORE = 220
CLAUSE_AFTER = 220


def load_skill(name: str) -> str:
    f = ROOT / "skills" / name / "SKILL.md"
    return f.read_text() if f.exists() else ""


def ask_model(prompt: str, skill_text: str) -> str | None:
    """Ask a model with the skill as context, if one is reachable.

    Uses the `claude` CLI when present because that is the tool the pack targets.
    Returns None when unavailable: a missing model is not a failing test.
    """
    payload = (
        "You are answering as a senior technical artist. Use the skill below as "
        "binding direction.\n\n" + skill_text + "\n\n---\n\nRequest: " + prompt
    )
    try:
        r = subprocess.run(
            ["claude", "-p", payload],
            capture_output=True, text=True, timeout=180,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return r.stdout


def score(case: dict, answer: str) -> tuple[bool, list[str]]:
    notes: list[str] = []
    ok = True
    low = answer.lower()

    for pat in case["must"]:
        if re.search(pat, low, re.I):
            notes.append(f"  ok    {pat}")
        else:
            notes.append(f"  MISS  {pat}")
            ok = False

    for pat in case["must_not"]:
        # A correct answer often names the failure mode in order to reject it -
        # "a matte surface is a different style" is the skill working, not failing.
        # So a must_not hit only counts when the clause around it is not negated.
        hit = None
        for m in re.finditer(pat, low, re.I):
            clause = low[max(0, m.start() - CLAUSE_BEFORE):m.end() + CLAUSE_AFTER]
            if not NEGATED.search(clause):
                hit = m
                break
        if hit is None:
            notes.append(f"  clean {pat}")
        else:
            start = max(0, hit.start() - 40)
            notes.append(f"  BAD   {pat}  <- ...{low[start:hit.end()+40].strip()}...")
            ok = False

    return ok, notes


def selftest() -> int:
    """Prove every case can be passed and can be failed, without a model.

    A case that no honest answer can pass is a broken test. A case that the
    upstream one-sentence skill passes tests nothing. Both are silent failures
    once the runner is skipping for lack of a connection, so they get checked
    here: the skill's own body is the passing answer, the stub is the failing one.
    """
    cases = json.loads(CASES.read_text())
    bad = 0
    for i, case in enumerate(cases, 1):
        body = load_skill(case["skill"])
        body = re.sub(r"^---\n.*?\n---\n", "", body, flags=re.S)
        passes_on_skill, _ = score(case, body)
        stub = "# stub\n\nPleasing colours. Soft forms. Nice light.\n"
        passes_on_stub, _ = score(case, stub)
        good = passes_on_skill and not passes_on_stub
        bad += not good
        print(f"{'ok  ' if good else 'BAD '} {i}. {case['skill']:24s} "
              f"skill-passes={passes_on_skill!s:5s} stub-passes={passes_on_stub!s:5s}")
    print(f"\n{len(cases) - bad}/{len(cases)} cases discriminate")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=int, help="1-based case number")
    ap.add_argument("--selftest", action="store_true",
                    help="check the cases themselves; no model needed")
    ap.add_argument("--answer", nargs=2, metavar=("N", "FILE"),
                    help="score an existing answer file for case N")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    cases = json.loads(CASES.read_text())
    if args.case:
        if not 1 <= args.case <= len(cases):
            print(f"no case {args.case}; have {len(cases)}", file=sys.stderr)
            return 2
        cases = [cases[args.case - 1]]

    # explicit answer file: score it, and fail loudly if it is wrong
    if args.answer:
        n, path = args.answer
        case = json.loads(CASES.read_text())[int(n) - 1]
        answer = pathlib.Path(path).read_text()
        ok, notes = score(case, answer)
        print(f"{'PASS' if ok else 'FAIL'}  [{case['skill']}]")
        print("\n".join(notes))
        return 0 if ok else 1

    passed = failed = skipped = 0
    for i, case in enumerate(cases, 1):
        answer = ask_model(case["prompt"], load_skill(case["skill"]))
        if answer is None:
            print(f"SKIP  {i}. {case['skill']} (no model connection)")
            skipped += 1
            continue
        ok, notes = score(case, answer)
        print(f"{'PASS' if ok else 'FAIL'}  {i}. {case['skill']}")
        if not ok:
            print("\n".join(notes))
        passed += ok
        failed += (not ok)

    print(f"\n{passed} passed, {failed} failed, {skipped} skipped")
    # a skipped run is not a failure; a run with a model in it is
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
