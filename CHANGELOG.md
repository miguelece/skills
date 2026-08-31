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

### 2026-08-31 — quality-of-life

- `references/report-form.md` now names the counting rule and the measurement
  date beside every figure it quotes. It previously gave each figure with the
  corpus it was measured on and named neither the rule nor the date, which made
  it the sharpest live instance found by a sweep of this lab's published figures
  — and the only one that ships to anyone.
- **Not a behaviour change.** The rules the file teaches are untouched: ration
  emphasis, add headings past roughly 150 words, and the four preservation
  guardrails all read exactly as before. What changed is the labelling of the
  evidence beneath them. Here it reaches `post-creation-audit`, `resume-handoff`
  and `spike`.
- No value is re-issued. The published 9.03% is correct under the counting rule
  in force when it was measured; a later rule change moves that pair to 9.10%,
  and the file now says so rather than restating the figure. Re-issuing it would
  put two counting rules inside one passage, which is the failure this research
  line is named for.
- The file points at a new register of counting rules in
  `output-compression-technique-package`, which names the rule, the date and the
  re-checkability of every live figure that finding carries.

### 2026-08-29 — quality-of-life (push confirmation)

- **Behaviour change.** `post-creation-audit` now confirms before pushing to a
  public remote under `+git`. A flag on the invocation line is not evidence that
  a person asked for the push — a model composing its own invocation writes its
  own flags — and a push to a public remote cannot be taken back. This narrows
  the first `quality-of-life` entry below, which said nothing but a branch
  deletion asks.
- Visibility is resolved by probing `gh repo view --json visibility`, and by
  asking when the probe cannot answer. Only a positive *private* answer
  suppresses the confirmation: a failed, errored or unauthenticated probe is not
  evidence of privacy, and reading it as one would disable the safeguard in
  exactly the case it exists for.
- Coverage is push only. `+git` implies `+commit`, so an escalated invocation
  has already committed by the time it reaches the push. That gap is accepted
  rather than overlooked — committing is reversible and publishing is not.
- `references/invocation-grammar.md` states the general rule behind it: a flag
  that adds a side-effecting capability confirms before an operation that cannot
  be taken back, keyed on the operation and never on who composed the
  invocation. It reaches `handoff`, `resume-handoff` and `post-creation-audit`.

### 2026-08-29 — diataxis-doc-migration

- **Behaviour change.** `references/report-form.md` gains a fourth preservation
  guardrail: never fold an open question into the prose around it. An item the
  reader has to decide something about goes under its own heading, carrying what
  was observed, what was deliberately not done about it, and the decision being
  asked for. Here it reaches all four migration skills.
- No skill body in this project changed. This is the third and last publish
  carrying the same shared-reference edit; the guardrail is now live in all
  eleven skills that cite `report-form.md`.

### 2026-08-29 — task-board-management

- **Behaviour change.** `references/report-form.md` gains a fourth preservation
  guardrail: never fold an open question into the prose around it. An item the
  reader has to decide something about goes under its own heading, carrying what
  was observed, what was deliberately not done about it, and the decision being
  asked for. Here it reaches `task-board-triage`, `task-interview`,
  `focused-implementation` and `orchestrate-implementation`.
- No skill body in this project changed. The guardrail arrives through the
  shared reference those four already cite, which is why a publish with no
  source edit of its own still changes behaviour.

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
