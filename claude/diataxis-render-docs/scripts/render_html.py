#!/usr/bin/env python3
"""Render Diataxis Markdown pages as self-contained, interactive HTML.

Two outputs, one template. The script render, the default, writes every page
of a tree (or one page) into a build directory that git must already ignore:
byte-reproducible, LF-only, and free of model tokens, so it is regenerated
rather than committed. The hybrid render (`--slots`) writes each page beside
its Markdown, with empty marked slots for a model to fill and the source's
fingerprint embedded, so `check` can report when the Markdown has moved on.

Every page carries a table of contents, collapsible sections, copy buttons on
code, light and dark themes, navigation across the four page types, and a
search index embedded inline, so a page opened from disk fetches nothing.

    render_html.py render <docs-root-or-page> [--root DIR] [--out DIR]
    render_html.py render --slots <docs-root-or-page> [--root DIR]
    render_html.py check <docs-root>

Exit 0 on success, 1 when `check` finds a failing hybrid page, 2 on a refusal
(a build directory git does not ignore, a path that is not Markdown). It never
edits the Markdown or `.gitignore`.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

from check_coverage import (
    fingerprint,
    frontmatter_end,
    markdown_headings,
    rendered_heading_text,
    section_id,
)


TYPES = (
    ("tutorial", "Tutorials", {"tutorial", "tutorials"}),
    ("how-to", "How-to guides", {"how-to", "how-tos", "howto", "howtos", "guides"}),
    ("reference", "Reference", {"reference", "references"}),
    ("explanation", "Explanation", {"explanation", "explanations", "concepts"}),
)
OTHER = ("other", "Other pages")
DEFAULT_OUT = "build/docs-html"
FINGERPRINT_META = "diataxis-source-fingerprint"
SEARCH_TEXT_LIMIT = 4000

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*([^`\s]*)")
ATX = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
SETEXT = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
RULE = re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")
ITEM = re.compile(r"^( {0,3})([-*+]|\d{1,9}[.)])[ \t]+(.*)$")
TABLE_RULE = re.compile(r"^ {0,3}\|?[ \t]*:?-+:?[ \t]*(\|[ \t]*:?-+:?[ \t]*)*\|?[ \t]*$")
SCHEME = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//)")
REMOTE = re.compile(r"^\s*(?:https?:)?//", re.IGNORECASE)


@dataclass
class Page:
    source: Path
    relative: Path
    kind: str
    title: str = ""
    body: str = ""
    toc: list[tuple[int, str, str]] = field(default_factory=list)
    headings: list[str] = field(default_factory=list)
    text: str = ""


def classify(relative: Path) -> str:
    for part in [*relative.parent.parts, relative.stem]:
        for kind, _, names in TYPES:
            if part.lower() in names:
                return kind
    return OTHER[0]


def posix_relpath(target: Path, start: Path) -> str:
    return Path(os.path.relpath(target, start)).as_posix()


# --- Markdown to HTML -----------------------------------------------------------


class Converter:
    """A small, strict Markdown converter: blocks, then inline spans."""

    def __init__(self, resolve) -> None:
        self.resolve = resolve
        self.toc: list[tuple[int, str, str]] = []
        self.headings: list[str] = []
        self.title = ""
        self.occurrences: dict[str, int] = {}

    def inline(self, text: str) -> str:
        held: list[str] = []

        def hold(value: str) -> str:
            held.append(value)
            return f"\x00{len(held) - 1}\x00"

        text = re.sub(r"(`+)(.+?)\1", lambda m: hold(
            f"<code>{html.escape(m.group(2).strip(), quote=False)}</code>"), text)
        # A comment is left out, as a Markdown viewer leaves it out; never shown as text.
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
        text = re.sub(r"<((?:https?|mailto):[^>\s]+)>", lambda m: hold(
            self.anchor(m.group(1), html.escape(m.group(1), quote=False))), text)
        text = html.escape(text, quote=True)
        text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+&quot;.*?&quot;)?\)",
                      lambda m: hold(self.image(m.group(1), html.unescape(m.group(2)))), text)
        text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+&quot;.*?&quot;)?\)",
                      lambda m: self.anchor(html.unescape(m.group(2)), m.group(1)), text)
        text = re.sub(r"(\*\*|__)(?=\S)(.+?)(?<=\S)\1", r"<strong>\2</strong>", text)
        text = re.sub(r"(?<![\w*])\*(?=\S)(.+?)(?<=\S)\*(?![\w*])", r"<em>\1</em>", text)
        text = re.sub(r"(?<![\w_])_(?=\S)(.+?)(?<=\S)_(?![\w_])", r"<em>\1</em>", text)
        return re.sub(r"\x00(\d+)\x00", lambda m: held[int(m.group(1))], text)

    def anchor(self, url: str, label: str) -> str:
        if SCHEME.match(url) and not re.match(r"^(?:https?|mailto):", url, re.IGNORECASE):
            if not url.startswith("//"):
                return label
        return f'<a href="{html.escape(self.resolve(url), quote=True)}">{label}</a>'

    def image(self, alt: str, url: str) -> str:
        escaped = html.escape(alt, quote=True)
        if SCHEME.match(url):
            # Kept as a link: loading a remote image is a network fetch.
            return f'<a class="image-link" href="{html.escape(url, quote=True)}">{escaped or url}</a>'
        return f'<img src="{html.escape(self.resolve(url), quote=True)}" alt="{escaped}">'

    def heading(self, level: int, title: str) -> str:
        base = section_id(rendered_heading_text(title))
        count = self.occurrences.get(base, 0)
        self.occurrences[base] = count + 1
        anchor = base if count == 0 else f"{base}-{count}"
        content = self.inline(title)
        self.headings.append(title)
        if level == 1 and not self.title:
            self.title = re.sub(r"<[^>]+>", "", content)
        elif level in (2, 3):
            self.toc.append((level, anchor, content))
        return f'<h{level} id="{anchor}">{content}</h{level}>'

    def blocks(self, lines: list[str], in_item: bool = False) -> list[tuple[int, str]]:
        """Return (heading level or 0, html) per block.

        Inside a list item (`in_item`), a nested list may start straight after the
        item's text, so a list line ends the paragraph there rather than joining it.
        """
        out: list[tuple[int, str]] = []
        paragraph: list[str] = []
        index = 0

        def flush() -> None:
            if paragraph:
                out.append((0, f"<p>{self.inline(' '.join(s.strip() for s in paragraph))}</p>"))
                paragraph.clear()

        while index < len(lines):
            line = lines[index]
            fence = FENCE.match(line)
            if not line.strip():
                flush()
            elif line.lstrip().startswith("<!--"):
                flush()
                while "-->" not in lines[index] and index + 1 < len(lines):
                    index += 1
                tail = lines[index].split("-->", 1)[-1] if "-->" in lines[index] else ""
                if tail.strip():
                    paragraph.append(tail)  # the comment ends; the rest of its line is text
            elif fence:
                flush()
                marker, language, code = fence.group(1), fence.group(2), []
                index += 1
                while index < len(lines) and not re.match(
                        rf"^ {{0,3}}{re.escape(marker[0])}{{{len(marker)},}}[ \t]*$", lines[index]):
                    code.append(lines[index])
                    index += 1
                css = f' class="language-{html.escape(language, quote=True)}"' if language else ""
                out.append((0, f"<pre><code{css}>{html.escape(chr(10).join(code), quote=False)}"
                               "</code></pre>"))
            elif ATX.match(line):
                flush()
                match = ATX.match(line)
                title = re.sub(r"[ \t]+#+$", "", (match.group(2) or "").strip()).strip()
                level = len(match.group(1))
                out.append((level, self.heading(level, title)))
            elif paragraph and SETEXT.match(line):
                level = 1 if line.strip().startswith("=") else 2
                title = " ".join(s.strip() for s in paragraph)
                paragraph.clear()
                out.append((level, self.heading(level, title)))
            elif RULE.match(line):
                flush()
                out.append((0, "<hr>"))
            elif line.lstrip().startswith(">"):
                flush()
                quoted = []
                while index < len(lines) and lines[index].lstrip().startswith(">"):
                    quoted.append(re.sub(r"^\s*> ?", "", lines[index]))
                    index += 1
                inner = "".join(block for _, block in self.blocks(quoted))
                out.append((0, f"<blockquote>{inner}</blockquote>"))
                continue
            elif "|" in line and index + 1 < len(lines) and TABLE_RULE.match(lines[index + 1]):
                flush()
                rows = [line]
                index += 2
                while index < len(lines) and "|" in lines[index] and lines[index].strip():
                    rows.append(lines[index])
                    index += 1
                out.append((0, self.table(rows)))
                continue
            elif ITEM.match(line) and (in_item or not paragraph):
                flush()
                index = self.list_block(lines, index, out)
                continue
            else:
                paragraph.append(line)
            index += 1
        flush()
        return out

    def table(self, rows: list[str]) -> str:
        def cells(row: str) -> list[str]:
            return [cell.strip() for cell in row.strip().strip("|").split("|")]

        head = "".join(f"<th>{self.inline(cell)}</th>" for cell in cells(rows[0]))
        body = "".join(
            "<tr>" + "".join(f"<td>{self.inline(cell)}</td>" for cell in cells(row)) + "</tr>"
            for row in rows[1:]
        )
        return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"

    def list_block(self, lines: list[str], index: int, out: list[tuple[int, str]]) -> int:
        ordered = ITEM.match(lines[index]).group(2)[0].isdigit()
        items: list[list[str]] = []
        width = 0  # the open item's content indent: leading spaces, marker, spaces after

        def sibling(line: str) -> bool:
            match = ITEM.match(line)
            return bool(match) and match.group(2)[0].isdigit() == ordered

        def inside(line: str) -> bool:
            return bool(line.strip()) and len(line) - len(line.lstrip(" ")) >= width

        while index < len(lines):
            line = lines[index]
            match = ITEM.match(line)
            if items and inside(line):
                # Belongs to the open item, de-indented by exactly its content indent,
                # so an item nested under it becomes a child list.
                items[-1].append(line[width:])
            elif sibling(line):
                width = match.start(3)
                items.append([match.group(3)])
            elif line.strip() and not (
                    ATX.match(line) or FENCE.match(line) or RULE.match(line) or match):
                items[-1].append(line.lstrip())  # lazy continuation
            elif not line.strip() and index + 1 < len(lines) and (
                    inside(lines[index + 1]) or sibling(lines[index + 1])):
                items[-1].append("")
            else:
                break
            index += 1
        rendered = []
        for item in items:
            while item and not item[-1].strip():
                item.pop()
            blocks = self.blocks(item, in_item=True)
            # A tight item, with no blank line inside it, holds no paragraphs.
            tight = len(blocks) == 1 or all(line.strip() for line in item)
            content = "".join(block[3:-4] if tight and block.startswith("<p>") else block
                              for _, block in blocks)
            rendered.append(f"<li>{content}</li>")
        tag = "ol" if ordered else "ul"
        out.append((0, f"<{tag}>{''.join(rendered)}</{tag}>"))
        return index


def convert(page: Page, markdown: str, resolve, slots: bool) -> None:
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = lines[frontmatter_end(lines):]
    converter = Converter(resolve)
    parts: list[str] = []
    open_section = None
    for level, block in converter.blocks(lines):
        if level == 2:
            if open_section is not None:
                parts.append(slot(f"callouts:{open_section}") if slots else "")
                parts.append("</details>")
            open_section = re.search(r'id="([^"]+)"', block).group(1)
            parts.append(f"<details open><summary>{block}</summary>")
        else:
            parts.append(block)
            if level == 1 and slots:
                parts.append(slot("summary") + slot("diagram"))
    if open_section is not None:
        parts.append((slot(f"callouts:{open_section}") if slots else "") + "</details>")
    if slots and not converter.title:
        parts.insert(0, slot("summary") + slot("diagram"))
    page.body = "\n".join(part for part in parts if part)
    page.title = converter.title or page.relative.stem
    page.toc = converter.toc
    page.headings = converter.headings
    plain = html.unescape(re.sub(r"<[^>]+>", " ", page.body))
    page.text = " ".join(plain.split())[:SEARCH_TEXT_LIMIT]


def slot(name: str) -> str:
    return (f'<div class="slot" data-slot="{name}">\n<!-- BEGIN SLOT {name} -->\n'
            f"<!-- END SLOT {name} -->\n</div>")


# --- the page template ------------------------------------------------------------

STYLE = """
:root{--bg:#ffffff;--fg:#1d1f23;--muted:#5b6170;--line:#d9dce3;--code:#f3f4f7;--accent:#2457c5}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15171b;--fg:#e6e8ec;--muted:#a0a6b4;--line:#2e323a;--code:#1f2228;--accent:#7aa2ff}}
:root[data-theme="dark"]{--bg:#15171b;--fg:#e6e8ec;--muted:#a0a6b4;--line:#2e323a;--code:#1f2228;--accent:#7aa2ff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,sans-serif}
a{color:var(--accent)}
header{display:flex;gap:12px;align-items:center;padding:12px 16px;border-bottom:1px solid var(--line)}
header input{flex:1;max-width:420px;padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
button{cursor:pointer;border:1px solid var(--line);border-radius:6px;background:var(--code);color:var(--fg);padding:4px 10px}
.layout{display:grid;grid-template-columns:260px minmax(0,1fr);gap:24px;padding:16px;max-width:1200px;margin:0 auto}
aside{font-size:14px}
aside ul{list-style:none;padding-left:12px;margin:4px 0 12px}
.nav-title{font-weight:600;color:var(--muted);margin:8px 0 0}
#search-results{list-style:none;padding:0 16px;margin:0}
pre{position:relative;background:var(--code);padding:12px;border-radius:6px;overflow-x:auto}
pre .copy{position:absolute;top:6px;right:6px;font-size:12px}
code{background:var(--code);padding:1px 4px;border-radius:4px}
pre code{padding:0;background:none}
table{border-collapse:collapse}
th,td{border:1px solid var(--line);padding:4px 8px}
blockquote{margin:0;padding:4px 16px;border-left:4px solid var(--accent);color:var(--muted)}
summary{cursor:pointer}
summary h2{display:inline}
@media (max-width:760px){.layout{grid-template-columns:1fr}}
"""

SCRIPT = """
(function(){
var root=document.documentElement;
try{var saved=localStorage.getItem("diataxis-theme");if(saved){root.setAttribute("data-theme",saved);}}catch(e){}
document.getElementById("theme").addEventListener("click",function(){
var dark=root.getAttribute("data-theme")==="dark"||(!root.getAttribute("data-theme")&&matchMedia("(prefers-color-scheme: dark)").matches);
var next=dark?"light":"dark";root.setAttribute("data-theme",next);
try{localStorage.setItem("diataxis-theme",next);}catch(e){}
});
document.querySelectorAll("pre").forEach(function(pre){
var button=document.createElement("button");button.className="copy";button.type="button";button.textContent="Copy";
button.addEventListener("click",function(){
navigator.clipboard.writeText(pre.querySelector("code").innerText).then(function(){button.textContent="Copied";});
});
pre.appendChild(button);
});
var index=JSON.parse(document.getElementById("search-index").textContent);
var input=document.getElementById("search"),results=document.getElementById("search-results");
input.addEventListener("input",function(){
results.textContent="";
var terms=input.value.toLowerCase().split(/\\s+/).filter(Boolean);
if(!terms.length){return;}
index.filter(function(entry){
var hay=(entry.title+" "+entry.headings.join(" ")+" "+entry.text).toLowerCase();
return terms.every(function(term){return hay.indexOf(term)!==-1;});
}).slice(0,10).forEach(function(entry){
var item=document.createElement("li"),link=document.createElement("a");
link.href=entry.url;link.textContent=entry.title;item.appendChild(link);results.appendChild(item);
});
});
})();
"""

# The policy allows the template's own script and style by hash, so a page runs
# nothing a slot adds. A test pins both hashes to the text above.
SCRIPT_HASH = "sha256-/KlBwAtIbgZ40uHA/+iNh/PsKErz4+Mv6HaQr40APzM="
STYLE_HASH = "sha256-T5+8TXiGPrKueuuRaGBcWAq91D2gqFeFwOhlxUGM0p8="
POLICY = (f"default-src 'none'; script-src '{SCRIPT_HASH}'; style-src '{STYLE_HASH}'; "
          "img-src 'self' data:; base-uri 'none'; form-action 'none'")
POLICY_META = f'<meta http-equiv="Content-Security-Policy" content="{POLICY}">'

# Every template script, style and policy ever shipped, append-only: `check`
# allows each only by one of these, so a page rendered by an older version passes.
SHIPPED_SCRIPT_HASHES: tuple[str, ...] = (
    "sha256-/KlBwAtIbgZ40uHA/+iNh/PsKErz4+Mv6HaQr40APzM=",
)
SHIPPED_STYLE_HASHES: tuple[str, ...] = (
    "sha256-T5+8TXiGPrKueuuRaGBcWAq91D2gqFeFwOhlxUGM0p8=",
)
SHIPPED_POLICIES: tuple[str, ...] = (
    "default-src 'none'; script-src 'sha256-/KlBwAtIbgZ40uHA/+iNh/PsKErz4+Mv6HaQr40APzM='; "
    "style-src 'sha256-T5+8TXiGPrKueuuRaGBcWAq91D2gqFeFwOhlxUGM0p8='; "
    "img-src 'self' data:; base-uri 'none'; form-action 'none'",
)


def source_hash(text: str) -> str:
    """A policy hash source for an inline script or style's exact text."""
    return "sha256-" + base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode()


def document(page: Page, nav: str, index: list[dict], meta: str) -> str:
    toc = "".join(
        f'<li class="toc-{level}"><a href="#{anchor}">{content}</a></li>'
        for level, anchor, content in page.toc
    )
    payload = json.dumps(index, ensure_ascii=True, sort_keys=True).replace("</", "<\\/")
    return "\n".join([
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        POLICY_META,
        *([meta] if meta else []),
        f"<title>{page.title}</title>",
        f"<style>{STYLE}</style>",
        "</head>",
        "<body>",
        '<header><input id="search" type="search" placeholder="Search the docs" '
        'aria-label="Search the docs">'
        '<button id="theme" type="button">Theme</button></header>',
        '<ul id="search-results"></ul>',
        '<div class="layout">',
        f'<aside>{nav}<nav id="toc"><p class="nav-title">On this page</p><ul>{toc}</ul></nav></aside>',
        f"<main><article>\n{page.body}\n</article></main>",
        "</div>",
        f'<script type="application/json" id="search-index">{payload}</script>',
        f"<script>{SCRIPT}</script>",
        "</body>",
        "</html>",
        "",
    ])


# --- render ----------------------------------------------------------------------


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=False)


def ignored_build_dir(anchor: Path, out: Path) -> str | None:
    """Return None when git ignores `out`, else the refusal to print."""
    top = git(anchor, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        return f"{anchor.as_posix()} is not inside a git repository; cannot confirm the build directory is ignored"
    repository = Path(top.stdout.strip()).resolve()
    try:
        relative = out.relative_to(repository).as_posix()
    except ValueError:
        return None
    probe = git(repository, "check-ignore", "-q", f"{relative}/index.html")
    if probe.returncode == 0:
        return None
    return (f"build directory {relative}/ is not ignored by git; nothing was written.\n"
            f"Add this line to the repository's .gitignore and re-run:\n  {relative}/")


def tree_root(target: Path, given: Path | None) -> Path:
    if given is not None:
        return given.resolve()
    if target.is_dir():
        return target
    folder = target.parent
    return folder.parent if classify(Path(folder.name) / "x") != OTHER[0] else folder


def render(args: argparse.Namespace) -> int:
    target = args.path.resolve()
    if target.is_file() and target.suffix.lower() != ".md":
        print(f"{args.path.as_posix()}: not a Markdown page", file=sys.stderr)
        return 2
    if not target.exists():
        print(f"{args.path.as_posix()}: no such page or directory", file=sys.stderr)
        return 2
    root = tree_root(target, args.root)
    sources = sorted(root.rglob("*.md"), key=lambda p: p.relative_to(root).as_posix())
    chosen = [p for p in sources if p == target or target in p.parents] if target != root else sources
    if not chosen:
        print(f"{args.path.as_posix()}: no Markdown pages to render", file=sys.stderr)
        return 2

    if args.slots:
        out_dir = root
    else:
        top = git(root, "rev-parse", "--show-toplevel")
        base = Path(top.stdout.strip()).resolve() if top.returncode == 0 else root
        out_dir = (args.out.resolve() if args.out else base / DEFAULT_OUT)
        refusal = ignored_build_dir(root, out_dir)
        if refusal:
            print(refusal, file=sys.stderr)
            return 2

    pages = {source: Page(source, source.relative_to(root), classify(source.relative_to(root)))
             for source in sources}
    hybrids = {s for s in sources if s.with_suffix(".html").is_file() or s in chosen}

    def output(source: Path) -> Path:
        return out_dir / source.relative_to(root).with_suffix(".html")

    def nav_target(source: Path) -> Path:
        if not args.slots:
            return output(source)
        return source.with_suffix(".html") if source in hybrids else source

    for source, page in pages.items():
        here = output(source).parent

        def resolve(url: str, source: Path = source, here: Path = here) -> str:
            if SCHEME.match(url) or url.startswith("#"):
                return url
            path, _, fragment = url.partition("#")
            suffix = f"#{fragment}" if fragment else ""
            linked = Path(os.path.normpath(source.parent / path))
            if linked in pages:
                return posix_relpath(nav_target(linked), here) + suffix
            if args.slots:
                return url
            return posix_relpath(linked, here) + suffix

        convert(page, source.read_text(encoding="utf-8", errors="strict"), resolve,
                args.slots)

    for source in chosen:
        page, here = pages[source], output(source).parent
        groups = []
        for kind, label in [(k, l) for k, l, _ in TYPES] + [OTHER]:
            members = [p for p in pages.values() if p.kind == kind]
            if not members:
                continue
            links = "".join(
                f'<li><a href="{posix_relpath(nav_target(p.source), here)}"'
                f'{" aria-current=" + chr(34) + "page" + chr(34) if p is page else ""}>'
                f"{p.title}</a></li>"
                for p in members
            )
            groups.append(f'<p class="nav-title">{label}</p><ul>{links}</ul>')
        nav = f'<nav id="site-nav">{"".join(groups)}</nav>'
        index = [
            {"headings": [rendered_heading_text(h) for h in p.headings], "text": p.text,
             "title": html.unescape(p.title), "type": p.kind,
             "url": posix_relpath(nav_target(p.source), here)}
            for p in pages.values()
        ]
        meta = ""
        if args.slots:
            print_fp = fingerprint(source.read_text(encoding="utf-8", errors="strict"))
            meta = (f'<meta name="{FINGERPRINT_META}" content="{print_fp}">\n'
                    f'<meta name="diataxis-source" content="{html.escape(source.name)}">')
        written = output(source)
        written.parent.mkdir(parents=True, exist_ok=True)
        written.write_bytes(document(page, nav, index, meta).encode("utf-8"))
        print(f"wrote {posix_relpath(written, Path.cwd())}")
    return 0


# --- check -----------------------------------------------------------------------


class Scan(HTMLParser):
    """Reads a page for `check`: headings, fetches, the policy and active content.

    The whole page is scanned, not only its slots, so markup edited outside a
    slot, or a lost policy, fails too.
    """

    FETCHING = ("src", "poster", "data", "action", "formaction")  # on any element
    FETCHING_HREF = ("link", "use", "image", "base")
    LINKING = ("href", "xlink:href")

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: list[str] = []
        self.fetches: list[str] = []
        self.active: list[str] = []
        self.meta: dict[str, str] = {}
        self.policies: list[str] = []
        self.ids: set[str] = set()
        self.fragments: list[str] = []  # SVG link targets, checked once every id is read
        self._heading: list[str] | None = None
        self._code: str | None = None
        self._script: list[str] | None = None
        self._style: list[str] | None = None
        self._svg = 0
        self._body = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        attributes = {name: value or "" for name, value in attrs}
        names = self.FETCHING + (self.LINKING if tag in self.FETCHING_HREF else ())
        for name in names:
            if REMOTE.match(attributes.get(name, "")):
                self.fetches.append(f"<{tag} {name}={attributes[name]}>")
        for name in ("srcset", "imagesrcset"):
            if name in attributes:
                self.fetches.append(f"<{tag} {name}>")
        self.read_active(tag, attributes)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if tag == "body":
            self._body = True
        if tag == "meta" and "name" in attributes:
            self.meta[attributes["name"]] = attributes.get("content", "")
        # A browser honours a policy <meta> only in the head.
        if (tag == "meta" and not self._body
                and attributes.get("http-equiv", "").lower() == "content-security-policy"):
            self.policies.append(attributes.get("content", ""))
        if re.fullmatch(r"h[1-6]", tag):
            self._heading = []
        if tag in ("script", "style"):
            self._code = tag
        if tag == "style":
            self._style = []
        # A JSON block never runs; a script with a src fails as active content.
        if (tag == "script" and "src" not in attributes
                and attributes.get("type", "").lower() != "application/json"):
            self._script = []

    def read_active(self, tag: str, attributes: dict[str, str]) -> None:
        for name, value in attributes.items():
            if name.startswith("on"):
                self.active.append(f"event handler {name} on <{tag}>")
            # A browser ignores whitespace and control characters in a URL.
            url = re.sub(r"[\x00-\x20]", "", value).lower()
            if url.startswith("javascript:"):
                self.active.append(f"javascript: URL in <{tag} {name}>")
            # Inside an SVG the same-page #id rule below fails it already.
            if url.startswith("data:") and name in self.LINKING and not self._svg:
                self.active.append(f"data: URL in <{tag} {name}>")
            if name == "style":
                self.active.append(f"style attribute on <{tag}>")
        if tag == "script" and "src" in attributes:
            self.active.append(f"<script> carries src={attributes['src']}")
        if tag in ("iframe", "frame", "object", "embed"):
            self.active.append(f"<{tag}> element")
        if tag == "meta" and attributes.get("http-equiv", "").lower() == "refresh":
            self.active.append("meta refresh")
        if tag == "svg":
            self._svg += 1
        if tag == "foreignobject":
            self.active.append("<foreignObject> in an SVG")
        for name in self.LINKING:
            if name not in attributes:
                continue
            if tag in ("use", "image"):
                self.active.append(f"<{tag}> carries {name}")
            elif tag == "a" and self._svg:
                if re.fullmatch(r"#[^\s#]+", attributes[name]):
                    self.fragments.append(attributes[name][1:])
                else:
                    self.active.append(
                        f"SVG link is not a same-page #id: {name}={attributes[name]}")

    def handle_endtag(self, tag: str) -> None:
        if re.fullmatch(r"h[1-6]", tag) and self._heading is not None:
            self.headings.append(plain_heading("".join(self._heading)))
            self._heading = None
        if tag in ("script", "style"):
            self._code = None
        if tag == "svg":
            self._svg = max(0, self._svg - 1)
        if tag == "script" and self._script is not None:
            digest = source_hash("".join(self._script))
            if digest not in SHIPPED_SCRIPT_HASHES:
                self.active.append(f"inline script not shipped by the template: {digest}")
            self._script = None
        if tag == "style" and self._style is not None:
            digest = source_hash("".join(self._style))
            if digest not in SHIPPED_STYLE_HASHES:
                self.active.append(f"style not shipped by the template: {digest}")
            self._style = None

    def handle_data(self, data: str) -> None:
        if self._heading is not None:
            self._heading.append(data)
        if self._script is not None:
            self._script.append(data)
        if self._style is not None:
            self._style.append(data)
        if self._code == "script":
            for call in ("fetch(", "XMLHttpRequest", "import(", "WebSocket", "EventSource"):
                if call in data:
                    self.fetches.append(f"script uses {call}")
        if self._code == "style" and ("@import" in data or re.search(r"url\(\s*['\"]?(https?:)?//", data)):
            self.fetches.append("style loads a remote resource")


def plain_heading(title: str) -> str:
    return " ".join(re.sub(r"[*_`]", "", rendered_heading_text(title)).split())


def check(args: argparse.Namespace) -> int:
    root = args.path.resolve()
    if not root.is_dir():
        print(f"{args.path.as_posix()}: not a directory", file=sys.stderr)
        return 2
    failures: list[str] = []
    checked = 0
    for page in sorted(root.rglob("*.html"), key=lambda p: p.relative_to(root).as_posix()):
        scan = Scan()
        scan.feed(page.read_text(encoding="utf-8", errors="replace"))
        if FINGERPRINT_META not in scan.meta:
            continue
        checked += 1
        name = page.relative_to(root).as_posix()
        source = page.with_suffix(".md")
        if not source.is_file():
            failures.append(f"{name}: source {source.name} is missing")
            continue
        markdown = source.read_text(encoding="utf-8", errors="strict")
        if fingerprint(markdown) != scan.meta[FINGERPRINT_META]:
            failures.append(f"{name}: fingerprint drift; {source.name} changed after the render")
        _, headings = markdown_headings(markdown, include_atx_level_one=True)
        for heading in headings:
            if plain_heading(heading.title) not in scan.headings:
                failures.append(f"{name}: heading missing from the HTML: {heading.title}")
        for fetch in scan.fetches:
            failures.append(f"{name}: network fetch: {fetch}")
        if not scan.policies:
            failures.append(f"{name}: the strict policy <meta> is missing from the head")
        for policy in scan.policies:
            if policy not in SHIPPED_POLICIES:
                failures.append(f"{name}: the policy <meta> is not one the template shipped")
        for fragment in scan.fragments:
            if fragment not in scan.ids:
                failures.append(f"{name}: active content: SVG link names no id on the page: "
                                f"#{fragment}")
        for item in scan.active:
            failures.append(f"{name}: active content: {item}")
    if failures:
        print(f"Hybrid check failed ({checked} page(s) checked):")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"{checked} hybrid page(s) checked; each matches its Markdown, fetches nothing "
          "and runs only the template's script and style.")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    render_parser = commands.add_parser("render", help="render a docs tree or one page")
    render_parser.add_argument("path", type=Path)
    render_parser.add_argument("--root", type=Path, help="docs root the navigation spans")
    render_parser.add_argument("--out", type=Path, help=f"build directory (default {DEFAULT_OUT}/)")
    render_parser.add_argument("--slots", action="store_true",
                               help="hybrid: write beside the Markdown with marked slots")
    check_parser = commands.add_parser("check", help="check every committed hybrid page")
    check_parser.add_argument("path", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.command == "render" and args.slots and args.out:
        print("--slots writes beside the Markdown; --out does not apply", file=sys.stderr)
        return 2
    return render(args) if args.command == "render" else check(args)


if __name__ == "__main__":
    sys.exit(main())
