#!/usr/bin/env python3
"""Validate a file-based task board against the frontmatter contract.

Checks every task document on the board for schema conformance, agreement
between its frontmatter and the folder it sits in, the gate/status rule, the
required body sections, and cross-reference resolution.

    scripts/validate_board.py --board .scratch/task_board
    scripts/validate_board.py --board .scratch/task_board --json

Exits 0 when the board is clean, 1 when any finding is reported, and 2 when the
board itself cannot be read. Reports findings; never edits or moves a file --
moving is the caller's job, so it can use `git mv` and keep history.

Most folder derivations read only the task's own frontmatter. `blocked-by` is
the exception: it reads the *blocker's* status, so a task's derived folder can
change while its own file is untouched. That is deliberate -- when a blocker
closes, the resulting folder mismatch is how the board reports that the
downstream task just became actionable.

Standard library only, so the script runs in any repository without installing
anything. The frontmatter dialect is deliberately small (flat scalars plus one
list form); anything richer belongs in the body, not the header.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STATUSES = ("draft", "scoped", "in-progress", "done", "superseded")
GATES = ("none", "manual", "owner")
PRIORITIES = ("high", "medium", "low")
KINDS = ("ticket", "spec")
DEFAULT_KIND = "ticket"
UNFINISHED = ("draft", "scoped", "in-progress")

# Composition depth is a policy nudge, not a mechanism limit: the model allows
# any depth, the validator warns past this to steer toward flat trees.
MAX_PART_OF_LEVELS = 3

ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LIST_ITEM = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+\S")
HEADING = re.compile(r"^#{2,}\s+(.+?)\s*$")

# Folders the board owns. Anything else at depth 1 is reported as unknown.
DERIVED_FOLDERS = (
    "superseded",
    "manual-blocked",
    "owner-deferred",
    "task-blocked",
    "revisit",
    "completed",
)

REQUIRED_SECTIONS = ("why this exists", "plan", "open questions", "owner")

# Files on the board that are not task documents.
NON_TASK = {"readme.md", "index.md", "archive.md"}

# An outcome shorter than this is a label, not a summary: "done", "shipped".
MIN_OUTCOME = 15


class Finding:
    """A validation result.

    severity 'error' fails the run (exit 1); 'warning' is a policy nudge that
    prints but does not fail (exit 0). Warnings are how the board stays
    permissive at the mechanism level while steering at the policy level.
    """

    __slots__ = ("path", "rule", "message", "severity")

    def __init__(self, path: str, rule: str, message: str, severity: str = "error") -> None:
        self.path = path
        self.rule = rule
        self.message = message
        self.severity = severity

    def as_dict(self) -> dict:
        return {
            "path": self.path,
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity,
        }

    def __str__(self) -> str:
        tag = "" if self.severity == "error" else "warning: "
        return f"{self.path}: [{self.rule}] {tag}{self.message}"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _scalar(raw: str) -> object:
    """Coerce one frontmatter scalar. Dates stay strings on purpose."""
    text = raw.strip()
    if not text or text in {"null", "~"}:
        return None
    if text[0] in "\"'" and text[-1] == text[0] and len(text) >= 2:
        return text[1:-1]
    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return text


def _inline_list(raw: str) -> list:
    inner = raw.strip()[1:-1].strip()
    if not inner:
        return []
    return [_scalar(part) for part in inner.split(",")]


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Split a task document into (frontmatter, body).

    Returns (None, text) when the document has no frontmatter block.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            header, body = lines[1:index], "\n".join(lines[index + 1 :])
            break
    else:
        return None, text

    data: dict = {}
    pending_key: str | None = None
    for line in header:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if pending_key and line.startswith((" ", "\t")) and line.lstrip().startswith("- "):
            data.setdefault(pending_key, [])
            if isinstance(data[pending_key], list):
                data[pending_key].append(_scalar(line.lstrip()[2:]))
            continue
        if ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()
        pending_key = None
        if not raw:
            data[key] = []
            pending_key = key
        elif raw.startswith("[") and raw.endswith("]"):
            data[key] = _inline_list(raw)
        else:
            data[key] = _scalar(raw)
    return data, body


def sections(body: str) -> dict[str, list[str]]:
    """Map normalized heading text -> the lines beneath it."""
    found: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        match = HEADING.match(line)
        if match:
            current = match.group(1).strip().rstrip(":.").lower()
            found.setdefault(current, [])
            continue
        if current is not None:
            found[current].append(line)
    return found


def question_counts(lines: list[str]) -> tuple[int, int]:
    """Return (total, unresolved) list items in an Open questions section.

    A question counts as resolved once its item text carries the literal marker
    RESOLVED -- a deliberate token, not incidental prose.
    """
    total = unresolved = 0
    for line in lines:
        if not LIST_ITEM.match(line):
            continue
        total += 1
        if "RESOLVED" not in line:
            unresolved += 1
    return total, unresolved


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------


def blocker_ids(front: dict) -> list[str]:
    """Task ids this task is waiting on. Tolerates the single-string form."""
    raw = front.get("blocked-by") or []
    if isinstance(raw, str):
        raw = [raw]
    return [str(item) for item in raw if item]


def unresolved_blockers(front: dict, resolved_ids: frozenset[str]) -> list[str]:
    """Blockers that have not reached done. Unknown ids count as unresolved."""
    return [task_id for task_id in blocker_ids(front) if task_id not in resolved_ids]


def part_of_id(front: dict) -> str | None:
    """The single task this one composes into, or None. Composition, not lineage."""
    value = front.get("part-of")
    return str(value) if value else None


def task_kind(front: dict) -> str:
    """Role of the task; absent means the default (ticket)."""
    return str(front.get("kind") or DEFAULT_KIND)


def find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Every dependency cycle in the blocked-by graph.

    A cycle is permanently stuck: no task in it can ever become actionable, and
    nothing else on the board would surface that.
    """
    cycles: list[list[str]] = []
    seen: set[frozenset[str]] = set()
    color: dict[str, int] = {node: 0 for node in graph}  # 0 white, 1 gray, 2 black
    stack: list[str] = []

    def visit(node: str) -> None:
        color[node] = 1
        stack.append(node)
        for nxt in graph.get(node, []):
            if nxt not in color:
                continue
            if color[nxt] == 1:
                cycle = stack[stack.index(nxt) :]
                key = frozenset(cycle)
                if key not in seen:
                    seen.add(key)
                    cycles.append(list(cycle))
            elif color[nxt] == 0:
                visit(nxt)
        stack.pop()
        color[node] = 2

    for node in sorted(graph):
        if color[node] == 0:
            visit(node)
    return cycles


