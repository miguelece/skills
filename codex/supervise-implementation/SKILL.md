---
name: supervise-implementation
description: 'Supervise a task board in gated tranches: open a tranche on the owner''s word, lease scoped tickets to up to three fresh workers, integrate one stream at a time, escalate only what the owner must decide, and hand the closed tranche to the analysis gate. Each cycle is one turn, re-read from disk. Use when asked to "supervise the board", "run a tranche", "work the queue with workers", "keep the workers going", or to run many board tasks without managing each one.'
---

# Supervise a tranche

Work a task board in tranches: lease scoped tickets to fresh workers, have
each stream verified and merged by a fresh integrator, escalate only what the
owner must decide, and hand the closed tranche to the analysis gate.

**The supervisor holds policy only**: what is leased, to whom, how large, and
what a stall or an escalation triggers. It never implements, verifies or
merges, so its context carries one cycle. Its state lives on disk, and it
trusts nothing carried in context from the cycle before.

Read [references/board-model.md](references/board-model.md).

## The cycle

**Each cycle is one turn.** A worker's or integrator's completion notice, the
owner's message or the heartbeat starts it, and it dispatches work and ends
the turn. It never works the queue itself, and never runs two cycles in one
turn.

1. **Re-read**, never from memory: first
   [references/cycle.md](references/cycle.md), then only the current sections
   of the tranche record and the lease table, the entries answered since the
   last cycle, and the board. Then reconcile every lease in flight against its
   agent's actual status, which catches a completion notice lost at a
   compaction.
2. **Collect** each finished return. Record it against its lease, save a
   worker's declared test changes under `.supervise-implementation/declared/`,
   and write its allocation-log row from
   `scripts/account_attempt.py <transcript>`.
3. **Test for stalls** (see *Progress and stalls*), writing each condition to
   the allocation log. Detection only; no action yet.
4. **Respond** to each condition: re-size, top up or escalate. Act on each
   answered entry by its id.
5. **Integrate**: if no integrator is in flight, mark the next ready
   stream's lease `integrating` and dispatch one for it. There is at most one
   integrator at a time.
6. **Lease**: fill free capacity, up to three workers, from the tranche's
   leasable items in interference order (see *Leasing*).
7. **Write back** the tranche record and the lease table, append the
   analyst's drafts, send at most one push for this cycle's new blocking
   entries, then end the turn.

When nothing is in flight and nothing can be leased, close the tranche.

**Model and effort are set on every call**, through the subagent call's model
and effort parameters. Every role runs on Opus 5.5: pass `opus`, which runs
on the session's own version when the family matches. Workers run at
`medium`; the integrator, the analyst and the gate at `high`. Record the model
each attempt actually ran on; any other model is logged for the gate's
report.

**Platform.** On Claude Code, a subagent is a fresh `Agent` call in the
background, never a fork; the heartbeat is `CronCreate`; a push is
`PushNotification`; the owner is asked through `AskUserQuestion`. Where the
platform lacks background subagents, do not run a tranche: say so and offer
`orchestrate-implementation`.

## Opening a tranche

Only on the owner's word. Then:

1. **Check the session.** It runs on Opus 5.5. When the context-occupancy
   tool is installed, read its `autoCompactThreshold`; if the window is not
   near 300k, recommend that the owner set it for this session only (a saved
   environment holding `CLAUDE_CODE_AUTO_COMPACT_WINDOW=300k`, or
   `--autocompact 300k` in a terminal). Never write a setting yourself.
2. **Check the worktree base.** Read `worktree.baseRef`. Unless it is
   `"head"`, a worker's worktree starts from the remote's default branch and
   misses everything integrated in this tranche. Recommend that the owner set
   it to `"head"` in the repository's `.claude/settings.local.json`, and until
   then lease one worker at a time, on a lease branch in the main checkout.
3. **Select** with [references/task-selection.md](references/task-selection.md)
   over the whole board, not a sample of it. Present the set and every
   exclusion with its reason, shaped per
   [references/report-form.md](references/report-form.md), and get the
   owner's agreement.
4. **File the tranche record** as a plan task from
   [assets/task.md](assets/task.md), with the added sections
   [references/run-state.md](references/run-state.md) defines. Create
   `.supervise-implementation/` at the repository root with a `.gitignore`
   holding `*`, and the lease table in it.
5. **Arm the heartbeat**: a recurring job about every 30 minutes, off the :00
   and :30 marks, that runs a cycle if none has run since the last one. It
   lives only in this session and expires after seven days; re-arm it on a
   longer tranche.
6. **Commit** the tranche record. Nothing is in flight yet.

**Joining.** A new `part-of` piece of a tranche item that is `scoped` and
`gate: none` joins the tranche, logged in the record. A lineage follow-on
(`parent`) and any tooling a worker reports for a follow-on wait for the next
tranche. A draft or gated piece becomes a routine entry.

## Leasing

Set the task `in-progress` and, before launching the worker, add a
`## Acceptance criteria` section to its task file: a short numbered list you
write from the task's *Plan*, with the check fixed for each. The worker never
sets its own bar. Then write the lease row ([references/run-state.md](references/run-state.md)):
task, attempt, grant with its justification, the start commit, the agent id.

**Admission.** Price the task's spend so far plus the next grant's estimate.
If it would pass the per-task cap, escalate instead of granting.

**Every worker runs in its own worktree**, branched from local `HEAD`, and
commits its verified work there. Launch it from
[references/worker-brief.md](references/worker-brief.md), filled from disk,
with the criteria in the brief. A new attempt always starts from a clean
worktree; a failed attempt's worktree is kept while an entry about it is open.

## Progress and stalls

