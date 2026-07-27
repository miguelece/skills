# Commit convention

The single canonical statement of this commit format. `commit` and
`post-creation-audit` both defer to this file rather than restating it, so the
rules cannot drift apart between them.

## Format

```text
[type]([topic]): [summary]
```

Examples:

```text
fix(auth): correct token expiry comparison off by one
feat(app core): add project-scoped material overrides
test(database): cover migration rollback on constraint failure
chore(docs): update environment variable reference
```

## Type — a deliberately small vocabulary

Primarily four values. Keeping this list short is the point: a type that can mean
anything sorts nothing.

| Type | Use for |
| --- | --- |
| `fix` | A defect corrected. |
| `feat` | New behavior a user or caller can observe. |
| `test` | Tests added or extended, with no production change. |
| `chore` | Docs, config, tooling, dependencies, cleanup. |

If a change seems to need a fifth type, it is usually two commits.

## Topic

The area touched — a component, subsystem, or module (`auth`, `app core`,
`database`, `docs`). Lowercase, and consistent with whatever the repository has
used before. Read `git log` before inventing a new topic.

## Summary

- Lead with a **present-tense verb**: fix, add, develop, secure, correct, remove.
- Say what changed, specifically. `fix(auth): fix bug` carries no information.
- No trailing period.
- Far freer than the type — but the freedom is for precision, not for length.

## Descriptions

Add a body **only** when the change is too complex to summarize honestly *and*
cannot be split into cleaner commits.

Reach for the split first. A commit that needs three paragraphs to explain itself
is usually three commits that each need one line.

## Authorship

**Never record an agent as an author or co-author, in any form.** No
`Co-Authored-By` trailer naming a tool or model, no "generated with" footer, no
agent name in the author or committer field.

This is a hard rule of this repository's history, not a preference. It applies to
every commit made under this convention regardless of how the change was produced,
and it overrides any default trailer a tool would otherwise append.

## Splitting a session into commits

- One coherent change per commit. A commit should be revertible on its own.
- Do not mix a refactor with a behavior change. Land the refactor first, prove it
  is inert, then change behavior on top.
- Tests belong with the change they cover, unless they are a standalone
  test-coverage effort — then they are their own `test(...)` commit.
- Mechanical sweeps (formatting, renames, lint fixes) go in their own commit so the
  substantive diff stays readable.
- Order commits so the tree builds and tests pass at each one, not just at the end.
