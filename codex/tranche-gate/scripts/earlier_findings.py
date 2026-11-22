#!/usr/bin/env python3
"""List the findings of every earlier closed tranche record, by checklist item.

The tranche gate counts a guidance candidate across tranches: a checklist item
this tranche found that an earlier tranche found too. Those findings live only
in the records' gate reports, so this script reads them, and the count is a
lookup rather than a reading by eye.

    earlier_findings.py --board <board>

It walks every `.md` file under the board, in every folder, and reads each one
whose frontmatter says `status: done` and whose body holds a `## Gate report`
heading. The record under review is still open while the gate runs, so it is
left out; a record the gate filed for a batch no supervisor ran is read like
any other.

Under each gate report it reads the `### Findings` subsection, up to the next
heading. A table there opens with a header whose first two cells are *ID* and
*Item*, and each row's first two cells are a finding id `F<n>` and a checklist
item `D<n>`. Nothing else in a row is read: the task and citation cells have
varied between reports, and the count needs neither. A subsection with no
table, such as "None.", holds no findings.

Output is one JSON object on stdout:

    {"records": [<stem>, ...],
     "items": {"D<n>": [{"record": <stem>, "finding": "F<n>"}, ...], ...}}

`records` is sorted; `items` is ordered by item number, and each item's pairs
by record, then finding number. Standard library only, and deterministic.

A record's `status` is read by the board's own parser, `validate_board.py`,
imported as a sibling module, so a value the board accepts, such as a quoted
`"done"`, reads the same here. The script therefore runs from its bundle's
`scripts/` directory, where the build places `validate_board.py` beside it,
and not from `src/` alone.

Exit 0 with the report. Exit 2, naming the record, when a gate report has no
findings subsection, its table's header is not *ID* then *Item*, or a row's
first two cells are not a finding id and an item id; exit 2 when the board is
not a directory.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from validate_board import parse_frontmatter

GATE_REPORT = re.compile(r"^## Gate report[ \t]*$", re.MULTILINE)
NEXT_SECTION = re.compile(r"^## ", re.MULTILINE)
FINDINGS = re.compile(r"^### Findings[ \t]*$", re.MULTILINE)
NEXT_HEADING = re.compile(r"^#{1,6} ", re.MULTILINE)
SEPARATOR = re.compile(r"^\|[\s:|-]+\|$")
FINDING_ID = re.compile(r"F([0-9]+)")
ITEM_ID = re.compile(r"D([0-9]+)")


class RecordError(Exception):
    """A gate report this script cannot read, with the record it is in."""


def cells(line: str) -> list[str]:
    """The cells of one markdown table row, stripped."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def gate_report(text: str) -> str | None:
    """The body of the `## Gate report` section of a done task, or None."""
    front, _ = parse_frontmatter(text)
    if front is None or front.get("status") != "done":
        return None
    heading = GATE_REPORT.search(text)
    if heading is None:
        return None
    rest = text[heading.end():]
    end = NEXT_SECTION.search(rest)
    return rest if end is None else rest[: end.start()]


def findings(stem: str, report: str) -> list[tuple[int, int]]:
    """Each `(item number, finding number)` of one gate report's findings table."""
    heading = FINDINGS.search(report)
    if heading is None:
        raise RecordError(f"{stem}: the gate report has no ### Findings subsection")
    rest = report[heading.end():]
    end = NEXT_HEADING.search(rest)
    section = rest if end is None else rest[: end.start()]
    rows = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if not rows:
        return []
    header = cells(rows[0])
    if header[:2] != ["ID", "Item"]:
        raise RecordError(
            f"{stem}: the findings header opens {header[:2]}, not ['ID', 'Item']"
        )
    pairs = []
    for line in rows[1:]:
        if SEPARATOR.match(line):
            continue
        row = cells(line)
        finding = FINDING_ID.fullmatch(row[0])
        item = ITEM_ID.fullmatch(row[1]) if len(row) > 1 else None
        if finding is None or item is None:
            raise RecordError(
                f"{stem}: a findings row opens {row[:2]}, not F<n> then D<n>"
            )
        pairs.append((int(item.group(1)), int(finding.group(1))))
    return pairs


def read_board(board: Path) -> dict:
    """The report: the records read, and each item's findings across them."""
    records = []
    found: dict[int, list[tuple[str, int]]] = {}
    for path in sorted(board.rglob("*.md")):
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        report = gate_report(text)
        if report is None:
            continue
        records.append(path.stem)
        for item, finding in findings(path.stem, report):
            found.setdefault(item, []).append((path.stem, finding))
    return {
        "records": sorted(records),
        "items": {
            f"D{item}": [
                {"record": record, "finding": f"F{finding}"}
                for record, finding in sorted(found[item])
            ]
            for item in sorted(found)
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--board", required=True, type=Path, help="the task board directory")
    args = parser.parse_args(argv)
    if not args.board.is_dir():
        print(f"earlier_findings: not a directory: {args.board}", file=sys.stderr)
        return 2
    try:
        report = read_board(args.board)
    except RecordError as error:
        print(f"earlier_findings: {error}", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
