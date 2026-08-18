# The board model

A task board is a directory of Markdown files inside the repository it describes.
Each file is one self-contained task specification, complete enough to hand to an
agent or a person with no other context.

## The rule

**Frontmatter is the only source of truth. The folder is a generated view of it.**

A task's state lives in its YAML frontmatter. Which subdirectory the file sits in
is a pure function of that frontmatter, and so is the board index. Both are
derived, both are checked, and neither is ever edited by hand to mean something
the frontmatter does not already say.

This exists because the obvious alternative fails in a specific, observed way.
When state is carried in three places at once — a prose `Status:` line, the folder
the file sits in, and a hand-maintained index — they drift apart, and the drift is
invisible until someone reads all three and notices they disagree. Reconciling them
becomes a reading exercise over the whole board. Deriving two of the three from the
first makes the disagreement a validation error instead.

## Frontmatter

```yaml
---
id: cache-variance-harness          # kebab-case; must equal the filename stem
title: Build the cache variance measurement harness
kind: ticket                        # ticket (default) | spec
status: draft                       # draft | scoped | in-progress | done | superseded
gate: none                          # none | manual | owner
priority: medium                    # high | medium | low
category: backend / tooling         # free text; grouping label for the index
created: 2026-07-22
updated: 2026-07-23
parent: cache-consistency           # optional — lineage: the task this split from
part-of: cache-variance-spec        # optional — composition: what this is a piece of
blocked-by: []                      # optional — tasks that must finish first
supersedes: []                      # optional — ids this replaces
superseded-by: null                 # required when status is superseded
revisit: false                      # only meaningful when status is done
outcome: null                       # required when status is done — one line
---
```

### `kind` — spec or ticket

Every task is one document-level unit of work, at any level. `kind` names its role:

| Value | Meaning |
| --- | --- |
| `ticket` | A particular role or portion — usually implementation, sometimes exploratory (research, a spike). The smallest ticket is still worth a subagent or a fresh session. **Default** when `kind` is absent. |
| `spec` | Architecture and composition: the vision, the decisions, how steps compose to a result. A spec keeps residual work of its own that may be too small to ticket. |

`kind` does **not** affect which folder a task derives — a spec and a ticket both
file by their own `status`/`gate`/`blocked-by` like any task. It affects only how
the task is read and how it composes (below).

### `part-of` — composition, kept distinct from lineage

Work decomposes: a spec is realized through several tickets, and a ticket that turns
out to be more than one slice can itself hold subtickets. `part-of` records that
composition — the single task this one is a component of.

```yaml
part-of: dashboard-redesign-spec   # this ticket is one slice of that spec
```

It is single-valued (a slice belongs to exactly one parent) and works at any depth:
a ticket is `part-of` a spec; a subticket is `part-of` a ticket. Depth comes from the
chain, not from new kinds — a subticket is just a ticket that is `part-of` another
ticket.

**`part-of` is not `parent`, and the difference is load-bearing:**

| Field | Question | Roll-up |
| --- | --- | --- |
| `parent` | *lineage* — where was this split from? | A follow-on must **not** roll up into what it was carved out of. |
| `part-of` | *composition* — what is this a piece of? | A completed piece **does** fold its outcome up into its parent. |

A task can carry both: split off X (lineage) yet be a piece of Y (composition).

**A spec's status is its own — never derived from its tickets.** It is tempting to
compute "spec done when all its tickets are done", but three real states break that:
a ticket with no spec at all (work too small to design-doc); a spec that is
`done`+`revisit` while the tickets for its deferred work stay open; and a spec's own
residual work that was never ticketed. Spec completion is more than "all tickets
done", so the spec carries its own `status`. At most, triage may emit a **soft note**
when a spec is `done` with open ticket descendants — never a hard failure.

**Fold-back is derived, not copied.** A spec (or any task with slices under it) opts
in by carrying an empty rollup block:

```text
## Slices

<!-- BEGIN SLICES -->
<!-- END SLICES -->
```

`generate_index.py` fills it with the task's direct slices — each slice's status,
and the one-line `outcome` of every finished one. So a completed ticket's outcome
appears in its spec with **no manual copying**: the spec is the single readable
record of how each slice went, and because the rollup is regenerated rather than
maintained by hand, it cannot drift. The full ticket document stays in the archive
normally.

