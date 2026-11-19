# Run-state formats

Two places hold a tranche's state, split by how often they change.

- **The tranche record** is a plan task on the board, committed. It keeps the
  audit trail.
- **The run directory**, `.supervise-implementation/` at the repository root,
  is rewritten every cycle and never committed. Its own `.gitignore` holds
  `*`, so it ignores itself and no tracked file changes. `git clean -x`
  deletes it.

Never put run files under the board folder: the board validator reads every
`.md` file there.

## The run directory

```text
.supervise-implementation/
├── .gitignore          # one line: *
├── leases.md           # the lease table
├── declared/           # each attempt's declared test changes, as JSON
│   └── <task>-<attempt>.json
└── drafts/             # the analyst's draft entries
    └── E<n>.md
```

## The lease table

`leases.md` opens with the tranche's id, its base commit, the heartbeat's job
id, the last cycle's number and time, and the size it counted, then one row
per attempt:

```markdown
| Task | Attempt | State | Agent id | Branch | Start commit | Grant | Fixed checks | Spend so far |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <task-id> | 1 | running | <agent-id> | <branch> | <sha> | standard: 40 calls | 0 | $0.00 |
```

`State` is one of `running`, `returned`, `integrating`, `merged`,
`unmerged`, `parked on E<n>` or `released`. Store the agent id, not only a
name: after a restart a subagent is reached by its id. The task's criteria
live in its task file, under `## Acceptance criteria`; the row only names the
task. `Fixed checks` is the number of checking calls those criteria require,
written at grant time from the criteria, zero when they fix none, and passed
unchanged to `account_attempt.py --fixed-checks`.

## The tranche record's added sections

The plan task carries `orchestrate-implementation`'s plan sections, plus
these, in this order:

```markdown
## Tranche

- Opened: <date>, on the owner's word; base commit <sha>.
- Size limit: 4,000 changed lines, the gate's, unmeasured.
- Window: <threshold read, or "not readable">; worktree.baseRef: <value>.
- Match rate: <`account_attempt.py --match-rate`'s figure, written at the
  close, for the gate's report>.

## Scope

- At opening: <task ids>.
- Joined: <task id>, <date>, `part-of` <tranche item>.

## Allocation log

| Date | Cycle | Task | Attempt | Event | Model, effort | Calls | Tokens in / write / read / out | Cost | Verif. | Grant, justification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

<Session costs, written at the close from `account_attempt.py <transcript>
--reconcile`, one row per session the attempts ran in. Each `Cost` above
stays transcript-priced, not scaled.>

| Session | Attempts | Priced | Harness total | Ratio |
| --- | --- | --- | --- | --- |
| <session id> | <task> <n>, ... | <`priced_usd`> | <`recorded_usd` \| absent> | <`ratio` \| absent> |

## Escalations

<one entry per escalation, in the format below>

## Integrator verdicts

- <date>, <task> attempt <n>: criteria moved <list>; tests <verdict>;
  <merged sha | unmerged: reason>.
```

`Event` is `grant`, `re-grant`, `top-up`, `stall: <diagnosis>`, `escalated
E<n>` or `released`. The execution log stays last, as in every task.

The session table is filled once, at the close. `--reconcile` prices every
transcript of the session an attempt's transcript belongs to and reads
Claude Code's own record of that session's cost: `Priced` is its
`priced_usd`, `Harness total` its `recorded_usd` and `Ratio` the one over the
other. The ratio reads a few percent under 1 because the harness bills calls
no transcript holds. A session still running has no record yet, the
supervisor's own included, so its row reads `absent` rather than an estimate.

## Escalation entry

Each entry is decidable on its own: it states the facts the decision needs
and points to the rest, because a worker's transcript ages off disk.

```markdown
### E<n>: <one-line title>

- **Opened:** <date>, cycle <n>; task <id>, attempt <n>.
- **Condition:** <stall unexplained | fix leaves the task | over the
  verification sub-ceiling | over the per-task cap | draft or gated piece>.
- **Urgency:** <blocking | routine>.
- **Cause:** <as diagnosed>.
- **Options:**
  1. <option> — evidence: <...>; cost: <...>; can be undone: <yes | no>.
  2. <option> — evidence: <...>; cost: <...>; can be undone: <yes | no>.
- **Recommendation:** <option>, because <reason>.
- **Evidence:** allocation-log rows <...>; verdict <...>; commits <...>;
  worktree <path>; agent id <...>.
- **While it waits:** <what is parked, and which tasks wait on it>.
- **Status:** <open | answered | withdrawn>.
- **Answer:** <date>, in the owner's words.
```

A routine entry is one line: `### E<n>: <piece> is <draft | gated>, for the
gate's report`, with its status.
