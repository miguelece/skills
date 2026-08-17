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

# Every field `shared/schema/task.schema.yaml` declares under `fields:`. Held
# equal to that block by a test rather than at runtime -- ALLOWED_IMPORTS admits
# no YAML parser, and the schema sits at a different relative path in a bundle
# (references/) than in source (../schema/), so a runtime read would have to
# guess between two layouts.
#
# Seven of these are legitimately optional, which is the whole reason the check
# below has to exist: absence carries no signal, so a misspelling of one of them
# leaves nothing anywhere to disagree with.
KNOWN_KEYS = frozenset(
    {
        "id",
        "title",
        "kind",
        "status",
        "gate",
        "priority",
        "category",
        "created",
        "updated",
        "parent",
        "part-of",
        "blocked-by",
        "supersedes",
        "superseded-by",
        "revisit",
        "outcome",
    }
)

# Composition depth is a policy nudge, not a mechanism limit: the model allows
# any depth, the validator warns past this to steer toward flat trees.
MAX_PART_OF_LEVELS = 3

ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# A question is a *top-level* item: no leading whitespace. The earlier pattern
# began `^\s*`, which made every nested bullet its own question.
TOP_LEVEL_ITEM = re.compile(r"^(?:[-*]|\d+[.)])\s+\S")
FENCE = re.compile(r"^\s*(?:```|~~~)")
HEADING = re.compile(r"^#{2,}\s+(.+?)\s*$")

# A Markdown link target. The class is `[^)\s]+` and deliberately not `[^)#]+`:
# the latter stops at '#', which silently skips every citation carrying a line
# range -- a third of a mature board's links. The fragment is split off after
# the match rather than excluded during it. Stopping at whitespace also ends the
# target before an optional "title".
LINK_TARGET = re.compile(r"\]\(\s*([^)\s]+)")

# The whole link, text and target. `body_links` is the single traversal both the
# link-target rule and the citation rule read from: the fragment the first
# discards is exactly the second's input, so this is one pass over the body
# rather than two that could disagree about what counts as prose.
LINK_FULL = re.compile(r"\[([^\]]*)\]\(\s*([^)\s]+)")

# A citation names what it points at, written `filename.ext:name`. The name may
# carry spaces (a Markdown heading) or dots (a key path). Link text without this
# shape is an ordinary link -- a task title, a prose phrase -- and is not a
# citation, which is what keeps this rule off the board's own cross-references.
CITATION_TEXT = re.compile(r"^([\w.\-]+\.[A-Za-z0-9]+):(.+)$")

# The historical form: the name as it was, plus the commit it was true at. It is
# recognised and skipped, never resolved -- ALLOWED_IMPORTS admits no subprocess,
# so a bundled script cannot ask git what a file held at a commit. The value is an
# exemption that is written down and greppable rather than a citation that quietly
# stops meaning anything.
COMMIT_PIN = re.compile(r"^(.+)@([0-9a-f]{7,40})$")

# What this rule abolishes. A range is in bounds and wrong in the same moment.
LINE_RANGE = re.compile(r"^L\d+(?:-L\d+)?$")

# A scheme (`https:`, `mailto:`) or a protocol-relative `//` means the target is
# not a path on this filesystem and there is nothing to resolve.
EXTERNAL_TARGET = re.compile(r"^(?:[a-z][a-z0-9+.\-]*:|//)", re.IGNORECASE)

# Inline code spans. Link syntax quoted inside backticks is documentation
# *about* a link, not a link -- and this board carries exactly that, in a task
# document about link checking.
CODE_SPAN = re.compile(r"`+[^`]*`+")

# Generated regions inside a hand-written file, per the repo-wide convention:
# the generator owns what sits between the markers and nothing outside. Matched
# by shape rather than by importing one generator's constants, so a region any
# generator emits is covered -- including the slice rollup a spec carries.
REGION_BEGIN = re.compile(r"^\s*<!--\s*BEGIN\b")
REGION_END = re.compile(r"^\s*<!--\s*END\b")

# Folded scalars (`>`) join to a single line, which every consumer of `outcome`
# requires; literal ones (`|`) keep newlines and are refused. The chomping
# indicator is irrelevant here because the value is stripped either way.
BLOCK_SCALAR = re.compile(r"^([>|])([-+]?)$")

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

# The generated indexes. Named here rather than in generate_index.py so the
# script that writes one and the skip-set that must ignore it cannot disagree:
# the generator imports these back. TREE.md was that disagreement -- the
# generator learned to write it, the skip-set never learned its name, and every
# run on a board with composition reported it as a task with no frontmatter.
README_NAME = "README.md"
ARCHIVE_NAME = "ARCHIVE.md"
TREE_NAME = "TREE.md"
GENERATED_INDEXES = (README_NAME, ARCHIVE_NAME, TREE_NAME)