**Depth: permissive mechanism, restrictive policy.** The model allows any depth. The
conventions do not: prefer siblings over nesting, and nest only when a group is a
real handoff unit with its own acceptance boundary. The validator emits a **soft
warning** past a shallow depth rather than forbidding it — the mechanism never fights
a genuine need, but everything steers toward flat. Over-decomposition, not the data
model, is the failure mode to guard against.

Cycles in `part-of` are rejected outright: a composition loop is a task that can
never be built.

### `status` — how far the work has got

| Value | Meaning |
| --- | --- |
| `draft` | Raised, but its Open Questions are unresolved. **Not implementable.** |
| `scoped` | Every open question walked down to a recorded decision. Ready to implement. |
| `in-progress` | Implementation started. |
| `done` | Shipped or resolved, with nothing further contemplated. |
| `superseded` | Replaced by a later spec. Kept for provenance only. |

### `gate` — which person is this waiting on

`gate` is orthogonal to `status`. It answers "what is this waiting on?", not "how
far along is it?".

The split is **action vs decision**:

| Value | Meaning |
| --- | --- |
| `none` | An agent can act on it with no external dependency. |
| `manual` | Waiting on a person to **perform an action** an agent cannot: provision, deploy, install, run against a live environment, verify by hand, or supply material. |
| `owner` | Waiting on a person to **make a decision** — product, founder, legal, or vendor. |

The two clear differently: a `manual` gate closes when someone *does* the thing; an
`owner` gate closes when someone *answers*. That is why they are separate values
rather than one "blocked on a human" bucket.

`manual` deliberately covers more than testing. An earlier version of this model
called it `qa`, which read as "quality assurance" and consistently drifted in
practice toward the broader meaning anyway — real boards filled that folder with
deployments, migrations, server reconciles, and "awaiting input material", almost
none of which are acceptance testing. The name now matches what the bucket does.

A gated task is **not finished**, so `gate` may only be non-`none` while `status`
is `draft`, `scoped`, or `in-progress`. If the remaining step of an otherwise
complete task is gated, the task is `in-progress` with a gate — not `done`. Its own
acceptance criterion is not met until the gated step runs, so recording it as `done`
would be false.

### `blocked-by` — waiting on the board, not on a person

A task can be un-startable because another task has to land first. That is not a
gate: nobody has to decide or do anything *about this task*, and when the blocker
closes it becomes actionable on its own.

```yaml
blocked-by: [data-layer-regional-expansion]
```

Blocked while **any** listed id has not reached `done`. This is the one field whose
folder effect depends on **another file's** state, which has a deliberate
consequence: a task's derived folder can change while its own file is untouched.
Closing a blocker makes every downstream task report a folder mismatch — and that
mismatch is the unblock notification. It is the only mechanism here that tells you
work became available without you going looking.

Three rules keep it honest:

- A blocker that reached `superseded` rather than `done` is a finding. Repoint at
  its successor instead of waiting on a replaced spec.
- **Cycles are rejected.** Two tasks blocking each other can never become
  actionable, and nothing else on the board would surface that.
- It **survives on a finished task**, like `parent`, as a permanent record of what
  the work came after. Only unfinished tasks are filed by it.

Do not use `blocked-by` for a dependency on a person — that is what `gate` is for.
A task with both is filed by its gate, because closing the sibling would not make
it startable.

### `revisit` — done, working, and deliberately not taken further

`revisit: true` marks work that is **finished and correct**, and that additionally
carries a recorded set of better-but-costlier options which were evaluated and
deliberately declined, each with the specific condition that would justify
revisiting it.

This is the category most easily blurred, so hold the line on it:

- `gate: manual` / `gate: owner` — waiting on someone; the work is **unfinished**.
- `status: done`, `revisit: false` — done, with nothing further contemplated.
- `status: done`, `revisit: true` — done **and working**, with a documented next
  tier that is a deliberate not-yet rather than a gap.

A `revisit` task is **not a backlog item**. Its upgrade paths were declined for
stated reasons. Before picking one up, check whether the stated condition has
actually changed. Read one before re-researching a problem it already covers — the
point is to avoid re-deriving a decision that was already made with evidence.

A task with `revisit: true` must carry an `## Upgrade paths` section listing each
declined option and its revisit condition. This is enforced.

### `outcome` — the one line the archive shows

Required once `status` is `done`: what changed, and how it was confirmed. The
`## Execution log` is the full account; `outcome` is its one-line form.

