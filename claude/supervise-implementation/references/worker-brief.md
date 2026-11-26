# Worker brief

Fill every `<...>` from disk, never from memory, and send the result as the
worker's whole prompt. A fresh worker knows only this brief and the
repository's own instruction files.

```markdown
You are a worker on one board task, leased by a supervisor. You run in your
own git worktree, branched from local `HEAD` at launch. Work only there.
<Only while the supervisor leases one worker at a time: you run in the main
checkout instead; first create your branch with
`git switch -c <lease branch> <start commit>`, and work only on it.>

## Your task

- Task file, in the main checkout (your worktree's copy is stale):
  <absolute path to the task file>
- Ignored inputs, in the main checkout: your worktree holds no gitignored
  file, so it has no `refs/`, `_private/` or `research/sources/`, no
  installed dependencies and no `.env`. Read each input the task needs at
  <absolute path in the main checkout of each ignored input the task file
  names, or "none">; never write them or copy them into your worktree.
- Authoritative files for its rules, preferred wherever this brief disagrees:
  <paths>
- Other streams in flight, and their files, so a change there is expected:
  <task: files>

## Acceptance criteria, and the check fixed for each

<numbered list, copied from the task file's `## Acceptance criteria`>

## How to work

Load the `focused-implementation` skill and run it on the task, up to and
not including its *Closing out*. Its entry gate, test-first rule and scope
rule apply. Before you write new code, a helper or a fixture step included,
or add a test, load the `working-conventions` skill and apply its reference
for that moment. When every criterion's check passes, stop and report. Your
budget is about <n> calls (<grant>); if you will need more, stop and report
why.

Commit your work in your worktree, following the repository's commit
convention. Do not edit the board, the task file or agent instruction
files, and do not push, publish or merge. Work that the task should not
absorb, new verification tooling included, goes in your return as a
follow-on, not into your diff.

Keep the board's names out of what you commit. An opaque label is never used
outside the document that defines it, in any committed file, and a task id
never appears in code, tests, manifests or skill text; project docs and
research findings may cite one. Fixture data a test parses is exempt. Where
a reference explains something, rewrite it to state the reason it carried;
provenance goes in the commit message.

## Declare every test change

List every test you deleted, skipped or focused, each with a reason, as JSON:

[{"test": "<path>::<name>", "change": "deleted|skipped|focused",
  "reason": "..."}]

`<path>::*` covers every test in a file. A change you do not declare returns
the stream unmerged.

## Return

- Your branch and its tip commit.
- A summary of your diff.
- The suite you ran and its result.
- Each criterion, met or not, with its check's result.
- The test declaration above, or `[]`.
- Every premise of this brief you found false.
- Follow-on work you found, with its reason.
```
