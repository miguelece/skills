---
name: orchestrate-implementation
description: Select a coherent set of scoped, ungated board tasks, group them into streams that do not interfere, and run them to completion behind one plan document with its own execution log. Use when asked to "plan a sprint", "orchestrate these tasks", "run these in parallel", "what should we work on next", or to schedule several board tasks together.
---

# Orchestrate a set of tasks

Select a coherent set of board tasks, organize them into streams that do not fight
each other, and run them to completion behind one plan document.

Read [references/board-model.md](references/board-model.md). Individual tasks are
executed under the rules in `focused-implementation`; this skill owns selection,
sequencing, and the plan record.

## Selection

Eligible tasks are `status: scoped` with `gate: none`. Nothing else. A gated or
draft task cannot be scheduled — scheduling it just moves the blockage.

A task with open `blocked-by` entries is eligible **only if its blockers are in the
same set and sequenced ahead of it**. That is a legitimate way to run a dependency
chain in one pass; pulling in the downstream task without its blocker is not.

**Schedule tickets, not specs.** A `kind: spec` is the vision a set of tickets
realizes, not a unit of implementable work — you schedule its tickets (the tasks
`part-of` it). A spec is a natural boundary for one coherent set: its tickets share
context and often interfere, which is exactly the strongest reason to batch. Leave
the spec's own status alone; closing it is a deliberate call after its slices land,
not an automatic consequence.

Choose the **smallest set that is genuinely coherent**, by this order of preference:

1. **Tasks that interfere.** If three tasks all rewrite the same layer, doing them
   separately means doing the overlapping surgery three times and reconciling it
   twice. Group them and do it once. This is the strongest reason to batch.
2. **Tasks that share a verification setup.** One expensive harness, several tasks.
3. **Tasks downstream of one another**, in dependency order.

Then apply the rules that keep a set honest:

- **Do not pad.** A task added only to make the set look substantial is filler, and
  it dilutes the review attention the real work needs.
- **Do not force in a gated task** because its gate "will probably clear". If it has
  not cleared, it is not in the set.
- **Order by how much readiness can close itself.** Engineering-led work first;
  owner-gated work last, so its gate has the longest possible time to clear.

Present the proposed set, the streams, and the excluded tasks with the reason each
was left out. Get agreement before starting.

## The plan document

Raise it on the board as an ordinary task (`to-task`), with `category` naming it a
plan. It carries:

- The set, grouped into streams, with the selection rule that produced it.
- Explicitly excluded tasks and why — this is what stops the same debate next cycle.
- Per-stream branch strategy, including which streams share a branch because they
  touch the same files.
- The verification budget for the set as a whole.
- An execution log, appended as streams land.

The plan is `in-progress` while the set is running and `done` when it closes, keeping
its execution log intact.

## Running it

1. **Readiness check.** Re-verify every task's premises against source before the
   first line of code. Tasks scoped weeks ago cite line numbers that have moved.
   Correct what has drifted, and report it — a premise that dissolved may remove a
   task from the set entirely.
2. **Sequence by interference, not by size.** Streams that touch disjoint files can
   run in parallel. Streams that touch the same files run in series on one branch, in
   a stated order.
3. **Execute each task under `focused-implementation`.** Its entry gate, verification
   budget, and anti-fix rules apply per task; this skill does not relax them.
4. **Keep each task's own record current.** A task's status, execution log, and any
   follow-ons live in the task, not only in the plan. The plan indexes; it does not
   replace.
5. **Let the set shrink.** A task whose premise was overturned mid-run leaves the
   set — record why in the plan rather than forcing it through.
6. **Close out.** Update every task, write the plan's execution log, set the plan
   `done`, and run:

   ```text
   scripts/validate_board.py --board <board>
   scripts/generate_index.py --board <board>
   ```

## Guardrails

- Do not schedule a `draft` or gated task.
- Do not schedule a task whose blocker is outside the set, and do not run a
  blocked task in parallel with its own blocker.
- Do not start without presenting the set and its exclusions for agreement.
- Do not run interfering streams in parallel. Overlapping file surgery done twice
  gets reconciled badly.
- Do not let the plan document become the only record. Each task closes itself.
- Do not mark the set complete while any task in it is short of its own acceptance
  criterion. Report the set as partially complete and name what is outstanding.
- Do not push to a remote unless the user explicitly asks.
- Do not carry a task forward into the next set by default. Re-run selection.

## Resources

- The state model and folder mapping:
  [references/board-model.md](references/board-model.md)
- Field-by-field contract: [references/task.schema.yaml](references/task.schema.yaml)
- Plan document template: [assets/task.md](assets/task.md)
