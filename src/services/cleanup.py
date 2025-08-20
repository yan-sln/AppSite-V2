# -*- coding: utf-8 -*-
"""Cleanup utilities."""

from __future__ import annotations

import os
import shutil
from services.paths import AppPaths


def clean_temp(paths: AppPaths) -> None:
    """Remove the temp folder content (but keep the folder)."""
    if not os.path.isdir(paths.temp_dir):
        return
    for name in os.listdir(paths.temp_dir):
        p = os.path.join(paths.temp_dir, name)
        try:
            if os.path.isfile(p) or os.path.islink(p):
                os.remove(p)
            elif os.path.isdir(p):
                shutil.rmtree(p)
        except Exception:
            # Best-effort cleanup; swallow errors to avoid breaking UX
            pass
