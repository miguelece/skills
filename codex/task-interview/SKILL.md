---
name: task-interview
description: Interview a draft task relentlessly until every open question is walked down to a recorded decision, exploring the codebase for anything the code can answer and asking the user only what the code cannot. Use when asked to "interview me", "grill me on this", "scope this task", "resolve the open questions", or before implementing a task still marked draft.
---

# Interview a task into a scoped spec

Walk a `draft` task's open questions down to recorded decisions, one branch at a
time, until nothing blocking is left unresolved. The output is a task that can be
implemented without further conversation.

Read [references/board-model.md](references/board-model.md) for the status contract.

## The rule that governs everything here

**If a question can be answered by exploring the codebase, explore it. Only ask the
user what only the user can answer.**

Asking someone to confirm a fact you could have read is how an interview becomes
tedious and starts getting skipped. Questions worth a person's attention are
preferences, priorities, risk tolerance, and external constraints — not the current
value of a constant.

## Boundaries

- Interview **one task**. If the conversation keeps pulling in another, that is a
  signal to split (`to-follow-on`), not to widen this one silently.
- Resolve questions **in place**: append the answer, the date, and the literal token
  `RESOLVED` to the existing item. Do not delete the question. The record of what was
  decided and when is the durable value.
- Walk the **dependency order**. A decision that changes what later questions even
  mean must be settled first. Do not present a flat list of every question at once.
- Expect the interview to change the task. Growing scope and overturning a premise
  are successful outcomes, not failures — record both explicitly.
- Do not set `status: scoped` while any blocking question is unresolved.

## Procedure

1. **Re-verify the premises first.** Before asking anything, check the task's factual
   claims against source. Tasks rot: paths move, counts change, a constant gets
   fixed. A premise that no longer holds can dissolve several questions at once — or
   the whole task.
2. **Map the decision tree.** Order the open questions by dependency: which answers
   constrain which others. Note which are code-answerable and which need the user.
3. **Close the code-answerable ones yourself.** Investigate, then record the answer
   with its citation and `RESOLVED`. Report what you closed rather than asking about
   it, shaped per [references/report-form.md](references/report-form.md) — this
   report sits between the user and the next question, so it earns its headings
   and it must not drop a hedge.
4. **Interview relentlessly on the rest.** One branch at a time, to a real decision —
   not a preference gesture. Push back when an answer is ambiguous or when it
   contradicts something already settled. Follow each answer to the questions it
   opens; a resolved decision that reveals a new question is the interview working.
5. **Record each decision** in place, with the date and the reasoning that decided
   it. Where an option was considered and rejected, say why — that is what stops it
   being re-proposed next month.
6. **Handle what the interview turns up:**
   - **A premise was wrong** → correct it in the task, and say plainly that it was
     overturned and by what evidence. Re-check whether the task still has a purpose.
   - **Scope grew** → record the new scope and what justified it.
   - **Work fell out of scope** → split it with `to-follow-on`.
   - **A question needs someone not in the room** → set the gate: `manual` when
     someone must *perform* an action, `owner` when someone must *decide*. Write
     the exact outstanding item under `Owner` and leave that question unresolved.
     A gate is an honest answer; a guess is not.
   - **The answer depends on another task landing first** → set `blocked-by`
     rather than guessing what that task will conclude.
7. **Promote and verify.** When no blocking question is left, set `status: scoped`,
   update `updated`, and run:

   ```text
   scripts/validate_board.py --board <board>
   scripts/generate_index.py --board <board>
   ```

## Guardrails

- Do not ask the user a question the repository answers. Explore first.
- Do not accept "whatever you think" on a question that genuinely needs their call.
  Narrow it to a concrete choice with stated trade-offs and ask again.
- Do not batch every question into one message. Dependencies get resolved out of
  order and answers contradict each other.
- Do not write implementation code during the interview. The deliverable is a scoped
  spec. Investigation to answer a question is in scope; building the feature is not.
- Do not mark a question `RESOLVED` with a restatement of the question. A resolution
  names the decision.
- Do not promote to `scoped` with an open gate question outstanding — that is what
  the gate field is for.
- Do not delete resolved questions to tidy the document.

## Resources

- The state model and folder mapping:
  [references/board-model.md](references/board-model.md)
- Field-by-field contract: [references/task.schema.yaml](references/task.schema.yaml)
- Emphasis, headings, and what must survive a shortened report:
  [references/report-form.md](references/report-form.md)
