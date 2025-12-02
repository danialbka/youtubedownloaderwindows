"""
YouTube-only extractor export.
"""

from .simple import YouTubeExtractor

# Only YouTube is supported for this build
ALL_EXTRACTORS = [
    YouTubeExtractor(),
]

__all__ = [
    'YouTubeExtractor',
    'ALL_EXTRACTORS',
]
