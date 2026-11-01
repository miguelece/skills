# The research base model

A research base is a directory of Markdown files inside the repository it serves.
It holds the material a repository's decisions are drawn from — gathered,
connected and analyzed — so the reasoning behind a choice can be found later by
someone who was not there when it was made.

It does not decide what to *do* with what it holds. Planning, prioritization and
scheduling belong to whatever board or tracker the repository already keeps. A
research base feeds those and must not duplicate them.

## The rule

**A record's location is keyed to what it is. Its state lives in frontmatter and
reaches the reader through a generated index.**

A record's directory is a function of its *kind* — raw input, pre-registered
material, synthesis — and of nothing else. Status, confidence and maturity are
declared in frontmatter. The index is derived and regenerated from that
frontmatter; the location is not derived at all.

This is deliberately **not** the rule a task board uses. A board derives a task's
folder from its status, which is a real answer to a real problem: state carried in
a prose line, a folder and a hand-maintained index drifts apart invisibly, and
deriving two of the three makes the disagreement a validation error instead.

**What that rule costs is file movement, and a research base cannot afford it.**
A base's records are cited from across the repository, so moving one breaks
every citation that named its old path, and repairing those links is what the
maintenance actually consists of. The cost was measured first-hand in the
repository this model was written for and is recorded in the finding
*location-keyed-to-kind-not-state*: among that repository's closed records, the
two most frequent reasons for a post-closure commit are both link repair caused
by a move, and its research records are the most heavily cited class it holds.

**Read that as directional.** It is one repository, measured under one set of
conventions, and the citation instrument counts occurrences of a filename stem
rather than resolved links, which over-counts. The direction is not in doubt; the
figures are not portable out of that corpus, and are quoted there with the
counting rule that produced them rather than restated here.

**Frontmatter-as-truth and the generated index transfer without qualification.**
Those are the board's genuinely portable half. What does not transfer is deriving
the path.

## Two regimes, and they are not two content types

**What decides how a record is maintained is whether it claims to describe the
present.** Not its format, not its source, not whether someone else wrote it.

### Frozen — the record describes a moment

A measurement taken on a given day, a transcript, a paper as it was downloaded, a
pre-registration fixed before the run it binds. It was true of that moment and
stays true of it. **Nothing re-verifies a frozen record**, and it carries no
maintenance burden at all beyond existing.

A frozen record is corrected only when it was already wrong when it was written.
A claim that was accurate and has since been overtaken is history, and history is
left standing.

### Living — the record claims the present

A synthesis, a conclusion, an index of what is currently known. It asserts
something about now, so it is wrong the moment the world moves and nobody notices.
**A living record carries a permanent re-verification burden** and is amended in
place, with the date, for as long as it exists.

### Every record declares its regime

The regime is written in the record's own frontmatter, not inferred by a reader
from the directory it sits in. Kind and regime agree today in most bases, and
where they agree the declaration looks redundant — but it is what a base checks
rather than assumes, and the two come apart in a case every base eventually meets:
**a living record whose evidence has become permanently unavailable, which can no
longer be advanced and is retired to frozen in place rather than moved or
deleted.** Moving it would cost exactly what this model exists to avoid.

### The test a new layer has to pass

A base may hold layers between its raw input and its synthesis — extracted claims,
connections between them, working notes. **Each candidate layer is tested by which
regime its records carry**, and the test is answerable rather than a matter of
taste:

- An extracted claim with its provenance **describes a moment**. It belongs in the
  frozen input layer, wherever that layer is divided.
- A connection asserted between claims **claims the present**. It belongs in the
  living layer and inherits its re-verification burden.

**A candidate layer whose records cannot be sorted by that test is not a layer.**
It is a mix of two that already exist, and creating it buys a directory and a
migration in exchange for nothing.

## Kind and tracking are independent axes

**Whether a record is committed is decided by its provenance, not by its regime.**
The two axes are routinely confused, because in the simplest base the frozen layer
happens to be the private one. They are not the same question, and a base that
treats them as one cannot hold pre-registered material at all.

| Kind | Regime | Committed | Why |
| --- | --- | --- | --- |
| Raw input | frozen | **no** | Third-party and often copyrighted. It is the input, not the product. |
| Pre-registered material | frozen | **yes** | A pre-registration is worthless unless it can be shown to predate the run it binds, and only version-control history can show that. |
| Synthesis | living | **yes** | The repository's own cited work product, and the thing a reviewer reads. |

**The private layer is gitignored by an anchored rule**, so it cannot match a
directory of the same name elsewhere in the repository, and raw material is put
there *before* it is worked with. Anything that reaches a commit is removable only
by rewriting history.

**A synthesis cites a private source by name and does not paste it in.** Short
quoted excerpts are fine; a whole third-party document is not.

