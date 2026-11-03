"""Idea generation: two families, both grounded in a demand signal.

FAMILY A — TREND CHASERS
  Built from live autocomplete expansions. These are ideas the audience is already
  typing. The risk is competition, not comprehension.

FAMILY B — EVERGREEN CURIOSITY
  Built from *cognitive mechanisms* rather than from keywords: curiosity gaps, schema
  violations, belief threats, self-reference, loss aversion. Each template is a
  structural bet, then dressed with the topic.

The FOMO/WTF vocabulary below is deliberate. It is the vocabulary that works, and every
template is written so the *claim stays true* — a hook that lies gets the click and loses
the retention, which is a net negative.

Every idea keeps `why_it_works` and `risk` populated. An idea list without objections is
a brainstorming session, not a plan.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict

TEMPLATES = [
    # (family, structure, template, why, risk)
    ("trend", "number-first", "{n_big} things nobody tells you about {topic}",
     "a number converts an opinion into an inventory", "the list must actually be worth the click"),
    ("trend", "time-boxed", "I tried {topic} for {days} days — here is the receipt",
     "effort + evidence beats advice", "requires real footage of the trial"),
    ("trend", "comparison", "{tool_a} vs {tool_b}: the only difference that matters",
     "comparisons pre-qualify the viewer", "needs a defensible verdict"),
    ("curiosity", "schema-violation", "This should be impossible: {topic}",
     "an impossible claim is registered as an error the brain wants to close",
     "the payoff must genuinely surprise"),
    ("curiosity", "belief-threat", "You have been doing {topic} backwards",
     "correcting a held belief creates relief and gratitude", "must be true, or it reads as a trick"),
    ("curiosity", "open-loop", "What actually happens when you {topic}",
     "an unanswered consequence runs in the background", "needs a visible outcome early"),
    ("curiosity", "self-reference", "If you have ever {pain}, this is why",
     "self-referential cues get priority attention", "the pain must be specific, not universal"),
    ("curiosity", "loss-frame", "The one {topic} mistake that costs you {cost}",
     "losses weigh roughly twice as much as gains", "invented cost = instant distrust"),
    ("curiosity", "hidden-mechanism", "The part of {topic} nobody films",
     "the un-filmed angle is a genuine information gap", "needs access competitors do not have"),
    ("evergreen", "rule-break", "Why the {topic} rules you were taught do not work",
     "authority challenge is a strong, reusable frame", "must name the rule and prove the failure"),
    ("evergreen", "small-number", "{small} seconds is enough to judge {topic}",
     "a small, checkable unit feels knowable", "needs a real measurement to back it"),
    ("evergreen", "behind-the-curtain", "I rebuilt {topic} from scratch to see how it really works",
     "rebuilding is proof of understanding, not opinion", "expensive to shoot well"),
]


def _fill(tpl: str, topic: str, ctx: dict) -> str:
    return (tpl
            .replace("{topic}", topic)
            .replace("{n_big}", str(ctx.get("n_big", 7)))
            .replace("{days}", str(ctx.get("days", 30)))
            .replace("{tool_a}", ctx.get("tool_a", "the free tool"))
            .replace("{tool_b}", ctx.get("tool_b", "the paid one"))
            .replace("{pain}", ctx.get("pain", "wondered why your videos stall"))
            .replace("{cost}", ctx.get("cost", "a month of work"))
            .replace("{small}", str(ctx.get("small", 3))))


def from_suggestions(suggestions: list[str], topic: str, limit: int = 8) -> list[dict]:
    """Trend family: turn real search suggestions into idea seeds, deduped by intent."""
    out, seen = [], set()
    for s in suggestions:
        low = s.lower()
        key = re.sub(r"\W+", " ", low.replace(topic.lower(), "")).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append({
            "family": "trend",
            "topic": s,
            "structure": "verbatim search intent",
            "why_it_works": "people are literally typing this phrase into YouTube",
            "risk": "if the phrase is underserved, the first decent video owns it; if it is served, you must out-execute",
            "source": "autocomplete",
        })
        if len(out) >= limit:
            break
    return out


def generate(topic: str, demand: dict | None = None, limit: int = 12, **ctx) -> list[dict]:
    demand = demand or {}
    ideas: list[dict] = []
    for fam, struct, tpl, why, risk in TEMPLATES:
        ideas.append({
            "family": fam, "structure": struct,
            "idea": _fill(tpl, topic, ctx), "why_it_works": why, "risk": risk,
            "source": "template",
        })
    if demand.get("suggestions"):
        ideas = from_suggestions(demand["suggestions"], topic, limit=6) + ideas

    # rank: trend ideas with a demand hit first, then curiosity (evergreen lasts longer)
    def rank(i):
        fam_score = {"trend": 2.0, "curiosity": 2.2, "evergreen": 2.4}[i["family"]]
        return -fam_score
    ideas.sort(key=rank)
    for i, idea in enumerate(ideas[:limit]):
        idea["rank"] = i + 1
    return ideas[:limit]


def wtf_bank(topic: str) -> list[str]:
    """Seed phrases for the 'what am I looking at' reaction. Structure, not clickbait."""
    return [
        f"The moment {topic} stops behaving like it should",
        f"{topic}, but the constraint is removed",
        f"{topic} at 1/1000th the normal scale",
        f"What {topic} looks like when nobody is watching",
        f"{topic} in reverse — the part that makes no sense",
    ]
