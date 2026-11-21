"""Build-time guards for the static site under docs/.

These catch the two classes of failure that are invisible to Python tests but
break the published page: JavaScript that does not parse, and internal links
that point nowhere. Both have shipped to production before.
"""

import importlib.util
import re
import shutil
from collections.abc import Iterator
from html.parser import HTMLParser
from pathlib import Path

import esprima
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent

_spec = importlib.util.spec_from_file_location("site_build", ROOT / "scripts" / "build.py")
site_build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(site_build)


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    """Assemble what actually deploys: rendered templates plus committed static assets.

    build.py only renders templates; docs/assets/ is checked in by hand and is not
    regenerated, so it has to be copied in for links to resolve the way they do in
    the published artifact.
    """
    out = tmp_path_factory.mktemp("site")
    site_build.build(out_dir=out)
    shutil.copytree(ROOT / "docs" / "assets", out / "assets")
    return out


def _pages(site: Path) -> list[Path]:
    return sorted(site.rglob("*.html"))


def _page_id(path: Path, site: Path) -> str:
    return str(path.relative_to(site))


# ──────────────────────────── JavaScript ────────────────────────────


class _ScriptExtractor(HTMLParser):
    """Collect the body of every inline <script> (i.e. those without src=)."""

    def __init__(self) -> None:
        super().__init__()
        self.scripts = []
        self._inline = False

    def handle_starttag(self, tag, attrs) -> None:
        if tag == "script":
            self._inline = not any(k == "src" for k, _ in attrs)

    def handle_endtag(self, tag) -> None:
        if tag == "script":
            self._inline = False

    def handle_data(self, data) -> None:
        if self._inline and data.strip():
            self.scripts.append(data)


def _inline_scripts(html: str) -> list[str]:
    parser = _ScriptExtractor()
    parser.feed(html)
    return parser.scripts


def _declared_names(node) -> Iterator[str]:
    """Yield the identifier names bound by a declarator target (incl. patterns)."""
    if not isinstance(node, dict):
        return
    kind = node.get("type")
    if kind == "Identifier":
        yield node["name"]
    elif kind == "ObjectPattern":
        for prop in node.get("properties") or []:
            yield from _declared_names(prop.get("value") or prop.get("argument"))
    elif kind == "ArrayPattern":
        for element in node.get("elements") or []:
            yield from _declared_names(element)
    elif kind in ("AssignmentPattern", "RestElement", "Property"):
        yield from _declared_names(node.get("left") or node.get("argument") or node.get("value"))


def _statement_lists(node) -> Iterator[list]:
    """Yield every list of statements that forms its own lexical scope."""
    if isinstance(node, dict):
        if node.get("type") in ("Program", "BlockStatement") and isinstance(node.get("body"), list):
            yield node["body"]
        if node.get("type") == "SwitchCase" and isinstance(node.get("consequent"), list):
            yield node["consequent"]
        for value in node.values():
            yield from _statement_lists(value)
    elif isinstance(node, list):
        for item in node:
            yield from _statement_lists(item)


def _duplicate_lexical_declarations(js: str) -> list[tuple[str, int, int]]:
    """Find let/const names declared twice in one scope.

    This is an ECMAScript *early error*: the whole script fails to parse, so a
    single duplicate silently disables every handler on the page. esprima-python
    parses such code happily, so the check has to walk the AST itself.
    """
    tree = esprima.parseScript(js, options={"loc": True}).toDict()
    duplicates = []
    for statements in _statement_lists(tree):
        seen = {}
        for statement in statements:
            if statement.get("type") != "VariableDeclaration":
                continue
            if statement.get("kind") not in ("let", "const"):
                continue
            line = (statement.get("loc") or {}).get("start", {}).get("line")
            for declarator in statement.get("declarations") or []:
                for name in _declared_names(declarator.get("id")):
                    if name in seen:
                        duplicates.append((name, seen[name], line))
                    else:
                        seen[name] = line
    return duplicates


def test_every_page_has_inline_script(site):
    """Guard the guard: if extraction silently returns nothing, the JS tests pass vacuously."""
    for page in _pages(site):
        assert _inline_scripts(page.read_text(encoding="utf-8")), (
            f"{_page_id(page, site)} has no inline <script>; script extraction is likely broken"
        )


def test_inline_javascript_parses(site):
    """Every inline script must be syntactically valid JavaScript."""
    failures = []
    for page in _pages(site):
        for index, js in enumerate(_inline_scripts(page.read_text(encoding="utf-8"))):
            try:
                esprima.parseScript(js)
            except Exception as exc:  # noqa: BLE001 - esprima raises bare Error
                failures.append(f"{_page_id(page, site)} script #{index}: {exc}")
    assert not failures, "JavaScript syntax errors:\n  " + "\n  ".join(failures)


def test_no_duplicate_lexical_declarations(site):
    """A let/const declared twice in one scope kills the entire script block."""
    failures = []
    for page in _pages(site):
        for index, js in enumerate(_inline_scripts(page.read_text(encoding="utf-8"))):
            for name, first, second in _duplicate_lexical_declarations(js):
                failures.append(
                    f"{_page_id(page, site)} script #{index}: "
                    f"'{name}' redeclared (lines {first} and {second})"
                )
    assert not failures, "Duplicate let/const declarations:\n  " + "\n  ".join(failures)


# ──────────────────────────── Links ────────────────────────────


def test_internal_links_resolve(site):
    """Every relative href must point at a file that the build actually produces."""
    broken = []
    for page in _pages(site):
        for href in re.findall(r'href="([^"]+)"', page.read_text(encoding="utf-8")):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = (page.parent / href.split("#")[0]).resolve()
            if href.endswith("/"):
                target = target / "index.html"
            if not target.exists():
                broken.append(f"{_page_id(page, site)} -> {href}")
    assert not broken, "Broken internal links:\n  " + "\n  ".join(broken)