Write it for someone scanning a hundred finished tasks who will **not** open the
file. "Done" and "shipped" are rejected — an outcome under fifteen characters is a
label, not a summary.

A one-line *value* need not be a one-line *source*. Wrap it with a folded scalar
and the parser joins it back into one line:

```yaml
outcome: >-
  Rewrote the frontmatter parser so folded values survive,
  confirmed by 16 new tests and a dogfood pass over this board.
```

`>`, `>-` and `>+` all fold. The literal forms `|`, `|-` and `|+` are **refused**,
as is a blank line inside a folded block: both keep newlines, and the generated
index emits `outcome` as a single continuation line beneath a list item, so a
value containing one would break the list it lands in.

This field exists to remove a maintenance surface rather than add one. Without it,
every completion means writing the doc *and* hand-writing a summary line into an
index somewhere — a second copy of the same fact, in the one place that has no
validation, which is exactly what goes stale. Storing it in frontmatter lets the
archive index be generated instead.

## Folder mapping

The subdirectory is derived from the frontmatter, first match wins:

| Condition | Folder |
| --- | --- |
| `status: superseded` | `superseded/` |
| `gate: manual` | `manual-blocked/` |
| `gate: owner` | `owner-deferred/` |
| `status: done` and `revisit: true` | `revisit/` |
| `status: done` | `completed/` |
| any `blocked-by` not yet `done` | `task-blocked/` |
| otherwise | *(board root)* |

The board root therefore holds exactly the tasks an agent can start right now. That
is the property worth protecting: **if a task is sitting at the top level, it is
actionable.** Everything else is filed by *what* it waits on — a person's action, a
person's decision, or another task.

Three orderings in that table are deliberate:

- **Gate outranks `done`**, encoding the rule above that a gated task is not
  finished.
- **Both gates outrank `blocked-by`.** A task waiting on a sibling *and* a person is
  still un-startable when the sibling closes, so it files by the person. Filing it
  under `task-blocked/` would promote it to the root on a false signal.
- **`done` outranks `blocked-by`**, which is what lets a finished task keep its
  `blocked-by` as provenance instead of being dragged back into `task-blocked/`.

## Required body sections

Beyond the frontmatter, a task body is free-form prose with four required headings:

- `## Why this exists` — the problem, and the evidence it is real.
- `## Plan` — what to do, in phases where the work warrants them.
- `## Open questions` — every unresolved decision. A `draft` task must have at
  least one. A `scoped` task must have none left unanswered: each becomes a
  **resolved decision**, recorded in place with the answer and the date, rather
  than deleted.
- `## Owner` — who owns each phase, and which phases need an external call.

Conditionally required:

- `## Upgrade paths` — required when `revisit: true`.
- `## Execution log` — required when `status: done`. What shipped, on which branch
  or commit, and how it was verified.

## Cross-references

Tasks link to each other with ordinary relative Markdown links. Three frontmatter
fields carry the links that matter structurally:

- `parent` — lineage: this task was split off that one. Set by `to-follow-on`, and
  the reason a follow-on never loses its provenance.
- `part-of` — composition: this task is a piece of that one. Distinct from `parent`
  (see the composition section above).
- `blocked-by` — this task cannot start until those finish. The only one that
  changes where a file belongs.
- `supersedes` / `superseded-by` — a replacement pair. Both sides are written, so
  the relationship is navigable from either end.

Every id referenced by `parent`, `part-of`, `blocked-by`, `supersedes`, or
`superseded-by` must resolve to a task that exists on the board. A dangling
reference is a validation error.

The prose links are checked too, but as a **warning** rather than an error. Every
relative Markdown link in a task's body is resolved against that task's own
directory; one whose target no longer exists is reported without failing the run.
The asymmetry is deliberate: an id is inert text that only a person edits, while a
relative path breaks on its own. Setting `status: done` derives the file into
`completed/`, stranding every link that pointed at it and every link it carried —
and the inbound half is silent, because the file that moved is the one under
attention and the files citing it are not. A hard failure would redden the board
during the ordinary window between the move and the repair.

Existence only, for the path itself. Links inside fenced blocks, inline code
spans, and generated regions are skipped — quoted link syntax is documentation
about a link, not a link, and a generated region is repaired by regeneration.

### Citations name things, never line ranges

A citation into source is written `filename:name`, and it asserts that **the named
thing still exists in the file the link points at**. A line range is not a
citation, and one is reported as an error.