## Declaring the layers

**A base declares its layers in `base.json`, at the base's root.** It maps each
layer's directory to the kind it holds, the regimes that kind admits, and whether
it is committed. The directory names are the base's own — a repository adopting
a base keeps the names it already uses, and the file records which is which.

```json
{
  "layers": {
    "sources":  {"kind": "source",           "regimes": ["frozen"],           "tracked": false},
    "eval":     {"kind": "pre-registration", "regimes": ["frozen"],           "tracked": true},
    "findings": {"kind": "finding",          "regimes": ["living", "frozen"], "tracked": true}
  }
}
```

**A base without the file is refused, not guessed at.** The file is the only
statement of which directory is which, so a check that inferred it would be
deriving location again — the thing *The rule* exists to avoid. It is JSON
rather than YAML because the tooling that reads it runs with nothing installed.

**A record is a Markdown file at the top level of a tracked layer.** Files in
subdirectories are material, not records, and a layer's `README.md` and
`TEMPLATE.md` are orientation. An untracked layer holds no records a check can
read, so nothing is required of it beyond its ignore rule.

**A tracked layer must hold a committed file**, records or not. Git commits no
empty directory, so a tracked layer with nothing in it is absent on every clone,
and a check refuses the base there that passes in the tree where it was made. A
layer `README.md` is the file that meets it while the layer has no records yet:
it is orientation, so it adds nothing a check reads as a record.

**Where a layer's material cannot carry frontmatter, a manifest record describes
it.** Pre-registered material is the usual case: an eval set is JSON, and a
fixture a measurement ran against cannot be edited without changing what was
measured. The manifest is a new Markdown record in the same layer, carrying
frontmatter and a `covers` list naming the files it describes. **The files
themselves are never edited** — adding frontmatter to a frozen file after its run
is the one change a pre-registration cannot survive.

## Frontmatter

Every record in a tracked layer carries frontmatter. The keys below are the
contract; a base may add its own, and a generated index reads only these.

**A record is UTF-8.** One that does not decode has no frontmatter anyone can
read, so it is refused by name rather than guessed at: the validator reports
`record-not-utf8`, and the index refuses to regenerate until it is re-saved.

```yaml
---
title: Key a record's location to what it is, never to what state it is in
kind: finding              # which layer this belongs to; must match its directory
regime: living             # frozen | living
status: supported          # exploring | supported | promoted
confidence: directional    # directional | evidenced | strong
updated: 2026-09-17        # the last amendment; moves only when the claim changes
authority: []              # what a living record is re-verified against
sources: []                # names in the private layer, public URLs, or <repo>@<sha>
informs: []                # what this record shapes — guidance, projects, decisions
covers: []                 # a manifest record only: the files it describes
---
```

`title`, `kind`, `regime` and `updated` are required on every record. **A living
record also requires `status`, `confidence` and a non-empty `authority`**, because
those are what an audit reads. A frozen record may carry them and is not required
to.

`kind` — which layer the record belongs to. **It must agree with the directory the
record sits in**, and that agreement is validated rather than derived in either
direction. A record whose `kind` and directory disagree is an error, not a cue to
move the file.

`regime` — `frozen` or `living`, per the test above. A base checks that a record's
regime is one its kind admits; where a kind admits both, the record's own
declaration is what decides.

`status` — how far the thinking has got, never where the file lives:

- **exploring** — an open question, framed, not yet concluded.
- **supported** — concluded and backed by evidence, not yet promoted.
- **promoted** — its conclusion has graduated into the repository's guidance.

`confidence` — how much weight the conclusion can bear. **This is the load-bearing
honesty of a research base**, and the one field that must never be softened to make
a record look better:

- **directional** — the direction is supported; specific figures are not verified.
- **evidenced** — backed by concrete, checkable evidence: a cited source, or a run
  that can be reproduced.
- **strong** — multiple independent lines, or first-hand replication.

**Never launder a directional claim into an evidenced one by dropping the caveat.**
A record that overstates its confidence is worse than an open question, because it
gets promoted into guidance and then silently steers everything written after it.

`updated` — moves when the claim changes. **A mechanical repair — a link, a
citation, a rename elsewhere — does not move it**, because a date that moves for
clerical reasons stops meaning anything about the claim.

`covers` — present only on a manifest record, per *Declaring the layers*. Each
entry is a path relative to the record, and it must exist inside the base. **An
empty `covers` is refused**: a manifest describing nothing is not a record of
anything.

## Citations, and which direction they are pinned in

The two regimes cite differently, and the difference is not stylistic.

**A frozen record pins its citations to a commit.** It described a moment, so the
material it cites is named as it stood at that moment — `<repo>@<sha>` for
first-hand measurement, a version or an access date for anything external. A pinned
citation cannot rot, because what it names cannot change.

