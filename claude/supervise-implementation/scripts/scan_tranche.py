#!/usr/bin/env python3
"""List what a tranche's commits left behind, for the tranche gate to judge.

The gate runs this once over the whole tranche, base to tip, and reads one
JSON report. Every list is a set of candidates, not of defects: the gate
verifies each against the code before it acts on it.

    scripts/scan_tranche.py --repo . --base <tranche-base> --tip <tranche-tip> \\
        [--record <board>/<tranche-record>.md] [--board tasks]

    scripts/scan_tranche.py --repo . --base <tranche-base> --tip <head> --size

- **units**: who changed what. With `--record`, each task is the ranges
  `<sha>^1..<sha>` of the `merged <sha>` lines under the record's
  `## Integrator verdicts`. Without one, or for a first-parent commit no task
  owns, each first-parent commit of base..tip is a unit of its own.
- **churn** (D1): files two or more units changed, and lines one commit added
  and a later one removed inside the tranche, followed across renames.
- **clones** (D3): Python functions and methods whose syntax trees are equal
  once docstrings are dropped and names are renamed in order of appearance;
  and, in every other text file, runs of 5 or more meaningful lines repeated
  elsewhere (blank lines and Markdown frontmatter are not meaningful). A group
  is listed only when at least one copy has a line the tranche added.
- **dead_code** (D4): functions, classes, methods, module-level names and
  Python modules the tranche added or changed, whose name occurs as a token
  in no tracked text file outside its own definition. pytest's test functions
  and classes, its `pytest_` hooks in `conftest.py`, and dunder names are not
  candidates. A `_` name is tagged `private`; any other is tagged
  `check published use`, because undocumented is not private.
- **leftovers** (D9): files the tranche added whose name no other tracked text
  file mentions (Python modules are reported under dead_code instead, and test
  files, `conftest.py`, `__init__.py` and dot-files are found by convention);
  and `print` calls on added lines outside `main` and the `__main__` block.
- **markers** (D10): `TODO` and `FIXME` on lines the tranche added.
- **size**: changed lines, as `git diff --shortstat` counts them, raw and
  without the board's generated `README.md`, `TREE.md` and `ARCHIVE.md`.
  `--size` prints only the second number; the supervisor closes a tranche on
  it.

The board's generated indexes are left out of every list, but they are still
searched for references. `--board` names the board folder, `tasks` by default.

Standard library and `git` only, deterministic. Exits 0 with a report, 2 when
the repository, a commit or the record cannot be read.
"""

from __future__ import annotations

import argparse
import ast
import copy
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path


GENERATED = ("README.md", "TREE.md", "ARCHIVE.md")
WINDOW = 5
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
MARKER = re.compile(r"\b(TODO|FIXME)\b")
TEST_FILE = re.compile(r"(^|/)(test_[^/]*|[^/]*_test)\.py$")
CONVENTION_FILES = {"conftest.py", "__init__.py"}


# --- git ------------------------------------------------------------------------


class GitError(Exception):
    pass


GIT_CONFIG = ("-c", "core.quotepath=false", "-c", "diff.noprefix=false",
              "-c", "diff.mnemonicprefix=false", "-c", "log.showsignature=false")


def git(repo: Path, *args: str, stdin: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", *GIT_CONFIG, "-C", str(repo), *args], input=stdin, capture_output=True,
    )
    if result.returncode != 0:
        raise GitError(result.stderr.decode("utf-8", "replace").strip() or f"git {args[0]} failed")
    return result.stdout


def git_ok(repo: Path, *args: str) -> bool:
    return subprocess.run(["git", *GIT_CONFIG, "-C", str(repo), *args], capture_output=True).returncode == 0


def resolve(repo: Path, rev: str) -> str:
    try:
        return git(repo, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}").decode().strip()
    except GitError:
        raise GitError(f"not a commit: {rev}") from None


def numstat(repo: Path, old: str, new: str) -> list[tuple[int, int, str]]:
    """(added, deleted, path) per file, as `git diff --shortstat` counts them."""
    fields = git(repo, "diff", "--numstat", "-z", "-M", old, new).decode("utf-8", "replace").split("\0")
    rows = []
    i = 0
    while i < len(fields):
        if not fields[i]:
            i += 1
            continue
        added, deleted, path = fields[i].split("\t", 2)
        if path == "":  # a rename: the two paths follow
            path = fields[i + 2]
            i += 3
        else:
            i += 1
        rows.append((int(added) if added != "-" else 0, int(deleted) if deleted != "-" else 0, path))
    return rows