A range rots without anything moving or being deleted. An edit *above* the cited
region shifts every number below it while the path, the file, and the quoted prose
all stay valid, so nothing reports a problem — nothing is broken except the claim.
A path check cannot see it, because the path never moved.

Four forms, and nothing else:

| Form | Written | Used for |
| --- | --- | --- |
| name | `validate_board.py:parse_frontmatter` | a symbol in code, a heading in prose |
| key path | `project.yaml:skills` | a structured file, where a key is the stable unit |
| bare file | `install.py` | where no single name encloses the target — an import block, a comment region, a span crossing several top-level names |
| commit-pinned | `validate_board.py:LIST_ITEM@8c43768` | a closed task that deliberately describes superseded code |

The **commit-pinned form is recognised and skipped, not resolved.** A bundled
script may import only the standard library, so it cannot ask git what a file
looked like at a commit. What the form buys is an exemption that is written down,
greppable and auditable, instead of a citation that quietly fails to mean
anything — and an exemption you have to type a commit hash into is not one anybody
reaches for by accident. Use it only where naming today's symbol would make a
closed document describe a bug that never existed.

**The reach is narrower than "reported as an error" makes it sound, and the
limit is the one stated just above.** The first two citation rules read the same
link traversal as `link-target-missing`, so both inherit its skips. Fenced blocks
and generated regions are meant to be skipped. The code-span skip left a real
gap: a line range written as a bare code span, with no link around it, is not a
link at all, so neither rule could ever see it — and instances survived on this
board while every check passed. `citation-code-span-range` closes that gap with a
separate scan over raw lines, matching a code span that holds a filename, a
colon and digits. Requiring the digits is what keeps it off the four forms above.

**A fourth rule closes the last of the gap, and what it deliberately leaves
alone is part of its design rather than an oversight.** A line reference written
as ordinary prose — a sentence claiming a symbol sits at a numbered line, with
no link and no backticks — is none of the three things the rules above read, so
it was invisible to all of them by construction. It rots exactly as a range
does. `citation-prose-line-reference` scans raw lines for the word followed by a
single number, and it is an `error` like its neighbours.

**It skips a reference carrying a second number, and that exclusion is
load-bearing.** A citation points at one line; a sentence *about* how a range
rotted carries two by its nature — a span, a before-and-after, or a pair. This
board keeps a population of such sentences on purpose, as the record of how
citations rot, and counting numbers drops every one of them without an allowlist
and without anything written down about them. **Do not "tighten" the rule to
catch them.** A before-and-after joined by a word rather than an arrow is the
one shape this misses; the safe harbour for it is a code span, which is
invisible to `citation-code-span-range` too because that rule needs a colon
before its digits and a prose reference has none.

**This rule is an error while `link-target-missing` beside it is only a warning,
and the asymmetry is deliberate.** A moved file leaves a legitimate window between
the `git mv` and the repair, so a hard failure there would redden the board during
ordinary work. A citation naming something that does not exist has no such window:
a rename and its citations are edited in one pass by one person, and where they
are not, the citation is a false statement in the record for as long as nobody
looks.

## Severity: two kinds of warning, and everything else an error

The asymmetry above is one instance of a general rule, written down here so the
next rule is not argued from scratch. **A rule reports at `warning` when it is
one of exactly two things:**

| Category | Meaning | Rules in it |
| --- | --- | --- |
| **Advisory** | The finding indicates **no defect**. The board is valid in this state; the rule is a policy nudge or a triage note, and a reader may legitimately decide to do nothing. | `part-of-too-deep`, `spec-done-open-tickets` |
| **Transient** | A **real defect** that a prescribed workflow produces and repairs in the same session. Failing the run would make a practice this repository recommends illegal. | `link-target-missing` |

**Every other rule is an error, and the test is whether a legitimate workflow
produces the state.** If none does, there is no window to tolerate and no reason
to exit 0 on it.

This is a description of the rules as they stand, not a preference imposed on
them — it was derived by reading all of them and finding that the warnings fell
into exactly these two groups. That is the evidence for it, and it is also the
reason it is worth pinning: a rule added at `warning` without fitting either
category is either a miscategorised error or a new category that has to be
argued for explicitly.

