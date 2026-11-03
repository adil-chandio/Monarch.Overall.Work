"""yt-intel — YouTube intelligence that runs on $0.

Design constraints, in order of importance:

1. **No key needed for depth.** Data API v3 is an optional accelerator; every core
   capability also has a keyless path (autocomplete, public web pages, transcripts).
2. **Nothing is estimated that can be observed.** Where a signal is a proxy (e.g. trend
   slope instead of absolute volume), the field name says so.
3. **Every score is explainable.** No opaque "viral score": each number comes from named
   inputs with published weights, and the report prints them.
4. **Honest failure.** A datacenter IP is not a residential user; YouTube will throttle
   us. When it does, the corpus says `status: rate_limited` instead of silently
   returning a biased sample.
"""
__version__ = "1.0.0"

from . import client  # noqa: F401
