# -*- coding: utf-8 -*-
"""Application paths and directories helpers."""

from __future__ import annotations
import os
from dataclasses import dataclass

def _project_root_from_services() -> str:
    # .../src/services/paths.py -> .../src -> .../
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

@dataclass(frozen=True)
class AppPaths:
    """Centralize all absolute paths from the project root (parent of src)."""
    root_dir: str = _project_root_from_services()

    # Top-level siblings of src
    temp_dir: str = os.path.join(_project_root_from_services(), "temp")
    exp_dir: str  = os.path.join(_project_root_from_services(), "exp")
    needs_dir: str = os.path.join(_project_root_from_services(), "needs")

    # Subfolders we actually write to
    temp_img_dir: str = os.path.join(_project_root_from_services(), "temp", "img")

    exp_post_dir: str = os.path.join(_project_root_from_services(), "exp", "post")
    exp_img_head: str = os.path.join(_project_root_from_services(), "exp", "img", "head_p")
    exp_img_post: str = os.path.join(_project_root_from_services(), "exp", "img", "post")
    exp_img_item: str = os.path.join(_project_root_from_services(), "exp", "img", "item")

@dataclass(frozen=True)
class AppAssets:
    """All CSS/JS paths as they must appear inside the HTML (RELATIVE to the HTML file)."""
    # Exported HTML lives in exp/post/post.html  -> use ../ to go to exp/
    css_bootstrap_exp: str = "../css/post/bootstrap.min.css"
    css_clean_blog_exp: str = "../css/post/clean-blog.min.css"
    js_jquery_exp: str = "../js/jquery/jquery.min.js"
    js_bootstrap_exp: str = "../js/bootstrap_v3.3.7.min.js"
    js_clean_blog_exp: str = "../js/clean-blog.min.js"

    # Temp HTML lives in temp/post.html -> siblings with needs/
    css_bootstrap_temp: str = "../needs/bootstrap.min.css"
    css_clean_blog_temp: str = "../needs/clean-blog.min.css"
    # (JS côté temp : on pointe vers needs/ si tu as copié les fichiers JS dedans)
    js_bootstrap_temp: str = "../needs/bootstrap.min.js"
    js_clean_blog_temp: str = "../needs/clean-blog.min.js"

def ensure_dirs(p: AppPaths) -> None:
    """Ensure folders exist; create them if missing."""
    for d in [
        p.temp_dir, p.temp_img_dir,
        p.exp_dir, p.exp_post_dir,
        p.exp_img_head, p.exp_img_post, p.exp_img_item
    ]:
        os.makedirs(d, exist_ok=True)
