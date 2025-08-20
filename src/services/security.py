# -*- coding: utf-8 -*-
"""Small security utilities for safer path handling and HTML escaping."""

from __future__ import annotations

import html
import os
from typing import Iterable


def safe_join(base: str, *paths: Iterable[str]) -> str:
    """
    Safer os.path.join to avoid path traversal outside of base.
    Raises ValueError if the final path escapes the base directory.
    """
    joined = os.path.join(base, *paths)
    norm_base = os.path.abspath(base)
    norm_path = os.path.abspath(joined)
    if not norm_path.startswith(norm_base + os.sep) and norm_path != norm_base:
        raise ValueError("Path traversal detected.")
    return norm_path


def esc(text: str) -> str:
    """HTML-escape user-provided text."""
    return html.escape(text or "", quote=True)
