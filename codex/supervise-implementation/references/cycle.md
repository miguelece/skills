# The cycle's limits and responses

Re-read this first, at step 1 of every cycle. It holds every number a cycle
decides with, so nothing depends on what a compaction kept. The reasons live
in the design this skill implements, not here.

## Capacity

| Role | At once | Model, effort | Counts against |
| --- | --- | --- | --- |
| Worker | 3 | `opus`, `medium` | the task's cap |
| Integrator | 1 | `opus`, `high` | the task's cap |
| Analyst | 1 per cycle | `opus`, `high` | overhead, not the task |

A cycle launches at most three leases and one integration, then ends its turn.

## Grants

A grant is an **advisory** call budget stated in the worker's brief. Pick one
and log why:

- **standard**: 40 calls;
- **large**: 70 calls, for a task whose plan or a prior attempt shows it needs
  more.

Nothing enforces a grant. After each attempt, account for it:

```text
scripts/account_attempt.py <transcript.jsonl> --grant "<size>: <n> calls" --justification "<why>"
```

The transcript is the subagent's own, under the session's project directory.
Write its figures into the allocation log: model and effort, API calls, the
four token counts, the list-price cost, the raw verification share, the
grant and its justification. The share is a logged figure and never
escalates: it counts test runners, linters, validators, `--check` builds,
check scripts and reviewing a change (`git diff`, `git show` of a commit),
and is kept as the data series a later calibration needs. Checking done by
reading files is invisible to it.

## The per-task cap

**$20 at list price**, across all of a task's attempts and integrations.
Check it at admission, before granting: if the spend so far plus the next
grant's estimate would pass $20, escalate instead. Estimate a standard grant
at about $2.4 and a large one at about $9, integration included. An overshoot
by the attempt already running is accepted.

The spend is what each attempt's transcript prices, not scaled to the bill.
The harness bills calls no transcript holds, so the priced figure reads about
4% under the bill and the cap acts nearer $20.80. Those calls belong to the
session, not to any one attempt, and the session's ratio is known only once
it ends, after the cap was checked.

## Stuck attempts

An attempt is **stuck** when it repeated a check without getting anywhere.
The script reads it from the transcript and lists each episode under
`stuck_episodes`:

- the same check failing the same way 3 times, edits between or not;
- the same check giving the same result 4 times with no edit between;
- 6 steps alternating an edit and a check whose result does not change.

"The same" is the command text and the result with its timings stripped,
and a changed result clears the pattern. A healthy attempt checks often;
only repetition without change marks one stuck. The thresholds are the
OpenHands SDK's defaults, borrowed: no supervised attempt here has been
stuck yet to calibrate them on.

Progress stays the integrator's confirmed criteria, and the per-task cap
stays the backstop. A stuck attempt can still have moved a criterion; the
integrator's verdict decides that, not the episodes.

The first stuck attempt's re-grant runs at one effort level above the
attempt it replaces (`medium` to `high`), and the allocation log records
that effort on its row, as for any attempt. A stuck attempt re-run at the
same effort tends to hit the same wall. First attempts stay at `medium`, and
a second stuck attempt still escalates.

## Responses

| What happened | Response |
| --- | --- |
| A criterion moved, the grant was exceeded | Top up: log it, no ask |
| No criterion confirmed, cause named, fix inside the task | Re-size: a fresh grant from a clean worktree, no ask |
| No criterion confirmed, the same failure again, no new diagnosis | Escalate (judgement: analyst) |
| The fix changes the criteria or scope, or another stream's files | Escalate (judgement: analyst) |
| The first stuck attempt on a task | Re-grant from a clean worktree with the stuck episodes in the brief, at one effort level above the attempt it replaces (`medium` to `high`), logged in the allocation log, no ask |
| The second stuck attempt on the same task | Escalate (mechanical) |
| The next grant would take the task past $20 | Escalate before granting (mechanical) |
| Never started, or cut off by a harness limit before any work | Not a stall: re-launch |
| A draft or gated piece of a tranche item | Routine entry, one line |
| A model other than Opus 5.5 in the accounting | Log it for the gate's report |

## The size limit

**8,000 changed lines**, declared by the gate, from the owner's ruling of
2026-11-22: tranches closed on the earlier 4,000 well short of the
running-time target, and no study sized either value. A seeded replay
measured it once: 22 of 26 plants found at about 8,300 lines, every chunk
read, and kept by the owner on 2026-11-26. One replay at the keep threshold
licenses no higher limit. Each gate keeps checking it, by its findings per
changed line and by whether it read every chunk or sampled. Count it every
cycle, at step 6 before leasing:

```text
scripts/scan_tranche.py --repo <path> --base <tranche base> --tip HEAD --size --board <board>
```

It prints one number, leaving out generated regions and every file under
the board, so the limit counts the code and docs the gate reads by task
chunk, not board bookkeeping. Write it to
the lease table's header. At or past the limit, grant no new lease: let the
work in flight finish and integrate, then close the tranche.

## Mechanical entries

Their options are fixed:

- **over the cap**: raise this task's cap to a stated figure, re-scope it, or
  release it;
- **stuck twice**: re-grant once more with both attempts' episodes in the
  brief, at one effort level above the attempt it replaces and never above
  `xhigh` (`high` to `xhigh`), re-scope, or release.

## Each cycle, in order

1. Re-read: this file, the record's current sections, the lease table, the
   answered entries, the board; reconcile every lease against its agent.
2. Collect returns and account for each; correct each branch's
   `Start commit` to `git merge-base <main line> <branch>`, logged, before
   any integrator.
3. Test for stalls; log each condition.
4. Respond per the table; check the precedent register before writing an
   entry; write entries, park streams, act on answers.
5. Integrate: one integrator, if none is in flight.
6. Lease: count the size; at the limit, no new lease. Otherwise up to three
   workers, criteria first, in interference order.
7. Write back, append drafts, at most one push, end the turn.

On the owner's message: ask the open entries first. On a heartbeat: run a
cycle only if none has run since the last heartbeat, and never ask.
