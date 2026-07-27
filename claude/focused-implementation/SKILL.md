---
name: focused-implementation
description: Implement one scoped task from the board end to end — re-verify its premises, set a verification budget, work in tested vertical slices, prove measurement probes actually detect the defect, and close it out with an execution log. Use when asked to "implement this task", "work the task", "do this one task", or to take a single board task to done.
---

# Implement one task

Take a single scoped task from the board to done, with evidence, and leave the
board honest about what happened.

Read [references/board-model.md](references/board-model.md) for the status contract.

## Entry gate

Do not start until all of these hold. If any fails, stop and say which.

- The task is `status: scoped`. A `draft` task has unresolved questions — run
  `task-interview` first. Implementing a draft means guessing the answers.
- Its `gate` is `none`. A gated task is waiting on someone; implementing it anyway
  produces work that cannot be accepted.
- Every `blocked-by` entry has reached `done`. Building on a blocker that has not
  landed means building against an interface that can still change.
- If the task is `part-of` a spec, read the spec first — it carries the vision and
  the decisions this slice must not contradict. Implement the ticket, not the whole
  spec; the spec's other slices are other tickets.
- Its premises still hold. Re-verify the paths, line numbers, and values it cites
  before writing anything — task docs rot, and line numbers cited in a spec are the
  first thing to go stale.

Set `status: in-progress` and update `updated` before starting.

## Procedure

1. **Re-locate everything the spec cites.** Do not trust line numbers. Find the code
   by name and confirm it still does what the task says it does. If a premise is
   wrong, stop and correct the task before continuing — the spec is now the thing
   under repair, not the code.
2. **Set a verification budget before writing code.** Decide now what evidence will
   prove this worked, and how many distinct assertions it takes. Write them down.
   Deciding afterwards means deciding once the answer is already known.
3. **Work in vertical slices.** One end-to-end behavior at a time, each independently
   verifiable. A slice that cannot be verified on its own is too big.
4. **Test first where a test can fail.** Write the failing test, watch it fail for
   the expected reason, then make it pass. A test that has never failed has proved
   nothing.
5. **Anti-fix validation for anything a test cannot catch.** When the evidence is a
   measurement rather than an assertion — a request count, a render count, a load
   count, a timing — prove the probe detects the bug: revert or stash the fix, run
   the probe, confirm it reports the defect, then restore the fix. An instrument that
   has only ever seen the healthy state is not an instrument.
6. **Measure against a realistic build.** Development modes lie: they double-invoke,
   skip caching, and disable optimizations. Anything you measure in counts must be
   measured against a production-equivalent build.
7. **Verify against the budget from step 2.** Every assertion, run, with the result
   recorded. Report shortfalls as shortfalls.
8. **Handle what implementation turns up.** Work discovered mid-task that the task
   should not absorb gets split with `to-follow-on`, not quietly added.

## Closing out

1. Write the `## Execution log`: what shipped, on which branch and commits, and how
   it was verified. Record defects that verification caught which no test would have
   — that is the part of the log worth reading a year later.
2. Write the one-line `outcome:` in frontmatter — what changed and how it was
   confirmed. This is what the archive index shows, so write it for someone
   scanning a hundred finished tasks who will not open the file. "Done" is not an
   outcome and is rejected.
3. Set `status: done`, `updated`, and — if the work is finished and correct but a
   better-but-costlier tier was evaluated and declined — `revisit: true` plus an
   `## Upgrade paths` section giving each declined option and the condition that
   would justify revisiting it.
4. **Fold-back is automatic — just regenerate.** If the task is `part-of` a spec,
   its one-line `outcome` rolls up into the spec's `## Slices` block when you run
   `generate_index.py` (step 6). Do not hand-copy it. Do **not** flip the spec's own
   status; a spec's status is its own (its other slices or residual work may remain).
5. If the remaining step is gated on a human, it is **not done**: keep
   `status: in-progress`, set the gate, and put the exact outstanding action under
   `Owner`.
6. Verify:

   ```text
   scripts/validate_board.py --board <board>
   scripts/generate_index.py --board <board>
   ```

## Guardrails

- Do not implement a `draft` task, one with a gate, or one whose blockers are still
  open.
- Do not write implementation code before the failing test, where a test applies.
- Do not claim a measurement-based fix works without anti-fix validation.
- Do not silently widen scope. Split it or state it.
- Do not mark `done` while any acceptance criterion is unmet — including one that
  can only be met by a human. Gate it instead.
- Do not push to a remote unless the user explicitly asks. Committing locally is
  ordinary; publishing is theirs to authorize.
- Do not write an execution log that only lists commits. It must say how the work was
  verified, or it is a changelog.
- Do not write an `outcome` that restates the title. It says what changed and how it
  was confirmed, or it is not worth generating an index from.
- Do not flip a spec to `done` just because its tickets are done. A spec's status is
  its own — check its residual work and any deferred slices before closing it.

## Resources

- The state model and folder mapping:
  [references/board-model.md](references/board-model.md)
- Field-by-field contract: [references/task.schema.yaml](references/task.schema.yaml)
