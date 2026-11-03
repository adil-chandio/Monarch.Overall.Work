"""CTR system — thumbnails, titles and hooks that are measured, not guessed.

Everything here is deterministic and offline: Pillow + numpy only, no paid APIs.
"""
from .thumb import ARCHETYPES, render_thumbnail, render_suite
from .title import title_variants, score_title
from .hook import hook_variants, score_hook
from .score import score_image, rank

__all__ = [
    "ARCHETYPES", "render_thumbnail", "render_suite",
    "title_variants", "score_title",
    "hook_variants", "score_hook",
    "score_image", "rank",
]
