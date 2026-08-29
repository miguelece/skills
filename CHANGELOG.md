# Changelog

Every publish into this repository gets an entry here, newest first. The publish
tool refuses to run when this file has not moved, so the record cannot quietly
stop tracking what shipped.

An entry describing a change in behaviour carries a **Behaviour change.** marker,
so the entries that matter stay findable among the routine ones. That marker is a
judgement made by whoever publishes: nothing checks it, and nothing infers it
from which files changed — a shared resource can change behaviour across many
skills at once, while a rewritten `SKILL.md` can change none.

This is a record of what changed, not a release process. There are no versions
and no tags. Publishes made before this file existed are not backfilled; they are
a dated record in the git history and are left as they are.

## Entries

### 2026-08-29 — quality-of-life (report form and `+question`)

- **Behaviour change.** `post-creation-audit` and `resume-handoff` now separate
  the items a reader has to decide about into their own *Needs a decision*
  section, on every run. Each entry carries what was observed, what was
  deliberately not done about it, and the decision being asked for. The
  separation is not gated on a flag, so it reaches the sessions where nobody
  thought to ask for it.
- **Behaviour change.** Both skills take `+question`, which asks each of those
  items as its own answerable question instead of listing them. It changes
  nothing about which items are listed. It names no harness tool — the skill
  states the form of the ask — so it degrades on its own where no structured
  prompt exists.
- `references/report-form.md` gains a fourth preservation guardrail: never fold
  an open question into the prose around it. It lands in that file's untiered
  category rather than beside the two evidence-tiered rules, because it rests on
  a report rather than a measurement. In this project it reaches
  `post-creation-audit`, `resume-handoff` and `spike`.
- `references/invocation-grammar.md` records `+question` for both holders, and
  adds the rule that a flag means the same thing in every skill that takes it.

### 2026-08-29 — quality-of-life

- **Behaviour change.** `post-creation-audit` no longer commits by default. It
  audits, reports, and stops with the working tree untouched. `+commit` restores
  what an unflagged invocation used to do, and `+git` implies `+commit` and adds
  merging, pushing, worktree management and pruning stale branches. Deleting a
  local branch proposes and asks first; nothing else asks.
- `handoff`, `resume-handoff` and `post-creation-audit` now document their
  invocation parameters against one shared reference,
  `references/invocation-grammar.md`, which also records which skills take a
  parameter at all. A skill absent from that list takes none.
