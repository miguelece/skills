# Task selection

Which board tasks may be scheduled together, and which of them may run beside
each other. Every skill that schedules tasks applies these rules unchanged.
How large a set to take is each skill's own rule, never this file's.

## Eligibility

Eligible tasks are `status: scoped` with `gate: none`. Nothing else. A gated or
draft task cannot be scheduled — scheduling it just moves the blockage.

A task with open `blocked-by` entries is eligible **only if its blockers are in
the same set and sequenced ahead of it**. That is a legitimate way to run a
dependency chain in one pass; pulling in the downstream task without its blocker
is not.

**Schedule tickets, not specs.** A `kind: spec` is the vision a set of tickets
realizes, not a unit of implementable work — you schedule its tickets (the tasks
`part-of` it). Leave the spec's own status alone; closing it is a deliberate
call after its slices land, not an automatic consequence. A `kind: digest` is
scheduled like a ticket: it is one, marked as a digest.

## Interference

Each stream has a **write set**, the files it edits, and a **read set**: the
tools, generators and suites it runs. Disjoint files are not disjoint inputs —
a close that runs a generator another stream is still editing records output
from code nothing has committed yet. A tool every close runs (the board
generator, a suite runner, a lint config) is in every close's read set.

**Sequence by interference, not by size.** Streams whose write sets are
disjoint, and whose write sets miss every other stream's read set, can run in
parallel. Streams that touch the same files run in series on one branch, in a
stated order. A blocked task never runs in parallel with its own blocker.