# The blank task document task-board-init step 4 copies onto the board. Deliberately
# not in GENERATED_INDEXES: no script writes it, an instruction does -- and the tests
# that hold GENERATED_INDEXES to "files the generator writes" would be wrong about it.
# Its placeholder frontmatter is not valid task frontmatter and is not meant to be;
# the file is a form to fill in, not work to do. Following step 4 used to leave a
# board reporting four errors on a file its own init skill had just created.
TEMPLATE_NAME = "_template.md"

# Files on the board that are not task documents: every generated index, the init
# skill's template, plus index.md for a board that carries a hand-written one under
# that name. Matched case-insensitively, so TREE.md and tree.md both skip.
NON_TASK = {name.lower() for name in GENERATED_INDEXES} | {
    TEMPLATE_NAME.lower(),
    "index.md",
}

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


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _consume_block(header: list[str], index: int, key_indent: int) -> tuple[list[str], int, bool]:
    """Collect the continuation lines of a block scalar opened at key_indent.

    A continuation is indented *strictly more* than its key; the block ends at
    the first line indented at or below it. Also reports whether the block held
    a blank line -- YAML folds one to a newline, so a folded value containing
    one cannot survive as the single line every consumer requires.
    """
    parts: list[str] = []
    saw_blank = False
    while index < len(header):
        line = header[index]
        if not line.strip():
            ahead = index + 1
            while ahead < len(header) and not header[ahead].strip():
                ahead += 1
            # A blank line belongs to the block only if the block resumes after it.
            if ahead < len(header) and _indent(header[ahead]) > key_indent:
                saw_blank = True
                index = ahead
                continue
            break
        if _indent(line) <= key_indent:
            break
        parts.append(line.strip())
        index += 1
    return parts, index, saw_blank


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Split a task document into (frontmatter, body).

    Returns (None, text) when the document has no frontmatter block.

    Block scalars are handled by halves, deliberately. `>`/`>-`/`>+` fold their
    continuation lines into one space-joined value, which is what `outcome`'s
    consumers require. `|`/`|-`/`|+` keep newlines and are refused, as is a
    blank line inside a folded block. Refusals are recorded under the reserved
    `_errors` key -- the parser has no reporter, and changing its return
    signature would break both other callers.

    Consuming these blocks explicitly is what stops a continuation line from
    reaching the `key: value` branch below: prose containing a colon used to be
    promoted to a real frontmatter key, silently, and could overwrite a genuine
    field such as `status`.
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
    errors: list[tuple[str, str]] = []
    pending_key: str | None = None
    cursor = 0
    while cursor < len(header):
        line = header[cursor]
        cursor += 1
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
        marker = BLOCK_SCALAR.match(raw)
        if marker:
            folded, cursor, saw_blank = _consume_block(header, cursor, _indent(line))
            data[key] = " ".join(folded).strip()
            if marker.group(1) == "|":
                errors.append((key, "literal"))
            elif saw_blank:
                errors.append((key, "blank"))
        elif not raw:
            data[key] = []
            pending_key = key
        elif raw.startswith("[") and raw.endswith("]"):
            data[key] = _inline_list(raw)
        else:
            data[key] = _scalar(raw)
    if errors:
        data["_errors"] = errors
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


def body_links(body: str) -> list[tuple[str, str]]:
    """(link text, raw target) for every relative link in body prose, in order.

    Three kinds of text are not prose and are skipped, each a false-positive
    source that was observed before this rule existed rather than imagined:
    fenced blocks, inline code spans, and generated regions. The code-span case
    is the one that bites -- writing link syntax literally to document it mints
    a phantom broken link, which is how a checker's own documentation degrades
    the ratio it exists to protect.

    The fenced-block skip carries a second load now that citations are checked:
    a document illustrating what a citation *looks like* writes the old form
    inside a fence on purpose, and a pass that read it would rewrite the record
    of what the convention replaced.

    The target is returned raw, fragment included, because the two rules that
    read this need different halves of it.
    """
    links: list[tuple[str, str]] = []
    in_fence = False
    in_region = False
    for line in body.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if REGION_BEGIN.match(line):
            in_region = True
            continue
        if REGION_END.match(line):
            in_region = False
            continue
        if in_region:
            continue
        for match in LINK_FULL.finditer(CODE_SPAN.sub("", line)):
            text, target = match.group(1), match.group(2)
            if EXTERNAL_TARGET.match(target):
                continue
            links.append((text, target))
    return links


def body_link_targets(body: str) -> list[str]:
    """Relative link targets in body prose, in order, with fragments stripped.

    The path half of `body_links`. Kept as its own name because the link-target
    rule wants only paths, and because a bare '#anchor' points inside this
    document and has no path to resolve.
    """
    targets: list[str] = []
    for _, target in body_links(body):
        path_part = target.split("#", 1)[0]
        if path_part:
            targets.append(path_part)
    return targets