- **Progress is the integrator confirming that a lease criterion moved.**
  A commit, a green suite or a worker's return counts only through that
  verdict.
- **Liveness is separate**: a return, a partial result at a call limit, a
  stall watchdog's abort. They show an attempt ended, never that it moved.
- **A stall is an attempt that ended with no criterion confirmed.** Diagnose
  it from the return and the verdict, and log the diagnosis.
- **A diagnosed stall is re-sized without asking, however many times**, when
  the cause is named, the fix is known, and the fix stays inside the task's
  criteria and scope.
- **Escalate a stall** only when the cause is unexplained (the same failure
  recurs and no new diagnosis accounts for it), when the fix leaves the task
  (it changes the criteria or scope, or touches another stream's files), or
  when the next grant would pass the per-task cap. The entry carries the
  sizing history and every diagnosis.
- **Not a stall**: an attempt that never started, or that a harness limit cut
  off before it did any work.
- The limits that decide top-ups and escalations are in
  [references/cycle.md](references/cycle.md).

## Integration

**The integrator is the only committer during a tranche.** It commits your
tranche record and criteria sections in a commit of their own, then merges.
You commit only when nothing is in flight: at opening, after a drain, at the
close. Launch a fresh integrator per stream from
[references/integrator-brief.md](references/integrator-brief.md). It verifies
the stream on the current main line, runs `scripts/check_test_changes.py`
against the worker's declared test changes, merges and closes the task or
returns it unmerged, and returns a verdict. Closing moves the task's file;
the brief points it at *Repairing the links a move breaks* in
[references/board-model.md](references/board-model.md). A stream returned
unmerged is an attempt with no progress; streams behind it are unaffected.

## Escalation

An entry is an exception report with an id, written to the tranche record in
the format [references/run-state.md](references/run-state.md) gives. Four
conditions open one: a stall that meets an escalation condition, a
verification sub-ceiling overrun, a need over the per-task cap (the three
*blocking* ones), and a draft or gated piece (*routine*, for the gate's
report).

- **Write the mechanical entries yourself**, from the allocation log. For
  each judgement entry (an unexplained cause, a fix that leaves the task),
  launch a fresh analyst from
  [references/analyst-brief.md](references/analyst-brief.md), at most one per
  cycle, outside worker capacity. Its spend is overhead, not the task's.
- **Park the stream**: its lease row reads *parked on E<n>*, the task stays
  `in-progress`, its slot is freed, and tasks depending on it wait. No agent
  sets an `owner` gate.
- **One push per cycle**, only for new blocking entries, under 200
  characters and leading with what to do. An entry still waiting is not
  pushed again. A push reported not sent is logged, not retried.
- **Never ask while the owner may be away**: a turn waiting on a prompt runs
  no cycle. On the owner's next message, re-read the open entries from the
  record and ask them through the structured prompt before anything else,
  blocking ones first, oldest first, at most four at a time, each with its
  options, evidence and recommendation. A heartbeat turn never asks.
- **Write each answer into its entry**, dated and in the owner's words; the
  next cycle acts on it by id. An answer that sets a rule for more than one
  task goes to the gate's report as a candidate precedent.
- **Nothing executes on silence.** No timeout approves an entry.

## Draining

When the owner asks for a pause: grant no new lease, let the work in flight
finish and integrate, write the state back, commit, and report a clean
boundary as [references/session-queue.md](references/session-queue.md)
defines one, listing the open entries. The owner can then compact or change
session. Never stop a tranche for context alone; compaction carries it.

## Closing a tranche

The tranche closes when nothing in it can be leased, or at the size limit the
gate declares it can review. Delete the heartbeat, write and commit the
record, then call the gate with the tranche's base and tip commits, the
record, each task's acceptance criteria and every integrator verdict. Its
report lists the open entries first, then the candidate precedents, and shows
`scripts/account_attempt.py --match-rate` over the project's recent finished
sessions; a rate near zero means the price table is stale. Push once when
the report is ready. The next tranche opens only on the owner's word.

Afterwards run `scripts/validate_board.py --board <board>` and
`scripts/generate_index.py --board <board>`.

## Guardrails

- Do not work a task, verify a stream or merge one yourself. Dispatch.
- Do not run two cycles in one turn, or launch more than three workers or
  more than one integrator at a time.
- Do not commit while an integrator or a worker is in flight.
- Do not let a worker set or change its own acceptance criteria, edit the
  board, or push.
- Do not top up a verification overrun, and do not grant past the per-task
  cap. Escalate both.
- Do not ask the owner while they may be away, and do not act on an entry
  until it is answered.
- Do not change a setting. Recommend it, with the reason.
- Do not push or publish. Every push asks the owner, after the gate.
- Do not trust a return, a summary or your own memory over the files on disk.

## Resources

- The cycle's limits and responses, re-read each cycle:
  [references/cycle.md](references/cycle.md)
- Run-state formats: [references/run-state.md](references/run-state.md)
- Briefs: [references/worker-brief.md](references/worker-brief.md),
  [references/integrator-brief.md](references/integrator-brief.md),
  [references/analyst-brief.md](references/analyst-brief.md)
- Selection and interference:
  [references/task-selection.md](references/task-selection.md)
- The state model, and the field contract:
  [references/board-model.md](references/board-model.md),
  [references/task.schema.yaml](references/task.schema.yaml)
- Plan template: [assets/task.md](assets/task.md)
- Report form: [references/report-form.md](references/report-form.md)
- Clean boundaries: [references/session-queue.md](references/session-queue.md)
- Scripts: `scripts/account_attempt.py` (with `scripts/prices.json`),
  `scripts/check_test_changes.py`, `scripts/validate_board.py`,
  `scripts/generate_index.py`
