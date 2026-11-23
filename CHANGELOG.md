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

### 2026-11-23 — software-evaluation (Go modules)

- **Behaviour change.** Three Go modules ship: `go-testing`,
  `go-error-handling` and `go-concurrency`, bringing the library to eight.
  None has yet been read against real Go code.
- **Behaviour change.** A module header must write all four trigger kinds,
  as `[]` where empty, and a header that omits one is refused.
- **Behaviour change.** A declined dynamic launch keeps its module in
  `modules.loaded` and records the reason in `phases.not-run`, which is
  what says whether the module's checks ran.
- **Behaviour change.** `advise-from-evaluation` runs the bundled report
  validator by its skill-directory path, and reads the unrun phases, each
  with its reason, before the findings.
- The prior-art reference records how a SARIF writer would carry an unrun
  phase's reason without a schema change. Other changes are rewraps.

### 2026-11-23 — task-board-management

- **Behaviour change.** `supervise-implementation` closes a tranche at
  8,000 changed lines outside the board, up from 4,000, and `tranche-gate`
  declares the same limit. The new value is a trial: the next gates measure
  it, and a seeded replay at that size has not been run.
- `tranche-gate`'s report gains a `Chunks read:` line saying whether the gate
  read every chunk or sampled, and which chunks a sample skipped.
- `supervise-implementation` quotes the integrator-verdict form,
  `<date>, <task> attempt <n>:`, where it writes a verdict, because the
  gate's scan reads only that form.

### 2026-11-22 — software-evaluation (first publish)

- **Behaviour change.** First publish of two skills.
  - `evaluate-software` evaluates a diff, a whole repository, or a design
    (read from code or from a design document) against modules loaded per
    language, framework and concept.
    - It reads in a static phase. A dynamic phase starts the application,
      but only by its declared command and only after asking.
    - Modules shipped: `python-testing`, `typescript-type-safety`,
      `architecture-design-from-code`, `architecture-design-document` and
      `application-runtime`.
    - The report is JSON. A bundled standard-library validator,
      `validate_report.py`, checks it, and each unrun phase's reason is
      recorded under `phases.not-run`.
  - `advise-from-evaluation` turns a report into ranked advisories, in a
    refactoring mode for code and an implementation mode for a design. It
    runs the same validator on the report it receives.
- Each check names the research findings it rests on. A diff finding sits in
  the changed lines, while its evidence may be read anywhere at the new
  revision. A check that depends on a tool's version names where the version
  is read.
- Open, and not settled by this publish:
  - which module a declined dynamic launch leaves loaded;
  - whether `design-headings: []` must be written out.

### 2026-11-22 — diataxis-doc-migration (render skill)

- **Behaviour change.** A new skill, `diataxis-render-docs`, renders a
  Diataxis Markdown tree to interactive HTML.
- **Behaviour change.** The coverage heading reader skips a page's leading
  frontmatter, and destination anchors get level-one titles, so a page's
  first heading is no longer misread or skipped.

### 2026-11-22 — research-tooling (digest support)

- **Behaviour change.** `index.py` lists a base's undigested captures, less
  those its decline list names. The research base model declares
  `undigested` as derived and names the digest command.
- **Behaviour change.** `research-base-audit` takes a `since <rev>` clause
  that narrows the audit to the living records changed in that range. The
  clause runs `git diff`, which the audit's read-only grant does not cover,
  so it may prompt. A follow-up changes it to take the record list from the
  caller.

### 2026-11-22 — task-board-management (eighth tranche)

- **Behaviour change.** The board accepts `kind: digest` on any board, and
  the index tags it.
- **Behaviour change.** `supervise-implementation` leases digest tickets
  only, or none, in one tranche. It closes a digest tranche with a
  `research-base-audit` of the records the tranche changed, after the gate.
- `supervise-implementation`'s *Closing a tranche* names the transferable
  guidance destination by its role, not by a lab path.
