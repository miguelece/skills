# Session queue

How to order a run of board work across more than one session, and where to put
the boundaries between them.

A queue is reasoning that is otherwise spent once and discarded: which item
decays fastest if deferred, which ordering keeps a downstream item from going
stale, where a session should stop. Nothing else in this lab takes that as input
or writes it down, so it gets rebuilt from scratch every time and two agents
asked the same question on the same board place the boundaries differently.

This file is the rule they can disagree against.

## What a queue must carry

Four things per item. An item missing any of them is not queued, it is
mentioned.

- **The item**, by task id, so it survives the conversation that produced it.
- **Why it sits where it sits** — what makes it more urgent than the item below,
  or what it must follow. Ordering without a reason cannot be revised by anyone
  who was not there.
- **Its gate.** Ungated, waiting on a named person, or waiting on a named task.
  An item nobody can start is not a queue position, it is a note.
- **What finishing it makes possible**, when anything depends on it. This is what
  stops a downstream item being scheduled before the thing it consumes exists.

And one thing for the queue as a whole: **the date it was built**, because every
ordering reason above is a claim about the board on that day.

## Ordering

Prefer, in this order:

1. **What decays fastest if deferred.** A task whose premises were verified this
   session is cheaper now than next week. A task whose blocker just cleared is at
   its most re-verifiable while the reason it cleared is still on hand.
2. **What unblocks the most.** An item several others consume earns its place
   ahead of an item nothing waits on, even a more interesting one.
3. **What is cheapest to close while its reasoning is fresh.** A task interviewed
   an hour ago implements faster than one interviewed in March, and the gap is
   the re-reading.

**Where one item defines something another consumes, the definer goes first**,
regardless of the three above. That is a dependency, not a preference, and
getting it backwards means the second item is built against something that then
changes.

## Choosing a boundary

**A boundary is a place where the work is provable, not merely paused.** That is
the whole rule, and the rest of this section is what it means in practice.

Stop where all of these hold:

- Nothing is mid-edit. No half-applied change, no file written but unverified.
- Whatever was done has been verified the way this repository verifies things,
  and the result is recorded rather than remembered.
- Any decision reached is written into tracked material, not left in the
  conversation.
- The next item can start from what is committed, without reconstructing state
  that only this session holds.

Do **not** stop:

- part-way through a deliverable, however tired the context is;
- immediately before a verification step, which hands the next session a state
  nobody has checked;
- after a decision was reached but before it was recorded, which is the most
  expensive boundary available — the reasoning is gone and the decision looks
  arbitrary to whoever inherits it.

## What a boundary must buy

**A boundary placed only where context ran out is the failure mode, not the
rule.** Context relief is what makes a boundary necessary; it is not what makes
one good. A good boundary also buys at least one of:

- **A clean resumption point** — the next session reads a committed tree and a
  handoff, and starts working rather than reconstructing.
- **A landed decision** — something that was open is now closed in tracked
  material, so it is not re-litigated.
- **A verified state** — the next session inherits a known-good tree rather than
  an unknown one, and any failure it then sees is its own.

A boundary that buys none of these has not divided the work, it has interrupted
it.

## No threshold is published here, and that is deliberate

**This file states no percentage, and none should be added to it.**

An agent cannot reliably observe its own context-window occupancy. Where a
running session surfaces a figure at all, it is typically a session-wide token
budget, which is a different quantity — a budget can be ample while the window is
nearly full, and the reverse. A rule written against the available number would
be measuring the wrong thing confidently.

So the signals above are **observable proxies**: whether a deliverable is
mid-edit, whether the next item needs a document that is already committed,
whether the next item's premises were verified this session or an earlier one,
and how many items have been taken to a verified close. Each of those an agent
can actually check.

A figure invented here would also be an unportable constant of exactly the kind
this lab audits elsewhere — measured on nothing, carried everywhere.

## A recorded queue is not a pre-approved set

**Having a queue does not authorize skipping selection.**
`orchestrate-implementation` admits `status: scoped` with `gate: none` and
nothing else, and it re-runs that selection for every set rather than carrying
items forward by default. **That guardrail is unchanged by this file**, and the reason it exists
is that an unreviewed set drifts: a queue built last week names tasks whose
status, gate, or premises have since moved.

The queue supplies an **ordering and a set of boundaries**. **Selection still
runs**, every set, and it is what decides eligibility. An item reaching the
front of the queue is a claim about priority, never about admissibility.

**Do not read "the queue says this one is next" as licence to start it.**
Re-check its status and its gate first; that check is cheap and the queue is
older than the board.

## What this does not do

Nothing in this repository can observe whether an agent actually paced a session
well, so nothing here is measured. These are arguments from the failure modes
this lab has already paid for, not results — and the distinction is the same one
the confidence markings on research findings exist to preserve.

Read this file as a rule to disagree against, which is what it was written to be.