# --- patches --------------------------------------------------------------------------

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


@dataclass
class FilePatch:
    old: str | None = None
    new: str | None = None
    renamed: bool = False
    removed: list[tuple[int, str]] = field(default_factory=list)
    added: list[tuple[int, str]] = field(default_factory=list)

    @property
    def path(self) -> str:
        return self.new or self.old or ""


def _patch_path(raw: str, prefix: str) -> str | None:
    raw = raw.rstrip("\t")
    if raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1].encode("latin-1", "backslashreplace").decode("unicode_escape").encode("latin-1").decode("utf-8")
    if raw == "/dev/null":
        return None
    return raw[len(prefix):] if raw.startswith(prefix) else raw


def parse_patch(text: str) -> list[FilePatch]:
    patches: list[FilePatch] = []
    current: FilePatch | None = None
    in_hunk = False
    old_ln = new_ln = 0
    for line in text.split("\n"):
        if line.startswith("diff --git "):
            current = FilePatch()
            patches.append(current)
            in_hunk = False
            continue
        if current is None:
            continue
        hunk = HUNK.match(line)
        if hunk:
            in_hunk = True
            old_ln, new_ln = int(hunk.group(1)), int(hunk.group(3))
            continue
        if not in_hunk:
            if line.startswith("rename from "):
                current.old, current.renamed = _patch_path(line[12:], ""), True
            elif line.startswith("rename to "):
                current.new, current.renamed = _patch_path(line[10:], ""), True
            elif line.startswith("--- "):
                current.old = _patch_path(line[4:], "a/")
            elif line.startswith("+++ "):
                current.new = _patch_path(line[4:], "b/")
            elif line.startswith("new file mode"):
                current.old = None
            continue
        if line.startswith("-"):
            current.removed.append((old_ln, line[1:]))
            old_ln += 1
        elif line.startswith("+"):
            current.added.append((new_ln, line[1:]))
            new_ln += 1
        elif line.startswith(" "):
            old_ln += 1
            new_ln += 1
    return patches


def diff_patches(repo: Path, old: str, new: str) -> list[FilePatch]:
    out = git(repo, "diff", "-U0", "-M", "--no-color", "--no-ext-diff", old, new)
    return parse_patch(out.decode("utf-8", "replace"))


# --- the tip's tree ----------------------------------------------------------------------


def read_tree(repo: Path, tip: str) -> dict[str, str]:
    """Every tracked text file at the tip, by path."""
    entries = []
    for row in git(repo, "ls-tree", "-r", "-z", "--full-tree", tip).decode("utf-8", "replace").split("\0"):
        if not row:
            continue
        meta, path = row.split("\t", 1)
        mode, kind, sha = meta.split()
        if kind == "blob" and mode in ("100644", "100755"):
            entries.append((path, sha))
    if not entries:
        return {}
    out = git(repo, "cat-file", "--batch", stdin="\n".join(sha for _, sha in entries).encode() + b"\n")
    files: dict[str, str] = {}
    pos = 0
    for path, _ in entries:
        header_end = out.index(b"\n", pos)
        size = int(out[pos:header_end].split()[2])
        data = out[header_end + 1 : header_end + 1 + size]
        pos = header_end + 1 + size + 1
        if b"\0" in data[:8000]:
            continue
        try:
            files[path] = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
    return files


# --- units ---------------------------------------------------------------------------------

VERDICT = re.compile(
    r"^-\s+.*?,\s*(?P<task>[A-Za-z0-9][\w.-]*)\s+attempt\s+\d+:.*?(?<![A-Za-z])merged\s+(?P<sha>[0-9a-f]{7,40})\b"
)


def record_merges(text: str) -> list[tuple[str, str]]:
    """(task, sha) for each `merged <sha>` verdict, in the record's order."""
    merges = []
    in_section = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_section = line.strip() == "## Integrator verdicts"
            continue
        if in_section:
            match = VERDICT.match(line)
            if match:
                merges.append((match.group("task"), match.group("sha")))
    return merges


