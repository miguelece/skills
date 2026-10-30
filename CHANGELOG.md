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

### 2026-10-30 — diataxis-doc-migration (create path)

- **Behaviour change.** New skill `diataxis-create-docs` writes new Diataxis
  documentation in one of two modes. It writes one requested page (a tutorial,
  how-to, reference or explanation) into an existing tree. Or it bootstraps a
  sparse repository, choosing first pages in a fixed order: a reference page
  for each public entrypoint, then one getting-started tutorial, then how-to
  pages, then explanation pages. Each candidate is kept or dropped with a
  stated reason, and the whole plan is approved once before any write.
- A page may exist because its author asked for it. Every factual claim in it
  still anchors to reachable code, and rationale is attributed to a recorded
  decision or to the author. A claim with neither is excluded with its reason,
  or recorded as a suspected code finding.
- New page templates for the four types ship with `diataxis-create-docs` only.
- **Behaviour change.** `diataxis-update-docs` no longer bootstraps. It hands a
  sparse domain to `diataxis-create-docs`, and its description now covers
  existing documentation only.
- **Behaviour change.** `diataxis-manage-docs` routes a sparse domain, and a
  request for a new page, to `diataxis-create-docs`.
- The shared manifest accepts `run.mode: create`.
- Whether create requests now reach `diataxis-create-docs` more reliably is
  **not measured**. The descriptions pass a static concept check only; no
  trigger evaluation has run on them.

### 2026-10-30 — quality-of-life (handoff write-back path)

- **Behaviour change.** `handoff`, and so `close-out`, now writes the new
  handoff back to the document the session resumed from, instead of always
  writing `.scratch/handoff.md`. It takes the first path it knows: the one
  `resume-handoff` read, then the document's own *Written to* line, then the
  default. If the conversation's path and the line disagree, the
  conversation's wins. The user can redirect it in plain words. A thread kept
  beside the default one no longer loses its state at close-out, and no longer
  overwrites the default's.
- The handoff template's header gains a *Written to `<path>`* line.
- At the clear step, `handoff` and `close-out` now always print the exact
  invocation to resume: `/resume-handoff from <path>`, or a bare
  `/resume-handoff` for the default, with `$` on Codex.
- `resume-handoff`'s check-in names the path the session will close to. A
  *Written to* line naming a different path is reported under *Needs a
  decision*.

### 2026-10-29 — quality-of-life (every push asks)

- **Behaviour change.** `post-creation-audit +git`, and so `close-out`, now asks
  before pushing to any remote, private ones included. It asks once per run, in
  one approval listing every planned push: repository, remote, branch, commits
  and visibility. The approval covers only what it lists. A commit made after
  it, a repository added later, or a re-push after a rejected non-fast-forward
  asks again. A declined approval pushes nothing, and `close-out` still writes
  its handoff. Visibility now only labels each entry. Before this change, a
  remote the probe reported as private was pushed without asking.
- `close-out`'s description and Codex `short_description` now say it pushes
  after approval. It stays user-only, because every run still commits.

### 2026-10-26 — quality-of-life (pause-check bands)

- **Behaviour change.** `pause-check`'s urgency bands move to below 35%, 35% to
  60%, and above 60%, from 50% and 75%. It now prefers a clean boundary, and
  later insists on the nearest one, at a lower occupancy. The edges are still
  starting values set by preference, not measured. Nothing else in the skill
  changes.

### 2026-10-26 — quality-of-life (pause-check)

- **Behaviour change.** A new skill, `pause-check`, judges whether a session
  should keep going or stop at a clean boundary. It is read-only and the agent
  may start it on its own. Its verdict is one of *keep going*, *keep going: no
  signal*, *this is a good pause point* (suggesting `close-out` with the next
  item as its `into` clause), or *stop at the nearest boundary*.
- It reads context-window occupancy from a tool named
  `mcp__context-occupancy__occupancy` when the session has one, and places the
  figure in bands (below 50%, 50% to 75%, above 75%) measured against the
  auto-compaction threshold when one is set. **That tool comes from a Claude
  Code mod that is not published here**, so on an ordinary install it is absent
  and `pause-check` reports *unavailable (not installed)*. It then judges from
  `references/session-queue.md`'s four observable proxies alone, and never
  estimates a figure.
