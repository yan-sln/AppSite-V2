# -*- coding: utf-8 -*-
"""
Application bootstrap (Kivy). No module-level globals.
- Registers UI screens (import side-effect), then loads KV.
- Provides dependency container (paths, services, state).
- Cleans temp folder on stop.
"""

from __future__ import annotations

import os
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.lang import Builder

# Import registers Kivy Screen classes before KV is loaded
from ui.screens import WindowManager  # noqa: F401 (used by KV)
from services.paths import AppPaths, AppAssets, ensure_dirs
from services.image_service import ImageService
from services.html_service import HtmlBuilder
from services.cleanup import clean_temp
from models.state import AppState


class AppSite(App):
    """Main Kivy app wiring dependencies and app state."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.paths = AppPaths()
        ensure_dirs(self.paths)
        self.images = ImageService(self.paths)
        self.html = HtmlBuilder(self.paths, AppAssets(), site_title="Ile-Segal")
        self.state = AppState()

    def build(self):
        # Load KV after classes are imported so rules are bound
        kv = Builder.load_file(os.path.join("ui", "kv", "AppSite.kv"))
        return kv

    def rmall(self):
        """Remove only temp/ content to avoid losing exported files."""
        try:
            clean_temp(self.paths)
        except Exception:
            pass

    def on_stop(self):
        """Clean temp/ when the app closes."""
        try:
            clean_temp(self.paths)
        except Exception:
            pass


if __name__ == "__main__":
    AppSite().run()
