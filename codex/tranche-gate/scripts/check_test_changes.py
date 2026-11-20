#!/usr/bin/env python3
"""Check what a stream did to the tests it started with.

The supervisor's integrator runs this between a lease's starting commit and
the stream's tip, with the list of test changes the worker declared, and gets
one JSON verdict:

- **deleted**: tests at the base that are gone at the tip. A test whose body
  reappears under another name or file is **moved**, not deleted.
- **markers**: skip, expected-failure and focus markers added to a test that
  existed at the base. A focus marker (`.only`, `fit`, `fdescribe`) is flagged
  on any test, new ones included, because it disables the others.
- **changed**: tests whose body changed, for the integrator to judge for
  weakening. Formatting alone is not a change for Python, which is compared
  by its syntax tree.
- **unparsed**: test files in the change where no test could be found. They
  are never reported clean.

    scripts/check_test_changes.py --repo . --base <lease-start> --tip <stream-tip> \\
        --declared declared.json

The declared list is JSON: `[{"test": "<path>::<name>", "change":
"deleted|skipped|focused", "reason": "..."}]`, where `<path>::*` covers every
test in a file. **Anything found and not declared makes the verdict
`blocked`**: the integrator returns the stream unmerged. Otherwise the verdict
is `judge` when anything was declared, changed or unparsed, and `clean` when
nothing was.

The tranche gate checks a whole tranche against every merged attempt's
declarations at once:

    scripts/check_test_changes.py --repo . --base <tranche-base> --tip <tranche-tip> \\
        --declared-dir <run-state>/declared --record <board>/<tranche-record>.md

It reads the record's `merged <sha>` integrator verdicts with
`scan_tranche.py`'s parser and loads `<task>-<attempt>.json` for each, its
entries' `reason` prefixed with the task id. A file with no merged verdict is
left out, so a declaration for a change that never landed explains nothing; a
merged verdict with no file contributes nothing. `declared_files` lists the
files loaded and missing. `--declared-dir` and `--record` go together, and
neither goes with `--declared`.

Python is parsed exactly with `ast`; JS/TS and Go are found by anchored
patterns, each only in its own language's test files. `--language` and
`--marker` add a language and its markers for one run.

Standard library and `git` only, deterministic. Exits 0 with a verdict, 2 when
the repository, a commit or the declared list cannot be read.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from scan_tranche import merged_attempts


@dataclass
class Test:
    body: str
    markers: set[tuple[str, str]] = field(default_factory=set)  # (kind, marker)


Parsed = dict[str, Test]  # test name -> test; None from a parser means unparsed

SKIPPED, FOCUSED = "skipped", "focused"


def _squash(text: str) -> str:
    return re.sub(r"\s+", "", text)


# --- Python, by syntax tree --------------------------------------------------

PY_SKIP_DECORATORS = {
    "mark.skip", "mark.skipif", "mark.xfail",
    "unittest.skip", "unittest.skipIf", "unittest.skipUnless", "unittest.expectedFailure",
    "skip", "skipIf", "skipUnless", "expectedFailure",
}
PY_SKIP_CALLS = {"pytest.skip", "pytest.xfail", "self.skipTest"}


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Call):
        node = node.func
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def _decorator_markers(decorators: list[ast.expr]) -> set[tuple[str, str]]:
    found = set()
    for decorator in decorators:
        name = _dotted(decorator)
        if any(name == d or name.endswith("." + d) for d in PY_SKIP_DECORATORS):
            found.add((SKIPPED, name))
    return found


def _python_test(node: ast.FunctionDef | ast.AsyncFunctionDef, inherited: set) -> Test:
    markers = set(inherited) | _decorator_markers(node.decorator_list)
    for inner in ast.walk(node):
        if isinstance(inner, ast.Call) and _dotted(inner) in PY_SKIP_CALLS:
            markers.add((SKIPPED, _dotted(inner)))
    body = ast.unparse(ast.Module(body=node.body, type_ignores=[]))
    return Test(body=body, markers=markers)


def parse_python(text: str) -> Parsed | None:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    module_markers: set[tuple[str, str]] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "pytestmark" for t in node.targets
        ):
            for inner in ast.walk(node.value):
                name = _dotted(inner)
                if any(name.endswith(d) for d in ("mark.skip", "mark.skipif", "mark.xfail")):
                    module_markers.add((SKIPPED, "pytestmark=" + name))
    tests: Parsed = {}
    functions = (ast.FunctionDef, ast.AsyncFunctionDef)
    for node in tree.body:
        if isinstance(node, functions) and node.name.startswith("test"):
            tests[node.name] = _python_test(node, module_markers)
        elif isinstance(node, ast.ClassDef):
            inherited = module_markers | _decorator_markers(node.decorator_list)
            for item in node.body:
                if isinstance(item, functions) and item.name.startswith("test"):
                    tests[f"{node.name}::{item.name}"] = _python_test(item, inherited)
    return tests


# --- line-based helpers --------------------------------------------------------


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def _block_end(lines: list[str], start: int, indent: int, strict: bool) -> int:
    """Index of the first nonblank line after `start` that leaves the block."""
    for i in range(start + 1, len(lines)):
        if not lines[i].strip():
            continue
        level = _indent(lines[i])
        if level < indent or (strict and level <= indent):
            return i
    return len(lines)


def _unique(tests: Parsed, name: str) -> str:
    if name not in tests:
        return name
    n = 2
    while f"{name}#{n}" in tests:
        n += 1
    return f"{name}#{n}"


# --- JS/TS, by anchored pattern ---------------------------------------------------

JS_TEST = re.compile(
    r"^(?P<indent>[ \t]*)(?P<prefix>x|f)?(?P<fn>it|test)"
    r"(?P<mods>(?:\.(?:skip|only|todo|fixme|fail|failing|concurrent|serial))*)"
    r"\s*\(\s*(?P<q>['\"`])(?P<name>(?:\\.|(?!(?P=q)).)*)(?P=q)"
)
JS_DESCRIBE = re.compile(
    r"^(?P<indent>[ \t]*)(?:test\.)?(?P<prefix>x|f)?(?:describe|context|suite)"
    r"(?P<mods>(?:\.(?:skip|only|fixme|serial|parallel))*)\s*\("
)
JS_RUNTIME = re.compile(r"^(?P<indent>[ \t]*)test\.(?P<mod>skip|fixme|fail)\s*\((?!\s*['\"`])")


def _js_kind(prefix: str | None, mods: str) -> str | None:
    words = set(mods.strip(".").split(".")) if mods else set()
    if prefix == "f" or "only" in words:
        return FOCUSED
    if prefix == "x" or words & {"skip", "todo", "fixme", "fail", "failing"}:
        return SKIPPED
    return None


def parse_js(text: str) -> Parsed | None:
    lines = text.splitlines()
    tests: Parsed = {}
    spans: list[tuple[str, int, int]] = []  # name, first line, end (exclusive)
    for i, line in enumerate(lines):
        match = JS_TEST.match(line)
        if not match:
            continue
        indent = len(match.group("indent"))
        end = _block_end(lines, i, indent, strict=True)
        name = _unique(tests, match.group("name"))
        head = line[: match.start("name")] + line[match.end("name"):]
        tests[name] = Test(body=_squash("\n".join([head, *lines[i + 1 : end]])))
        kind = _js_kind(match.group("prefix"), match.group("mods"))
        if kind:
            tests[name].markers.add((kind, line.strip()[: match.end("mods") - len(match.group("indent"))]))
        spans.append((name, i, end))
    for i, line in enumerate(lines):
        scoped = JS_DESCRIBE.match(line)
        if scoped:
            kind = _js_kind(scoped.group("prefix"), scoped.group("mods"))
            if kind:
                end = _block_end(lines, i, len(scoped.group("indent")), strict=True)
                marker = line.strip().split("(", 1)[0]
                for name, first, _ in spans:
                    if i < first < end:
                        tests[name].markers.add((kind, marker))
            continue
        runtime = JS_RUNTIME.match(line)
        if runtime:
            marker = f"test.{runtime.group('mod')}()"
            owner = [name for name, first, end in spans if first < i < end]
            if owner:
                tests[owner[-1]].markers.add((SKIPPED, marker))
            else:
                end = _block_end(lines, i, len(runtime.group("indent")), strict=False)
                for name, first, _ in spans:
                    if i < first < end:
                        tests[name].markers.add((SKIPPED, marker))
    return tests


# --- Go, by anchored pattern ----------------------------------------------------------

GO_TEST = re.compile(r"^func\s+(?P<name>Test\w*)\s*\(\s*(?P<recv>\w+)\s+\*testing\.T\s*\)")
GO_BUILD = re.compile(r"^//\s*(?:go:build|\+build)\b.*")


def parse_go(text: str) -> Parsed | None:
    lines = text.splitlines()
    file_markers = {(SKIPPED, m.group(0).strip()) for line in lines if (m := GO_BUILD.match(line))}
    starts = [i for i, line in enumerate(lines) if GO_TEST.match(line)]
    funcs = [i for i, line in enumerate(lines) if line.startswith("func ")]
    tests: Parsed = {}
    for i in starts:
        match = GO_TEST.match(lines[i])
        end = next((f for f in funcs if f > i), len(lines))
        body_lines = lines[i + 1 : end]
        skip = re.compile(rf"\b{re.escape(match.group('recv'))}\.Skip(?:f|Now)?\(")
        markers = set(file_markers)
        if any(skip.search(line) for line in body_lines):
            markers.add((SKIPPED, f"{match.group('recv')}.Skip"))
        head = lines[i][: match.start("name")] + lines[i][match.end("name"):]
        name = _unique(tests, match.group("name"))
        tests[name] = Test(body=_squash("\n".join([head, *body_lines])), markers=markers)
    return tests


# --- languages ---------------------------------------------------------------------------


@dataclass
class Language:
    name: str
    files: re.Pattern
    parse: object  # Callable[[str], Parsed | None]


def generic_parser(test_re: re.Pattern, markers: list[tuple[str, re.Pattern]]):
    """A language added for one run: tests by pattern, markers in each test's block.

    A test's block runs from the attributes, annotations or comments directly
    above it to the line before the next test.
    """

    def parse(text: str) -> Parsed | None:
        lines = text.splitlines()
        starts = [i for i, line in enumerate(lines) if test_re.match(line)]
        leads = []
        for i in starts:
            j = i
            while j > 0 and lines[j - 1].strip().startswith(("#", "@", "//", "[")):
                j -= 1
            leads.append(j)
        tests: Parsed = {}
        for n, i in enumerate(starts):
            end = leads[n + 1] if n + 1 < len(starts) else len(lines)
            block = lines[leads[n] : end]
            match = test_re.match(lines[i])
            head = lines[i][: match.start("name")] + lines[i][match.end("name"):]
            found = {(kind, pattern.pattern) for kind, pattern in markers if any(pattern.search(b) for b in block)}
            body = [line for line in lines[i + 1 : end]]
            name = _unique(tests, match.group("name"))
            tests[name] = Test(body=_squash("\n".join([head, *body])), markers=found)
        return tests

    return parse


DEFAULT_LANGUAGES = [
    Language("python", re.compile(r"(^|/)(test_[^/]*|[^/]*_test)\.py$"), parse_python),
    Language("js", re.compile(r"(\.(test|spec)\.[cm]?[jt]sx?$)|((^|/)__tests__/.*\.[cm]?[jt]sx?$)"), parse_js),
    Language("go", re.compile(r"_test\.go$"), parse_go),
]


def language_for(path: str, languages: list[Language]) -> Language | None:
    return next((lang for lang in languages if lang.files.search(path)), None)


# --- git ---------------------------------------------------------------------------------


class GitError(Exception):
    pass


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if result.returncode != 0:
        raise GitError(result.stderr.decode("utf-8", "replace").strip() or f"git {args[0]} failed")
    return result.stdout


def changed_files(repo: Path, base: str, tip: str) -> list[tuple[str, str | None, str | None]]:
    """(status, base path, tip path) for every file the change touched."""
    out = git(repo, "diff", "--name-status", "-z", "-M", base, tip).decode("utf-8", "replace")
    fields = [f for f in out.split("\0") if f]
    entries = []
    i = 0
    while i < len(fields):
        status = fields[i]
        if status[0] in "RC":
            entries.append((status[0], fields[i + 1], fields[i + 2]))
            i += 3
            continue
        path = fields[i + 1]
        entries.append((status[0], None if status[0] == "A" else path, None if status[0] == "D" else path))
        i += 2
    return entries


def content(repo: Path, commit: str, path: str) -> str:
    return git(repo, "show", f"{commit}:{path}").decode("utf-8", "replace")


# --- the verdict ---------------------------------------------------------------------------


def covers(entry: dict, test_id: str, change: str) -> bool:
    if entry.get("change") != change:
        return False
    name = str(entry.get("test", ""))
    return name == test_id or (name.endswith("::*") and test_id.startswith(name[:-1]))


def verdict(repo: Path, base: str, tip: str, declared: list[dict], languages: list[Language]) -> dict:
    before: dict[str, Test] = {}  # test id at the tip's path -> base test
    after: dict[str, Test] = {}
    base_ids: dict[str, str] = {}  # id at tip path -> id at base path, for reporting
    unparsed: list[str] = []
    for status, old, new in changed_files(repo, base, tip):
        lang = language_for(new or old, languages)
        if lang is None:
            continue
        tip_path = new or old
        if old is not None:
            parsed = lang.parse(content(repo, base, old)) or {}
            for name, test in parsed.items():
                key = f"{tip_path}::{name}"
                before[key] = test
                base_ids[key] = f"{old}::{name}"
        if new is not None:
            text = content(repo, tip, new)
            parsed = lang.parse(text)
            if parsed is None or (not parsed and text.strip()):
                unparsed.append(new)
                parsed = parsed or {}
            for name, test in parsed.items():
                after[f"{new}::{name}"] = test

    gone = sorted(set(before) - set(after))
    new_ids = sorted(set(after) - set(before))
    moved: list[dict] = []
    deleted_ids: list[str] = []
    claimed: set[str] = set()
    origin: dict[str, Test] = {}
    for key in gone:
        twin = next((n for n in new_ids if n not in claimed and after[n].body == before[key].body), None)
        if twin:
            claimed.add(twin)
            origin[twin] = before[key]
            moved.append({"from": base_ids[key], "to": twin})
        else:
            deleted_ids.append(base_ids[key])

    marker_rows: list[tuple[str, str, str]] = []  # test, kind, marker
    changed: list[str] = []
    for key in sorted(after):
        test = after[key]
        source = before.get(key) or origin.get(key)
        if source is None:  # a new test: only focus matters
            added = {m for m in test.markers if m[0] == FOCUSED}
        else:
            added = test.markers - source.markers
            if key in before and test.body != source.body:
                changed.append(key)
        marker_rows += [(key, kind, marker) for kind, marker in sorted(added)]

    used: set[int] = set()

    def declared_for(test_id: str, change: str) -> dict | None:
        for n, entry in enumerate(declared):
            if covers(entry, test_id, change):
                used.add(n)
                return entry
        return None

    def row(base_row: dict, entry: dict | None) -> dict:
        base_row["declared"] = entry is not None
        if entry is not None:
            base_row["reason"] = str(entry.get("reason", ""))
        return base_row

    deleted = [row({"test": t}, declared_for(t, "deleted")) for t in deleted_ids]
    markers = [
        row({"test": t, "kind": kind, "marker": marker}, declared_for(t, kind))
        for t, kind, marker in marker_rows
    ]
    flagged = deleted + markers
    if any(not r["declared"] for r in flagged):
        result = "blocked"
    elif flagged or changed or unparsed:
        result = "judge"
    else:
        result = "clean"
    return {
        "base": base,
        "tip": tip,
        "verdict": result,
        "deleted": deleted,
        "moved": moved,
        "markers": markers,
        "changed": changed,
        "unparsed": sorted(unparsed),
        "declared_unmatched": sorted(
            str(e.get("test", "")) for n, e in enumerate(declared) if n not in used
        ),
    }


def read_declared(path: Path) -> list:
    declared = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(declared, list):
        raise ValueError(f"the declared list must be a JSON array: {path.name}")
    return declared


def tranche_declared(directory: Path, record: Path) -> tuple[list[dict], dict]:
    """Every merged attempt's declarations, each reason prefixed with its task id.

    Returns the union and `declared_files`: the file names loaded and missing.
    """
    declared: list[dict] = []
    loaded: list[str] = []
    missing: list[str] = []
    for task, attempt, _ in merged_attempts(record.read_text(encoding="utf-8")):
        name = f"{task}-{attempt}.json"
        if name in loaded or name in missing:
            continue
        path = directory / name
        if not path.is_file():
            missing.append(name)
            continue
        loaded.append(name)
        for entry in read_declared(path):
            if not isinstance(entry, dict):
                raise ValueError(f"a declared entry must be a JSON object: {name}")
            declared.append({**entry, "reason": f"{task}: {entry.get('reason', '')}"})
    return declared, {"loaded": loaded, "missing": missing}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--base", required=True, help="the lease's starting commit")
    parser.add_argument("--tip", required=True, help="the stream's tip commit")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--declared", type=Path, default=None, help="the worker's declared changes (JSON)")
    source.add_argument(
        "--declared-dir", type=Path, default=None,
        help="a tranche's declared files, <task>-<attempt>.json; needs --record",
    )
    parser.add_argument(
        "--record", type=Path, default=None,
        help="the tranche record whose merged verdicts pick the declared files",
    )
    parser.add_argument(
        "--language", action="append", default=[], metavar="NAME:FILE_REGEX:TEST_REGEX",
        help="add a language for this run; TEST_REGEX needs a (?P<name>...) group (repeatable)",
    )
    parser.add_argument(
        "--marker", action="append", default=[], metavar="NAME:KIND:REGEX",
        help="add a marker (KIND skipped or focused) to an added language (repeatable)",
    )
    args = parser.parse_args(argv)
    if (args.declared_dir is None) != (args.record is None):
        parser.error("--declared-dir and --record go together")

    try:
        extra_markers: dict[str, list[tuple[str, re.Pattern]]] = {}
        for spec in args.marker:
            name, kind, pattern = spec.split(":", 2)
            if kind not in (SKIPPED, FOCUSED):
                raise ValueError(f"marker kind must be {SKIPPED} or {FOCUSED}: {kind}")
            extra_markers.setdefault(name, []).append((kind, re.compile(pattern)))
        languages = list(DEFAULT_LANGUAGES)
        for spec in args.language:
            name, files, tests = spec.split(":", 2)
            test_re = re.compile(tests)
            if "name" not in test_re.groupindex:
                raise ValueError(f"--language {name}: the test pattern needs a (?P<name>...) group")
            languages.insert(0, Language(name, re.compile(files), generic_parser(test_re, extra_markers.get(name, []))))
        declared = []
        files = None
        if args.declared is not None:
            declared = read_declared(args.declared)
        elif args.declared_dir is not None:
            declared, files = tranche_declared(args.declared_dir, args.record)
        for commit in (args.base, args.tip):
            git(args.repo, "rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}")
        result = verdict(args.repo, args.base, args.tip, declared, languages)
        if files is not None:
            result["declared_files"] = files
    except (GitError, ValueError, OSError, re.error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
