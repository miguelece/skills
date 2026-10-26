---
name: close-out
description: 'Close out a work session in one step — run the post-creation audit with +git, then write the handoff the next session resumes from, then hand back for a clear. Use when ending a session that would otherwise take "/post-creation-audit +git and /handoff into continuing". It runs only when typed, because every run commits and pushes. A trailing into clause names the next session''s agenda: "/close-out into ticket 4" records that, and a bare "/close-out" first runs pause-check to propose one, recording "into continuing" when none is accepted.'
---

# Close out a session

Land the session's work, then write down what the next session needs, then hand
back for a clear — in one invocation instead of two.

From the user's side this is one act, always performed in the same order: the
audit lands the work, and the handoff records the state the audit left. So it
gets one entry point. It runs two skills, `post-creation-audit` and `handoff`,
and restates neither. Every rule of both applies unchanged; what this skill adds
is the order, a default agenda, and what happens when the first half stops
short.

**It owns one step of its own.** Typed bare, it first runs `pause-check` to
propose the next session's agenda, so the judgment of where the work stands
also says where the next session starts.

## Grammar

```text
/close-out                    proposes an agenda; records "into continuing" if none is accepted
/close-out into ticket 4      records the agenda "into ticket 4"
```

- **It takes one parameter, `into <agenda>`, and nothing else.** With no clause
  it runs `pause-check` to propose one (step 1). When nothing is proposed, or
  the user declines the proposal, the handoff records `into continuing`
  verbatim, which `handoff` already resolves to its *What is pending* list. A
  typed clause replaces both the proposal and that default; it is never
  appended to either.
- **`into` keeps the meaning it has on `handoff`.** It records the next session's
  agenda and is never a work order for this one. The clause is passed through
  unchanged.
- **A bare argument is refused.** `/close-out ticket 4` names no agenda. Ask
  whether `into ticket 4` was meant, rather than guessing.
- **A `+` flag is refused, not passed through.** The audit always receives
  `+git` and nothing else. A session that wants a different audit runs the two
  skills separately, which still works.
- **It runs only when the user types it.** Every run commits and pushes, and
  there is no default that stops short of that.

The full rules for parameters, and the list of which skills take one, are in
[references/invocation-grammar.md](references/invocation-grammar.md).

## Steps

1. **When typed bare, run `pause-check` first**, to name the next item of work.
   Skip this step when an `into` clause was typed: that clause is already the
   user's agenda. If `pause-check` names an item, put the proposal to the user
   as a question — `into <that item>`, or the default `into continuing` — and
   record what they choose. If it names none, the agenda is `into continuing`
   and there is nothing to ask. Its keep-going-or-pause verdict decides nothing
   here: the user already chose to stop by typing this. The proposal comes
   first because the audit's own prompts would otherwise bury it.
2. **Run `post-creation-audit` with `+git`**, exactly as if it had been invoked
   that way, and follow it to its end. Its prompts stay its own: it will confirm
   before pushing to a public remote, ask before deleting a local branch, and
   ask when it is unsure whether something is an artifact. Each of those is a
   question for the user. Wait for the answer, and never answer one on the
   user's behalf — a composite that does has removed the only safeguard a
   self-composed `+git` has.
3. **Run `handoff` with the agenda**, even when the audit stops partway — a
   declined or refused push, a failing suite it reported, a branch the user
   chose to keep. That is when the next session needs the document most. It
   starts only once the audit has ended: every prompt the audit raised has been
   answered by the user, and a question the user explicitly put off goes into
   the handoff's *Open questions*. Three things carry across:
   - **The audit's *Needs a decision* items** go into the handoff's *Open
     questions* section when they block the next session, and into *Loose ends*
     when they do not. The clear destroys the audit's report; the handoff is
     the only place they survive.
   - **State is verified fresh.** The handoff checks the repository after the
     audit's commits and pushes, and records whatever did not land. The audit's
     test numbers are not copied across: they were taken before its own
     corrections.
   - **The document goes where `handoff` says** — scratch space, never a commit.
     It is written after the audit has landed the session, so committing it
     would reopen what the audit just closed.
4. **End the way `handoff` ends a change of shift.** Confirm the document stands
   alone, then tell the user to run `/clear` and to start the next session with
   `resume-handoff`. The agent cannot clear its own context; that is the user's
   to do, and it is why a one-step handoff-and-clear was never built.

**What a failing suite does to the audit is the audit's rule.** This skill adds
no gate of its own and removes none, and the handoff records the suite's state,
verified fresh.

## Reporting

The audit reports first, shaped by its own rules. After it, say where the handoff
was written and list what did not land, if anything. The instruction to clear
comes last, and only once the handoff is written and verified — if it is not,
say so and do not tell the user to clear.

## Guardrails

- Do not answer any of the audit's prompts on the user's behalf — the push
  confirmation, a branch deletion, an unsure cleanup. Wait for the user.
- Do not skip the handoff because the audit stopped partway.
- Do not carry out the agenda. It is recorded for the next session, as `handoff`
  records it — a list of imperatives included.
- Do not push anything yourself. Every push in a close-out is the audit's,
  under `+git`, behind its own confirmation.
- Do not pass the audit any flag but `+git`, and do not accept a `+` flag on
  this skill.
- Do not restate either skill's steps in place of running them.
- Do not record a proposed agenda the user has not accepted, and do not run
  `pause-check` when an `into` clause was typed.
- Do not tell the user to clear before the handoff is written and verified.
- Do not try to clear the context yourself.

## Resources

- What `into` means on every holder, the default here, and why a composite
  inherits the audit's confirmation:
  [references/invocation-grammar.md](references/invocation-grammar.md)
