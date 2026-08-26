---
name: resume-handoff
description: Read the handoff document a previous session left on disk and resume from it — verify the repository still matches what the document claims, report what moved, then check in before acting on the agenda. Use when opening a fresh session with "resume the handoff", "read .scratch/handoff.md and continue", "pick up where we left off", or "continue from the handoff". This is the reading half of the cycle handoff writes. "/resume-handoff from .scratch/old.md" resumes from a document other than the default one, and "/resume-handoff into next steps" makes that the session's agenda, warning first when it contradicts the agenda the document already recorded.
---

# Resume from a handoff

Pick up work a previous session left in a handoff document: verify what it claims
is still true, report what moved, then check in before acting.

`handoff` writes the document; this skill reads it. The two halves fire in
different sessions and share nothing but the file on disk.

## Grammar

```text
/resume-handoff                                       default source
/resume-handoff from .scratch/old.md                  explicit source
/resume-handoff into next steps                       typed agenda
/resume-handoff from .scratch/old.md into next steps  both
```

`from` takes **one token, a path**. `into` takes **the rest of the line, an
agenda**. The object types differ, so either order parses unambiguously.

A bare argument is not accepted. `/resume-handoff next steps` could be a path or
an agenda, and the only way to tell them apart is testing whether the argument
resolves on disk — a guess that misclassifies a mistyped path in silence.

### `into` is not inverted between the two skills

`into <X>` means *"the agenda is X"* in both. Only the addressee differs:
`handoff` **records** it, because the agenda belongs to a future session; this
skill **acts** on it, because the agenda belongs to the present one.

`handoff`'s guardrail *"Do not carry out a trailing `into` directive"* is a rule
about `handoff`'s own invocation, written when no other skill held the grammar.
**It does not apply here.** Carrying it across means refusing to act on a
directive that was typed for this session.

## Phase 1 — Orientation

### Locate the document

- **`from <path>` given** — read exactly that path. If it does not resolve,
  report the path and **stop**. Do not scan and do not fall back: an explicit
  `from` is the user's claim about which document to resume from, so quietly
  reading a different one is the silent failure this grammar exists to prevent.
- **No `from`** — read `.scratch/handoff.md`. If it is absent, scan `.scratch/`
  for a handoff-shaped file.
- **Nothing found** — say so and stop. Do not infer an agenda from the task
  board, from `git log`, or from anywhere else. Inventing work is worse than the
  retyped sentence this skill replaces.

### Read it by section

`handoff` writes these nine top-level headings, in this order, and this skill
keys on them by name. Read every one. A section that is missing is **reported by
name and reading continues** — an unreadable section is information, not a stop
condition. A document written before the nine-section format existed, or written
by another tool, will be missing some.

| Section | What to take from it |
| --- | --- |
| `Next session — start here` | The recorded agenda: the verbatim directive, what the writing session resolved it to, and the preconditions for acting. Its `What is pending` subsection is the ranked shortlist of candidates — carry it into the check-in rather than rebuilding one. When the document omits it, say so and stop; do not build the list yourself. |
| `Orientation` | Which repositories exist and where. This is the list the cheap tier iterates over. |
| `The task` | What is done, what is in progress and exactly where it stopped, and what is not started. |
| `Open questions — must be resolved before proceeding` | Blockers. These **outrank the agenda** — carry any that are unresolved into the check-in. |
| `Non-negotiable conventions` | The rules to obey in phase 3, each with the reason it exists and what enforces it. |
| `Commands` | Exact invocations with the directory each runs from. Use these rather than inventing equivalents. |
| `Traps found the hard way` | What already went wrong here. Read before acting, not after repeating one. |
| `Loose ends` | Deliberately unfinished work. Not the agenda unless the agenda says so. |
| `Verified state` | The dated snapshot. Supplies the commits the staleness check compares against, and the commands the expensive tier escalates to. |

### Verify — the cheap tier, always

Run these unconditionally. They cost seconds and they catch the failures that
actually occur: uncommitted work, a moved `HEAD`, a file that was renamed away.

- In **every** repository the document's *Orientation* names, not only the
  first: `git status --short`, `git log --oneline -1`, and `HEAD` against
  `origin/main`. A handoff that covers one repository and not its sibling is the
  common shape of the error.
- Confirm the files and paths the agenda names still exist.

### Measure staleness by `HEAD`, not by the date

`Written <date>` proves nothing on its own. A month-old handoff against an
untouched tree is current, and one written an hour ago is stale the moment a
commit lands. *Verified state* records the commits that were at the top when the
document was written — compare those against the current `HEAD`.

Report both: the date, because it is cheap and a reader wants it; the commit
delta, because it is the one that decides anything.

### Verify — the expensive tier, on cause only

Escalate to the commands *Verified state* records — test suites, lint, board
checks — when **either** holds:

- a cheap check disagrees with the document, or
- the agenda depends on that state. "Implement something" depends on the suite
  being green; "interview a task" does not.

Do not run the whole block by default. It mostly re-confirms what the writing
session verified minutes earlier, and it re-spends the context the handoff
existed to save. The gap is accepted rather than hidden: a suite that broke
*after* the document was written is caught only when the agenda touches it.

## Phase 2 — Check in

**Unconditional. Every invocation stops here.** Do not judge whether the agenda
is concrete enough, or whether an open question is genuinely outstanding — that
judgment is the one that fails silently, and an unconditional stop has no
discretion to exercise.

Report, in this order:

1. **The agenda**, and where it came from: the document's recorded one, a typed
   `into` clause, or both.
2. **Anything unresolved** under *Open questions — must be resolved before
   proceeding*. This **outranks the agenda**, recorded or typed. A directive
   never settles a question the writing session left open.
3. **What moved** since the document was written — the commit delta, anything
   uncommitted, any path the agenda names that no longer exists, and any section
   that was missing.
4. **The override warning**, when a typed `into` contradicts the recorded
   agenda. Name both plainly and let the user choose. Do not silently prefer
   either. When the document records no agenda, there is nothing to contradict,
   so the typed clause simply is the agenda and no warning is due.

Shape the check-in per
[references/report-form.md](references/report-form.md). The ordering above is
fixed; what that file governs is the form — emphasis, headings, and the
guardrails that keep a shortened report honest.

Then wait. An unnecessary check-in costs one message; acting on a stale premise
costs whatever the session then builds on it.

## Phase 3 — Act

Once the user confirms, do the work the agenda names.

*Non-negotiable conventions*, *Commands*, and *Traps found the hard way* apply
from here on. Read them before the first edit, not after the first mistake —
they are the sections that exist precisely because a previous session paid for
them.

## Guardrails

- Do not act before the check-in, and do not treat a confident reading of the
  agenda as permission to skip it. The check-in is unconditional.
- Do not invent an agenda. No handoff, or no agenda in one, means say so and
  stop — never infer work from the board or the commit log.
- Do not fall back to the scan when an explicit `from` path fails to resolve.
  Report the path that did not resolve and stop.
- Do not carry `handoff`'s *"Do not carry out a trailing `into` directive"* rule
  into this skill. That rule governs writing the document; here the directive is
  addressed to the present session and is acted on, after the check-in.
- Do not treat *Verified state* as current. It was true when it was written; the
  cheap tier is what makes it true now.
- Do not let a typed `into` clause override an unresolved open question.
- Do not re-run the whole *Verified state* block on every resume.

## Resources

- The document read here is the one `handoff` writes.
