"""Render Jinja2 templates into docs/ for GitHub Pages."""

from __future__ import annotations

import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"
DOCS_DIR = ROOT / "docs"


def build() -> None:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    templates = sorted(TEMPLATES_DIR.rglob("*.html.jinja"))
    rendered = 0

    for tmpl_path in templates:
        if tmpl_path.name.startswith("_"):
            continue

        rel = tmpl_path.relative_to(TEMPLATES_DIR)
        out_name = str(rel).replace(".html.jinja", ".html")
        out_path = DOCS_DIR / out_name

        template = env.get_template(str(rel))
        html = template.render()

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html)
        rendered += 1
        print(f"  {rel} -> docs/{out_name}")

    print(f"\nRendered {rendered} templates into docs/")


if __name__ == "__main__":
    try:
        build()
    except Exception as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        sys.exit(1)
