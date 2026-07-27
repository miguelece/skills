---
name: to-follow-on
description: Split work off an in-flight task into its own board task — either a composition slice (a ticket that is part-of a spec, or a subticket of a ticket, that folds back up when done) or a lineage follow-on (separate work carved out, that does not). Use when asked to "split this off", "spin this off", "make that a follow-on", "break this spec into tickets", "add a subtask", or when work surfaces mid-task that is out of the parent's scope.
---

# Split work off an existing task

Carve work out of a task that is already in flight, without losing why it was
discovered or letting the parent's scope quietly grow.

Read [references/board-model.md](references/board-model.md). Start from
[assets/task.md](assets/task.md).

## First: lineage or composition?

Two different relations, two different frontmatter fields. Decide which before you
write anything — they behave oppositely at completion.

- **Composition (`part-of`)** — the new task is *a piece of completing the parent*: a
  ticket that is one slice of a spec, or a subticket that is one slice of a larger
  ticket. Its outcome **folds back up** into the parent when it finishes. Set
  `part-of`, and set `kind: ticket`.
- **Lineage (`parent`)** — the new task is *separate work discovered while doing the
  parent*, explicitly carved **out** of it. The parent completes **without** it, and
  it must **not** fold back up. Set `parent`.

A task can carry both: separate work (lineage) that is also a piece of some other
effort (composition). If you cannot say which relation applies, you have not yet
decided whether this work is part of the parent or merely spawned by it — settle
that first.

## When a split is the right move

Split when work surfaces mid-task that is **real but not this task's job**:

- The parent's scope would grow past what was agreed.
- The new work has a different gate — the parent can proceed, this cannot (or the
  reverse).
- The new work is independently fundable: someone could reasonably do one and not
  the other.
- A premise turned out to be wrong, and correcting it is its own piece of work.

Do **not** split to avoid finishing something. If the work is inside the agreed
scope and merely tedious, it stays in the parent.

## Boundaries

- The follow-on must carry its **provenance**: `parent` in frontmatter, plus a
  sentence saying which decision or finding in the parent produced it. A follow-on
  whose origin is lost gets re-litigated from scratch.
- The parent must be **amended in the same pass** — a follow-on that leaves the
  parent claiming the work is still in scope creates two contradicting documents.
- Follow-ons are `draft`. They have not had their own interview yet, whatever the
  parent's status.
- Do not split work that has already been done. That is an execution-log entry.

## Steps

1. **Name the trigger.** Write, in one sentence, what in the parent produced this:
   which decision, which finding, which overturned premise. If you cannot, the split
   is probably arbitrary — reconsider.
2. **Test the boundary.** State what the parent is now explicitly *not* doing. If you
   cannot draw that line cleanly, the work belongs in the parent.
3. **Write the follow-on** from the template. In `Why this exists`, lead with the
   trigger and link the parent. Carry across the evidence the parent already
   gathered — a follow-on that makes its implementer re-read the same code wastes
   the parent's work.
4. **Set the relation** chosen above: `part-of` for a composition slice, `parent`
   for a lineage split. Not both unless both genuinely apply.
5. **Set its own gate**, independently. This is the point of the split: inheriting
   the parent's gate by default defeats it. (Composition does not change this —
   a subtask files by its own status and gate like any task.)
6. **Amend the parent.** Add the follow-on to its `Dependencies / cross-refs`, and
   record the descope explicitly — name what moved out and why, so nobody later
   "fixes" the omission. If the parent has an execution log, note the spin-off there.
7. **Verify.**

   ```text
   scripts/validate_board.py --board <board>
   scripts/generate_index.py --board <board>
   ```

## Guardrails

- Do not write the follow-on and stop. The parent amendment is half the job, and it
  is the half that gets skipped.
- Do not inherit the parent's gate, priority, or status without deciding each one.
- Do not restate the parent's whole context. Link it, and carry across only the
  evidence the follow-on actually needs.
- Do not split one task into many small ones speculatively. Each follow-on should be
  something you could hand to someone today.
- Do not use a follow-on to park a disagreement. If the user and the evidence
  disagree, say so directly.
- Do not set `part-of` for work merely spawned by the parent, or `parent` for a
  genuine slice of it — the two fold back oppositely, so the wrong one corrupts the
  spec's rollup.
- Do not nest composition for its own sake. Prefer sibling tickets under one spec
  over deep subticket chains; nest only when a group is its own handoff unit.

## Resources

- The state model and folder mapping:
  [references/board-model.md](references/board-model.md)
- Field-by-field contract: [references/task.schema.yaml](references/task.schema.yaml)
- Template: [assets/task.md](assets/task.md)
