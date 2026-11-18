#!/usr/bin/env python3
"""Fingerprint written pages, or check them against the manifest's `pages`.

A page a lifecycle run writes carries `*Last updated: YYYY-MM-DD*` on the line
after its H1, and an entry in the manifest's `pages` recording its path, its
content fingerprint and that date. The date is for readers; the fingerprint is
what catches drift, including a same-day edit and an edit that left the date
alone, which a date alone cannot. Fingerprints use `check_coverage.fingerprint`,
so there is one hashing rule, not two.

    check_pages.py --fingerprint <page>...          print each page's fingerprint
    check_pages.py --manifest <path> --root <repo>  check every `pages` entry

Exit 0 when every page holds, 1 when any page fails or cannot be read.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from check_coverage import fingerprint, load_manifest, safe_relative


H1_PATTERN = re.compile(r"^ {0,3}# ")
DATE_LINE_PATTERN = re.compile(r"^\*Last updated: (?P<date>\d{4}-\d{2}-\d{2})\*$")


def read_page(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def date_line(text: str) -> str | None:
    """The date on the line after the H1, one blank line between, if present."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if H1_PATTERN.match(line):
            following = lines[index + 1 : index + 3]
            if len(following) == 2 and following[0] == "":
                match = DATE_LINE_PATTERN.fullmatch(following[1])
                if match:
                    return match.group("date")
            return None
    return None


def check_entry(entry: Any, index: int, root: Path) -> list[str]:
    if not isinstance(entry, dict):
        return [f"$.pages[{index}]: entry must be an object"]
    label = entry.get("path")
    try:
        relative = safe_relative(label, f"$.pages[{index}].path")
        path = root / relative
        path.resolve().relative_to(root.resolve())
    except ValueError as error:
        return [str(error)]
    if not path.is_file():
        return [f"{label}: page file is missing"]
    try:
        text = read_page(path)
    except (OSError, UnicodeError) as error:
        return [f"{label}: cannot read page: {error}"]

    errors: list[str] = []
    if fingerprint(text) != entry.get("fingerprint"):
        errors.append(
            f"{label}: content no longer matches its recorded fingerprint; "
            "it was edited outside the skills, so its date may be stale"
        )
    found = date_line(text)
    recorded = entry.get("last_updated")
    if found is None:
        errors.append(f"{label}: date line is missing under the H1")
    elif found != str(recorded):
        errors.append(
            f"{label}: date line reads {found} but last_updated is {recorded}"
        )
    return errors


def check_pages(manifest: dict[str, Any], root: Path) -> tuple[int, list[str]]:
    pages = manifest.get("pages") or []
    if not isinstance(pages, list):
        return 0, ["$.pages: must be an array"]
    errors: list[str] = []
    for index, entry in enumerate(pages):
        errors.extend(check_entry(entry, index, root))
    return len(pages), errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fingerprint Diataxis pages, or check the manifest's pages "
            "against the pages on disk."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--fingerprint",
        nargs="+",
        type=Path,
        metavar="PAGE",
        help="print the fingerprint of each page, to record in the manifest",
    )
    mode.add_argument(
        "--manifest",
        type=Path,
        help="check every pages entry of this manifest; requires --root",
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="repository root the manifest's page paths are relative to",
    )
    args = parser.parse_args()
    if args.manifest is not None and args.root is None:
        parser.error("--manifest requires --root")
    return args


def main() -> int:
    args = parse_args()
    if args.fingerprint:
        failed = False
        for page in args.fingerprint:
            try:
                print(f"{fingerprint(read_page(page))}  {page.as_posix()}")
            except (OSError, UnicodeError) as error:
                print(f"{page.as_posix()}: cannot read page: {error}")
                failed = True
        return 1 if failed else 0

    try:
        count, errors = check_pages(load_manifest(args.manifest), args.root)
    except ValueError as error:
        count, errors = 0, [str(error)]
    if errors:
        print(f"Page check failed for {count} recorded pages:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"{count} page(s) recorded; each holds its fingerprint and date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