- `tranche-gate`'s earlier-findings reader reads a record's status through
  the board's own frontmatter parser, so a quoted `done` is counted.

### 2026-11-21 — research-tooling (capture-knowledge)

- **Behaviour change.** A new skill, `capture-knowledge`, files one session
  item into a knowledge base's private `sources/` layer, at the path its
  bundled `capture_path.py` names, and only where git ignores that path. It
  runs on command.

### 2026-11-21 — task-board-management (seventh tranche)

- **Behaviour change.** `scan_tranche.py --size --board <board>` leaves the
  board's files out of the tranche size count, so the limit measures
  integrated work rather than the record-keeping around it.
- **Behaviour change.** `supervise-implementation`'s *Collect* step corrects
  each lease's start commit to the branch's `git merge-base` with the main
  line before any integrator runs, and the worker brief names no commit.
- **Behaviour change.** `tranche-gate` ships `scripts/earlier_findings.py`,
  which lists the checklist items the earlier done gate reports found, and
  its step 6 runs it instead of counting by hand.
- **Behaviour change.** `scan_tranche.py` reads the gate's checklist ids from
  `checklist.md` at run time and treats them as defined inside their own
  project, reads YAML and TOML comments quote-aware, names its prose
  suffixes, and skips eval run output by path.
- **Behaviour change.** Each gate guidance candidate and candidate precedent
  carries a proposed scope, this repository or transferable, and the
  supervisor's close routes a ruled one there: a transferable precedent also
  goes to the central judgment register. The board model states promotion.

### 2026-11-21 — quality-of-life (working-conventions)

- **Behaviour change.** A new skill, `working-conventions`, packages three
  standing checks that hold in every project: estimate a heavy run's
  hardware use against a safety budget before launching it, check a runtime
  or package against current security advisories before running or
  installing it, and research a question before putting it to the user. It
  is model-invocable, so it loads at the moment each check applies.

### 2026-11-21 — research-tooling (cross-repository references)

- **Behaviour change.** `research-base-model.md` defines one reference form
  for a record in another repository's store, under *Citations*:
  `<repository>:<path-in-repository>`, optionally pinned to a heading or a
  commit. Such a reference goes in a record's `sources` or in prose, never
  in `authority`, because nothing resolves it from this repository.

### 2026-11-21 — task-board-management (sixth tranche)

- **Behaviour change.** `validate_board.py`'s `citation-bare-line-reference`
  rule now reports a bare `name.ext` + colon + number that ends a sentence
  mid-paragraph. The skip for a full stop and a space after the digits is
  retired; a numbered list item's name form is written in a code span,
  which the rule reads around. `board-model.md`'s citation rules say so.
- **Behaviour change.** `tranche-gate` counts a guidance candidate across
  tranches as well as within one: before writing *Guidance candidates* it
  reads the findings tables of every earlier closed tranche record.
- **Behaviour change.** `scan_tranche.py` reads a marker in Markdown only
  after an HTML comment opener outside code spans, so prose and code spans
  that merely mention a marker are no longer reported.
- **Behaviour change.** `account_attempt.py --sessions` prints each attempt
  in the session table's attempts cell as its id in a code span, then the
  attempt number, so the cell no longer reads as a citation.
  `supervise-implementation`'s `run-state.md` and `tranche-gate`'s
  `report.md` show the new form.

### 2026-11-21 — task-board-management (tranche length)

- **Behaviour change.** `supervise-implementation` sizes a tranche against a
  target of 6 to 8 hours of running time, net of owner waits. At opening it
  estimates the pool from earlier records' per-ticket times. When the pool
  falls short, it first scopes drafts through `task-interview` agents that
  use the precedent register, and asks the owner what is left in one batch.
  It never offers a tranche below the target without reporting the
  shortfall.
