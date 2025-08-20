# -*- coding: utf-8 -*-
"""
Kivy screen controllers only (UI logic).
- No file IO or HTML logic here (delegated to services).
- Minimal popups (errors + important info).
"""

from __future__ import annotations

import os
from time import strftime

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App

from ui.helpers import show_error, show_info
from services.cleanup import clean_temp


class WindowManager(ScreenManager):
    """Referenced by KV as root manager."""
    pass


class StartWindow(Screen):
    name = "Start"

    def entry(self, val: int):
        """
        Compatibility stub: some KV may still call entry().
        We keep it as no-op setter to avoid KV breakage.
        """
        app = App.get_running_app()
        try:
            app.state.screen_entry = int(val)
        except Exception:
            app.state.screen_entry = 1

    def start(self):
        """
        Start flow:
        - If temp/post.html AND exp/post/post.html exist -> resume project (-> Menu).
        - Else -> force header creation (-> FileChooser).
        """
        app = App.get_running_app()
        temp_html = os.path.join(app.paths.temp_dir, "post.html")
        exp_html = os.path.join(app.paths.exp_post_dir, "post.html")

        # Ensure dirs exist
        from services.paths import ensure_dirs
        ensure_dirs(app.paths)

        if os.path.exists(temp_html) and os.path.exists(exp_html):
            # Resume existing project: inform HtmlBuilder about current files
            try:
                app.html.resume_post(temp_html, exp_html)
            except Exception as e:
                show_error(f"Impossible de reprendre le projet: {e}")
                return
            app.state.post_started = True
            self.manager.current = 'Menu'
            self.manager.transition.direction = "up"
        else:
            # New project: reset transient state then go choose header image
            app.state.screen_entry = 1
            app.state.selected_file = ""
            app.state.post_started = False
            self.manager.current = 'FileChooser'
            self.manager.transition.direction = "up"


class HeaderWindow(Screen):
    name = "Header"

    def HEADinputProcess(self):
        """Create the post header from user inputs and selected image."""
        app = App.get_running_app()
        ids = self.ids

        page_title = ids.HEAD_input_a.text.strip()
        article_title = ids.HEAD_input_b.text.strip()
        subtitle = ids.HEAD_input_c.text.strip()
        author = ids.HEAD_input_d.text.strip()

        if not (page_title and article_title and subtitle and author):
            show_error("Entrez toutes les données (titre, sous-titre, auteur).")
            return
        if not app.state.selected_file:
            show_error("Sélectionnez d'abord une image pour le header.")
            return

        try:
            _, temp_header_rel, exp_header_rel = app.images.generate_header_assets(app.state.selected_file)
            date_str = strftime('%d/%m/%y')
            app.html.start_post(
                page_title=page_title,
                title=article_title,
                subtitle=subtitle,
                author=author,
                date_str=date_str,
                header_img_temp_rel=temp_header_rel,
                header_img_exp_rel=exp_header_rel,
            )
        except Exception as e:
            show_error(f"Erreur lors de la création du header: {e}")
            return

        # Reset inputs and mark post as started
        ids.HEAD_input_a.text = ""
        ids.HEAD_input_b.text = ""
        ids.HEAD_input_c.text = ""
        ids.HEAD_input_d.text = ""
        app.state.post_started = True

        self.manager.current = 'Menu'
        self.manager.transition.direction = "up"


class MenuWindow(Screen):
    name = "Menu"

    def add_image(self):
        """
        Navigate to FileChooser to select an image for content insertion.
        We store a sentinel in state.screen_entry (any non-1 value).
        """
        app = App.get_running_app()
        app.state.screen_entry = 245
        self.manager.current = "FileChooser"
        self.manager.transition.direction = "left"

    def entry(self, val: int):
        """Legacy KV compatibility; prefer add_image()."""
        app = App.get_running_app()
        try:
            app.state.screen_entry = int(val)
        except Exception:
            app.state.screen_entry = 245


class ShowWindow(Screen):
    name = "Show"

    def show(self):
        """Preview the current project (pywebview if available, else browser)."""
        app = App.get_running_app()
        temp_html = os.path.join(app.paths.temp_dir, "post.html")
        if not os.path.exists(temp_html):
            show_error("Aucun article en cours. Crée d'abord un en-tête.")
            return

        try:
            # Prefer integrated preview if pywebview is installed
            import webview  # type: ignore
            webview.create_window("Aperçu - Article", f"file://{os.path.abspath(temp_html)}", width=900, height=700)
            webview.start()
        except Exception:
            # Fallback to system browser
            try:
                app.html.open_preview(temp_html)
            except Exception as e:
                show_error(f"Impossible d'ouvrir l'aperçu: {e}")


