#!/usr/bin/env python3
"""Verify archived Markdown sections against the lifecycle section ledger."""

from __future__ import annotations

import argparse
import html
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

import yaml


HEADING_PATTERN = re.compile(
    r"^ {0,3}(?P<marks>#{2,6})[ \t]+(?P<title>.+?)[ \t]*$"
)
SETEXT_PATTERN = re.compile(r"^ {0,3}(?P<marks>=+|-+)[ \t]*$")
FENCE_PATTERN = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,}).*$")
FINGERPRINT_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
SECTION_ID_PATTERN = re.compile(
    r"^(?:__preamble__|[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
PORTABLE_INVALID_CHARS = re.compile(r'[<>:"|?*\x00-\x1f]')
WINDOWS_RESERVED_NAMES = {
    "AUX",
    "CON",
    "NUL",
    "PRN",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


@dataclass(frozen=True)
class Heading:
    start: int
    level: int
    title: str


@dataclass(frozen=True)
class Section:
    identifier: str
    fingerprint: str


def section_id(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "section"


def fingerprint(value: str) -> str:
    canonical = value.strip() + "\n"
    digest = hashlib.sha256(canonical.encode("utf-8", errors="strict")).hexdigest()
    return f"sha256:{digest}"


def markdown_headings(markdown: str) -> tuple[str, list[Heading]]:
    normalized = markdown.replace("\r\n", "\n").replace("\r", "\n")
    headings: list[Heading] = []
    lines = normalized.splitlines(keepends=True)
    offsets: list[int] = []
    offset = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line)
    fence_character: str | None = None
    fence_length = 0

    for index, line in enumerate(lines):
        content = line.rstrip("\n")
        fence_match = FENCE_PATTERN.match(content)
        if fence_character is not None:
            closing = re.match(
                rf"^ {{0,3}}{re.escape(fence_character)}"
                rf"{{{fence_length},}}[ \t]*$",
                content,
            )
            if closing:
                fence_character = None
                fence_length = 0
            continue
        if fence_match:
            fence = fence_match.group("fence")
            fence_character = fence[0]
            fence_length = len(fence)
            continue
        heading_match = HEADING_PATTERN.match(content)
        if heading_match:
            title = re.sub(
                r"[ \t]+#+[ \t]*$",
                "",
                heading_match.group("title"),
            ).strip()
            headings.append(
                Heading(
                    start=offsets[index],
                    level=len(heading_match.group("marks")),
                    title=title,
                )
            )
            continue
        setext_match = SETEXT_PATTERN.match(content)
        if setext_match and index > 0:
            previous = lines[index - 1].rstrip("\n")
            if previous.strip():
                headings.append(
                    Heading(
                        start=offsets[index - 1],
                        level=1 if setext_match.group("marks").startswith("=") else 2,
                        title=previous.strip(),
                    )
                )
    return normalized, headings


def markdown_sections(markdown: str) -> list[Section]:
    normalized, headings = markdown_headings(markdown)
    sections: list[Section] = []
    if headings:
        preamble = normalized[: headings[0].start]
    else:
        preamble = normalized
    if preamble.strip():
        sections.append(Section("__preamble__", fingerprint(preamble)))

    used_ids: set[str] = set()
    next_occurrence: dict[str, int] = {}
    for index, heading in enumerate(headings):
        end = len(normalized)
        for next_heading in headings[index + 1 :]:
            if next_heading.level <= heading.level:
                end = next_heading.start
                break
        base = section_id(heading.title)
        occurrence = next_occurrence.get(base, 1)
        candidate = base if occurrence == 1 else f"{base}-{occurrence}"
        while candidate in used_ids:
            occurrence += 1
            candidate = f"{base}-{occurrence}"
        next_occurrence[base] = occurrence + 1
        used_ids.add(candidate)
        sections.append(
            Section(
                identifier=candidate,
                fingerprint=fingerprint(normalized[heading.start : end]),
            )
        )
    return sections


def markdown_section_fingerprints(markdown: str) -> dict[str, str]:
    """Return stable occurrence-qualified section fingerprints."""
    return {section.identifier: section.fingerprint for section in markdown_sections(markdown)}


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise ValueError(f"{path}: cannot read YAML: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path}: manifest root must be an object")
    return value


def safe_relative(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{label}: path must be a nonempty trimmed string")
    normalized = value.replace("\\", "/")
    posix = PurePosixPath(normalized)
    windows = PureWindowsPath(value)
    if posix.is_absolute() or windows.is_absolute() or windows.drive:
        raise ValueError(f"{label}: path must be relative")
    if "//" in normalized or any(part in {"", ".", ".."} for part in posix.parts):
        raise ValueError(f"{label}: path contains empty, dot, or traversal segments")
    for part in posix.parts:
        if PORTABLE_INVALID_CHARS.search(part):
            raise ValueError(f"{label}: path contains nonportable characters")
        if (
            part.endswith((" ", "."))
            or part.split(".", 1)[0].upper() in WINDOWS_RESERVED_NAMES
        ):
            raise ValueError(f"{label}: path contains a nonportable segment")
    return Path(*posix.parts)


def is_linklike(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def ensure_beneath(root: Path, path: Path, label: str) -> Path:
    resolved_root = root.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"{label}: resolved path escapes archive root") from error
    return resolved


def reject_link_components(root: Path, relative: Path, label: str) -> None:
    current = root
    for part in relative.parts:
        current = current / part
        if current.exists() and is_linklike(current):
            raise ValueError(f"{label}: symlink or junction sources are not allowed")


def archive_sections(root: Path) -> tuple[dict[tuple[str, str], str], list[str]]:
    sections: dict[tuple[str, str], str] = {}
    errors: list[str] = []
    resolved_root = root.resolve()
    stack = [root]

    while stack:
        directory = stack.pop()
        try:
            children = sorted(directory.iterdir(), key=lambda item: item.name)
        except OSError as error:
            relative = directory.relative_to(root).as_posix() or "."
            errors.append(f"{relative}: cannot list archive directory: {error}")
            continue
        for path in children:
            relative = path.relative_to(root)
            display = relative.as_posix()
            if is_linklike(path):
                errors.append(
                    f"{display}: symlink or junction archive sources are not allowed"
                )
                continue
            try:
                resolved = path.resolve()
                resolved.relative_to(resolved_root)
            except (OSError, ValueError):
                errors.append(f"{display}: resolved path escapes archive root")
                continue
            if path.is_dir():
                stack.append(path)
                continue
            if not path.is_file() or path.suffix.lower() not in {".md", ".mdx"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="strict")
            except (OSError, UnicodeError) as error:
                errors.append(f"{display}: cannot read archived document: {error}")
                continue
            for section in markdown_sections(text):
                key = (display, section.identifier)
                if key in sections:
                    errors.append(
                        f"{display}#{section.identifier}: duplicate section identity"
                    )
                sections[key] = section.fingerprint
    return sections, errors


def ledger_semantic_errors(
    entry: dict[str, Any],
    index: int,
    archive_root: Path,
    repository_root: Path | None,
) -> tuple[tuple[str, str] | None, str | None, list[str]]:
    errors: list[str] = []
    label = f"section_ledger[{index}]"
    try:
        relative = safe_relative(entry["source_path"], f"{label}.source_path")
        reject_link_components(archive_root, relative, f"{label}.source_path")
        source = archive_root / relative
        ensure_beneath(archive_root, source, f"{label}.source_path")
        if not source.is_file():
            errors.append(f"{label}.source_path: archived source file is missing")
        identifier = str(entry["section_id"])
        if not SECTION_ID_PATTERN.fullmatch(identifier):
            errors.append(f"{label}.section_id: invalid stable section ID")
        fingerprint_value = str(entry["source_fingerprint"])
        if not FINGERPRINT_PATTERN.fullmatch(fingerprint_value):
            errors.append(f"{label}.source_fingerprint: invalid SHA-256 fingerprint")
    except (KeyError, ValueError) as error:
        errors.append(f"{label}: {error}")
        return None, None, errors

    disposition = entry.get("disposition")
    if disposition not in {"migrated", "retired", "blocked"}:
        errors.append(f"{label}.disposition: invalid disposition")
    destination = entry.get("destination_path")
    if disposition == "migrated":
        if not isinstance(destination, str) or not destination.strip():
            errors.append(
                f"{label}: migrated disposition requires destination_path"
            )
        else:
            try:
                destination_relative = safe_relative(
                    destination,
                    f"{label}.destination_path",
                )
                if repository_root is not None:
                    reject_link_components(
                        repository_root,
                        destination_relative,
                        f"{label}.destination_path",
                    )
                    destination_file = repository_root / destination_relative
                    ensure_beneath(
                        repository_root,
                        destination_file,
                        f"{label}.destination_path",
                    )
                    if not destination_file.is_file():
                        errors.append(
                            f"{label}.destination_path: destination file is missing"
                        )
                    else:
                        anchor = entry.get("destination_anchor")
                        if isinstance(anchor, str) and anchor.strip():
                            available = destination_anchors(destination_file)
                            if anchor not in available:
                                errors.append(
                                    f"{label}.destination_anchor: missing anchor "
                                    f"#{anchor}"
                                )
            except ValueError as error:
                errors.append(str(error))
    reason = entry.get("notes") or entry.get("reason")
    if disposition in {"retired", "blocked"} and not (
        isinstance(reason, str) and reason.strip()
    ):
        errors.append(
            f"{label}: {disposition} disposition requires nonempty notes or reason"
        )
    key = (relative.as_posix(), identifier)
    return key, fingerprint_value, errors


def check_coverage(
    manifest: dict[str, Any],
    archive_root: Path,
    repository_root: Path | None = None,
) -> tuple[int, list[str]]:
    sections, errors = archive_sections(archive_root)
    ledger = manifest.get("section_ledger")
    if not isinstance(ledger, list):
        return len(sections), ["manifest section_ledger must be an array"]

    accounted: dict[tuple[str, str], str] = {}
    for index, item in enumerate(ledger):
        if not isinstance(item, dict):
            errors.append(f"section_ledger[{index}]: expected object")
            continue
        key, fingerprint_value, semantic_errors = ledger_semantic_errors(
            item,
            index,
            archive_root,
            repository_root,
        )
        errors.extend(semantic_errors)
        if key is None or fingerprint_value is None:
            continue
        relative_key, identifier = key
        if key in accounted:
            errors.append(f"{relative_key}#{identifier}: duplicate ledger entry")
            continue
        accounted[key] = fingerprint_value
        actual = sections.get(key)
        if actual is None:
            errors.append(
                f"{relative_key}#{identifier}: ledger section missing from archive"
            )
        elif actual != fingerprint_value:
            errors.append(
                f"{relative_key}#{identifier}: fingerprint mismatch "
                f"(manifest {fingerprint_value}, archive {actual})"
            )

    for relative, identifier in sorted(set(sections) - set(accounted)):
        errors.append(f"{relative}#{identifier}: unaccounted archived section")
    return len(sections), errors


def rendered_heading_text(title: str) -> str:
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", title)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"<[^>]+>", "", value)
    return html.unescape(value)


def destination_anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="strict")
    _, headings = markdown_headings(text)
    anchors: set[str] = set()
    occurrences: dict[str, int] = {}
    for heading in headings:
        base = section_id(rendered_heading_text(heading.title))
        occurrence = occurrences.get(base, 0)
        anchor = base if occurrence == 0 else f"{base}-{occurrence}"
        occurrences[base] = occurrence + 1
        anchors.add(anchor)
    return anchors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check section coverage for archived Markdown and MDX."
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--archive-root", required=True, type=Path)
    parser.add_argument("--repository-root", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    count = 0
    try:
        root = args.archive_root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError(f"{root}: archive root is not a directory")
        if is_linklike(args.archive_root):
            raise ValueError(f"{args.archive_root}: archive root cannot be a symlink")
        repository_root = (
            args.repository_root.resolve(strict=True)
            if args.repository_root
            else None
        )
        if repository_root is not None and not repository_root.is_dir():
            raise ValueError(
                f"{repository_root}: repository root is not a directory"
            )
        count, errors = check_coverage(
            load_manifest(args.manifest),
            root,
            repository_root,
        )
    except (OSError, ValueError) as error:
        errors = [str(error)]

    payload = {"accounted": not errors, "sections": count, "errors": errors}
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif errors:
        print(f"Coverage failed for {count} archived sections:")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"{count} archived sections accounted for.")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
