---
name: handoff
description: Write a self-contained handoff document to disk so a fresh session can resume the work with no memory of the conversation — carrying the conventions, the exact commands, the dead ends, and what is still undecided. Use when asked to "write a handoff", "change shift", "hand this off", "write a handoff and clear", or when context is running short mid-task. A trailing `into` clause names the next session's agenda rather than work to do now — "/handoff into next task" means record that directive in the document, not act on it.
---

# Write a handoff

Write a document that lets a fresh session pick up this work with no memory of the
conversation — then, when asked, clear and resume from it.

A written handoff beats automatic summarization because you choose what survives.
Summarization keeps what was *said*; a handoff keeps what is *load-bearing*, and
those are different sets. The parts that get dropped first — the dead ends, the
reasons behind a convention, the thing that is not yet decided — are the parts a
fresh session most needs.

Start from [assets/handoff.md](assets/handoff.md).

## Boundaries

- Write to disk, in scratch space (`.scratch/handoff.md` or similar). Confirm the
  path. A handoff in the transcript is not a handoff.
- Write for a reader with **zero** context. No pronouns pointing at the
  conversation, no "as discussed", no "the file we were editing".
- **Absolute paths or repo-relative paths, always.** "the config file" is useless.
- State what is **not** known or **not** decided as explicitly as what is. An
  unresolved question papered over becomes a wrong assumption in the next session.
- Do not write a chronology. Nobody needs the order things happened in; they need
  the current state and the next action.

## What must be in it

1. **Next session — start here.** First, above everything. The agenda, when the
   invocation carried a trailing directive (see below). Record it **verbatim**,
   then what you verified it resolves to, then the preconditions for acting on
   it. When there was no directive, say so — do not drop the section.
2. **Orientation.** Where the work lives. A directory tree if the layout is not
   obvious. Which repository, which branch, whether anything is uncommitted.
3. **The task.** What is being done and how far it got. Split cleanly into done,
   in progress, and not started.
4. **Open questions — must be resolved before proceeding.** What the next session
   must decide, or ask the user, before it starts. Mark these unmistakably — a
   placeholder that reads as a decision is worse than an empty section. This
   section outranks the agenda, so it sits near the top where it will be read.
5. **Non-negotiable conventions.** Each with the reason it exists. A rule without
   its reason gets "improved" by the next session. If a test or a hook enforces
   it, say which. **Number them, and say in the section that the numbering is
   local to the document and must never be cited from a tracked file** — an
   ordinal reads like a stable identifier, so work written during the session
   cites it, and the next handoff renumbers and strands every one.
6. **Commands.** The exact invocations, with the directory to run each from.
   Copy-pasteable. Not "run the tests" — the actual command line.
7. **Traps found the hard way.** Every dead end, wrong assumption, and
   non-obvious failure this session hit. **This is the highest-value section** and
   the one a summary always loses. Each entry: what looked true, what was actually
   true, and how it was found.
8. **Loose ends.** Everything deliberately left undone, with its current state and
   why it was left. A table works well.
9. **Verified state.** The facts checked against the repository immediately before
   writing, not recalled: commits, the test suite's real result, build and lint
   status, anything uncommitted. Being explicitly a dated snapshot is what makes
   this the one section where exact counts belong — stated anywhere else they go
   stale without anything noticing.

## The `into` grammar

`/handoff into <something>` names **the next session's agenda**. It is content
for the document, not a work order for now:

```text
/handoff into next task
/handoff into the new tasks
```

Record the clause verbatim under *Next session — start here*, then add what you
verified it resolves to. Both halves matter — the verbatim text preserves what
was asked, the resolution saves the fresh session from re-deriving it.

Executing the directive instead is the failure this section exists to prevent,
and it is expensive exactly when it happens: the invocation exists *because*
context is nearly gone, so spending what remains on the work is the outcome the
request was trying to avoid.

Only a trailing `into` clause is a directive. Other phrasings are ordinary
conversation — act on them normally.

## Steps

1. Establish the true current state from the repository, not from memory:
   `git status`, `git log --oneline -10`, and the test suite's actual result.
2. Draft the document from the template.
3. **Re-read it as a stranger.** For each paragraph ask: could someone act on this
   with no other context? Every "it", "that file", or "the usual way" is a defect —
   replace it with the specific thing.
4. Verify every path, command, and claim you wrote. A handoff's authority is the
   reason it is trusted; one wrong path undermines all of it.
5. Save it and tell the user the path.

## Clearing and resuming

This is continuing **the same work** in a fresh session — not `into`, which
names *different* work for the next session. The two wear similar words and mean
opposite things: `change shift` keeps the task and drops the context;
`into <topic>` keeps the context long enough to write it down and changes the
task. An invocation can be both, and then it does both.

When the request is to hand off *and continue* (`change shift`, "write a handoff
and clear"):

1. Write and verify the handoff as above.
2. **Confirm it stands alone before clearing.** Once context is gone, anything
   missing is gone with it. This gate is the whole point.
3. Tell the user the handoff is ready and that they should `/clear`, then open the
   new session by reading the handoff path. You cannot clear your own context —
   that is theirs to do.

## Guardrails

- Do not carry out a trailing `into` directive. It is the next session's agenda,
  and the document is where it goes. This holds for a list of them too — a
  sequence of imperatives reads like a work order and is not one. **The rule is
  about invoking `handoff`, not about the keyword**: `resume-handoff` holds the
  opposite rule for the same word, because a directive typed there addresses the
  session reading the document rather than a future one.
- Do not resolve a directive by guessing. Record it verbatim and say what could
  not be checked.
- Do not let an agenda override an unresolved open question.
- Do not write a handoff that assumes the reader saw the conversation.
- Do not omit the traps because the work eventually succeeded. They are the reason
  it succeeded.
- Do not record an open question as though it were settled.
- Do not claim a state you did not verify — especially "tests pass". Run them.
- Do not summarize the conversation. Describe the state of the work.
- Do not tell the user to clear before the handoff is written and verified.

## Resources

- Template: [assets/handoff.md](assets/handoff.md)
