#!/usr/bin/env python3
"""Check a research base against its contract, and own the one frontmatter parser.

    scripts/validate_base.py --base <base>

Reads the base's `base.json`, then every record in each tracked layer, and
reports findings by rule id. Exits 0 with an `OK:` line when there are none and
1 when there are any; every rule is an error, because no workflow the contract
prescribes produces any of these states on its way to a valid one.

**The base is an argument, not a location**, for the reason `index.py` gives:
this script is bundled into a skill payload, where no base exists at any depth.

**The contract is `references/research-base-model.md`.** What this script checks
is its *Declaring the layers* and *Frontmatter* sections:

- the base declares its layers in `base.json`, and a base without one is refused;
- a tracked layer's directory exists; an untracked one's need not, because git
  creates no directory for content it ignores, so a fresh clone has none;
- a record is a Markdown file at the top level of a tracked layer, other than
  `README.md` and `TEMPLATE.md`; subdirectories hold material, not records;
- a record is UTF-8, and one that does not decode is reported, not crashed on;
- every record carries `title`, `kind`, `regime` and `updated`, and a living one
  also `status`, `confidence` and a non-empty `authority`;
- `kind` agrees with the layer's declared kind, and `regime` is one it admits;
- a manifest record's `covers` names files that exist inside the base;
- a living record's `authority` entries can be found, by its *Citations* rules.

**An authority is resolved against the repository root**: the nearest
directory above the base holding a `.git` entry, a file in a worktree. It is
found from the base the caller passes, never from where this script sits, and
looking is a filesystem test, not a git call. With no root, a base whose living
records name a repository path gets one finding, never a silent pass. An entry
is a URL or a repository path, with an optional `path:Name` locator:

- an `http://` or `https://` entry needs a host; it is never fetched, so whether
  the page still exists stays with `research-base-audit`;
- a path must stay inside the root and exist;
- after a Markdown document, `Name` is the whole text of one heading, at any
  level and outside fenced blocks;
- after a `.py` file, `Name` is the first word, and what follows is the
  instrument's inputs, not resolved. It must be a `def`, `async def` or `class`
  at any depth, or a module-level assignment; a file that does not parse is a
  finding;
- after any other file, `Name` need only appear in it as a whole word. That is
  weaker than the two rules above, because the standard library parses no other
  language and refusing what it cannot parse would fail a valid entry.

A frozen record is not resolved: it pins its citations to a moment, when what it
names existed.

`references/record.schema.yaml` restates these rules as documentation. This
script does not read it -- a bundled script has no YAML parser -- and a test in
the authoring repository pins the two in agreement.

**`read_frontmatter` is the base's one parser**, and `index.py` imports it.
Standard library only: flat scalars, inline lists and block lists, with `#`
comments stripped. Nothing a record carries needs a YAML engine.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import json
import re
import sys
import urllib.parse
from pathlib import Path


BASE_FILE = "base.json"
NON_RECORDS = {"readme.md", "template.md"}

REGIMES = ("frozen", "living")
ENUMS = {
    "regime": REGIMES,
    "status": ("exploring", "supported", "promoted"),
    "confidence": ("directional", "evidenced", "strong"),
}
LIST_KEYS = ("authority", "sources", "informs", "covers")
REQUIRED_ALWAYS = ("title", "kind", "regime", "updated")
REQUIRED_LIVING = ("status", "confidence")
KNOWN_KEYS = REQUIRED_ALWAYS + REQUIRED_LIVING + LIST_KEYS

# Every rule this script reports. The schema's `rules:` block and the tests are
# pinned against this mapping, so a rule cannot be added in one place only.
RULES = {
    "base-file-missing": "the base has no base.json",
    "base-file-invalid": "base.json does not parse, or declares no valid layers",
    "layer-directory-missing": "a declared tracked layer's directory does not exist",
    "record-not-utf8": "a record's bytes do not decode as UTF-8",
    "frontmatter-missing": "a record has no leading frontmatter block",
    "key-missing": "a required key is absent",
    "authority-missing": "a living record names no authority, so nothing can audit it",
    "value-invalid": "a value is outside its allowed set, or has the wrong shape",
    "kind-matches-directory": "a record's kind disagrees with its layer's",
    "regime-not-admitted": "a record's regime is one its layer does not admit",
    "covers-empty": "a manifest record covers nothing",
    "covers-target-missing": "a manifest record names a file that does not exist",
    "covers-outside-base": "a manifest record names a file outside the base",
    "authority-root-missing": "no directory above the base holds .git, so no "
                              "repository path an authority names can be resolved",
    "authority-outside-root": "an authority entry is absolute, or resolves outside "
                              "the repository",
    "authority-target-missing": "an authority entry names a path that does not exist",
    "authority-locator-unresolved": "an authority's `:Name` matches nothing in its path",
    "authority-url-invalid": "an http(s) authority entry has no host",
}

KEY = re.compile(r"^([A-Za-z][\w-]*):\s*(.*)$")
ITEM = re.compile(r"^\s+-\s*(.*)$")
COMMENT = re.compile(r"(^|\s)#.*$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL = re.compile(r"^https?://", re.IGNORECASE)
ABSOLUTE = re.compile(r"^([A-Za-z]:)?[\\/]")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
HEADING = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+(.*?))?[ \t]*$")
CLOSING_HASHES = re.compile(r"(?:^|[ \t]+)#+$")
MARKDOWN = {".md", ".markdown"}

Finding = tuple[str, str, str]


def _clean(raw: str) -> str:
    """Strip a trailing `#` comment, surrounding space and matching quotes."""
    return COMMENT.sub("", raw).strip().strip("\"'")


def read_frontmatter(text: str) -> dict[str, str | list[str]]:
    """The fields of a leading `--- ... ---` block; empty when there is none.

    A key with an inline value is a scalar; `[a, b]` is a list; a key with no
    value followed by indented `- item` lines is a block list. A key with no
    value and no items is omitted, so an empty scalar never masquerades as a
    present one.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str | list[str]] = {}
    pending: str | None = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        item = ITEM.match(line)
        if item and pending is not None:
            value = _clean(item.group(1))
            if value:
                fields.setdefault(pending, [])
                fields[pending].append(value)  # type: ignore[union-attr]
            continue
        match = KEY.match(line)
        if not match:
            continue  # blank, comment, or an item with no open key
        key, value = match.group(1), _clean(match.group(2))
        pending = None
        if not value:
            pending = key
        elif value.startswith("[") and value.endswith("]"):
            fields[key] = [
                part.strip().strip("\"'")
                for part in value[1:-1].split(",")
                if part.strip()
            ]
        else:
            fields[key] = value
    return fields