- **Behaviour change.** A ticket scoped during a tranche joins it while the
  target is unmet. Lineage follow-ons and worker-reported tooling still wait
  for the next tranche. The record gains `Target:` and `Running time:`
  lines, and the tranche still closes only on drain or at the size limit.

### 2026-11-21 — task-board-management (precedent register)

- **Behaviour change.** A board may carry a precedent register,
  `precedents.md` at its root, defined in `board-model.md`. It holds the
  owner's rulings that settle more than one decision, one entry each, with
  six fields: *When*, *Ruling*, *Scope*, *Source*, *Applied* and *Status*.
  `validate_board.py` skips it by name and the index does not list it.
- **Behaviour change.** `supervise-implementation` reads the register before
  opening any escalation entry. When a standing entry fits in full, it applies
  the ruling, logs the use with the entry's id and opens no entry; a partial
  fit still escalates. The analyst cites any entry bearing on its draft, and
  the session that applies the owner's decisions on a gate report adds the
  confirmed candidate precedents to the register in the same commit.
- **Behaviour change.** `task-interview` reads the register before each
  question to the user, and records a fitting entry's ruling `RESOLVED` with
  the entry's id instead of asking.

### 2026-11-21 — task-board-management (fifth tranche)

- **Behaviour change.** `tranche-gate`'s checklist gains a thirteenth item,
  task references: a task id in code, tests, manifests or skill text, or an
  opaque label used outside the document that defines it. `scan_tranche.py`
  gains a `task_refs` scan that reports `id` and `label` hits on added lines.
  Comments and docstrings are remediated by rewriting each reference to state
  the reason it carried; a hit in published skill text is reported. The
  skill's description now counts thirteen defects.
- **Behaviour change.** `supervise-implementation`'s worker and integrator
  briefs state the task-label rule, so workers keep board ids and labels out
  of what they commit and integrators check for them in the diff.

### 2026-11-20 — task-board-management (fourth tranche)

- **Behaviour change.** `supervise-implementation`'s *Opening a tranche*
  gains a step 4 that archives the previous tranche's run files: the run
  directory's `leases.md`, `declared/` and `drafts/` move under
  `.supervise-implementation/archive/<tranche>/`, and `.tranche-gate/`'s loose
  files under `.tranche-gate/<tranche>/`, named by the previous record's `id`.
  Archives are kept and never pruned. The later opening steps are renumbered
  5 to 8, and the true-up now reads the archive this step wrote.
- **Behaviour change.** `account_attempt.py` refuses a lease row whose
  `Attempt` cell is not a number, exiting 2 and naming the row, where it used
  to pass the text through.
- `tranche-gate`'s report template names `account_attempt.py --sessions` over
  the lease table as the session table's source, in place of `--reconcile`.
  *Closing a tranche* says a session row reading `absent` is filled by the
  next opening's true-up.

### 2026-11-20 — task-board-management (third tranche)

- **Behaviour change.** `validate_board.py` has a new error rule,
  `citation-bare-line-reference`: a bare `name.ext:<digits>` citation in a
  task's prose or a table cell is reported. A number followed by a full stop
  and a space is skipped, as a list item. A board that cites by line number
  now fails validation until those citations name the symbol instead.
- **Behaviour change.** `check_test_changes.py` takes `--declared-dir` and
  `--record`, and reads only the declarations of attempts the tranche record
  shows as merged, so an unmerged attempt's files no longer count.
  `tranche-gate` passes them.
- `account_attempt.py --sessions <leases.md> --project <dir>` prints the
  allocation log's session table, one row per session, with `--json`.
  `supervise-implementation` fills the table from it at the close, and true-ups
  the previous tranche's rows at opening. A session still running reads
  `absent`.
- `supervise-implementation`'s window check reads the compaction threshold
  against a band net of the compaction reserve.

### 2026-11-20 — task-board-management (stuck detector)

