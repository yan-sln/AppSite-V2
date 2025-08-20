# -*- coding: utf-8 -*-
"""
Image handling for header and in-article images.

- Reads a source image (jpg/jpeg/png/webp), validates it, and produces WEBP outputs.
- Header image is saved to:
    - temp: temp/img/<unique>.webp          (for local preview from temp/post.html)
    - exp : exp/img/head_p/<unique>.webp    (for exported HTML at exp/post/post.html)
- Body image is saved to:
    - temp: temp/img/<unique>.webp
    - exp : exp/img/post/<unique>.webp

Returns for each operation:
    (abs_export_path, temp_rel_path, exp_rel_path)

Where:
    - abs_export_path  : absolute path to the exported WEBP (under exp/img/...)
    - temp_rel_path    : relative path to be used from temp/post.html
                         (e.g. "img/<file>.webp")
    - exp_rel_path     : relative path to be used from exp/post/post.html
                         (e.g. "../img/head_p/<file>.webp" or "../img/post/<file>.webp")
"""

from __future__ import annotations

import io
import os
import time
import uuid
from dataclasses import dataclass
from typing import Tuple

from PIL import Image, UnidentifiedImageError

from .paths import AppPaths, ensure_dirs


# -------- helpers / guards ---------------------------------------------------

def _secure_unique_name(prefix: str = "") -> str:
    """Generate a collision-resistant file stem."""
    return f"{prefix}{int(time.time() * 1e6)}_{uuid.uuid4().hex}"


def _is_image(path: str) -> bool:
    """Quick extension check (we still decode to be sure)."""
    return os.path.splitext(path.lower())[1] in {".jpg", ".jpeg", ".png", ".webp"}


def _open_image_safe(path: str) -> Image.Image:
    """Load image from disk with clear error messages."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Image not found: {path}")
    if not _is_image(path):
        raise ValueError("Unsupported extension (allowed: .jpg, .jpeg, .png, .webp).")
    try:
        with open(path, "rb") as f:
            data = f.read()
        im = Image.open(io.BytesIO(data))
        im.load()  # force decoding now
        return im
    except UnidentifiedImageError as e:
        raise ValueError("Invalid image file.") from e


# Pillow 10 moved resampling filters to Image.Resampling
try:
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS  # type: ignore[attr-defined]
except Exception:  # Pillow < 10
    RESAMPLE_LANCZOS = Image.LANCZOS


# -------- service ------------------------------------------------------------

@dataclass
class ImageService:
    """Deal with image inputs and produce WEBP assets for temp/export."""
    paths: AppPaths

    def __post_init__(self) -> None:
        # Ensure directories exist right away (also re-checked at write time)
        ensure_dirs(self.paths)

    # ---- internal IO helpers ----
    def _save_webp(self, img: Image.Image, out_path: str, size: Tuple[int, int]) -> None:
        """
        Save a resized WEBP derivative to out_path (RGB).
        Parent folders are created if missing.
        """
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        # Avoid mutating the original Image object
        canvas = img.copy().convert("RGB")
        # Resize while preserving aspect ratio by fitting into the target box
        canvas = canvas.resize(size, RESAMPLE_LANCZOS)
        canvas.save(out_path, "WEBP", method=6, quality=90)

    # ---- public API ----
    def generate_header_assets(self, source_path: str) -> Tuple[str, str, str]:
        """
        Produce header hero WEBP in temp/img and exp/img/head_p.

        Returns:
            abs_export_path: absolute path to exp/img/head_p/<file>.webp
            temp_rel      : "img/<file>.webp"      (from temp/post.html)
            exp_rel       : "../img/head_p/<file>.webp" (from exp/post/post.html)
        """
        img = _open_image_safe(source_path)
        file_stem = _secure_unique_name("head_")

        # Output absolute paths
        temp_header_abs = os.path.join(self.paths.temp_img_dir, f"{file_stem}.webp")
        exp_header_abs  = os.path.join(self.paths.exp_img_head, f"{file_stem}.webp")

        # Write derivatives
        self._save_webp(img, temp_header_abs, (1900, 800))
        self._save_webp(img, exp_header_abs,  (1900, 800))

        # Relative paths as consumed by the two HTML locations
        temp_rel = f"img/{os.path.basename(temp_header_abs)}"          # from temp/post.html
        exp_rel  = f"../img/head_p/{os.path.basename(exp_header_abs)}" # from exp/post/post.html

        return exp_header_abs, temp_rel, exp_rel

    def generate_post_image(self, source_path: str) -> Tuple[str, str, str]:
        """
        Produce in-article image WEBP in temp/img and exp/img/post.

        Returns:
            abs_export_path: absolute path to exp/img/post/<file>.webp
            temp_rel      : "img/<file>.webp"      (from temp/post.html)
            exp_rel       : "../img/post/<file>.webp" (from exp/post/post.html)
        """
        img = _open_image_safe(source_path)

        # Basic safety: enforce minimum size before downscale
        w, h = img.size
        if w < 778 or h < 514:
            raise ValueError(f"Image too small for article body (min 778x514). Got {w}x{h}.")

        file_stem = _secure_unique_name("img_")

        # Output absolute paths
        temp_body_abs = os.path.join(self.paths.temp_img_dir, f"{file_stem}.webp")
        exp_body_abs  = os.path.join(self.paths.exp_img_post, f"{file_stem}.webp")

        # Write derivatives
        self._save_webp(img, temp_body_abs, (778, 514))
        self._save_webp(img, exp_body_abs,  (778, 514))

        # Relative paths as consumed by the two HTML locations
        temp_rel = f"img/{os.path.basename(temp_body_abs)}"         # from temp/post.html
        exp_rel  = f"../img/post/{os.path.basename(exp_body_abs)}"  # from exp/post/post.html

        return exp_body_abs, temp_rel, exp_rel
