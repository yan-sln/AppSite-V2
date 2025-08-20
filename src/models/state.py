# -*- coding: utf-8 -*-
"""Lightweight transient UI state with no module-level globals."""

from dataclasses import dataclass

@dataclass
class AppState:
    # Which flow should FileChooser follow (1=header, other=image/content)
    screen_entry: int = 1
    # Absolute path selected by FileChooser
    selected_file: str = ""
    # Whether a post is currently started (new or resumed)
    post_started: bool = False
