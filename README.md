# Kivy Blog Builder

A desktop application built with **Python** and **Kivy** that lets you create and export blog posts as standalone HTML pages.
The app provides a simple interface to add headers, sections, text, images, quotes, and links, and generates clean, responsive HTML output.

---

## Features

* User-friendly interface with Kivy screens (`.kv` + Python UI logic).
* Modular architecture with services for:

  * HTML generation
  * Image processing
  * Security (escaping, validations)
  * Path management
* Local preview (`temp/`) with CSS/JS assets from `needs/`.
* Export mode (`exp/`) with proper Bootstrap/Clean Blog integration.
* Automatic resizing and conversion of images to optimized **WebP** format.
* Safe and append-only HTML builder with resume support.
* Separation of concerns (UI, models, services, assets).

---

## Project Structure

```
project_root/
│
├── LICENCE
├── README.md
│
├── exp/                # Final exported site
├── temp/               # Local preview (HTML + generated images)
├── needs/              # Front-end dependencies for preview
│
├── src/                # Application source code
│   ├── main.py         # Entry point
│   │
│   ├── assets/         # Fonts, icons, static files for the app
│   │   ├── fonts/
│   │   └── images/
│   │
│   ├── models/         # Application state management
│   ├── services/       # Core services (HTML, images, paths, security)
│   └── ui/             # User interface (helpers, screens, KV)
│
└── requirements.txt    # Python dependencies
```

---

## Requirements

* Python 3.9+
* [Kivy](https://kivy.org/) 2.3+
* [Pillow](https://pypi.org/project/Pillow/) for image processing

---

## Usage

1. Clone the repository:

```bash
git clone https://github.com/yan-s/kivy-blog-builder.git
cd kivy-blog-builder
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python src/main.py
```

4. Workflow:

   * Start a new project or resume an existing one.
   * Add headers, text, images, quotes, and links.
   * Preview the post in `temp/post.html`.
   * Export the final version to `exp/post/post.html`.

---

## Assets and Styling

* Local preview (`temp/`) uses assets from `needs/`.
* Exported HTML (`exp/`) links to Bootstrap 3.3.7 and Clean Blog theme files.
* Images are resized and stored under:

  * `temp/img/`
  * `exp/img/head_p/`
  * `exp/img/post/`
