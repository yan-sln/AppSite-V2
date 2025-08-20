# -*- coding: utf-8 -*-
"""UI helpers for feedback (reduced: only error and important info)."""

from kivy.uix.label import Label
from kivy.uix.popup import Popup


def _popup(title: str, text: str):
    popup = Popup(
        title=title,
        title_align='left',
        title_size='18sp',
        content=Label(text=text, halign='center', valign='top'),
        size_hint=(.75, .35),
    )
    popup.open()


def show_error(text: str):
    """Use for errors or blocking issues."""
    _popup("Error", text)


def show_info(text: str):
    """Use for important user-visible milestones (e.g., export done)."""
    _popup("Info", text)