- **Behaviour change.** `supervise-implementation` no longer escalates an
  attempt for its share of verification calls. The 25% sub-ceiling, the
  lease's fixed-check count and the adjusted share are gone; the raw share
  stays in the allocation log as a figure only.
- **Behaviour change.** `account_attempt.py` reports `stuck` and
  `stuck_episodes`: the same check failing the same way 3 times, the same
  result 4 times with no edit between, or 6 steps alternating an edit and an
  unchanged check. The supervisor re-grants a task's first stuck attempt
  without asking and escalates the second. `--fixed-checks` is no longer
  accepted.

### 2026-11-19 — task-board-management (tranche fixes)

- **Behaviour change.** `supervise-implementation`'s verification
  sub-ceiling is now computed net of the checks a task's acceptance
  criteria fix, so an attempt is no longer flagged for checks its brief
  required.
- **Behaviour change.** `account_attempt.py --match-rate` no longer asks
  for an exact match per session. It takes each model's median ratio of
  priced to recorded cost and flags the price table only when that median
  leaves 0.90 to 1.02. A billed model no transcript called is reported
  apart and never fails the table, and the per-session tolerance is gone.
  The reconciliation shows each session's harness total and ratio beside
  its priced cost.
- **Behaviour change.** `supervise-implementation` now says who closes the
  tranche record and when: the supervisor commits it at the close, and the
  owner's review of the gate's report sets it done.
- **Behaviour change.** `tranche-gate` runs the test-change check over the
  whole range in every case, with the merged attempts' declarations, rather
  than trusting integrator verdicts that may predate later changes.
- **Behaviour change.** `tranche-gate` commits leftover and convention
  fixes (D9, D11) in published files too, where it previously only reported
  them there.
- **Behaviour change.** `tranche-gate` cites findings as `path:name`, never
  by line number, so its report passes the board validator.
- `scan_tranche.py` now attributes integrator verdicts whose merge line
  wraps or is backticked.

### 2026-11-19 — diataxis-doc-migration (date line without a lint directive)

- **Behaviour change.** The date line the Diataxis skills write under a
  page's H1 now ends in a period: `*Last updated: YYYY-MM-DD.*`. The period
  keeps the line clear of markdownlint's MD036, so the four page templates
  no longer carry a `markdownlint-configure-file` directive turning MD036
  off for the whole page. This closes the known issue in the 2026-11-18
  page-dating entry.
- `check_pages.py` still reads the old form, `*Last updated: YYYY-MM-DD*`,
  so pages dated before this change keep passing the audit; it is never
  written.

### 2026-11-18 — diataxis-doc-migration (page dating)

- **Behaviour change.** Every page the Diataxis skills write now carries a
  `*Last updated: YYYY-MM-DD*` line directly under its H1. The four page
  templates in `diataxis-create-docs` include it.
- **Behaviour change.** The manifest gains an optional `pages` list: one
  entry per page a run wrote, with its path, a `sha256:` fingerprint of its
  content and the date on its line. It is additive, so `schema_version` stays
  1 and existing manifests still validate.
- **Behaviour change.** A new bundled script, `check_pages.py`, fingerprints
  pages or checks every `pages` entry against the repository. When a
  manifest records `pages`, `diataxis-audit-docs` runs it and reports each
  missing page, missing or mismatched date line, and page edited outside the
  skills. Pages no run wrote carry no entry and are not checked.
- Known issue: the page templates carry a `markdownlint-configure-file`
  directive that turns MD036 off for the whole of each page, so the date
  line passes lint. A narrower fix is planned.

### 2026-11-18 — task-board-management (scan and checklist fixes)

- **Behaviour change.** `scan_tranche.py`, bundled with `tranche-gate` and
  `supervise-implementation`, now leaves out generated regions, the text
  between `<!-- BEGIN GENERATED ... -->` and `<!-- END ... -->` markers, in
  any file, instead of skipping the board's `README.md`, `TREE.md` and
  `ARCHIVE.md` whole. Hand-written text in those files now counts, and
  generated text elsewhere no longer does. Its `--board` flag is removed; a
  call that passes it now fails.