@dataclass
class Unit:
    id: str
    kind: str
    ranges: list[tuple[str, str]] = field(default_factory=list)
    commits: set[str] = field(default_factory=set)


def build_units(repo: Path, base: str, tip: str, merges: list[tuple[str, str]] | None) -> tuple[list[Unit], list[str]]:
    first_parent = git(repo, "rev-list", "--first-parent", "--reverse", f"{base}..{tip}").decode().split()

    def commits_of(old: str, new: str) -> set[str]:
        return set(git(repo, "rev-list", f"{old}..{new}").decode().split())

    tasks: dict[str, Unit] = {}
    ignored: list[str] = []
    for task, short in merges or []:
        try:
            sha = resolve(repo, short)
        except GitError:
            raise GitError(f"the record names a commit this repository does not have: {short}") from None
        if not git_ok(repo, "merge-base", "--is-ancestor", sha, tip) or git_ok(repo, "merge-base", "--is-ancestor", sha, base):
            ignored.append(f"{task} merged {short}: outside base..tip")
            continue
        unit = tasks.setdefault(task, Unit(task, "task"))
        if (f"{sha}^1", sha) not in unit.ranges:
            unit.ranges.append((f"{sha}^1", sha))
            unit.commits |= commits_of(f"{sha}^1", sha)

    units: list[Unit] = []
    emitted: set[str] = set()
    for commit in first_parent:
        owner = next((t for t in tasks.values() if commit in t.commits), None)
        if owner is not None:
            if owner.id not in emitted:
                emitted.add(owner.id)
                units.append(owner)
            continue
        units.append(Unit(commit, "commit", [(f"{commit}^1", commit)], commits_of(f"{commit}^1", commit)))
    units += [t for t in tasks.values() if t.id not in emitted]
    return units, ignored


# --- D1, churn -----------------------------------------------------------------------------


def churn_files(per_unit: list[tuple[Unit, dict[str, list[int]]]]) -> list[dict]:
    by_path: dict[str, list[dict]] = defaultdict(list)
    for unit, files in per_unit:
        for path, (added, deleted) in files.items():
            by_path[path].append({"unit": unit.id, "added": added, "deleted": deleted})
    return [{"path": p, "units": rows} for p, rows in sorted(by_path.items()) if len(rows) > 1]


def rewritten_lines(repo: Path, base: str, tip: str, unit_of: dict[str, str], excluded: set[str]) -> list[dict]:
    out = git(repo, "log", "--reverse", "--topo-order", "--no-merges", "-M", "-U0", "-p",
              "--no-color", "--no-ext-diff", "--format=%x01%H", f"{base}..{tip}").decode("utf-8", "replace")
    order: dict[str, int] = {}
    live: dict[tuple[str, str], list[str]] = defaultdict(list)
    pairs: Counter = Counter()
    for chunk in out.split("\x01")[1:]:
        commit, _, patch = chunk.partition("\n")
        commit = commit.strip()
        order[commit] = len(order)
        for fp in parse_patch(patch):
            if fp.renamed and fp.old and fp.new:
                for key in [k for k in live if k[0] == fp.old]:
                    live[(fp.new, key[1])] += live.pop(key)
            path = fp.path
            if path in excluded:
                continue
            removed = Counter(t.rstrip() for _, t in fp.removed if t.strip())
            added = Counter(t.rstrip() for _, t in fp.added if t.strip())
            moved = removed & added
            for text, count in (removed - moved).items():
                stack = live.get((path, text), [])
                for _ in range(min(count, len(stack))):
                    pairs[(path, stack.pop(0), commit)] += 1
            for text, count in (added - moved).items():
                live[(path, text)] += [commit] * count
    rows = [
        {"path": path, "lines": n, "added_by": a, "removed_by": r,
         "cross_unit": unit_of.get(a, a) != unit_of.get(r, r)}
        for (path, a, r), n in pairs.items()
    ]
    return sorted(rows, key=lambda row: (row["path"], order[row["added_by"]], order[row["removed_by"]]))


# --- Python structure ----------------------------------------------------------------------

DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


