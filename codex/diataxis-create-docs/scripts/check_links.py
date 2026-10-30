#!/usr/bin/env python3
"""Check repository-local links, anchors, and redirect destinations."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import unquote, urlsplit


FENCE_PATTERN = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,}).*$")
HEADING_PATTERN = re.compile(
    r"^ {0,3}#{1,6}[ \t]+(?P<title>.+?)[ \t]*$",
    re.MULTILINE,
)
EXPLICIT_ANCHOR_PATTERN = re.compile(
    r"""(?:\bid\s*=\s*["'](?P<html>[^"']+)["']|\{#(?P<markdown>[^}]+)\})"""
)
REFERENCE_DEFINITION_PATTERN = re.compile(
    r"^ {0,3}\[[^\]\n]+]:[ \t]*(?P<target><[^>\n]+>|[^\s]+)",
    re.MULTILINE,
)
TAG_PATTERN = re.compile(
    r"<(?P<tag>[A-Za-z][A-Za-z0-9_.:-]*)\b(?P<attrs>[^>]*)>",
    re.DOTALL,
)
QUOTED_ATTRIBUTE_PATTERN = re.compile(
    r"""\b(?P<name>href|src|to)\s*=\s*(?P<quote>["'])(?P<target>.*?)(?P=quote)""",
    re.IGNORECASE | re.DOTALL,
)
BRACED_ATTRIBUTE_PATTERN = re.compile(
    r"""\b(?P<name>href|src|to)\s*=\s*\{\s*(?P<quote>["'])(?P<target>.*?)(?P=quote)\s*\}""",
    re.IGNORECASE | re.DOTALL,
)
ALLOWED_EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel"}
DANGEROUS_SCHEMES = {"data", "javascript"}
EXCLUDED_DIRECTORY_NAMES = {
    ".cache",
    ".git",
    ".mypy_cache",
    ".next",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "cache",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "target",
    "vendor",
    "venv",
}
TEXT_SUFFIXES = {
    ".cfg",
    ".conf",
    ".cs",
    ".go",
    ".htm",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".md",
    ".markdown",
    ".mdx",
    ".php",
    ".ps1",
    ".py",
    ".rb",
    ".rst",
    ".rs",
    ".sh",
    ".svelte",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".vue",
    ".yaml",
    ".yml",
}


def is_linklike(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def excluded(relative: Path) -> bool:
    lowered = [part.lower() for part in relative.parts]
    if any(part in EXCLUDED_DIRECTORY_NAMES for part in lowered):
        return True
    return any(
        lowered[index : index + 2] == [".docs-migration", "archive"]
        for index in range(max(0, len(lowered) - 1))
    )


def relevant_text(path: Path) -> bool:
    name = path.name.lower()
    return path.suffix.lower() in TEXT_SUFFIXES or name == "readme" or name.startswith(
        "readme."
    )


def lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(path))


def relative_to_root(root: Path, path: Path, label: str) -> Path:
    lexical = lexical_absolute(path)
    try:
        return lexical.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label}: path escapes repository root") from error


def reject_link_components(root: Path, path: Path, label: str) -> None:
    relative = relative_to_root(root, path, label)
    current = root
    for part in relative.parts:
        current = current / part
        if is_linklike(current):
            raise ValueError(f"{label}: symlink or junction path is not allowed")


def safe_resolve(root: Path, path: Path, label: str) -> Path:
    lexical = lexical_absolute(path)
    relative_to_root(root, lexical, label)
    reject_link_components(root, lexical, label)
    resolved = lexical.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label}: resolved path escapes repository root") from error
    return lexical