# ---------------------------------------------------------------------------
# The derived folder
# ---------------------------------------------------------------------------


def derive_folder(front: dict, resolved_ids: frozenset[str] = frozenset()) -> str:
    """The one place the folder mapping is written down. First match wins.

    Human gates outrank blocked-by: a task waiting on both a sibling and a
    person is still un-startable once the sibling closes, so it files by the
    person. The done checks outrank it too, which lets blocked-by survive on a
    finished task as a permanent record of what it came after.
    """
    if front.get("status") == "superseded":
        return "superseded"
    if front.get("gate") == "manual":
        return "manual-blocked"
    if front.get("gate") == "owner":
        return "owner-deferred"
    if front.get("status") == "done":
        return "revisit" if front.get("revisit") is True else "completed"
    if unresolved_blockers(front, resolved_ids):
        return "task-blocked"
    return ""


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def collect_tasks(board: Path) -> list[Path]:
    paths: list[Path] = []
    for path in sorted(board.rglob("*.md")):
        if path.name.lower() in NON_TASK:
            continue
        paths.append(path)
    return paths


def validate_one(
    path: Path,
    board: Path,
    known_ids: set[str],
    statuses: dict[str, str],
    resolved_ids: frozenset[str],
) -> list[Finding]:
    rel = path.relative_to(board).as_posix()
    findings: list[Finding] = []

    def report(rule: str, message: str, severity: str = "error") -> None:
        findings.append(Finding(rel, rule, message, severity))

    text = path.read_text(encoding="utf-8")
    front, body = parse_frontmatter(text)
    if front is None:
        report("frontmatter-missing", "no YAML frontmatter block")
        return findings

    stem = path.stem
    task_id = front.get("id")

    # --- scalar field contracts -------------------------------------------
    if not task_id:
        report("id-missing", "frontmatter has no id")
    else:
        if not ID_PATTERN.match(str(task_id)):
            report("id-format", f"id {task_id!r} is not kebab-case")
        if task_id != stem:
            report("id-matches-filename", f"id {task_id!r} != filename stem {stem!r}")

    title = front.get("title")
    if not title or len(str(title).strip()) < 8:
        report("title-missing", "title is absent or shorter than 8 characters")

    if front.get("kind") is not None and front.get("kind") not in KINDS:
        report("kind-invalid", f"kind {front.get('kind')!r} not one of {list(KINDS)}")

    status = front.get("status")
    if status not in STATUSES:
        report("status-invalid", f"status {status!r} not one of {list(STATUSES)}")

    gate = front.get("gate")
    if gate not in GATES:
        report("gate-invalid", f"gate {gate!r} not one of {list(GATES)}")

    if front.get("priority") not in PRIORITIES:
        report(
            "priority-invalid",
            f"priority {front.get('priority')!r} not one of {list(PRIORITIES)}",
        )

    if not front.get("category"):
        report("category-missing", "category is required")

    created, updated = front.get("created"), front.get("updated")
    for name, value in (("created", created), ("updated", updated)):
        if not value or not DATE_PATTERN.match(str(value)):
            report(f"{name}-invalid", f"{name} {value!r} is not YYYY-MM-DD")
    if (
        isinstance(created, str)
        and isinstance(updated, str)
        and DATE_PATTERN.match(created)
        and DATE_PATTERN.match(updated)
        and updated < created
    ):
        report("updated-before-created", f"updated {updated} precedes created {created}")

    revisit = front.get("revisit", False)
    if revisit not in (True, False, None):
        report("revisit-invalid", f"revisit {revisit!r} is not a boolean")

    # The generated archive index is built from this, so a finished task without
    # one forces its summary back into hand-maintained prose somewhere else.
    outcome = front.get("outcome")
    if status == "done":
        if not outcome:
            report(
                "outcome-required",
                "status done requires a one-line outcome; the archive index is "
                "generated from it",
            )
        elif len(str(outcome).strip()) < MIN_OUTCOME:
            report(
                "outcome-too-thin",
                f"outcome {outcome!r} is a label, not a summary; say what "
                "changed and how it was confirmed",
            )

    # --- cross-field rules -------------------------------------------------
    if gate in ("manual", "owner") and status not in UNFINISHED:
        report(
            "gate-implies-unfinished",
            f"gate {gate!r} requires status in {list(UNFINISHED)}, got {status!r}; "
            "a gated task is not finished",
        )

    if revisit is True and status != "done":
        report(
            "revisit-implies-done",
            f"revisit: true requires status done, got {status!r}",
        )

    # --- folder mapping ----------------------------------------------------
    actual_folder = path.parent.relative_to(board).as_posix()
    actual_folder = "" if actual_folder == "." else actual_folder
    if actual_folder and actual_folder not in DERIVED_FOLDERS:
        report(
            "folder-unknown",
            f"{actual_folder!r} is not a board folder; expected one of "
            f"{list(DERIVED_FOLDERS)} or the board root",
        )
    elif status in STATUSES and gate in GATES:
        expected = derive_folder(front, resolved_ids)
        if actual_folder != expected:
            where = expected or "the board root"
            message = (
                f"frontmatter derives {where!r} but the file is in "
                f"{actual_folder or 'the board root'!r}"
            )
            # A blocked-by task moves without its own file changing, so name the
            # blocker that cleared -- the mismatch is the unblock notification.
            if actual_folder == "task-blocked" and expected != "task-blocked":
                cleared = [b for b in blocker_ids(front) if b in resolved_ids]
                if cleared:
                    message = (
                        f"blocker(s) {cleared} are done; frontmatter now derives "
                        f"{where!r} -- this task is unblocked"
                    )
            report("folder-matches-frontmatter", message)

    # --- required sections -------------------------------------------------
    present = sections(body)
    for name in REQUIRED_SECTIONS:
        if name not in present:
            report("section-missing", f"required section '## {name}' is absent")

    if revisit is True and "upgrade paths" not in present:
        report(
            "section-missing",
            "revisit: true requires an '## Upgrade paths' section recording each "
            "declined option and the condition that would justify revisiting it",
        )
    if status == "done" and "execution log" not in present:
        report(
            "section-missing",
            "status done requires an '## Execution log' section",
        )

    # --- open questions vs status -----------------------------------------
    if "open questions" in present:
        _, unresolved = question_counts(present["open questions"])
        if status == "draft" and unresolved == 0:
            report(
                "draft-has-open-questions",
                "status draft but no unresolved open questions remain; "
                "promote it to scoped",
            )
        if status in ("scoped", "in-progress", "done") and unresolved:
            report(
                "scoped-has-no-unresolved",
                f"status {status!r} but {unresolved} open question(s) are still "
                "unresolved; resolve them in place or move back to draft",
            )

    # --- cross-reference resolution ---------------------------------------
    parent = front.get("parent")
    if parent and str(parent) not in known_ids:
        report("references-resolve", f"parent {parent!r} is not a task on this board")

    # part-of is composition, not lineage. Cycles and depth are cross-task and
    # handled in validate_board; self and resolution are local.
    part_of = part_of_id(front)
    if part_of == task_id:
        report("part-of-self", "part-of names this task itself")
    elif part_of and part_of not in known_ids:
        report("references-resolve", f"part-of {part_of!r} is not a task on this board")

    supersedes = front.get("supersedes") or []
    if isinstance(supersedes, str):
        supersedes = [supersedes]
    for other in supersedes:
        if other and str(other) not in known_ids:
            report(
                "references-resolve", f"supersedes {other!r} is not a task on this board"
            )

    successor = front.get("superseded-by")
    if status == "superseded" and not successor:
        report(
            "superseded-has-successor",
            "status superseded requires superseded-by",
        )
    if successor and str(successor) not in known_ids:
        report(
            "references-resolve",
            f"superseded-by {successor!r} is not a task on this board",
        )

    # --- blocked-by --------------------------------------------------------
    for blocker in blocker_ids(front):
        if blocker == task_id:
            report("blocked-by-self", "blocked-by names this task itself")
            continue
        if blocker not in known_ids:
            report(
                "references-resolve",
                f"blocked-by {blocker!r} is not a task on this board",
            )
            continue
        if statuses.get(blocker) == "superseded":
            report(
                "blocker-superseded",
                f"blocker {blocker!r} was superseded; repoint blocked-by at its "
                "successor rather than waiting on a replaced spec",
            )

    return findings