@dataclass
class Definition:
    name: str      # the token searched for
    qualname: str
    kind: str      # function | method | class | variable
    node: ast.AST
    start: int
    end: int


def definitions(tree: ast.Module) -> list[Definition]:
    found: list[Definition] = []

    def walk(body: list[ast.stmt], prefix: str, in_class: bool) -> None:
        for node in body:
            if isinstance(node, DEFS):
                qual = f"{prefix}{node.name}"
                start = min([node.lineno] + [d.lineno for d in node.decorator_list])
                if isinstance(node, ast.ClassDef):
                    kind = "class"
                else:
                    kind = "method" if in_class else "function"
                found.append(Definition(node.name, qual, kind, node, start, node.end_lineno or node.lineno))
                walk(node.body, qual + ".", isinstance(node, ast.ClassDef))
            elif not prefix and isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    for name in ast.walk(target):
                        if isinstance(name, ast.Name):
                            found.append(Definition(name.id, name.id, "variable", node, node.lineno,
                                                    node.end_lineno or node.lineno))

    walk(tree.body, "", False)
    return found


def shape(node: ast.AST) -> str:
    """The function's syntax tree with its docstring dropped and names renamed in order."""
    node = copy.deepcopy(node)
    body = node.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        node.body = body[1:] or [ast.Pass()]
    names: dict[str, str] = {}

    def alias(name: str) -> str:
        return names.setdefault(name, f"_{len(names)}")

    node.name = "_"
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name):
            sub.id = alias(sub.id)
        elif isinstance(sub, ast.arg):
            sub.arg = alias(sub.arg)
        elif isinstance(sub, DEFS) and sub is not node:
            sub.name = alias(sub.name)
        elif isinstance(sub, (ast.Global, ast.Nonlocal)):
            sub.names = [alias(n) for n in sub.names]
    return ast.dump(node, include_attributes=False)


def touches(start: int, end: int, lines: set[int]) -> bool:
    return any(start <= n <= end for n in lines)


# --- D3, clones ------------------------------------------------------------------------------