def has_frontmatter(text: str) -> bool:
    lines = text.splitlines()
    return bool(lines) and lines[0].strip() == "---" and any(
        line.strip() == "---" for line in lines[1:]
    )


def read_layers(base: Path) -> tuple[dict[str, dict] | None, list[Finding]]:
    """The declared layers, or None with the finding that explains why not."""
    path = base / BASE_FILE
    if not path.is_file():
        return None, [(BASE_FILE, "base-file-missing",
                       f"no {BASE_FILE} at {base}; a base declares its layers there")]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        return None, [(BASE_FILE, "base-file-invalid", f"does not parse: {error}")]

    def invalid(message: str) -> tuple[None, list[Finding]]:
        return None, [(BASE_FILE, "base-file-invalid", message)]

    layers = data.get("layers") if isinstance(data, dict) else None
    if not isinstance(layers, dict) or not layers:
        return invalid("needs a non-empty `layers` object")
    for directory, layer in layers.items():
        if not directory or Path(directory).is_absolute() or ".." in Path(directory).parts:
            return invalid(f"layer {directory!r} must be a directory inside the base")
        if not isinstance(layer, dict):
            return invalid(f"layer {directory!r} must be an object")
        kind, regimes, tracked = layer.get("kind"), layer.get("regimes"), layer.get("tracked")
        if not isinstance(kind, str) or not kind:
            return invalid(f"layer {directory!r} needs a non-empty `kind`")
        if (not isinstance(regimes, list) or not regimes
                or any(regime not in REGIMES for regime in regimes)):
            return invalid(f"layer {directory!r}: `regimes` must be a non-empty "
                           f"list drawn from {list(REGIMES)}")
        if not isinstance(tracked, bool):
            return invalid(f"layer {directory!r}: `tracked` must be true or false")
    return layers, []