**The two clear differently, which is why they are not one bucket.** An advisory
finding may stand forever without anything being wrong. A transient one is
expected to be gone by the end of the session that caused it — and a transient
warning that is *still there* next session is a defect that got missed, not a
state anyone chose. Collapsing them into "things that do not fail the build"
loses exactly that distinction.

**What this does not settle.** Whether a warning on a board is in fact acted on
in practice is unmeasured, and deliberately so: the only way to measure it is to
leave a population of findings standing that nobody must act on, which corrupts
the channel being measured. The principle above does not depend on the answer.

## What the scripts own

- `scripts/validate_board.py` — parses every task, checks the schema, the folder
  mapping, the gate/status rule, the required sections, cross-reference
  resolution, the dependency graph, and the relative link targets each body
  cites. Exits non-zero with a list of findings; link targets are the one check
  that warns rather than fails.
- `scripts/generate_index.py` — rewrites every generated region: the `README.md`
  and `ARCHIVE.md` indexes, the `TREE.md` composition view, and each opted-in task's
  in-place `## Slices` rollup. `--check` reports staleness without writing.

Narrative outside those blocks — retrospectives, why a decision was made, what a
session found — is hand-written and is never touched by the generator. That
narrative is the part of a board worth keeping; the per-task lines are the part
worth generating.

## Generated views

Different readers want the board sliced differently, so the generator writes
several regions, each derived from the same task frontmatter:

| File | Holds | Grouped by |
| --- | --- | --- |
| `README.md` | everything still in play, plus `revisit/` | folder (status), then category |
| `ARCHIVE.md` | `completed/` and `superseded/` | folder, then month closed |
| `TREE.md` | every task in a composition relation | `part-of` (nested tree) |
| spec docs | each task's own direct slices | in-place `## Slices` rollup |

The live index shows completed and superseded only as a count and a pointer, so
the file a person opens daily does not grow without bound as the board ages.

`README.md` and `TREE.md` are the two axes the same tasks can be read along:
README groups by *what a task is waiting on* (status/folder), for auditing and
picking work; TREE groups by *what a task is a piece of* (composition), for seeing
how an effort decomposes. `TREE.md` exists only when the board has composition.

`revisit/` stays in the **live** index deliberately. Its entire value is being seen
before someone re-researches a problem it already settled; filed into an archive
nobody reads, it stops doing its job.

### Generated output lints clean under default markdownlint rules

**An adopting repo needs no markdownlint configuration**, and that is a contract
rather than a courtesy: a generated region is one a human is forbidden to edit, so
if it fails a lint rule nobody can fix it — hand-editing is against the model and
the next run would revert it anyway. Two rules are in play, handled differently on
purpose.

**Duplicate headings are prevented structurally.** Every heading the generator
emits is qualified by the group it sits under — `Active — <category>` in the live
index, `Completed — <month>` in the archive. The same category routinely appears
in two folder groups, and the same month in both archive groups, which would
otherwise emit byte-identical headings. That is markdownlint MD024, and worse: two
indistinguishable table-of-contents entries pointing at different sections, in a
document whose job is orientation.

**Line length is suppressed, narrowly.** An entry line carries a title, a link, a
status and a priority together, and an archive entry adds a prose `outcome`
beneath it. Wrapping those would break scanning, which is the index's whole job;
truncating titles would lose information. So the generator emits a markdownlint
disable comment naming the line-length rule immediately inside each opening
marker, and the matching enable immediately before the closing one. **The
suppression names that one rule only** — a later duplicate-heading regression still
surfaces as a failure instead of being masked.

The enable is emitted **inside** the region on purpose. A disable with no matching
enable would switch the rule off for every hand-written line below the block,
which is prose the board owner does own. Prose outside the markers is never
covered by this contract and stays the owner's to wrap or accept.

## Completed tasks are frozen

A finished task is a **dated record, not living documentation**. Its claims describe
what was true when the work happened, and they are not maintained afterwards.

This matters because it removes a maintenance burden people expect to have. A
completed task saying "this file is 27% of the codebase" does not become wrong when
the file shrinks — it becomes history, which is what it was for. Documents only
drift when they claim to describe the present, and a completed task does not.

So: **never re-verify a completed task's body against current source.** Triage reads
non-completed tasks. The two exceptions are narrow and deliberate:

- A `revisit/` task's declined conditions *are* re-checked, because the whole point
  of recording a condition is to notice when it occurs.
- A dangling cross-reference is repaired anywhere, since it breaks navigation rather
  than making a stale claim.