def python_clones(parsed: dict[str, ast.Module], added: dict[str, set[int]]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for path, tree in parsed.items():
        for d in definitions(tree):
            if d.kind in ("function", "method"):
                groups[shape(d.node)].append({
                    "path": path, "name": d.qualname, "lines": [d.node.lineno, d.end],
                    "new": touches(d.node.lineno, d.end, added.get(path, set())),
                })
    found = []
    for members in groups.values():
        if len(members) > 1 and any(m["new"] for m in members):
            found.append({"members": sorted(members, key=lambda m: (m["path"], m["lines"][0]))})
    return sorted(found, key=lambda g: (g["members"][0]["path"], g["members"][0]["lines"][0]))


def meaningful_lines(path: str, text: str) -> list[tuple[int, str]]:
    lines = text.splitlines()
    start = 0
    if path.endswith(".md") and lines and lines[0].strip() == "---":
        close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if close is not None:
            start = close + 1
    return [(i + 1, " ".join(lines[i].split())) for i in range(start, len(lines)) if lines[i].strip()]


def text_clones(files: dict[str, str], added: dict[str, set[int]], excluded: set[str]) -> list[dict]:
    meaningful: dict[str, list[tuple[int, str]]] = {}
    windows: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for path, text in files.items():
        if path.endswith(".py") or path in excluded:
            continue
        lines = meaningful_lines(path, text)
        meaningful[path] = lines
        for i in range(len(lines) - WINDOW + 1):
            windows["\n".join(t for _, t in lines[i : i + WINDOW])].append((path, i))
    groups = {tuple(sorted(locs)) for locs in windows.values() if len(locs) > 1}

    def shifted(sig: tuple, by: int) -> tuple:
        return tuple((p, i + by) for p, i in sig)

    found = []
    for sig in groups:
        if shifted(sig, -1) in groups:
            continue  # the continuation of a run that starts earlier
        length = 1
        while shifted(sig, length) in groups:
            length += 1
        locations = []
        for path, i in sig:
            span = meaningful[path][i : i + length + WINDOW - 1]
            first, last = span[0][0], span[-1][0]
            new = any(n in added.get(path, set()) for n, _ in span)
            locations.append({"path": path, "lines": [first, last], "new": new})
        if any(loc["new"] for loc in locations):
            found.append({"locations": locations, "windows": length})
    return sorted(found, key=lambda g: (g["locations"][0]["path"], g["locations"][0]["lines"][0]))


# --- D4, dead-code candidates -----------------------------------------------------------------


def is_test_file(path: str) -> bool:
    return bool(TEST_FILE.search(path)) or path.rsplit("/", 1)[-1] == "conftest.py"


def exempt(d: Definition, path: str) -> bool:
    if d.name.startswith("__") and d.name.endswith("__"):
        return True
    if is_test_file(path):
        if d.kind in ("function", "method") and d.name.startswith("test"):
            return True
        if d.kind == "class" and d.name.startswith("Test"):
            return True
        if path.rsplit("/", 1)[-1] == "conftest.py" and d.name.startswith("pytest_"):
            return True
    return False


def dead_code(files: dict[str, str], parsed: dict[str, ast.Module], added: dict[str, set[int]], tip: str) -> list[dict]:
    counts = {path: Counter(TOKEN.findall(text)) for path, text in files.items()}
    total: Counter = Counter()
    for c in counts.values():
        total.update(c)
    searched = f"every token in {len(files)} tracked text files at {tip[:12]}, outside the definition"

    def tag(name: str) -> str:
        return "private" if name.startswith("_") else "check published use"

    found = []
    for path, tree in parsed.items():
        lines = added.get(path, set())
        if not lines:
            continue
        source = files[path].splitlines()
        for d in definitions(tree):
            if exempt(d, path) or not touches(d.start, d.end, lines):
                continue
            own = Counter(TOKEN.findall("\n".join(source[d.start - 1 : d.end])))
            if total[d.name] - own[d.name] <= 0:
                found.append({"name": d.qualname, "kind": d.kind, "path": path, "line": d.start,
                              "tag": tag(d.name), "searched": searched})
        base_name = path.rsplit("/", 1)[-1]
        stem = base_name[:-3]
        if base_name in CONVENTION_FILES or is_test_file(path) or not TOKEN.fullmatch(stem):
            continue
        if total[stem] - counts[path][stem] <= 0:
            found.append({"name": base_name, "kind": "script", "path": path, "line": 1,
                          "tag": tag(stem), "searched": searched})
    return sorted(found, key=lambda c: (c["path"], c["line"], c["name"]))


# --- D9, leftovers -----------------------------------------------------------------------------


def unreferenced_files(files: dict[str, str], new_files: list[str], excluded: set[str]) -> list[str]:
    found = []
    for path in new_files:
        base_name = path.rsplit("/", 1)[-1]
        if path in excluded or path.endswith(".py") or base_name.startswith(".") or path not in files:
            continue
        if not any(base_name in text for other, text in files.items() if other != path):
            found.append(path)
    return sorted(found)


def _is_main_guard(node: ast.stmt) -> bool:
    if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
        return False
    sides = [node.test.left, *node.test.comparators]
    names = {s.id for s in sides if isinstance(s, ast.Name)}
    values = {s.value for s in sides if isinstance(s, ast.Constant)}
    return names == {"__name__"} and values == {"__main__"}


def print_calls(parsed: dict[str, ast.Module], added: dict[str, set[int]]) -> list[dict]:
    found = []

    def visit(node: ast.AST, path: str, lines: set[int], function: str | None, outer: str | None) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qual = f"{function}.{child.name}" if function else child.name
                visit(child, path, lines, qual, outer or child.name)
                continue
            if isinstance(child, ast.ClassDef):
                qual = f"{function}.{child.name}" if function else child.name
                visit(child, path, lines, qual, outer)
                continue
            if function is None and _is_main_guard(child):
                continue
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == "print" \
                    and child.lineno in lines and outer != "main":
                found.append({"path": path, "line": child.lineno, "function": function})
            visit(child, path, lines, function, outer)

    for path, tree in parsed.items():
        lines = added.get(path, set())
        if lines:
            visit(tree, path, lines, None, None)
    return sorted(found, key=lambda p: (p["path"], p["line"]))


# --- D10, markers ------------------------------------------------------------------------------


def markers(patches: list[FilePatch], excluded: set[str]) -> list[dict]:
    found = []
    for fp in patches:
        if fp.new is None or fp.new in excluded:
            continue
        for line_no, text in fp.added:
            match = MARKER.search(text)
            if match:
                found.append({"path": fp.new, "line": line_no, "marker": match.group(1), "text": text.strip()})
    return sorted(found, key=lambda m: (m["path"], m["line"]))


# --- the report ---------------------------------------------------------------------------------


def generated_paths(board: str) -> set[str]:
    folder = board.strip().replace("\\", "/").strip("/")
    return {f"{folder}/{name}" if folder and folder != "." else name for name in GENERATED}


def size_of(repo: Path, base: str, tip: str, excluded: set[str]) -> dict:
    rows = numstat(repo, base, tip)
    return {
        "raw": sum(a + d for a, d, _ in rows),
        "excluding_generated": sum(a + d for a, d, p in rows if p not in excluded),
    }


def report(repo: Path, base: str, tip: str, record: Path | None, board: str) -> dict:
    excluded = generated_paths(board)
    merges = record_merges(record.read_text(encoding="utf-8")) if record is not None else None
    units, ignored = build_units(repo, base, tip, merges)

    unit_of: dict[str, str] = {}
    per_unit: list[tuple[Unit, dict[str, list[int]]]] = []
    unit_rows = []
    for unit in units:
        for commit in unit.commits:
            unit_of.setdefault(commit, unit.id)
        files: dict[str, list[int]] = {}
        for old, new in unit.ranges:
            for a, d, path in numstat(repo, old, new):
                if path in excluded:
                    continue
                row = files.setdefault(path, [0, 0])
                row[0] += a
                row[1] += d
        per_unit.append((unit, files))
        unit_rows.append({
            "id": unit.id, "kind": unit.kind,
            "ranges": [f"{old}..{new}" for old, new in unit.ranges],
            "commits": sorted(unit.commits),
            "files": sorted(files),
            "added": sum(r[0] for r in files.values()),
            "deleted": sum(r[1] for r in files.values()),
        })

    patches = diff_patches(repo, base, tip)
    added: dict[str, set[int]] = {}
    new_files = []
    for fp in patches:
        if fp.new is not None:
            added[fp.new] = {n for n, _ in fp.added}
            if fp.old is None:
                new_files.append(fp.new)

    files = read_tree(repo, tip)
    parsed: dict[str, ast.Module] = {}
    unparsed = []
    for path, text in files.items():
        if path.endswith(".py"):
            try:
                parsed[path] = ast.parse(text)
            except SyntaxError:
                if added.get(path):
                    unparsed.append(path)

    return {
        "base": base,
        "tip": tip,
        "attribution": "record" if record is not None else "first-parent",
        "record": None if record is None else {"path": record.as_posix(), "ignored": ignored},
        "excluded": sorted(excluded),
        "size": size_of(repo, base, tip, excluded),
        "units": unit_rows,
        "churn": {
            "files": churn_files(per_unit),
            "rewritten": rewritten_lines(repo, base, tip, unit_of, excluded),
        },
        "clones": {
            "python": python_clones(parsed, added),
            "text": text_clones(files, added, excluded),
        },
        "dead_code": {"candidates": dead_code(files, parsed, added, tip)},
        "leftovers": {
            "unreferenced_files": unreferenced_files(files, new_files, excluded),
            "print_calls": print_calls(parsed, added),
        },
        "markers": markers(patches, excluded),
        "unparsed": sorted(unparsed),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--base", required=True, help="the tranche's base commit")
    parser.add_argument("--tip", required=True, help="the tranche's tip commit")
    parser.add_argument("--record", type=Path, default=None, help="the tranche record, to attribute commits to tasks")
    parser.add_argument("--board", default="tasks", help="the board folder whose generated indexes are left out")
    parser.add_argument("--size", action="store_true", help="print only the changed-line count, generated indexes left out")
    args = parser.parse_args(argv)

    try:
        base = resolve(args.repo, args.base)
        tip = resolve(args.repo, args.tip)
        if args.size:
            sys.stdout.write(f"{size_of(args.repo, base, tip, generated_paths(args.board))['excluding_generated']}\n")
            return 0
        result = report(args.repo, base, tip, args.record, args.board)
    except (GitError, OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
