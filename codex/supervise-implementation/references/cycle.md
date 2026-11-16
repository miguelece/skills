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
four token counts, the list-price cost, the verification share, the grant
and its justification.

## The per-task cap

**$20 at list price**, across all of a task's attempts and integrations.
Check it at admission, before granting: if the spend so far plus the next
grant's estimate would pass $20, escalate instead. Estimate a standard grant
at about $2.4 and a large one at about $9, integration included. An overshoot
by the attempt already running is accepted.

## The verification sub-ceiling

**25% of an attempt's tool calls.** The script's verification share counts
test runners, linters, validators, `--check` builds, check scripts, and
reviewing a change (`git diff`, `git show` of a commit), because the
measurement behind 25% counted them. An overrun escalates and is **never
topped up**. Checking done by reading files is invisible to the count.

## Responses

| What happened | Response |
| --- | --- |
| A criterion moved, the grant was exceeded | Top up: log it, no ask |
| No criterion confirmed, cause named, fix inside the task | Re-size: a fresh grant from a clean worktree, no ask |
| No criterion confirmed, the same failure again, no new diagnosis | Escalate (judgement: analyst) |
| The fix changes the criteria or scope, or another stream's files | Escalate (judgement: analyst) |
| Verification passed 25% of tool calls | Escalate (mechanical) |
| The next grant would take the task past $20 | Escalate before granting (mechanical) |
| Never started, or cut off by a harness limit before any work | Not a stall: re-launch |
| A draft or gated piece of a tranche item | Routine entry, one line |
| A model other than Opus 5.5 in the accounting | Log it for the gate's report |

## The size limit

**4,000 changed lines**, declared by the gate and unmeasured: a starting
value, which no study has sized. Count it every cycle, at step 6 before
leasing:

```text
scripts/scan_tranche.py --repo <path> --base <tranche base> --tip HEAD --size
```

It prints one number, leaving out the board's generated indexes. Write it to
the lease table's header. At or past the limit, grant no new lease: let the
work in flight finish and integrate, then close the tranche.

## Mechanical entries

Their options are fixed:

- **over the cap**: raise this task's cap to a stated figure, re-scope it, or
  release it;
- **over the verification sub-ceiling**: re-grant with verification held to
  the ceiling, re-scope, or release.

## Each cycle, in order

1. Re-read: this file, the record's current sections, the lease table, the
   answered entries, the board; reconcile every lease against its agent.
2. Collect returns and account for each.
3. Test for stalls; log each condition.
4. Respond per the table; write entries, park streams, act on answers.
5. Integrate: one integrator, if none is in flight.
6. Lease: count the size; at the limit, no new lease. Otherwise up to three
   workers, criteria first, in interference order.
7. Write back, append drafts, at most one push, end the turn.

On the owner's message: ask the open entries first. On a heartbeat: run a
cycle only if none has run since the last heartbeat, and never ask.