def read_record(base: Path, path: Path) -> tuple[str | None, list[Finding]]:
    """A record's text, or None with the finding that explains why not.

    The one place a record is decoded, so `index.py` and this script cannot
    disagree about which records can be read.
    """
    try:
        return path.read_text(encoding="utf-8"), []
    except UnicodeDecodeError as error:
        name = path.relative_to(base).as_posix()
        return None, [(name, "record-not-utf8", f"does not decode: {error}")]


def repository_root(base: Path) -> Path | None:
    """The nearest directory at or above the base holding `.git`, or None."""
    start = base.resolve()
    for directory in (start, *start.parents):
        if (directory / ".git").exists():
            return directory
    return None


def headings(text: str) -> set[str]:
    """Every heading's text outside fenced blocks, closing hashes dropped."""
    found: set[str] = set()
    fence: str | None = None
    for line in text.splitlines():
        opening = FENCE.match(line)
        if fence is not None:
            marker = opening.group(1) if opening else ""
            if (marker[:1] == fence[0] and len(marker) >= len(fence)
                    and line.strip() == marker):
                fence = None
            continue
        if opening:
            fence = opening.group(1)
            continue
        match = HEADING.match(line)
        if match:
            found.add(CLOSING_HASHES.sub("", match.group(1) or "").strip())
    return found


def _assigned(target: ast.expr) -> list[str]:
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, ast.Starred):
        return _assigned(target.value)
    if isinstance(target, (ast.Tuple, ast.List)):
        return [name for element in target.elts for name in _assigned(element)]
    return []


