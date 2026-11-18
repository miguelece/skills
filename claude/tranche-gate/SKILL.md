---
name: tranche-gate
description: 'Gate a closed tranche, or any batch of agent commits, before the owner''s review: scan base to tip against a closed checklist of twelve defects (churn, reinvented helpers, duplication, dead code, surplus or weakened tests, over-building, leftovers and more), remediate only behaviour-preserving cleanup of what the batch introduced in revertable local commits, and append one report to the tranche record. Use when supervise-implementation closes a tranche, or when asked to "run the tranche gate", "gate this batch", "clean up what the agents left", or to analyse and remediate a range of agent-written commits before packaging.'
---

# Gate a tranche

Analyse a closed tranche of agent work, or any batch of commits, against a
closed checklist; commit only behaviour-preserving cleanup of what the batch
introduced; and write one report the owner reviews instead of the whole diff.

**A tranche is too large to review well in one pass.** A reviewer's recall
falls as a diff grows, and a reviewer asked to find problems always finds
some. So the gate is bounded by what it looks for and how it reads: a closed
list, detectors over the whole range, the model over one task at a time, and
every finding verified against the code before anything acts on it.

Read [references/board-model.md](references/board-model.md).

## Inputs

- **From a supervised tranche**: its base and tip commits, the tranche
  record, each task's `## Acceptance criteria` section and every integrator
  verdict under the record's integrator verdicts. Each `merged <sha>` in a
  verdict attributes that merge to its task.
- **After any other batch**: base, tip and, optionally, the task ids the
  batch worked.
  - **On a repository with a board**, file a minimal plan task as the
    record, from [assets/task.md](assets/task.md): `category` naming it a
    tranche record, `in-progress`, with a *Tranche* section holding the
    base, the tip and the task ids. It is committed, before any remediation,
    and the report goes into it like any record.
  - **With no board**, the report goes to `.tranche-gate/report.md`, and its
    first line says it is uncommitted.
- **Without integrator verdicts**, run
  `scripts/check_test_changes.py --repo <path> --base <base> --tip <tip>`
  yourself for D6.
- **Without criteria**, D5 and D7 are marked "not checked: no criteria" for
  each task that has none. They are never judged against a guessed standard.

**The size limit the gate declares is 4,000 changed lines**, as
`scripts/scan_tranche.py --size` counts them over base..tip, without
generated regions. It is a starting value, unmeasured: no study gives
a size at which an agent reviewer fails. A supervisor closes its tranche on
it. Run alone over a larger batch, say so in the report and read it all the
same; the chunks stay small.

**Effort is `high`, not `max`**, set by the caller. At `max` a reviewer
overthinks and makes more choices on its own.

## The run directory

`.tranche-gate/` at the repository root, with a `.gitignore` holding `*`, so
it ignores itself. It holds the scan, the chunk notes and the patches for
surplus verification. Never put run files under the board folder: the board
validator reads every `.md` there. `git clean -x` deletes it.

## Steps

1. **Scan the whole range first.** The detectors cover the whole range, base
   to tip, so the tranche-wide defects need no model:

   ```text
   scripts/scan_tranche.py --repo <path> --base <base> --tip <tip> [--record <record>]
   ```

   Save its JSON to `.tranche-gate/scan.json`. Run the test check over the
   same range when there are no verdicts (see *Inputs*), and the
   repository's own linters and contract tests for D11.
2. **Read one task's diff per chunk**, taking each task's commits from the
   scan's units. Above about 400 changed lines, split the chunk by file.
   In each chunk, judge only two things: the detectors' candidates that fall
   in it, and D2, D7, D8 and D10, which no detector settles. Judge against
   [references/checklist.md](references/checklist.md) and nothing else. The
   list is closed: style and correctness bugs are out, and a defect outside
   it goes in the report as a proposal to add to the list, never as a
   remediation.
3. **Write each finding with its `file:line` and its checklist item**, and
   the task it came from.
4. **Verify every finding against the code before anything acts on it**: re-read
   the cited lines, or run the detector again on them. A finding is
   verified against the code, never by scoring your own confidence in it. One
   that does not hold is dropped and counted.
5. **Classify and remediate** under
   [references/remediation.md](references/remediation.md): commit the
   structural cleanup, one kind per commit, after the tip; re-verify each
   commit and revert it on failure. Prepare each surplus-verification removal
   as an unapplied patch. Everything else is reported.
6. **Write the report** from [references/report.md](references/report.md), as
   a `## Gate report` section appended to the tranche record. It carries at
   most 32 findings, in the template's order, and counts the rest. Count
   findings per changed line as well as raw, so tranches of different sizes
   compare.
7. **Close out.** Run `scripts/validate_board.py --board <board>` and
   `scripts/generate_index.py --board <board>`, then commit the report.
   Leave the record's status and gate as they are: the owner's review closes
   it. Tell the owner where the report is, how many commits the gate added
   and how many findings wait on them.

## Guardrails

- Do not push, publish, or write into a publish target. Every commit stays
  local, after the tip, for the owner's review.
- Do not report a finding without its `file:line` and checklist item, and do
  not act on one that was not verified against the code.
- Do not commit anything but behaviour-preserving cleanup of code the batch
  introduced. A published skill's text, a bundled script's flags or output, a
  test whose subject remains, and any behaviour change are reported.
- Do not fix a failing remediation commit forward. Revert it and report it.
- Do not apply a surplus-verification removal. Prepare it and report it.
- Do not hunt for style or correctness bugs, and do not grow the checklist
  during a run.
- Do not judge D5 or D7 without criteria.
- Do not change the record's status or gate.

## Resources

- The checklist, with each item's detector, class and known false positives:
  [references/checklist.md](references/checklist.md)
- What is committed and what is reported:
  [references/remediation.md](references/remediation.md)
- The report template: [references/report.md](references/report.md)
- The state model, and the field contract:
  [references/board-model.md](references/board-model.md),
  [references/task.schema.yaml](references/task.schema.yaml)
- Plan template, for a record the gate files: [assets/task.md](assets/task.md)
- Scripts: `scripts/scan_tranche.py`, `scripts/check_test_changes.py`,
  `scripts/validate_board.py`, `scripts/generate_index.py`
