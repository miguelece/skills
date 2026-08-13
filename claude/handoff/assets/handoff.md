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