- **Behaviour change.** The scan's marker check reports `TODO` and `FIXME`
  only where a comment leaves one: inside a Python comment, or after a
  comment opener (`#`, `//`, `<!--`) on the same line in other files. Prose
  that names the terms is no longer reported. A marker on a later line of a
  multi-line HTML comment is now missed.
- `tranche-gate`'s checklist drops its two notes on these false positives,
  and its `SKILL.md` and `supervise-implementation`'s cycle reference describe
  the size count as leaving out generated regions.
- Comments and docstrings in the bundled scripts no longer cite internal task
  names. No behaviour changes with that.

### 2026-11-16 — task-board-management (tranche-gate)

- **Behaviour change.** A new skill, `tranche-gate`, published on both
  platforms. It gates a closed tranche, or any batch of agent commits, before
  the owner's review. A bundled scan covers the whole range, base to tip, and
  the model reads one task's diff at a time, judging against a closed
  checklist of twelve defects. It does not look for style or correctness bugs.
  Every finding cites its `file:line` and is verified against the code.
- It commits only behaviour-preserving cleanup of what the batch introduced,
  one kind of change per commit. It re-runs the owning suite and the test
  check after each commit, and reverts the commit if either fails. It
  reports, without making them, changes to a published skill, removal of a
  test whose subject remains, and any behaviour change. Each
  surplus-verification removal is prepared as an unapplied patch. The report
  is appended to the tranche record, and nothing is pushed.
- **Behaviour change.** `supervise-implementation` now has a size limit: the
  4,000 changed lines the gate declares, labelled unmeasured. It counts that
  size every cycle with the bundled `scan_tranche.py --size`, and at the limit
  it leases nothing new and closes the tranche once the work in flight has
  integrated. At the close it writes the price table's match rate into the
  record, then launches `tranche-gate` as a fresh agent.
- `check_test_changes.py` now ships in both skills, unchanged.

### 2026-11-15 — task-board-management (supervise-implementation)

- **Behaviour change.** A new skill, `supervise-implementation`, published on
  both platforms. On the owner's word it opens a tranche over the whole
  eligible board and leases scoped tickets to up to three fresh workers, each
  in its own worktree. A fresh integrator verifies, merges and closes each
  stream, one at a time, and is the only committer while the tranche runs.
  Stalls within tolerance are re-sized without asking; the rest become
  escalation entries that are asked when the owner returns, with one push per
  cycle. Each cycle is one turn, re-read from disk. The closed tranche goes to
  an analysis gate, and nothing is pushed.
- It bundles two scripts: `account_attempt.py`, which prices a worker's
  transcript and measures its verification share, and `check_test_changes.py`,
  which flags tests that were deleted, skipped or focused without being
  declared.
- At opening it checks two settings and recommends values, without writing
  them: an auto-compact window near 300k for the supervisor's session, and
  `worktree.baseRef: "head"`. Until the second is set, it runs one worker at a
  time.
- `orchestrate-implementation`'s eligibility and interference rules moved,
  unchanged, into a shared `references/task-selection.md` that both skills
  carry. No change in its behaviour.

### 2026-11-15 — task-board-management (verification scope rule)

- **Behaviour change.** `focused-implementation` now keeps new verification
  tooling out of the task it is implementing. A test written for the task, and
  a helper used only by its tests in its own test files, are the task's own.
  Anything meant to outlive the task (a shared fixture library, a test runner,
  a harness, a new measurement script, a validator or lint rule) is filed with
  `to-follow-on`, at the priority its value warrants. If the task's checks
  cannot run without it, it is filed as the task's blocker and the task stops.
- Steps 5 and 6, anti-fix validation and the realistic build, now send an
  instrument or build the repository does not already have to that rule.