**A living record names the authority it is re-verified against.** That is what
`authority` carries: the shipped contract, the code, or the external source whose
present state the record must agree with. **A living record with no authority
cannot be audited**, and is a claim nobody can check rather than a conclusion.

**A first-hand measured claim's authority is its instrument.** The entry names it
by `path:symbol`, followed by the inputs it ran on. Re-verifying the claim means
re-running the instrument over those inputs. A private input is named in
`sources`, never in `authority`, because `authority` is what an audit is handed
to read and a private layer is not committed.

**Citations name things, never line ranges.** A line number is invalidated by an
edit anywhere above it, silently.

**A `path:Name` locator names one thing inside the path.** After a document,
`Name` is the full text of one heading, at any level, inline code included; a
line inside a fenced block is never a heading. After code, `Name` is a symbol the
file defines. A locator that matches nothing does not resolve. A heading's
passage runs to the next heading of the same or a higher level, so it includes
its subsections.

**A record does not link to the work item that commissioned it.** A work item moves
when it closes, and that link is exactly the liability this model is built to
avoid. Name it by id; let the work item resolve the relationship from its side,
where the reference is one the mover already repairs.

## What is derived, and what is not

| Thing | Derived? |
| --- | --- |
| The index of records, with their status and confidence | **yes** — regenerated from frontmatter, never hand-edited |
| A record's directory | **no** — keyed to kind, and changed only by a deliberate re-classification |
| A record's regime, status, confidence | **no** — declared in frontmatter |

**Generated regions are delimited and never hand-edited.** Narrative outside the
markers is hand-written and never touched by the generator. Regenerating is how a
stale index is fixed; editing one by hand reintroduces the drift the rule exists to
prevent.

## Audit means re-verification, not reconciliation

**A research base borrows half of a task board's audit, and the other half would
mislead it.**

A board's audit, `task-board-triage`, does both. Its *Pass 1 — mechanical* and
*Pass 3 — index* reconcile derived state: they check that each task's folder and
the index still agree with its frontmatter, refile what has drifted and
regenerate the index. Its *Pass 2 — substantive* re-verifies: it reads every
non-completed task, checks its factual claims against source and corrects them in
place with the date.

**Two things do not transfer.** A base whose location is keyed to kind has almost
no derived state to reconcile, so the reconciling passes would find nothing and
report health they had not established. And a base's audit does not correct what
it finds: it reports what does not hold instead of correcting it in place.

**A base's audit re-verifies living claims against their authorities.** It reads
what each living record says is currently true, checks it against the authority the
record names, and reports contradiction, drift and any record whose authority does
not exist or does not resolve. The nearer relative is a documentation audit, not a
board triage.

Two things follow, and both are easy to get wrong:

- **Frozen records are outside the audit's subject entirely.** Re-verifying one is
  a category error: it never claimed the present.
- **An audit reports; it does not refile.** There is nothing to refile. What it
  produces is a list of claims that do not hold, which a person decides about.

## What this model deliberately does not carry

**No trim role.** The intuition that a base must be pruned as it grows treats
accumulation as the cost. In the corpus this model was measured against the cost is
movement, and **trimming a citation-dense corpus creates movement** — every removal
breaks the citations that named what was removed. Frozen records that nothing
re-verifies are cheap to keep and expensive to touch.

**That is a conclusion about this corpus, not a prohibition.** A base that measures
a genuine accumulation cost in its own repository has grounds this one does not.
What is ruled out is carving the role out by analogy, on the assumption that
because a board archives, a base must prune.

**No status-derived folders**, per *The rule*. This is worth restating as a
non-feature, because it is the first thing anyone adapting a board will add back.

## Adopting a base in a repository

1. **One base per repository**, and it is the directory the repository already
   keeps its research in. **Do not build the new structure beside the old one** —
   two bases in one repository means the old one still holds the real material and
   the new one only demonstrates the model.
2. **Divide by kind**: a private input layer, a committed synthesis layer, and any
   further layer that passes the test above. Anchor the private layer's ignore rule
   so it cannot match a directory elsewhere in the tree. **Declare every layer in
   `base.json`**, per *Declaring the layers*.
3. **Declare the frontmatter on every tracked record**, including records that
   predate the base — an undeclared record is invisible to the index and to the
   audit both.
4. **Generate the index and commit the generator**, so the index can be rebuilt by
   anyone rather than maintained by whoever wrote it.
5. **Migrate the existing material with the base's own tooling, not by hand.** A
   model that cannot migrate the one base that already exists has not been shown to
   work, and doing it by hand demonstrates nothing about whether the tooling is
   usable.
