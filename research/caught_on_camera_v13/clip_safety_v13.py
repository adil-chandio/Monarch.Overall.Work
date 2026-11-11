#!/usr/bin/env python3
"""Single source of truth for the V13 caught-on-camera content-safety gate.

The first V13 acquisition pass used generic CCTV / "caught on camera" queries and
returned murder CCTV, suicide bombings, missile strikes, plane crashes and robberies.
The owner asked for funny / engaging / eye-catching / shocking / mind-blowing moments,
NOT graphic or tragic footage. This module is imported by both the acquisition script
and the hard QC validator so a clip cannot slip through one gate and be used anyway.
"""
from __future__ import annotations
import re

# POSITIVE, on-brand discovery: wildlife / animals / funny / surprising / skill moments.
QUERIES = [
    'animal "caught on camera" filetype:video',
    'wildlife "caught on camera" filetype:video',
    'CCTV animal filetype:video',
    '"security camera" bear filetype:video',
    'dog "caught on camera" filetype:video',
    'cat "caught on camera" filetype:video',
    'funny animal fail filetype:video',
    '"unexpected moment" animal filetype:video',
    'animal rescue "caught on camera" filetype:video',
    'bird "caught on camera" filetype:video',
    'squirrel feeder camera filetype:video',
    'raccoon "caught on camera" filetype:video',
    'trick shot caught on camera filetype:video',
    'skateboard fail filetype:video',
    'parkour fail filetype:video',
    'flash mob filetype:video',
    'funny fail video filetype:video',
    'octopus "caught on camera" filetype:video',
    'whale "caught on camera" filetype:video',
    'goat "caught on camera" filetype:video',
    'funny animals filetype:video',
    'cute animals filetype:video',
    'animal fails filetype:video',
    'cat fails filetype:video',
    'dog fails filetype:video',
    'wildlife camera filetype:video',
    'bear enters house filetype:video',
    'animal in shop filetype:video',
    'unexpected animal filetype:video',
    'amazing animal moment filetype:video',
    'sports fail filetype:video',
    'fail compilation filetype:video',
    '"caught on camera" filetype:video',
    'CCTV filetype:video',
    'dashcam filetype:video',
    '"viral video" filetype:video',
    '"unexpected moment" filetype:video',
]

# Hard exclusions. Single words are matched with word boundaries so benign text
# like "Warrior Custom Golf" or "toward" is NOT rejected as "war". Multi-word
# phrases catch the exact graphic/tragedy titles seen in the rejected first pool.
BLOCK_WORDS = (
    "kill", "killing", "killed", "murder", "homicide", "fatal", "shoot", "shooting",
    "firearm", "gun", "bomb", "bombing", "explosion", "blast", "missile", "suicide",
    "terror", "military", "soldier", "combat", "drone", "rocket", "artillery",
    "invasion", "robbery", "burglary", "assault", "crime", "criminal", "suspect",
    "arrest", "stabbing", "knife", "blood", "gore", "kidnap", "abduct", "hostage",
    "cantonment", "precinct", "crash", "collision", "earthquake", "hurricane",
    "tornado", "disaster", "tragedy", "wreck", "riot", "protest", "dead",
    "volgograd", "crimean", "bannu", "saratov", "ramat",
)
BLOCK_PHRASES = (
    "missile strikes", "drone bomb", "cantonment attack", "police chase",
    "seeking information", "missing person", "flight 3054", "flight 703",
    "airlines flight", "flight77", "thai cctv", "crimean bridge", "ramat gan",
    "volgograd", "bannu", "nancy guthrie", "brian thompson", "saratov",
    "homicide suspects", "9/11",
)
BLOCK_TERMS = BLOCK_WORDS + BLOCK_PHRASES

GOOD_TERMS = (
    "cat", "dog", "puppy", "kitten", "bear", "bird", "squirrel", "raccoon", "animal",
    "wildlife", "funny", "fail", "unexpected", "surprise", "trick", "skill", "catch",
    "jump", "dance", "skate", "parkour", "rescue", "monkey", "fox", "deer", "owl",
    "penguin", "whale", "dolphin", "octopus", "goat", "cow", "horse", "rabbit", "parrot",
    "hilarious", "cute", "adorable", "incredible", "amazing", "smart", "clever",
)

# Only the NASA / Artemis V10 / Short assets remain hard-excluded.
# REVERSED: the ten V7 social-origin Commons candidates were initially excluded by V13
# to force a fully new search. The positive-only Commons pass produced 20 safe but
# mostly low-energy clips (landscape repeats, microscopy, interviews), so those ten
# rights-cleared V7 candidates are now reintroduced as a CURATED recovery pool.
# They are NOT the rejected V12 eight archived finals and are NOT the NASA Short.
EXCLUDE_TOKENS = ["artemis", "water bubble", "nasa "]

ALLOWED_LICENSES = {"cc0", "public domain", "pd", "cc by 3.0", "cc by 4.0",
                    "cc-by-3.0", "cc-by-4.0", "public domain mark 1.0", "pd-usgov"}


def safety_gate(text):
    """Return (allowed, blocked_term, positive_score)."""
    low = (text or "").lower()
    for phrase in BLOCK_PHRASES:
        if re.search(r"\b" + re.escape(phrase) + r"\b", low):
            return False, phrase, 0
    for word in BLOCK_WORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", low):
            return False, word, 0
    score = sum(1 for g in GOOD_TERMS if g in low)
    return True, None, score