def symbols(tree: ast.Module) -> set[str]:
    """Every def, async def and class at any depth, and every module-level name."""
    found = {
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                found.update(_assigned(target))
        elif isinstance(node, ast.AnnAssign):
            found.update(_assigned(node.target))
    return found


def check_url(entry: str) -> tuple[str, str] | None:
    """Why an http(s) authority entry is malformed, or None. Never fetched."""
    try:
        host = urllib.parse.urlsplit(entry).hostname
    except ValueError:
        host = None
    if not host:
        return "authority-url-invalid", f"`{entry}` has no host"
    return None


def check_authority(entry: str, root: Path) -> tuple[str, str] | None:
    """Why a repository-path authority entry does not resolve, or None."""
    if ABSOLUTE.match(entry):
        return "authority-outside-root", (
            f"`{entry}` is absolute; name it from the repository root")
    relative, has_name, name = entry.partition(":")
    target = (root / relative).resolve()
    if not target.is_relative_to(root):
        return "authority-outside-root", f"`{relative}` resolves outside the repository"
    if not target.exists():
        return "authority-target-missing", f"`{relative}` does not exist in the repository"
    if not has_name:
        return None

    unresolved = "authority-locator-unresolved"
    if not target.is_file():
        return unresolved, f"`{entry}`: `{relative}` is a directory, which names nothing"
    try:
        text = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return unresolved, f"`{relative}` does not decode as UTF-8, so nothing in it is found"
    suffix = target.suffix.lower()
    if suffix == ".py":
        words = name.split()
        wanted, what = (words[0] if words else ""), "symbol"
        try:
            found = wanted in symbols(ast.parse(text))
        except (SyntaxError, ValueError) as error:
            return unresolved, (
                f"`{relative}` does not parse as Python ({error}), "
                f"so `{wanted}` cannot be found")
    elif suffix in MARKDOWN:
        wanted, what = name.strip(), "heading"
        found = wanted in headings(text)
    else:
        wanted, what = name.strip(), "whole word"
        found = bool(re.search(rf"(?<!\w){re.escape(wanted)}(?!\w)", text))
    if wanted and found:
        return None
    return unresolved, f"`{entry}`: `{relative}` has no {what} `{wanted}`"


def check_record(base: Path, path: Path, layer: dict, root: Path | None) -> list[Finding]:
    name = path.relative_to(base).as_posix()
    text, unreadable = read_record(base, path)
    if text is None:
        return unreadable
    if not has_frontmatter(text):
        return [(name, "frontmatter-missing", "no leading --- frontmatter block")]
    front = read_frontmatter(text)
    findings: list[Finding] = []

    def report(rule: str, message: str) -> None:
        findings.append((name, rule, message))

    for key in REQUIRED_ALWAYS:
        if key not in front:
            report("key-missing", f"`{key}` is required on every record")

    for key in LIST_KEYS:
        if key in front and not isinstance(front[key], list):
            report("value-invalid", f"`{key}` must be a list")
    for key, allowed in ENUMS.items():
        value = front.get(key)
        if value is not None and value not in allowed:
            report("value-invalid", f"`{key}: {value}` is not one of {list(allowed)}")
    updated = front.get("updated")
    if updated is not None:
        try:
            if not isinstance(updated, str) or not DATE.match(updated):
                raise ValueError(updated)
            datetime.date.fromisoformat(updated)
        except ValueError:
            report("value-invalid", f"`updated: {updated}` is not a YYYY-MM-DD date")

    if front.get("regime") == "living":
        for key in REQUIRED_LIVING:
            if key not in front:
                report("key-missing", f"`{key}` is required on a living record")
        if not front.get("authority"):
            report("authority-missing",
                   "a living record must name what it is re-verified against")
        authority = front.get("authority")
        for entry in authority if isinstance(authority, list) else []:
            if URL.match(entry):
                problem = check_url(entry)
            elif root is None:
                # Collapsed by `validate` into one finding for the whole base.
                problem = ("authority-root-missing", f"`{entry}` cannot be resolved")
            else:
                problem = check_authority(entry, root)
            if problem:
                report(*problem)

    kind = front.get("kind")
    if kind is not None and kind != layer["kind"]:
        report("kind-matches-directory",
               f"`kind: {kind}` sits in a layer declared as `{layer['kind']}`; "
               "correct the kind or re-classify deliberately -- never move to match")
    regime = front.get("regime")
    if regime in REGIMES and regime not in layer["regimes"]:
        report("regime-not-admitted",
               f"`regime: {regime}` is not admitted by this layer ({layer['regimes']})")

    if "covers" in front and isinstance(front["covers"], list):
        if not front["covers"]:
            report("covers-empty", "a manifest record must name the files it describes")
        root = base.resolve()
        for entry in front["covers"]:
            target = (path.parent / entry).resolve()
            if not target.is_relative_to(root):
                report("covers-outside-base", f"`{entry}` resolves outside the base")
            elif not target.exists():
                report("covers-target-missing", f"`{entry}` does not exist")
    return findings


def validate(base: Path) -> list[Finding]:
    """Every finding for one base, in a stable order. Empty means valid."""
    layers, findings = read_layers(base)
    if layers is None:
        return findings
    repository = repository_root(base)
    for directory in sorted(layers):
        layer = layers[directory]
        root = base / directory
        # Checked before the directory, because an untracked layer is absent on
        # every fresh clone: git creates no directory for content it ignores.
        if not layer["tracked"]:
            continue
        if not root.is_dir():
            findings.append((directory, "layer-directory-missing",
                             f"declared in {BASE_FILE} but not on disk"))
            continue
        for path in sorted(root.glob("*.md")):
            if path.name.lower() not in NON_RECORDS:
                findings.extend(check_record(base, path, layer, repository))
    rootless = {name for name, rule, _ in findings if rule == "authority-root-missing"}
    if rootless:
        findings = [finding for finding in findings if finding[1] != "authority-root-missing"]
        findings.append((".", "authority-root-missing",
                         f"no directory above {base} holds .git, so the repository "
                         f"paths {len(rootless)} living record(s) name as their "
                         "authority cannot be resolved"))
    return findings


def count_records(base: Path, layers: dict[str, dict]) -> int:
    return sum(
        1
        for directory, layer in layers.items()
        if layer["tracked"] and (base / directory).is_dir()
        for path in (base / directory).glob("*.md")
        if path.name.lower() not in NON_RECORDS
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", type=Path, required=True,
                        help="the research base directory to check")
    args = parser.parse_args(argv)

    findings = validate(args.base)
    if findings:
        print(f"{len(findings)} error(s) on {args.base}:\n")
        for name, rule, message in findings:
            print(f"  {name}: [{rule}] {message}")
        return 1
    layers, _ = read_layers(args.base)
    print(f"OK: {count_records(args.base, layers or {})} record(s) on "
          f"{args.base}, no findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
