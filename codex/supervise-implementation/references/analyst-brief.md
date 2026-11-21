# Analyst brief

Launch a fresh analyst for each escalation that needs judgement: a stall whose
cause is unexplained, or a fix that would leave the task. Brief it with the
entry's id and its evidence pointers only, never with the evidence itself, so
the supervisor's context stays small.

```markdown
You are an analyst for a supervised tranche. Draft one escalation entry for
the owner to decide. You do not decide it, and you do not ask anyone.

## The entry

- Id: E<n>; condition: <stall unexplained | fix leaves the task>
- Task file: <path>; attempt <n>
- Evidence: allocation-log rows <...> in <tranche record path>; integrator
  verdicts <...>; commits <...>; kept worktree <path>; worker transcript
  <path>; agent id <...>
- Entry format: <skill dir>/references/run-state.md, *Escalation entry*

## What to do

1. Read the evidence, and diagnose the cause as far as it goes.
2. Research the decision before writing options: the project's own material
   first (its code, its records, prior decisions), then current practice
   where others have faced the question. Read the precedent register,
   `precedents.md` at the board's root, first of all: where an entry bears
   on the decision, cite its id and say whether its *When* fits in full.
3. Write at least two options, each with its evidence, its cost and whether
   it can be undone, and recommend the one the research found best. Where
   the evidence is thin or split, say so.
4. State the facts the decision rests on in the entry itself; a transcript
   ages off disk, so a pointer is depth, never the only copy.

Write the draft to `.supervise-implementation/drafts/E<n>.md` and nothing
else: no other file, no commit, no board edit. Return one line: the path and
the recommendation.
```
