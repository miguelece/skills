# Handoff — <subject>

Written <YYYY-MM-DD>. Starting point for a fresh session with no prior context.

---

## Next session — start here

<The agenda, when the invocation carried a trailing directive — `/handoff into
<what the next session should do>`. If it carried none, write "No directive
given; see The task below." and keep the heading.>

**Agenda, verbatim:** <the directive exactly as it was typed, unedited. This is
the authority. Do not tidy it, shorten it, or turn a list into a summary.>

**What it resolves to today:** <what this session checked the directive refers
to — the actual task id, branch, file, or command, with its path — and how that
was checked. If it could not be resolved, say so and say why. Never guess: a
wrong resolution is worse than an unresolved one, because the verbatim text
above is the only thing that can correct it.>

**Before acting on it:** <the preconditions. Anything unresolved under Open
questions below outranks this agenda — a directive never settles a question the
writing session left open. If the agenda needs a choice the user has not made,
say that the next session must ask before starting.>

### What is pending

<Always present, whether or not a directive was given. The ranked shortlist of
what the next session could actually pick up. This is what makes a directive
with an open referent — `/handoff into continuing` — satisfiable: it names the
candidates, so the reading session does not rebuild them from the board.>

<Not the same as two sections below that look similar. *Loose ends* is
exhaustive and unranked; *The task → Not started* is a status list. This is the
filtered, ordered subset that is startable now, and it is worth its own slot
precisely because neither of those answers "what should I do next".>

- **<candidate>** — <why it is startable, what it costs, and its gate: ungated,
  or waiting on a named person or task. Name the owner when it is not
  engineering's to take.>

<Then, separately, what is deliberately NOT a candidate and why — parked,
deferred, or someone else's. A reader who cannot see why something was excluded
will re-propose it, which is the cost this list exists to stop paying.>

---

## Orientation

<Where the work lives. Repository, branch, whether the tree is clean. A directory
tree if the layout is not self-evident. Say explicitly which directories are
repositories and which are plain folders.>

```text
<tree>
```

---

## The task

<What is being done, in one paragraph.>

**Done:**

- <item>

**In progress:**

- <item, and exactly where it stopped>

**Not started:**

- <item>

---

## Open questions — must be resolved before proceeding

<Anything genuinely undecided. Mark it unmistakably. If the next session must ask
the user something, write the question here in the form it should be asked. If
there are none, write "None." — do not delete the section.>

---

## Non-negotiable conventions

<Numbered. Each with the reason it exists, and what enforces it. A rule without a
reason gets "improved" by the next session.>

**Cite these by name, never by number. The numbering is local to this document
and dies when it is replaced.** An ordinal reads exactly like a stable
identifier, so work written during the session picks it up — and the next
handoff renumbers or reorganises this list, leaving every one of those citations
pointing at nothing. Inside this document, refer by number freely; in anything
tracked, name the rule.

1. **<Rule>** — <why it exists>. <What enforces it: a test name, a hook, a
   gitignore rule.>

---

## Commands

<Exact, copy-pasteable, each with the directory to run it from.>

```powershell
# <what this does>
<command>
```

---

## Traps found the hard way

<The highest-value section. Every dead end and wrong assumption this session hit.
For each: what looked true, what was actually true, and how the difference was
found. Do not omit these because the work eventually succeeded.>

- **<What looked true>.** <What was actually true, and how it surfaced.>

---

## Loose ends

| Item | State |
| --- | --- |
| <thing> | <where it stands, and why it was left> |

---

## Verified state

<Facts checked against the repository just before writing this — not from memory.>

```text
<git log --oneline -N output>
```

<Test suite result, with real numbers. Build status. Anything uncommitted.>
