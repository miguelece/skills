---
name: focused-implementation
description: Implement one scoped task from the board end to end — re-verify its premises, set a verification budget, work in tested vertical slices, prove measurement probes actually detect the defect, and close it out with an execution log. Use when asked to "implement this task", "work the task", "do this one task", or to take a single board task to done.
---

# Implement one task

Take a single scoped task from the board to done, with evidence, and leave the
board honest about what happened.

Read [references/board-model.md](references/board-model.md) for the status
contract.

## Entry gate

Do not start until all of these hold. If any fails, stop and say which.

- The task is `status: scoped`. A `draft` task has unresolved questions — run
  `task-interview` first. Implementing a draft means guessing the answers.
- Its `gate` is `none`. A gated task is waiting on someone; implementing it
  anyway produces work that cannot be accepted.
- Every `blocked-by` entry has reached `done`. Building on a blocker that has
  not landed means building against an interface that can still change.
- If the task is `part-of` a spec, read the spec first — it carries the vision
  and the decisions this slice must not contradict. Implement the ticket, not
  the whole spec; the spec's other slices are other tickets.
- Its premises still hold. Re-verify the paths, line numbers, and values it
  cites before writing anything — task docs rot, and line numbers cited in a
  spec are the first thing to go stale.

Set `status: in-progress` and update `updated` before starting.

## Procedure

1. **Re-locate everything the spec cites.** Do not trust line numbers. Find the
   code by name and confirm it still does what the task says it does. If a
   premise is wrong, stop and correct the task before continuing — the spec is
   now the thing under repair, not the code.
2. **Set a verification budget before writing code.** Decide now what evidence
   will prove this worked, and how many distinct assertions it takes. Write them
   down. Deciding afterwards means deciding once the answer is already known.
   Build the evidence from the task's own tests and the instruments the
   repository already has. A test written for this task, and a helper used only
   by this task's tests in its own test files, are the task's own. Anything
   meant to outlive the task — a shared fixture library, a test runner, a
   harness, a new measurement script, a validator or lint rule — is new
   verification tooling, and is out of this task's scope (step 8). Before a
   helper, a fixture step or a test is added, load the `working-conventions`
   skill and apply its reference for that moment.
3. **Work in vertical slices.** One end-to-end behavior at a time, each
   independently verifiable. A slice that cannot be verified on its own is too
   big.
4. **Test first where a test can fail.** Write the failing test, watch it fail
   for the expected reason, then make it pass. A test that has never failed has
   proved nothing.
5. **Anti-fix validation for anything a test cannot catch.** When the evidence
   is a measurement rather than an assertion — a request count, a render count,
   a load count, a timing — prove the probe detects the bug: revert or stash the
   fix, run the probe, confirm it reports the defect, then restore the fix. An
   instrument that has only ever seen the healthy state is not an instrument. If
   proving the probe needs an instrument the repository does not have, that
   instrument is new verification tooling (step 8).
6. **Measure against a realistic build.** Development modes lie: they
   double-invoke, skip caching, and disable optimizations. Anything you measure
   in counts must be measured against a production-equivalent build. Use a build
   the repository already produces; building one is new verification tooling
   (step 8).
7. **Verify against the budget from step 2.** Every assertion, run, with the
   result recorded. When they pass, stop: no further review rounds, reviewer
   subagents, or re-runs of a green suite. Mention anything more you think would
   help in the execution log instead of doing it. Report shortfalls as
   shortfalls, shaped per [references/report-form.md](references/report-form.md)
   — a shortfall is a negation, and that file's first guardrail is the one that
   keeps it from being trimmed away.
8. **Handle what implementation turns up.** Work discovered mid-task that the
   task should not absorb gets split with `to-follow-on`, not quietly added. New
   verification tooling is always such work. File it with its reason, at the
   priority its value warrants — tooling that makes code easier to change is not
   low priority for being tooling — and finish with the checks step 2 fixed. If
   those checks cannot run without it, file it as this task's blocker and stop.

## Closing out

1. Write the `## Execution log`: what shipped, on which branch and commits, and
   how it was verified. Record defects that verification caught which no test
   would have — that is the part of the log worth reading a year later.
2. **Log each precedent applied.** For every entry of the board's precedent
   register that the task applied, named in its *Plan* or its report, append
   the use to the entry's *Applied*, with the date and this task's record. A
   transferable entry exists twice, so append it to the central judgment
   register's copy too, in the same pass. The rule is in *The precedent
   register* in [references/board-model.md](references/board-model.md); the
   close is the one point every task passes, so it is applied here.
3. Write the one-line `outcome:` in frontmatter — what changed and how it was
   confirmed. This is what the archive index shows, so write it for someone
   scanning a hundred finished tasks who will not open the file. "Done" is not
   an outcome and is rejected.
4. Set `status: done`, `updated`, and — if the work is finished and correct but
   a better-but-costlier tier was evaluated and declined — `revisit: true` plus
   an `## Upgrade paths` section giving each declined option and the condition
   that would justify revisiting it. **Setting `status: done` moves the file**
   into `completed/` or `revisit/`, which breaks every relative link into and
   out of it; repair them per *Repairing the links a move breaks* in
   [references/board-model.md](references/board-model.md).
5. **Fold-back is automatic — just regenerate.** If the task is `part-of` a
   spec, its one-line `outcome` rolls up into the spec's `## Slices` block when
   you run `generate_index.py` (step 7). Do not hand-copy it. Do **not** flip
   the spec's own status; a spec's status is its own (its other slices or
   residual work may remain).
6. If the remaining step is gated on a human, it is **not done**: keep
   `status: in-progress`, set the gate, and put the exact outstanding action
   under `Owner`.
7. Verify:

   ```text
   scripts/validate_board.py --board <board>
   scripts/generate_index.py --board <board>
   ```

8. **Act on the findings this close caused.** Read the validator's output,
   not only its exit code. A task it reports unblocked by this close — a
   folder mismatch naming the cleared blocker, which is the unblock
   notification in [references/board-model.md](references/board-model.md) —
   is refiled now to the folder its frontmatter derives, and its links are
   repaired per *Repairing the links a move breaks*, the scan of the whole
   repository for its id included. Fix every other error on the closed task,
   on a task it unblocked or on a follow-on the close filed, then re-run both
   scripts until they report none of these, before the close is committed.
   An error on any other task was not this close's: it stays with
   `task-board-triage`, so the close never becomes a triage pass.

## Guardrails

- Do not implement a `draft` task, one with a gate, or one whose blockers are
  still open.
- Do not write implementation code before the failing test, where a test
  applies.
- Do not claim a measurement-based fix works without anti-fix validation.
- Do not silently widen scope. Split it or state it.
- Do not build new verification tooling inside a task. File it with
  `to-follow-on`, and verify with what step 2 fixed.
- Do not mark `done` while any acceptance criterion is unmet — including one
  that can only be met by a human. Gate it instead.
- Do not push to a remote unless the user explicitly asks. Committing locally is
  ordinary; publishing is theirs to authorize.
- Do not write an execution log that only lists commits. It must say how the
  work was verified, or it is a changelog.
- Do not write an `outcome` that restates the title. It says what changed and
  how it was confirmed, or it is not worth generating an index from.
- Do not flip a spec to `done` just because its tickets are done. A spec's
  status is its own — check its residual work and any deferred slices before
  closing it.

## Resources

- The state model and folder mapping:
  [references/board-model.md](references/board-model.md)
- Field-by-field contract:
  [references/task.schema.yaml](references/task.schema.yaml)
- Emphasis, headings, and what must survive a shortened report:
  [references/report-form.md](references/report-form.md)
