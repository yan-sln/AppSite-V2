# -*- coding: utf-8 -*-
"""
Robust, append-only HTML builder with 'resume' support.
- Writes to both temp/ and exp/post/ in parallel.
- Escapes all user-provided content.
- Resolves CSS/JS href/src relatively from the HTML file to the project root.
"""

from __future__ import annotations
import os
import webbrowser
from html import escape as esc
from typing import Optional

from .paths import AppPaths, AppAssets, ensure_dirs

class HtmlBuilder:
    def __init__(self, paths: AppPaths, assets: AppAssets, site_title: str = "Site"):
        self.p = paths
        self.a = assets
        ensure_dirs(self.p)
        self.site_title = site_title
        self._post_started = False
        self._temp_path: Optional[str] = None
        self._exp_path: Optional[str] = None

    # -------------------
    # Lifecycle
    # -------------------
    def start_post(
        self,
        *,
        page_title: str,
        title: str,
        subtitle: str,
        author: str,
        date_str: str,
        header_img_temp_rel: str,
        header_img_exp_rel: str,
    ) -> None:
        """Create temp/post.html and exp/post/post.html with Clean Blog header."""
        temp_html = os.path.join(self.p.temp_dir, "post.html")
        exp_html  = os.path.join(self.p.exp_post_dir, "post.html")

        head_tpl = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{site} - {page}</title>
  <link href="{bootstrap_css}" rel="stylesheet">
  <link href="{clean_blog_css}" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css?family=Lora:400,700,400italic,700italic" rel="stylesheet" type="text/css">
</head>
<body>
  <nav class="navbar navbar-default navbar-custom navbar-fixed-top">
    <div class="container-fluid">
      <div class="navbar-header page-scroll">
        <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
          <span class="sr-only">Basculer la navigation</span>
          Menu <i class="fa fa-bars"></i>
        </button>
        <a class="navbar-brand" href="./index">&lt; Précédent</a>
        <a class="navbar-brand" href="./index">Suivant &gt;</a>
      </div>
      <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
        <ul class="nav navbar-nav navbar-right">
          <li><a href="./index">Home</a></li>
          <li><a href="./contact">Contact</a></li>
        </ul>
      </div>
    </div>
  </nav>
  <header class="intro-header" style="background-image: url('{header_img}')">
    <div class="container">
      <div class="row">
        <div class="col-lg-8 col-lg-offset-2 col-md-10 col-md-offset-1">
          <div class="post-heading">
            <h1>{title}</h1>
            <h2 class="subheading">{subtitle}</h2>
            <span class="meta">Post par <a href="#">{author}</a> le {date}</span>
          </div>
        </div>
      </div>
    </div>
  </header>
  <article>
    <div class="container">
      <div class="row">
        <div class="col-lg-8 col-lg-offset-2 col-md-10 col-md-offset-1">
"""

        head_temp = head_tpl.format(
            site=esc(self.site_title), page=esc(page_title),
            bootstrap_css=self.a.css_bootstrap_temp,
            clean_blog_css=self.a.css_clean_blog_temp,
            header_img=esc(header_img_temp_rel),
            title=esc(title), subtitle=esc(subtitle),
            author=esc(author), date=esc(date_str),
        )
        head_exp = head_tpl.format(
            site=esc(self.site_title), page=esc(page_title),
            bootstrap_css=self.a.css_bootstrap_exp,
            clean_blog_css=self.a.css_clean_blog_exp,
            header_img=esc(header_img_exp_rel),
            title=esc(title), subtitle=esc(subtitle),
            author=esc(author), date=esc(date_str),
        )

        self._write(temp_html, head_temp, mode="w")
        self._write(exp_html,  head_exp,  mode="w")

        self._temp_path = temp_html
        self._exp_path  = exp_html
        self._post_started = True

    def resume_post(self, temp_path: str, exp_path: str) -> None:
        if not (os.path.exists(temp_path) and os.path.exists(exp_path)):
            raise FileNotFoundError("Impossible de reprendre : fichiers HTML manquants.")
        self._temp_path = temp_path
        self._exp_path  = exp_path
        self._post_started = True

    def end_post(self) -> None:
        tail_tpl = """
        </div>
      </div>
    </div>
  </article>
  <hr>
  <footer>
    <div class="container">
      <div class="row">
        <div class="col-lg-8 col-lg-offset-2 col-md-10 col-md-offset-1">
          <ul class="list-inline text-center">
            <li><a href="#"><span class="fa-stack fa-lg"><i class="fa fa-circle fa-stack-2x"></i><i class="fa fa-twitter fa-stack-1x fa-inverse"></i></span></a></li>
            <li><a href="#"><span class="fa-stack fa-lg"><i class="fa fa-circle fa-stack-2x"></i><i class="fa fa-facebook fa-stack-1x fa-inverse"></i></span></a></li>
            <li><a href="#"><span class="fa-stack fa-lg"><i class="fa fa-circle fa-stack-2x"></i><i class="fa fa-github fa-stack-1x fa-inverse"></i></span></a></li>
          </ul>
          <p class="copyright text-muted">Copyright &copy; {site}</p>
        </div>
      </div>
    </div>
  </footer>
  {scripts}