def validate_board(board: Path) -> list[Finding]:
    paths = collect_tasks(board)

    known_ids: set[str] = set()
    statuses: dict[str, str] = {}
    kinds: dict[str, str] = {}
    graph: dict[str, list[str]] = {}
    part_graph: dict[str, list[str]] = {}
    children: dict[str, list[str]] = {}
    id_to_path: dict[str, str] = {}
    structural: list[Finding] = []

    for path in paths:
        front, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        task_id = (front or {}).get("id")
        if not task_id:
            continue
        task_id = str(task_id)
        rel = path.relative_to(board).as_posix()
        if task_id in known_ids:
            structural.append(
                Finding(
                    rel,
                    "id-duplicate",
                    f"id {task_id!r} is already used by another task",
                )
            )
        known_ids.add(task_id)
        statuses[task_id] = str((front or {}).get("status"))
        kinds[task_id] = task_kind(front or {})
        graph[task_id] = blocker_ids(front or {})
        id_to_path.setdefault(task_id, rel)
        # Exclude self-edges from the composition graph so a part-of-self shows
        # only as part-of-self, not also as a one-node cycle.
        parent = part_of_id(front or {})
        part_graph[task_id] = [parent] if parent and parent != task_id else []
        if parent and parent != task_id:
            children.setdefault(parent, []).append(task_id)

    resolved_ids = frozenset(
        task_id for task_id, status in statuses.items() if status == "done"
    )

    for cycle in find_cycles(graph):
        chain = " -> ".join(cycle + [cycle[0]])
        for task_id in cycle:
            structural.append(
                Finding(
                    id_to_path.get(task_id, task_id),
                    "blocked-by-cycle",
                    f"dependency cycle: {chain}. No task in a cycle can ever "
                    "become actionable; break it by removing one blocked-by.",
                )
            )

    for cycle in find_cycles(part_graph):
        chain = " -> ".join(cycle + [cycle[0]])
        for task_id in cycle:
            structural.append(
                Finding(
                    id_to_path.get(task_id, task_id),
                    "part-of-cycle",
                    f"composition cycle: {chain}. A task cannot be a part of "
                    "itself; break it by removing one part-of.",
                )
            )

    # Depth is a policy nudge (warning), not a mechanism limit. Guard the walk
    # against cycles (already reported above) with a visited set.
    for task_id in sorted(part_graph):
        levels, node, seen = 1, task_id, {task_id}
        while part_graph.get(node):
            node = part_graph[node][0]
            if node in seen:
                break
            seen.add(node)
            levels += 1
        if levels > MAX_PART_OF_LEVELS:
            structural.append(
                Finding(
                    id_to_path.get(task_id, task_id),
                    "part-of-too-deep",
                    f"composition is {levels} levels deep (> {MAX_PART_OF_LEVELS}); "
                    "prefer siblings over nesting unless this is a real handoff unit",
                    severity="warning",
                )
            )

    # A done spec may legitimately keep open ticket descendants (deferred or
    # revisit work), so this is a triage note, never a failure.
    for spec_id, status in statuses.items():
        if kinds.get(spec_id) != "spec" or status != "done":
            continue
        stack, open_descendants = list(children.get(spec_id, [])), []
        seen = set(stack)
        while stack:
            child = stack.pop()
            if statuses.get(child) not in ("done", "superseded"):
                open_descendants.append(child)
            for grandchild in children.get(child, []):
                if grandchild not in seen:
                    seen.add(grandchild)
                    stack.append(grandchild)
        if open_descendants:
            structural.append(
                Finding(
                    id_to_path.get(spec_id, spec_id),
                    "spec-done-open-tickets",
                    f"spec is done but has open ticket descendant(s) "
                    f"{sorted(open_descendants)}; intended if this is deferred or "
                    "revisit work",
                    severity="warning",
                )
            )

    findings: list[Finding] = []
    for path in paths:
        findings.extend(validate_one(path, board, known_ids, statuses, resolved_ids))
    return findings + structural


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, required=True, help="board root directory")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = parser.parse_args()

    board = args.board
    if not board.is_dir():
        print(f"not a directory: {board}", file=sys.stderr)
        return 2

    findings = validate_board(board)
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    if args.json:
        print(json.dumps([f.as_dict() for f in findings], indent=2))
    elif findings:
        summary = f"{len(errors)} error(s), {len(warnings)} warning(s)"
        print(f"{summary} on {board}:\n")
        for finding in findings:
            print(f"  {finding}")
        if errors:
            print("\nFrontmatter is the source of truth. Move files to the folder it")
            print("derives (use `git mv`), or correct the frontmatter -- not both.")
    else:
        task_count = len(collect_tasks(board))
        print(f"OK: {task_count} task(s) on {board}, no findings")

    # Warnings are policy nudges; only errors fail the run.
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
