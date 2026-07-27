---
name: task-board-triage
description: Audit a file-based task board and bring its recorded state back into agreement with the repository — validate frontmatter, refile tasks whose folder no longer matches, re-check blocked tasks whose gate may have cleared, correct stale claims, and regenerate the index. Use when asked to "triage the board", "audit the task board", "the board is stale", or to clean up task statuses.
---

# Triage the task board

Bring a board's recorded state back into agreement with reality, then regenerate
its index. Triage is the maintenance pass that keeps the board worth reading.

Read [references/board-model.md](references/board-model.md) before starting.

## Boundaries

- Triage **verifies and refiles**. It does not implement tasks, and it does not
  rewrite a task's specification. If a task needs its scope changed, say so and stop.
- Verify against the repository, not against the board's own claims. A `Status:`
  line, a folder, and an index can all agree with each other and all be wrong.
- Do not promote a task to `done` on the strength of a plausible narrative. Require
  a commit, a passing check, or a file you can read.
- Do not silently downgrade a task the user believes is finished. Report the evidence
  gap and let them decide.
- Never edit between the index markers by hand.

## Pass 1 — mechanical

Run the validator first. Everything it reports is objective and cheap to fix.

```text
scripts/validate_board.py --board <board>
```

Fix findings in this order, because later ones depend on earlier ones:

1. **Malformed or missing frontmatter** — a document the parser cannot read is
   invisible to every other check.
2. **Field errors** — id/filename mismatch, bad dates, invalid enum values.
3. **Cross-field rule violations** — a gate on a `done` task, `revisit` without
   `done`, `superseded` with no successor, a `blocked-by` cycle. Treat a cycle as
   urgent: every task in one is permanently invisible until it is broken.
4. **Folder mismatches** — decide which side is right. If the frontmatter is
   correct, `git mv` the file to the derived folder. If the folder is correct, fix
   the frontmatter. Never "fix" both to meet in the middle.
5. **Dangling references** — a `parent`, `supersedes`, or `superseded-by` pointing at
   nothing. Either the id is stale or the target was deleted; recover it from git
   history rather than dropping the link.

Re-run until clean.

## Pass 2 — substantive

The validator cannot tell whether a task's *content* is still true. Read each
**non-completed** task and check it against source.

Completed tasks are **frozen**: they are dated records of what was true when the
work happened, not living documentation, and re-verifying them is wasted effort
that grows without bound as the board ages. Two narrow exceptions — a `revisit/`
task's declined conditions, which are the point of recording a condition; and a
dangling cross-reference anywhere, which breaks navigation rather than making a
stale claim.

For each non-completed task:

1. **Do its factual claims still hold?** File paths, line numbers, version pins,
   configuration defaults, and counts all rot. Re-verify each one you can check
   cheaply, and correct it in place with the date.
2. **Has its blocker cleared?** For every `gate: manual` and `gate: owner` task,
   check whether the thing it waited on has happened — the action performed, the
   decision made. A gate nobody re-checks is how a board silently stops being a
   plan.

   Task-to-task blockers need no such sweep: the validator reports them as folder
   mismatches the moment a blocker reaches `done`, and those findings read as good
   news. Move each one to the root and say which tasks became available — a newly
   unblocked task is the most useful thing a triage pass can surface.
3. **Is it actually still wanted?** A task whose premise was overtaken belongs in
   `superseded/` with a successor, not at the top level forever.
4. **Is a `done` task genuinely done?** Its acceptance criterion, not its commit
   count, decides. If the remaining step is gated, it is `in-progress` with a gate.
5. **Is a `revisit` task's declined condition still declined?** If the condition it
   named has now occurred, that is a finding worth raising with the user — it is the
   whole reason the condition was written down.

Record each correction in the task itself, with the date and what it was checked
against. A corrected claim with no provenance invites the next pass to re-derive it.

## Pass 3 — index

```text
scripts/generate_index.py --board <board>
scripts/validate_board.py --board <board>
```

Then read the board root. Every task sitting there should be one an agent could
start today. If it is not, its gate is missing.

## Report

Present, in this order:

- Findings fixed mechanically, by rule.
- Claims verified against source, and which ones had drifted.
- Gates re-checked, and which have cleared.
- Tasks whose status you changed, with the evidence for each.
- Anything you could not verify, stated as unverified rather than assumed.

## Guardrails

- Do not batch-fix folder mismatches without reading each task. The mismatch is
  sometimes the frontmatter's fault and sometimes the folder's.
- Do not mark verification complete for a claim you did not actually check. Say
  "not checked" — an unverified claim recorded as verified is worse than an open one.
- Do not delete tasks. `superseded/` exists so provenance survives.
- Do not re-verify completed tasks against current source, and do not "correct" a
  dated observation in one. That work never ends and produces nothing.
- Do not close a `gate: owner` task by inferring the owner's decision.
- Triage is not done when the validator passes. The validator only proves the board
  is internally consistent, not that it is true.

## Resources

- The state model and folder mapping:
  [references/board-model.md](references/board-model.md)
- Field-by-field contract: [references/task.schema.yaml](references/task.schema.yaml)
