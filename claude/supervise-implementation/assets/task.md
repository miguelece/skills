---
id: <kebab-case-id>
title: <one line, 8+ characters, readable out of context>
kind: ticket
status: draft
gate: none
priority: medium
category: <component or area> / <kind of work>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
parent: null
part-of: null
blocked-by: []
supersedes: []
superseded-by: null
revisit: false
outcome: null
---

# Task: <title>

## Why this exists

<The problem, and the evidence that it is real. Prefer an observation, a
measurement, or a file-and-line citation over a description of a feeling. If the
task came out of another task's interview, say which, and link it.>

## What the code says

<Optional but strongly preferred. Grounded findings with paths and line numbers,
written after actually reading the code rather than from memory. State which
claims are verified and which are still hypotheses -- a task that mislabels a
guess as a finding sends its implementer down a false trail.>

## Plan

<Numbered steps, or phases where the work warrants them. Each phase should name
its own deliverable. Where a phase produces evidence rather than code, say so --
"deliverable is numbers, not a fix" is a legitimate phase.>

## Open questions

<Every unresolved decision, one list item each. A draft must have at least one.
Resolve them in place rather than deleting them: append the answer, the date, and
the marker RESOLVED to the item, so the record shows what was decided and when.>

1. <Question — what has to be decided, and who can decide it.>
2. <Question.>

## Dependencies / cross-refs

<Sibling tasks that must not be conflated with this one, and any prior task whose
findings this one should start from rather than re-derive. Relative Markdown links.

A task that literally cannot start until another lands belongs in `blocked-by`
frontmatter, not only in prose here — that is what files it and what clears it.

Set `kind: spec` if this task is the architecture/vision a set of tickets realizes;
leave it `ticket` (the default) otherwise. A ticket that is one slice of a spec — or
a subticket that is one slice of a larger ticket — sets `part-of:` to that parent.
`part-of` is composition (a piece of), distinct from `parent`, which is lineage
(split from).>

## Owner

<Who owns each phase. Name explicitly which phases an agent can start with no
external gate, and which need a person. If the task carries a gate, the exact
outstanding item goes here: for `manual`, the action someone must perform; for
`owner`, the question someone must answer.>

<!-- Add when status becomes done, with a one-line `outcome:` in frontmatter:

## Execution log

<What shipped, on which branch and commits, and how it was verified. Record
defects found during verification that no test would have caught -- that is the
part of the log worth reading later.

The frontmatter `outcome` is the one-line version of this, and is what the
archive index shows. Write it for someone scanning a hundred finished tasks who
will not open this file.>

-->

<!-- Add when revisit becomes true:

## Upgrade paths

<Each better-but-costlier option that was evaluated and deliberately declined,
with the specific condition that would justify revisiting it. Without the
condition, an entry here is just a wish and will be re-litigated.>

-->

<!-- Add when this task has slices under it (a spec, or a ticket with subtickets):
a "## Slices" heading followed by an empty BEGIN SLICES / END SLICES comment pair.
The exact marker text is in references/board-model.md — it cannot be shown inside
this comment because its closing token would end the comment early. Leave the block
empty; generate_index.py fills it from the children's frontmatter, so a finished
slice's outcome appears here with no manual copying. -->
