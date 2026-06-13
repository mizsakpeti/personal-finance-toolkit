"""Render Jinja2 templates into docs/ for GitHub Pages."""

from __future__ import annotations

import sys
from pathlib import Path
import logging

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"
DOCS_DIR = ROOT / "docs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


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

        template = env.get_template(rel.as_posix())
        html = template.render()

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        rendered += 1
        logger.info("  %s -> docs/%s", rel, out_name)

    logger.info("  %s templates rendered into docs/", rendered)


if __name__ == "__main__":
    try:
        build()
    except Exception as exc:
        logger.exception("Build failed: %s", exc)
        sys.exit(1)