- **Behaviour change.** Step 7 now says when to stop: once the budget's checks
  pass, no further review rounds, reviewer subagents or re-runs of a green
  suite. Anything more that would help goes in the execution log.
- No other skill in the project changed.

### 2026-11-02 — research-tooling (authority resolution)

- **Behaviour change.** `validate_base.py`, bundled into all three
  research-tooling skills, now checks that every `authority` entry on a living
  record can be found. A path is resolved from the nearest directory above the
  base holding `.git`, and must exist inside it. A `path:Name` locator must
  match a heading in a Markdown document, a definition in a `.py` file, or a
  whole word in any other file. A URL must have a host, and is never fetched.
- Five new rules, all errors: `authority-root-missing`,
  `authority-outside-root`, `authority-target-missing`,
  `authority-locator-unresolved` and `authority-url-invalid`. A base whose
  living records name repository paths, but with no `.git` above it, now gets
  one finding instead of a clean result. Frozen records are not checked.

### 2026-11-01 — research-tooling (first publish)

- **Behaviour change.** Three skills are published here for the first time, on
  both platforms. `research-base-init` adopts a research base in a repository,
  `synthesize-research` turns raw source material into a cited finding, and
  `research-base-audit` re-verifies a base's living claims against the
  authorities they name.
- Each skill carries its own copy of the research-base contract and the base's
  two scripts. The two measurement instruments the lab's own research runs are
  not included in any bundle.
- `research-base-audit` now tells a Codex agent to resolve `CLAUDE_SKILL_DIR`
  itself, as its two siblings already did.

### 2026-11-01 — task-board-management (worktree streams)

- **Behaviour change.** `orchestrate-implementation`'s *Dispatch* section now
  covers a stream in its own worktree. A worktree is cut from committed state,
  so the brief names every uncommitted file it cites, the task file included,
  by the main checkout's absolute path, and says the worktree's own copies are
  stale.
- Bringing a worktree's diff back now counts as a write to the shared tree. The
  main session takes the diff as a patch, checks that it still applies, and
  applies it only once no in-flight stream's read set meets its files. The
  stream's close waits with the patch.

### 2026-11-01 — task-board-management (orchestrate dispatch)

- **Behaviour change.** `orchestrate-implementation` now says it is the
  planning skill, and gains a *Dispatch* section. When two or more independent
  streams are ready, it launches them all at once, each in its own subagent. A
  lone ready stream runs inline, unless the plan records context as the reason
  to delegate it. Where the platform offers no subagent primitive, the streams
  run serially. The section names no platform tool.
- A delegated stream implements only its own task's code and tests, and stops
  before `focused-implementation`'s close-out. It does not edit the board, task
  files or agent instruction files, and it does not commit, push or publish. It
  returns a diff summary, its suite's result with any excluded files, and every
  premise of its brief it found false. The main session re-runs the suite,
  reads the diff, then closes and commits, one close at a time.
- The plan document now names each stream's read set as well as its write set,
  and orders a dependency at the step that needs it. A stream whose writes meet
  another stream's reads, or a tool the closes run, gets its own worktree, or
  the closes wait for it.
- The description leads with planning rather than "run them to completion". The
  name and the trigger phrases are unchanged.

### 2026-11-01 — task-board-management (index rows)

- **Behaviour change.** A row in a board's generated `README.md` now shows
  every relation its task still has, in this order: composition (`⊂ part of`),
  live blockers (`⇠ blocked by`), then lineage (`↳ from`). Each part appears
  only when present. Before, one suffix was picked by precedence, so a blocker
  hid the task's `part-of`.
- **Behaviour change.** A blocker that has reached `done` no longer appears in
  the row. Its history stays in the task's `blocked-by:` frontmatter. A
  `superseded-by` redirect still replaces the whole suffix.
- `board-model.md` states the row contract under *Generated views*. It ships to
  all seven task-board skills, as does the generator.

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
