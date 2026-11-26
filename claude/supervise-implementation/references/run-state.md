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
├── drafts/             # the analyst's draft entries
│   └── E<n>.md
└── archive/            # earlier tranches' run files, moved at each opening
    └── <tranche>/      # its leases.md, declared/ and drafts/
```

Each opening moves the previous tranche's run files under `archive/<tranche>/`,
named by that tranche record's `id`, and `.tranche-gate/`'s under
`.tranche-gate/<tranche>/`. Archives are kept, never pruned: they are the only
copy of each tranche's lease table and patches. They are local only, like the
rest of the run directory, so `git clean -x` deletes them.

## The lease table

`leases.md` opens with the tranche's id, its base commit, the heartbeat's job
id, the last cycle's number and time, and the size it counted, then one row
per attempt:

```markdown
| Task | Attempt | State | Agent id | Branch | Start commit | Grant | Spend so far |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <task-id> | 1 | running | <agent-id> | <branch> | <sha> | standard: 40 calls | $0.00 |
```

The `Start commit` cell holds `HEAD` as read at lease until collection
replaces it with `git merge-base <main line> <branch>`.

`State` is one of `running`, `returned`, `integrating`, `merged`,
`unmerged`, `parked on E<n>` or `released`. Store the agent id, not only a
name: after a restart a subagent is reached by its id. The task's criteria
live in its task file, under `## Acceptance criteria`; the row only names the
task.

## The tranche record's added sections

The plan task carries `orchestrate-implementation`'s plan sections, plus
these, in this order:

```markdown
## Tranche

- Opened: <date>, on the owner's word; base commit <sha>.
- Size limit: 8,000 changed lines outside the board, the gate's, unmeasured.
- Target: 6 to 8 hours of running time, net of owner waits; pool estimate
  <hours> from <n> tickets at opening.
- Running time: <hours, opening to last integration, net of owner waits,
  written at the close>.
- Window: <threshold read, or "not readable">; worktree.baseRef: <value>.
- Match rate: <`account_attempt.py --match-rate`'s figure, written at the
  close, for the gate's report>.
- Cost per closed ticket: <`<task>` $<sum of its allocation-log `Cost`
  rows>, one entry per task the tranche closed, written at the close>.

## Scope

- At opening: <task ids>.
- Joined: <task id>, <date>, `part-of` <tranche item>.

## Allocation log

| Date | Cycle | Task | Attempt | Event | Model, effort | Calls | Tokens in / write / read / out | Cost | Verif. | Grant, justification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

<Session costs, printed at the close by `account_attempt.py --sessions
<run-dir>/leases.md --project <project-dir>`, one row per session the
attempts ran in. Each `Cost` above stays transcript-priced, not scaled.>

| Session | Attempts | Priced | Harness total | Ratio |
| --- | --- | --- | --- | --- |
| <session id> | `<task>` <n>, ... | <`priced_usd`> | <`recorded_usd` \| absent> | <`ratio` \| absent> |

## Previous tranche's session costs

<Written at opening, when the previous tranche's run directory was archived:
the rows `account_attempt.py --sessions
.supervise-implementation/archive/<tranche>/leases.md --project
<project-dir>` prints. The previous record is not edited; a row still absent
stays absent, with no estimate.>

| Session | Attempts | Priced | Harness total | Ratio |
| --- | --- | --- | --- | --- |

## Escalations

<one entry per escalation, in the format below>

## Integrator verdicts

- <date>, <task> attempt <n>: criteria moved <list>; tests <verdict>;
  <merged sha | unmerged: reason>.
```

`Event` is `grant`, `re-grant`, `top-up`, `stall: <diagnosis>`, `escalated
E<n>` or `released`. The execution log stays last, as in every task.

The session table is filled once, at the close, from one `--sessions` run
over the lease table, so the lease table's columns are a contract the script
reads them by. It finds each attempt's transcript by its agent id, groups the
attempts by session, prices every transcript of each session and reads
Claude Code's own record of that session's cost: `Priced` is its
`priced_usd`, `Harness total` its `recorded_usd` and `Ratio` the one over the
other. The ratio reads a few percent under 1 because the harness bills calls
no transcript holds. A session still running has no record yet, the
supervisor's own included, so its row reads `absent` rather than an estimate;
the supervisor's own row is filled at the next tranche's opening, under
*Previous tranche's session costs* in the new record.
A lease row whose transcript is not found is named on stderr and the run
exits 1; `--json` prints the same rows as JSON.

## Escalation entry

Each entry is decidable on its own: it states the facts the decision needs
and points to the rest, because a worker's transcript ages off disk.

```markdown
### E<n>: <one-line title>

- **Opened:** <date>, cycle <n>; task <id>, attempt <n>.
- **Condition:** <stall unexplained | fix leaves the task | over the
  second stuck attempt | over the per-task cap | draft or gated piece>.
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
