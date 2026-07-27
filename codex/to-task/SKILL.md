---
name: to-task
description: Turn a request, bug report, or loose intention into one self-contained, code-grounded task specification and file it on the task board with the right status and gate. Use when asked to "make this a task", "add this to the board", "write this up as a task", "file a ticket", or to capture work for later.
---

# Raise a task onto the board

Turn a request, an observation, or a loose intention into one self-contained task
specification and file it in the right place.

Read [references/board-model.md](references/board-model.md) for the frontmatter
contract and folder mapping. Start from [assets/task.md](assets/task.md).

## Boundaries

- A task doc must stand alone. Someone reading only this file, with no memory of the
  conversation that produced it, must be able to act on it. Conversation context that
  does not make it into the file is lost.
- **Ground the task before writing it.** Read the code the task touches and cite what
  you find. A task built on a remembered claim sends its implementer down a false
  trail, and that costs far more than the reading would have.
- Separate what you verified from what you suspect. Label hypotheses as hypotheses.
- New tasks are `draft` unless the interview has already happened in this
  conversation. Do not write `scoped` on something you merely feel confident about.
- One task, one coherent objective. If it has two objectives that could be funded
  separately, it is two tasks.
- Do not raise a duplicate. Check the board first, including `completed/` and
  `revisit/` — a `revisit/` entry may already have evaluated and declined this exact
  idea, with the condition that would justify it.

## Steps

1. **Check for an existing home.** Search the board for the same subject. If a task
   already covers it, extend that one instead. If a `revisit/` task declined it,
   read the stated condition and address it directly rather than re-raising blind.
2. **Ground it.** Read the relevant code, config, or docs. Collect paths, line
   numbers, and current values. Note anything that contradicts the request's premise
   — an overturned premise is the single most valuable thing this step produces.
3. **Choose the id and the kind.** Kebab-case id, specific enough to be unambiguous a
   year later — prefer `<area>-<problem>` over a bare verb; it becomes the filename.
   Set `kind: spec` only if this task is the architecture/vision a set of tickets
   will realize; otherwise leave it `ticket` (the default). If it is one slice of an
   existing spec, set `part-of` to that spec — composition, not lineage.
4. **Fill the template.** `Why this exists` carries the evidence. `What the code
   says` carries the grounded findings with citations. `Plan` carries phases with
   named deliverables.
5. **Write the open questions.** Every decision you could not settle from the code,
   one item each, naming who can settle it. A draft with no open questions is either
   trivial or under-examined — check which.
6. **Set the gate — action or decision.** `manual` if a person must *perform*
   something an agent cannot: provision, deploy, install, run against a live
   environment, verify by hand, or supply material. `owner` if a person must
   *decide* something — product, founder, legal, vendor. `none` if an agent could
   start it today. Put the exact outstanding item under `Owner`.
7. **Cross-reference.** Link sibling tasks that must not be conflated with this one,
   and upstream tasks whose findings this one should start from. If the task
   genuinely cannot start until another lands, set `blocked-by` — prose alone will
   not file it, and will not clear it when the blocker closes.
8. **File and verify.**

   ```text
   scripts/validate_board.py --board <board>
   scripts/generate_index.py --board <board>
   ```

## Guardrails

- Do not write the file before reading the code. "Why this exists" with no evidence
  is a wish, not a task.
- Do not copy the request's wording as the problem statement. Restate the problem in
  terms of observable behavior.
- Do not set `gate: none` to make a task look actionable. The board root's value is
  entirely in being trustworthy.
- Do not use `blocked-by` for a dependency on a person; that is what `gate` is for.
  It names tasks on this board and nothing else.
- Do not put a solution in `Why this exists`. The plan is a separate section because
  the problem must survive the plan being wrong.
- Do not leave `created`/`updated` as template placeholders.
- Do not report the task as raised until the validator exits clean.

## Resources

- The state model and folder mapping:
  [references/board-model.md](references/board-model.md)
- Field-by-field contract: [references/task.schema.yaml](references/task.schema.yaml)
- Template: [assets/task.md](assets/task.md)