def mask_fenced_blocks(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    output: list[str] = []
    fence_character: str | None = None
    fence_length = 0
    for line in normalized.splitlines(keepends=True):
        content = line.rstrip("\n")
        newline = "\n" if line.endswith("\n") else ""
        fence_match = FENCE_PATTERN.match(content)
        if fence_character is not None:
            closing = re.match(
                rf"^ {{0,3}}{re.escape(fence_character)}"
                rf"{{{fence_length},}}[ \t]*$",
                content,
            )
            output.append(" " * len(content) + newline)
            if closing:
                fence_character = None
                fence_length = 0
            continue
        if fence_match:
            fence = fence_match.group("fence")
            fence_character = fence[0]
            fence_length = len(fence)
            output.append(" " * len(content) + newline)
            continue
        output.append(line)
    return "".join(output)


def slugify(title: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", title)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = html.unescape(re.sub(r"<[^>]+>", "", text)).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="strict")
    visible = mask_fenced_blocks(text)
    result: set[str] = set()
    next_occurrence: dict[str, int] = {}
    for match in HEADING_PATTERN.finditer(visible):
        title = re.sub(r"[ \t]+#+[ \t]*$", "", match.group("title")).strip()
        base = slugify(title)
        if not base:
            continue
        occurrence = next_occurrence.get(base, 0)
        candidate = base if occurrence == 0 else f"{base}-{occurrence}"
        while candidate in result:
            occurrence += 1
            candidate = f"{base}-{occurrence}"
        next_occurrence[base] = occurrence + 1
        result.add(candidate)
    for match in EXPLICIT_ANCHOR_PATTERN.finditer(visible):
        result.add(match.group("html") or match.group("markdown"))
    return result


def inline_markdown_targets(text: str):
    index = 0
    while True:
        opening = text.find("](", index)
        if opening < 0:
            return
        start = opening + 2
        depth = 1
        quote: str | None = None
        angle = False
        escaped = False
        cursor = start
        while cursor < len(text):
            character = text[cursor]
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif quote:
                if character == quote:
                    quote = None
            elif character in {'"', "'"}:
                quote = character
            elif character == "<":
                angle = True
            elif character == ">" and angle:
                angle = False
            elif not angle and character == "(":
                depth += 1
            elif not angle and character == ")":
                depth -= 1
                if depth == 0:
                    yield text[start:cursor]
                    index = cursor + 1
                    break
            cursor += 1
        else:
            index = start


def strip_optional_title(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<"):
        closing = value.find(">")
        if closing >= 0:
            return value[1:closing]
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if character == "\\":
            escaped = True
            continue
        if character.isspace():
            value = value[:index]
            break
    return re.sub(r"\\([\\() ])", r"\1", value)


def tag_targets(text: str):
    for tag_match in TAG_PATTERN.finditer(text):
        tag = tag_match.group("tag").lower()
        attributes = tag_match.group("attrs")
        for pattern in (QUOTED_ATTRIBUTE_PATTERN, BRACED_ATTRIBUTE_PATTERN):
            for attribute in pattern.finditer(attributes):
                name = attribute.group("name").lower()
                if name == "to" and not tag.endswith("link"):
                    continue
                yield attribute.group("target")


def extract_targets(text: str) -> list[str]:
    visible = mask_fenced_blocks(text)
    targets = list(inline_markdown_targets(visible))
    targets.extend(
        match.group("target")
        for match in REFERENCE_DEFINITION_PATTERN.finditer(visible)
    )
    targets.extend(tag_targets(visible))
    return list(dict.fromkeys(targets))


def git_tracked_paths(root: Path) -> list[Path] | None:
    try:
        top = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=10,
            check=True,
        ).stdout.strip()
        if Path(top).resolve() != root:
            return None
        output = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "-z",
            ],
            capture_output=True,
            timeout=10,
            check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return None
    return [
        root / value.decode("utf-8", errors="strict")
        for value in output.split(b"\0")
        if value
    ]


def fallback_paths(root: Path) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    errors: list[str] = []
    stack = [root]
    while stack:
        directory = stack.pop()
        try:
            children = sorted(directory.iterdir(), key=lambda item: item.name)
        except OSError as error:
            errors.append(f"{directory}: cannot list directory: {error}")
            continue
        for child in children:
            relative = child.relative_to(root)
            if excluded(relative):
                continue
            if is_linklike(child):
                errors.append(
                    f"{relative.as_posix()}: symlink or junction source is not read"
                )
                continue
            try:
                resolved = child.resolve()
                resolved.relative_to(root)
            except (OSError, ValueError):
                errors.append(
                    f"{relative.as_posix()}: resolved source escapes repository root"
                )
                continue
            if child.is_dir():
                stack.append(child)
            elif child.is_file() and relevant_text(child):
                files.append(child)
    return sorted(files), errors


def discover_text_paths(root: Path) -> tuple[list[Path], list[str]]:
    tracked = git_tracked_paths(root)
    if tracked is None:
        return fallback_paths(root)
    files: list[Path] = []
    errors: list[str] = []
    for path in tracked:
        try:
            relative = relative_to_root(root, path, str(path))
        except ValueError as error:
            errors.append(str(error))
            continue
        if excluded(relative) or not relevant_text(path) or not path.exists():
            continue
        try:
            safe_resolve(root, path, relative.as_posix())
        except ValueError as error:
            errors.append(str(error))
            continue
        if path.is_file():
            files.append(path)
    return sorted(files), errors


def candidate_files(path: Path) -> list[Path]:
    candidates = [path]
    if not path.suffix:
        candidates.extend(
            [
                path.with_suffix(".md"),
                path.with_suffix(".mdx"),
                path / "README.md",
                path / "README.mdx",
                path / "index.md",
                path / "index.mdx",
            ]
        )
    return candidates


def resolve_target(
    repository_root: Path,
    docs_root: Path,
    source: Path,
    raw_target: str,
) -> tuple[Path | None, str | None, str | None]:
    target = strip_optional_title(raw_target)
    parsed = urlsplit(target)
    scheme = parsed.scheme.lower()
    if scheme in DANGEROUS_SCHEMES:
        return None, None, f"unsafe scheme {scheme}:"
    if scheme in ALLOWED_EXTERNAL_SCHEMES:
        return None, None, None
    if scheme:
        return None, None, f"unsupported scheme {scheme}:"
    if target.startswith("//"):
        return None, None, "protocol-relative external targets are not allowed"
    if not parsed.path:
        return source, unquote(parsed.fragment) or None, None

    decoded_path = unquote(parsed.path)
    if "\x00" in decoded_path:
        return None, None, "target contains a null byte"
    windows_path = PureWindowsPath(decoded_path)
    if windows_path.is_absolute() or windows_path.drive:
        return None, None, f"unsafe absolute target: {decoded_path}"
    normalized = decoded_path.replace("\\", "/")
    relative = PurePosixPath(normalized.lstrip("/"))
    base = docs_root if decoded_path.startswith("/") else source.parent
    direct = base.joinpath(*relative.parts)

    for candidate in candidate_files(direct):
        try:
            safe = safe_resolve(
                repository_root,
                candidate,
                candidate.relative_to(repository_root).as_posix()
                if candidate.is_relative_to(repository_root)
                else str(candidate),
            )
        except ValueError as error:
            return None, None, str(error)
        if safe.is_file():
            return safe, unquote(parsed.fragment) or None, None
    return direct, unquote(parsed.fragment) or None, "missing target"


def load_redirect_destinations(path: Path) -> list[str]:
    value = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    if isinstance(value, list):
        destinations = [
            item.get("destination")
            for item in value
            if isinstance(item, dict) and isinstance(item.get("destination"), str)
        ]
    elif isinstance(value, dict):
        destinations = [item for item in value.values() if isinstance(item, str)]
    else:
        raise ValueError("redirect file must contain an array or object")
    return sorted(destinations)


def check_target(
    repository_root: Path,
    docs_root: Path,
    source: Path,
    raw_target: str,
    source_label: str,
) -> list[str]:
    target, anchor, problem = resolve_target(
        repository_root,
        docs_root,
        source,
        raw_target,
    )
    if problem:
        return [f"{source_label}: {raw_target}: {problem}"]
    if target is None or not anchor:
        return []
    try:
        available = anchors(target)
    except (OSError, UnicodeError) as error:
        return [f"{source_label}: {raw_target}: cannot read anchors: {error}"]
    if anchor not in available:
        return [f"{source_label}: {raw_target}: missing anchor #{anchor}"]
    return []


def check_links(
    repository_root: Path,
    docs_root: Path,
    redirects_path: Path | None,
) -> list[str]:
    sources, errors = discover_text_paths(repository_root)
    for source in sources:
        display_source = source.relative_to(repository_root).as_posix()
        try:
            text = source.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError) as error:
            errors.append(f"{display_source}: cannot read tracked text: {error}")
            continue
        for raw_target in extract_targets(text):
            errors.extend(
                check_target(
                    repository_root,
                    docs_root,
                    source,
                    raw_target,
                    display_source,
                )
            )

    if redirects_path:
        try:
            safe_resolve(repository_root, redirects_path, str(redirects_path))
            destinations = load_redirect_destinations(redirects_path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
            errors.append(f"{redirects_path}: cannot read redirects: {error}")
            destinations = []
        synthetic_source = docs_root / "index.md"
        for destination in destinations:
            errors.extend(
                check_target(
                    repository_root,
                    docs_root,
                    synthetic_source,
                    destination,
                    f"redirect {destination}",
                )
            )
    return sorted(set(errors))


def cli_relative(root: Path, value: Path, label: str) -> Path:
    raw = str(value)
    windows = PureWindowsPath(raw)
    if value.is_absolute() or windows.is_absolute() or windows.drive:
        raise ValueError(f"{label}: path must be relative to --root")
    return safe_resolve(root, root / value, label)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check repository-local links and optional redirect targets."
    )
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--docs", required=True, type=Path)
    parser.add_argument("--redirects", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    try:
        if is_linklike(args.root):
            raise ValueError(f"{args.root}: repository root cannot be a symlink")
        root = args.root.resolve(strict=True)
        docs = cli_relative(root, args.docs, "--docs")
        if not docs.is_dir():
            raise ValueError(f"{docs}: docs path is not a directory")
        redirects = (
            cli_relative(root, args.redirects, "--redirects")
            if args.redirects
            else None
        )
        errors = check_links(root, docs, redirects)
    except (OSError, UnicodeError, ValueError) as error:
        errors = [str(error)]

    if args.as_json:
        print(json.dumps({"broken": len(errors), "errors": errors}, indent=2))
    elif errors:
        print(f"{len(errors)} broken links or redirects:")
        for error in errors:
            print(f"- {error}")
    else:
        print("0 broken links or redirects.")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
