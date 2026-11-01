---
name: orchestrate-implementation
description: 'Plan a coherent set of scoped, ungated board tasks: select them, group them into streams that do not interfere, and file one plan document with its own execution log. Then dispatch the streams, launching independent ones at once through subagents, with each task executed under focused-implementation. Use when asked to "plan a sprint", "orchestrate these tasks", "run these in parallel", "what should we work on next", or to schedule several board tasks together.'
---

# Orchestrate a set of tasks

Plan a coherent set of board tasks: select them, organize them into streams that do
not fight each other, and file one plan document. Then dispatch the streams and keep
the record until the set closes.

**This is the planning skill.** Selection, sequencing, the plan document and the
closes are its job. Individual tasks are executed under the rules in
`focused-implementation`, inline or in a subagent; this skill decides which, and
never relaxes those rules.

Read [references/board-model.md](references/board-model.md).

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
was left out. Get agreement before starting. Shape that presentation per
[references/report-form.md](references/report-form.md) — it is the longest report
this skill emits and the one the user decides from.

## The plan document

Raise it on the board as an ordinary task (`to-task`), with `category` naming it a
plan. It carries:

- The set, grouped into streams, with the selection rule that produced it.
- Explicitly excluded tasks and why — this is what stops the same debate next cycle.
- Per-stream branch strategy, including which streams share a branch because they
  touch the same files.
- Each stream's write set **and its read set**: the tools, generators and suites
  it runs as well as the files it edits. Disjoint files are not disjoint inputs —
  a close that runs a generator another stream is still editing records output
  from code nothing has committed yet.
- Dependencies ordered at the step that needs it, not at the whole task. When
  only a task's final verification uses another task's result, its
  implementation can run beside that task.
- The verification budget for the set as a whole.
- An execution log, appended as streams land.

The plan is `in-progress` while the set is running and `done` when it closes, keeping
its execution log intact.

## Running it

1. **Readiness check.** Re-verify every task's premises against source before the
   first line of code. Tasks scoped weeks ago cite line numbers that have moved.
   Correct what has drifted, and report it — a premise that dissolved may remove a
   task from the set entirely.
2. **Sequence by interference, not by size.** Streams whose write sets are disjoint,
   and whose write sets miss every other stream's read set, can run in parallel.
   Streams that touch the same files run in series on one branch, in a stated order.
3. **Execute each task under `focused-implementation`**, dispatched per *Dispatch*
   below. Its entry gate, verification budget, and anti-fix rules apply per task;
   this skill does not relax them.
4. **Keep each task's own record current.** A task's status, execution log, and any
   follow-ons live in the task, not only in the plan. The plan indexes; it does not
   replace.
5. **Let the set shrink.** A task whose premise was overturned mid-run leaves the
   set — record why in the plan rather than forcing it through.
6. **Close out.** Update every task, write the plan's execution log, and set the
   plan `done`. **Each close moves a file into another folder**, which breaks every
   relative link into and out of it; repair them per *Repairing the links a move
   breaks* in [references/board-model.md](references/board-model.md). Then run:

   ```text
   scripts/validate_board.py --board <board>
   scripts/generate_index.py --board <board>
   ```

## Dispatch

Where each stream runs. The main session plans, verifies and closes; a subagent only
implements.

**The default.** When two or more independent streams are ready, launch them all at
once, each in its own subagent. A delegated stream run alone saves context and
nothing else, because the main session waits on it. So a lone ready stream runs
inline, unless the plan records that the main session's context is the reason to
delegate it. Where the platform offers no subagent primitive, run the streams
serially in the main session, in the plan's order. That is a slower plan, not a
different one.

**Before launching**, set each task `in-progress` on the board yourself. The stream
never touches the board.

**The brief.** Each brief:

- names the task file and the authoritative files for its rules, and tells the
  stream to prefer them wherever the brief disagrees. A brief's error otherwise
  reaches the implementer intact;
- names the concurrent streams and their files, so a foreign change in the working
  tree reads as expected rather than as a hazard;
- states the contract below.

**What a delegated stream may do.** It touches only its own task's code and tests.
It runs `focused-implementation` up to, and not including, *Closing out*. It does
not edit the board, task files or the agent instruction files, and it does not
commit, push or publish.

**What it returns:**

- a summary of its diff;
- its suite's result, naming any files the run excluded because another stream had
  them in flight;
- every premise of the brief it found false.

**The main session verifies every return** before trusting it. It re-runs the owning
suite, reads the diff against the tree, then closes the task, writes the plan's log
and commits, one close at a time. A return arrives confident whether or not it is
right.

**A shared working tree is the default.** Give a stream its own worktree only when
its write set meets another stream's read set, or meets a tool the closes run: the
board generator, a suite runner, a lint config. Otherwise make the closes wait for
that stream. While streams are in flight, every verification run in the shared tree
states which in-flight files it excluded.

## Guardrails

- Do not schedule a `draft` or gated task.
- Do not schedule a task whose blocker is outside the set, and do not run a
  blocked task in parallel with its own blocker.
- Do not start without presenting the set and its exclusions for agreement.
- Do not run interfering streams in parallel. Overlapping file surgery done twice
  gets reconciled badly.
- Do not launch ready, independent streams one at a time and wait on each. That
  is serial execution with a wait added.
- Do not let a delegated stream close its task, edit the board, commit, push or
  publish. Closes stay in the main session, one at a time.
- Do not trust a stream's return until the main session has re-run its suite and
  read its diff.
- Do not run a close, or any shared tool, while a stream is still modifying that
  tool.
- Do not let the plan document become the only record. Each task closes itself.
- Do not mark the set complete while any task in it is short of its own acceptance
  criterion. Report the set as partially complete and name what is outstanding.
- Do not push to a remote unless the user explicitly asks.
- Do not carry a task forward into the next set by default. Re-run selection.
  A queue recorded per [references/session-queue.md](references/session-queue.md)
  supplies an ordering, never a pre-approved set — an item reaching the front of
  it is a claim about priority and never about eligibility, so selection still
  runs. This guardrail is unchanged by that file.

## Resources

- The state model and folder mapping:
  [references/board-model.md](references/board-model.md)
- Field-by-field contract: [references/task.schema.yaml](references/task.schema.yaml)
- Plan document template: [assets/task.md](assets/task.md)
- Emphasis, headings, and what must survive a shortened report:
  [references/report-form.md](references/report-form.md)
- Ordering work across sessions, and where a boundary belongs:
  [references/session-queue.md](references/session-queue.md)