- **Behaviour change.** `close-out`, typed bare, now runs `pause-check` first
  and puts the item it names to the user as a proposed `into` clause. It
  records `into continuing` when nothing is proposed or the user declines. A
  typed `into` clause skips the step. This is the first step `close-out` owns
  rather than delegates.
- `references/invocation-grammar.md` states the new bare-`close-out` behaviour.
  It reaches `handoff`, `resume-handoff`, `post-creation-audit` and `close-out`,
  and changes nothing else.
- **Not verified:** that an agent calls the tool, judges well, or stops where
  the verdict says. The skill's tests read its source; nothing here observes an
  agent pacing a session.

### 2026-10-20 — quality-of-life (close-out)

- **Behaviour change.** A new skill, `close-out`, closes a session in one
  invocation: it runs `post-creation-audit` with `+git`, then `handoff` with the
  trailing `into` clause or `into continuing` when none is typed, then tells the
  user to clear and resume with `resume-handoff`. **It is invocation-only on both
  runtimes** — `/close-out` in Claude Code, `$close-out` in Codex — because every
  run commits and pushes.
- `close-out` restates neither skill. The audit's prompts, including its
  confirmation before a public push, stay the audit's, and `close-out` never
  answers one for the user. It writes the handoff even when the audit stops
  partway, and carries the audit's *Needs a decision* items into the handoff's
  *Open questions*, because the clear would otherwise destroy them.
- `references/invocation-grammar.md` lists `close-out` as a fourth holder of
  `into`, records its default, and adds that a skill writing a side-effecting
  flag for another inherits that skill's confirmation unchanged. It reaches
  `handoff`, `resume-handoff`, `post-creation-audit` and `close-out` on both
  runtimes, and changes nothing about how the existing three behave.
- `handoff` now names `close-out` as a route into *Clearing and resuming* and as
  a holder of its `into` rule. No behaviour change.
- **Not verified:** that a live run reaches the handoff after the audit stops to
  ask, and that a Codex agent can chain the two skills. The skill's tests read
  its text; nothing observes an agent following it.

### 2026-09-16 — task-board-management (freeze exception and move pointers)

- **Behaviour change.** `references/board-model.md` gains a third exception to
  *Completed tasks are frozen*: a claim that was already false when the closing
  session wrote it is corrected by a dated amendment beneath it, with the original
  left standing. **A claim that was true when written and has since been
  overtaken is still history and is not amended** — the section's worked example
  is unchanged and now says so explicitly. The exception had been practised on a
  board without being written down; a sweep of every frozen task against eight
  recorded behaviour changes found overtaken descriptions rare and already
  covered by the worked example, and found one claim that was wrong on the day
  it was written, which is the case the exception covers.
- **Behaviour change.** The five skills whose steps move a task file between
  folders now say so at that step and name *Repairing the links a move breaks* in
  `references/board-model.md`: `task-board-init` (the bulk move on adoption),
  `task-board-triage` (a folder mismatch), `task-interview` (setting a gate or an
  unfinished `blocked-by`), `focused-implementation` (closing a task), and
  `orchestrate-implementation` (closing a set). **None restates the procedure**;
  the one copy stays in the reference.
- `task-board-triage` no longer counts the freeze exceptions itself. It names the
  two that concern triage and points at the reference for the rule, so the skill
  cannot fall out of step with it again.
- `board-model.md` declares no `skills:` key, so the freeze change reaches all
  seven skills on both platforms; the `SKILL.md` changes reach the five above.

### 2026-09-16 — task-board-management (instrument rule reach)

- **Behaviour change.** `instrument-outside-the-repository` in
  `validate_board.py` now reaches further, so a board that passed before can
  fail. A script path anchored on gitignored private material — `refs/`,
  `_private` or `research/sources` — is now reported, as well as one in a
  scratch directory or a session scratchpad. The extension list grew from `.py`,
  `.sh` and `.ps1` to sixteen script extensions, since nothing in the rule's
  reasoning separates a Python instrument from a JavaScript one.
- **Each anchor must begin a path segment.** Without that, `crossrefs/build.py`
  matched on its `refs` suffix. An ordinary word ending in an anchor name is not
  reported.
- **An instrument cited by basename alone is outside the rule's reach, and that
  is a bound rather than a gap to be closed.** It carries no directory to anchor
  on, and resolving the name on disk was measured to be anti-correlated with the
  rule's intent. The finding's message now says so, beside the existing note
  that a scan recorded outside the board is not covered either.