class ExportWindow(Screen):
    name = "Export"

    def thisIstheeEnd(self):
        """Finalize the HTML and clean temp/."""
        app = App.get_running_app()
        try:
            app.html.end_post()
        except Exception as e:
            show_error(f"Erreur lors de la finalisation: {e}")
            return

        # Optional cleanup: temp folder only
        try:
            clean_temp(app.paths)
        except Exception:
            pass

        app.state.post_started = False
        show_info("Export terminé. Fichier: exp/post/post.html")

        self.manager.current = 'Start'
        self.manager.transition.direction = "up"


class FCWindow(Screen):
    name = "FileChooser"

    def load(self, path, filename):
        """
        FileChooser callback. Stores selection then routes to the right screen:
        - If screen_entry == 1: we are in header flow -> Header screen
        - Else: we add an image -> Img screen
        """
        app = App.get_running_app()
        selected = ""

        # filename can be a list/tuple or a string depending on the widget
        if isinstance(filename, (list, tuple)):
            selected = filename[0] if filename else ""
        else:
            selected = str(filename) if filename else ""

        if not selected:
            show_error("Sélectionnez un fichier.")
            return

        app.state.selected_file = os.path.join(path, os.path.basename(selected))

        if app.state.screen_entry == 1:
            self.manager.current = 'Header'
            self.manager.transition.direction = "up"
        else:
            self.manager.current = 'Img'
            self.manager.transition.direction = "left"

    def cancelScreen(self):
        """Cancel: back to Start (header flow) or Menu (content flow)."""
        app = App.get_running_app()
        if app.state.screen_entry == 1:
            # New project cancelled: wipe temp and return to Start
            try:
                clean_temp(app.paths)
            except Exception:
                pass
            self.manager.current = 'Start'
            self.manager.transition.direction = "down"
        else:
            self.manager.current = 'Menu'
            self.manager.transition.direction = "right"


class TDPWindow(Screen):
    name = "TDP"

    def TDPinputProcess(self):
        app = App.get_running_app()
        text = self.ids.tdp_input.text.strip()
        if not text:
            show_error("Entrez un titre de section.")
            return
        if not app.state.post_started:
            show_error("Crée d'abord un en-tête.")
            return
        try:
            app.html.add_section_heading(text)
        except Exception as e:
            show_error(f"Erreur HTML: {e}")
            return
        self.ids.tdp_input.text = ""
        self.manager.current = 'Menu'
        self.manager.transition.direction = "left"


class TxtWindow(Screen):
    name = "Texte"

    def TXTinputProcess(self):
        app = App.get_running_app()
        text = self.ids.txt_input.text
        if not text:
            show_error("Entrez du texte.")
            return
        if not app.state.post_started:
            show_error("Crée d'abord un en-tête.")
            return
        try:
            app.html.add_paragraph(text)
        except Exception as e:
            show_error(f"Erreur HTML: {e}")
            return
        self.ids.txt_input.text = ""
        self.manager.current = 'Menu'
        self.manager.transition.direction = "left"


class ImgWindow(Screen):
    name = "Img"

    def IMGinputProcess(self):
        app = App.get_running_app()
        if not app.state.selected_file:
            show_error("Sélectionnez d'abord une image.")
            return

        alt = self.ids.IMG_input_c.text.strip()
        caption = self.ids.IMG_input_l.text.strip()
        if not (alt and caption):
            show_error("Entrez texte alternatif et légende.")
            return

        try:
            _, temp_rel, exp_rel = app.images.generate_post_image(app.state.selected_file)
            app.html.add_image(temp_rel, exp_rel, alt, caption)
        except Exception as e:
            show_error(f"Erreur image/HTML: {e}")
            return

        self.ids.IMG_input_c.text = ""
        self.ids.IMG_input_l.text = ""
        app.state.selected_file = ""

        self.manager.current = 'Menu'
        self.manager.transition.direction = "left"


class QuoteWindow(Screen):
    name = "Quote"

    def QUOTEinputProcess(self):
        app = App.get_running_app()
        text = self.ids.QUOTE_input.text
        if not text:
            show_error("Entrez une citation.")
            return
        if not app.state.post_started:
            show_error("Crée d'abord un en-tête.")
            return
        try:
            app.html.add_quote(text)
        except Exception as e:
            show_error(f"Erreur HTML: {e}")
            return
        self.ids.QUOTE_input.text = ""
        self.manager.current = 'Menu'
        self.manager.transition.direction = "left"


class LinkWindow(Screen):
    name = "Link"

    def LINKinputProcess(self):
        """
        Placeholder for link insertion (not implemented yet).
        Captures 4 inputs then returns to Menu without modifying HTML.
        """
        ids = self.ids
        a = ids.LINK_input_a.text.strip()
        b = ids.LINK_input_b.text.strip()
        c = ids.LINK_input_c.text.strip()
        d = ids.LINK_input_d.text.strip()
        if not (a and b and c and d):
            show_error("Entrez toutes les données du lien.")
            return
        ids.LINK_input_a.text = ""
        ids.LINK_input_b.text = ""
        ids.LINK_input_c.text = ""
        ids.LINK_input_d.text = ""
        self.manager.current = 'Menu'
        self.manager.transition.direction = "left"