def question_counts(lines: list[str]) -> tuple[int, int]:
    """Return (total, unresolved) questions in an Open questions section.

    A question is one *top-level* list item together with every line beneath it,
    up to the next top-level item; the literal marker RESOLVED anywhere in that
    block resolves it -- a deliberate token, not incidental prose.

    The unit is the block rather than the line because a decision that records
    why the alternatives lost is naturally written as a paragraph under its
    question. Counting per line reported those as unresolved and forced authors
    to flatten real reasoning onto one line, and counted each nested bullet as
    an extra unresolved question. Lines inside a fenced code block are skipped
    so that a sample containing a bullet cannot register as a question.
    """
    blocks: list[list[str]] = []
    in_fence = False
    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence and TOP_LEVEL_ITEM.match(line):
            blocks.append([])
        if blocks:
            blocks[-1].append(line)
    unresolved = sum(1 for block in blocks if not any("RESOLVED" in line for line in block))
    return len(blocks), unresolved


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

    # Parser refusals come back out-of-band; report them before the field rules
    # so the finding names the real cause instead of the downstream symptom (a
    # refused `outcome` would otherwise surface as outcome-too-thin).
    for key, reason in front.pop("_errors", []):
        if reason == "literal":
            report(
                "frontmatter-multiline",
                f"{key} uses a literal block scalar; multi-line values are not "
                f"supported because the generated index emits {key} as one line "
                "-- write it on one line, or fold it with '>-'",
            )
        else:
            report(
                "frontmatter-multiline",
                f"{key} has a blank line inside a folded block, which YAML folds "
                "to a newline; a frontmatter value must stay on one line",
            )

    # Deliberately after the `_errors` pop above and not before it. `_errors` is
    # the parser's own out-of-band channel, so a check placed higher would report
    # it as an unknown field on exactly the documents that already have a real
    # problem, naming the wrong cause. The exclusion costs nothing but is
    # load-bearing on statement order, so a test pins the ordering.
    #
    # `error`, not `warning`, unlike link-target-missing: that rule is a warning
    # because there is a legitimate window between a `git mv` and repairing the
    # links. A typo has no legitimate window, and a warning exits 0 -- which on
    # the blocked-by case would name the defect while still letting the task be
    # scheduled as actionable.
    unknown = sorted(set(front) - KNOWN_KEYS)
    if unknown:
        report(
            "frontmatter-unknown-key",
            f"unknown frontmatter key(s) {unknown}; a misspelled field name is "
            f"silently a new field nobody reads, while the field intended stays "
            f"unset at its default -- declared fields are {sorted(KNOWN_KEYS)}",
        )

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

    # --- link targets ------------------------------------------------------
    # Every rule above resolves an *id*. This one resolves a *path*, which is
    # the half that breaks when a status change derives a file into a new
    # folder: the moved file is under attention, the files citing it are not.
    #
    # A warning rather than an error, because the window between `git mv` and
    # repairing the links is ordinary and nobody mid-close wants a red board.
    # The cost is recorded rather than argued away -- a warning nobody must act
    # on is how a set of broken links survived a whole session unnoticed. What
    # makes it acceptable is that the alternative was silence, not a discipline
    # that already worked.
    for target in body_link_targets(body):
        if not (path.parent / target).exists():
            report(
                "link-target-missing",
                f"link target {target!r} does not exist",
                severity="warning",
            )

    # --- citations ----------------------------------------------------------
    # A citation names a thing and asserts it still exists in the file cited.
    # This is `error` where the rule above is `warning`, and the asymmetry is
    # deliberate rather than an inconsistency: a moved file leaves a legitimate
    # window between the `git mv` and the repair, while a citation naming
    # something that does not exist has none -- a rename and its citations are
    # edited in one pass by one person, and where they are not, the citation is
    # a false statement in the record for as long as nobody looks.
    #
    # Simpler than the range form it replaces: no bounds arithmetic, no fragment
    # parsing, no range splitting. The convention, with all four written forms,
    # is in references/board-model.md.
    for text, target in body_links(body):
        path_part, _, fragment = target.partition("#")
        if LINE_RANGE.match(fragment):
            report(
                "citation-line-range",
                f"citation {text!r} points at a line range; name the thing "
                "instead -- a range goes wrong when anything above it is edited, "
                "while the path stays valid and nothing reports it",
            )
            continue
        match = CITATION_TEXT.match(text.strip())
        if not match:
            continue
        name = match.group(2).strip()
        if COMMIT_PIN.match(name):
            # Recognised, never resolved. See board-model.md.
            continue
        cited = path.parent / path_part
        if not path_part or not cited.is_file():
            continue  # a missing path is link-target-missing's finding, not this
        try:
            source = cited.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not re.search(rf"(?<!\w){re.escape(name)}(?!\w)", source):
            report(
                "citation-name-missing",
                f"citation {text!r} names {name!r}, which does not appear in "
                f"{path_part} -- repair it to the current name, or pin it to the "
                "commit it was true at if the document deliberately describes "
                "code that has since been superseded",
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