- `references/board-model.md` gains a passage separating what the rule matches
  from the general idea it serves, and `references/task.schema.yaml` updates the
  rule's `check:` prose to the widened reach, which it had not described.
- All three files declare no `skills:` key, so this reaches all seven skills on
  both platforms. No `SKILL.md` changed.

### 2026-09-02 — task-board-management (link repair after a move)

- **Behaviour change.** `references/board-model.md` gains a *Repairing the links
  a move breaks* subsection, so a skill that moves a task file now has an
  instruction for repairing what the move breaks. The detection half shipped
  2026-08-13; the repair half has never existed, and every close since has been
  repaired by hand from a procedure that lived only in an untracked session
  document.
- **One rule covers both directions**: a link is a path from a directory to a
  target, so when either endpoint moves, re-express the target relative to the
  directory it is now read from. Applied to the file that moved it repairs every
  link it carries; applied to each citing file it repairs the link pointing at
  it. There is no table of cases, and the rule does not care what the target is.
- **The validator's own output is what says the repair is finished, warnings
  included.** `link-target-missing` is a warning, so a run exits 0 across the
  whole breakage and an exit code alone reports success.
- **A sweep must not share a filter with the check that verifies it.** A rewrite
  scoped to one file extension once reported every link clean while four links
  to `.py` files were broken, because the verification carried the same filter
  and confirmed the bug rather than catching it.
- **Links from outside the board need their own pass**, because the validator
  walks the board and nothing else. A document elsewhere in the repository that
  links to a task is broken silently by a move.
- No script changed. `board-model.md` declares no `skills:` key, so this reaches
  all seven skills on both platforms. Pinned by a section-scoped literal-phrase
  assertion in `test_validate_board.py`, watched failing on all four clauses
  before the prose was written, and grounded by replaying a real recorded move
  out of git history — where the rule reproduced the human repair's 15 unique
  targets with no divergence.

### 2026-08-31 — task-board-management (instrument recoverability)

- **Behaviour change.** `validate_board.py` reports a new **error**,
  `instrument-outside-the-repository`: a task must not name a script path in a
  scratch directory or a session scratchpad. A run that passed before can now
  fail, which is the point — a figure produced by an instrument no repository
  holds stops being reproducible the moment that file is gone.
- The trigger is a script extension inside such a path, not the path itself. A
  handoff document lives in a scratch directory by design and is referenced
  across many board documents; flagging those would leave a permanent finding
  nobody can act on. Fenced blocks are skipped, as they are by every other body
  rule, and the accepted cost of that is recorded in the source.
- It lands at `error` rather than `warning` because neither warning category
  admits it. Not advisory: a board recording a figure nobody can reproduce is
  not valid in that state. Not transient: the repair is committing a file, which
  no prescribed workflow does and undoes within one session.
- **Its reach is the board and nothing else, and the finding says so in its own
  message.** A scan recorded outside the board is beyond it. A rule that swept
  the board and reported nothing would otherwise be read as covering a
  population it never measured.
- `task.schema.yaml` and `references/board-model.md` both declare the rule, so
  the schema, the reference and the validator cannot drift apart. Reaches all
  seven skills in this project, none of which changed its own body.

### 2026-08-31 — diataxis-doc-migration

- `references/report-form.md` now names the counting rule and the measurement
  date beside every figure it quotes. Here it reaches all four migration skills.
- **Not a behaviour change.** No skill body in this project changed. This is the
  third and last publish carrying one lab-tier edit; the labelling of the
  evidence moved and the guidance did not.
- With this publish the rule and date are live in all eleven skills that cite
  `report-form.md`, and no live document in this lab quotes a figure of this
  research line without naming the rule that produced it.

### 2026-08-31 — task-board-management

- `references/report-form.md` now names the counting rule and the measurement
  date beside every figure it quotes. Here it reaches `task-board-triage`,
  `task-interview`, `focused-implementation` and `orchestrate-implementation`.
- **Not a behaviour change.** No skill body in this project changed, and the
  rules the shared reference teaches are untouched. This is the second of three
  publishes carrying one lab-tier edit; the labelling is what moved, not the
  guidance.
- Why a reference that four board skills cite needed this: those skills report
  figures into a conversation, and a figure quoted without its counting rule is
  not portable. The reference now carries its own provenance rather than
  assuming a reader will go looking for it.

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
