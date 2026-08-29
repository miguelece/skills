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
