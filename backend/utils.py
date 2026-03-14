"""
utils.py — Shared utility helpers.
"""

import re


def normalize_text(text: str) -> str:
    """Lowercase and collapse whitespace."""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def safe_float(val) -> float | None:
    """Safely cast a value to float, returning None on failure."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def sanitize_filename(filename: str) -> str:
    """
    B2 fix: Strip directory components and dangerous characters from a
    user-supplied filename so it can never escape the intended directory.

    Examples
    --------
    >>> sanitize_filename("../../app.py")
    'app.py'
    >>> sanitize_filename("my resume (final).pdf")
    'my resume (final).pdf'
    """
    # Take only the basename — removes any path traversal components
    name = os.path.basename(filename)
    # Remove characters that are problematic on common filesystems
    name = re.sub(r'[^\w\s\-_.()\[\]]', '_', name)
    # Collapse multiple underscores / spaces
    name = re.sub(r'_{2,}', '_', name).strip()
    return name or "upload"


import os  # noqa: E402  (kept at bottom to avoid circular issues)