</body>
</html>
""".strip()

        scripts_exp = f"""
<script src="{self.a.js_jquery_exp}"></script>
<script src="{self.a.js_bootstrap_exp}"></script>
<script src="{self.a.js_clean_blog_exp}"></script>""".rstrip()

        # Côté temp : si tu as copié les .js dans needs/, ces tags marcheront en local
        scripts_temp = f"""
<script src="{self.a.js_bootstrap_temp}"></script>
<script src="{self.a.js_clean_blog_temp}"></script>""".rstrip()

        tail_temp = tail_tpl.format(site=esc(self.site_title), scripts=scripts_temp)
        tail_exp  = tail_tpl.format(site=esc(self.site_title), scripts=scripts_exp)
        self._append_pair(tail_temp, tail_exp)

    # -------------------
    # Content helpers
    # -------------------
    def add_section_heading(self, text: str) -> None:
        self._append_both(f'\n<h2 class="section-heading">{esc(text)}</h2>\n')

    def add_paragraph(self, text: str) -> None:
        safe = esc(text).replace("\n", "<br>\n")
        self._append_both(f"\n<p>{safe}</p>\n")

    def add_image(self, img_temp_rel: str, img_exp_rel: str, alt: str, caption: str) -> None:
        tpl = """\n<a href="#"><img class="img-responsive" src="{src}" alt="{alt}"></a>
<span class="caption text-muted">{caption}</span>\n"""
        temp_html = tpl.replace("{src}", esc(img_temp_rel)).replace("{alt}", esc(alt)).replace("{caption}", esc(caption))
        exp_html  = tpl.replace("{src}", esc(img_exp_rel)).replace("{alt}", esc(alt)).replace("{caption}", esc(caption))
        self._append_pair(temp_html, exp_html)

    def add_quote(self, text: str) -> None:
        self._append_both(f'\n<blockquote>{esc(text)}</blockquote>\n')

    # -------------------
    # Utilities
    # -------------------
    @staticmethod
    def open_preview(html_path: str) -> None:
        webbrowser.open_new_tab(f"file://{os.path.abspath(html_path)}")

    def _write(self, path: str, content: str, mode: str = "a") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode, encoding="utf-8") as f:
            f.write(content)

    def _append_both(self, html_snippet: str) -> None:
        if not self._post_started or not self._temp_path or not self._exp_path:
            raise RuntimeError("Post has not been started yet.")
        self._write(self._temp_path, html_snippet, mode="a")
        self._write(self._exp_path,  html_snippet, mode="a")

    def _append_pair(self, temp_snippet: str, exp_snippet: str) -> None:
        if not self._post_started or not self._temp_path or not self._exp_path:
            raise RuntimeError("Post has not been started yet.")
        self._write(self._temp_path, temp_snippet, mode="a")
        self._write(self._exp_path,  exp_snippet, mode="a")
