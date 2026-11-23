---
name: working-conventions
description: 'Standing working conventions that hold in every project: check the hardware budget before a resource-heavy run, check a runtime or package against current security advisories before running or installing it, research a question before putting it to the user, search for an existing helper before writing one, and add a test only for a failure nothing else catches. Use when about to launch a heavy run (a GPU model, a large batch job, a big build), before running a runtime or package manager or installing or fetching a package, before putting a question or decision to the user, and before writing a helper or adding a test.'
---

# Working conventions

Standing conventions that hold in every project. Each one governs a moment
the work reaches on its own, so check this list at that moment, not at the end.
Read the convention's reference file before acting; the line here only says
when it applies.

| Moment | Convention |
| --- | --- |
| Before a resource-heavy run: a GPU model, a large batch job, a big build | [references/hardware-budget.md](references/hardware-budget.md) |
| Before running a runtime or package manager, or installing or fetching a package | [references/tooling-advisories.md](references/tooling-advisories.md) |
| Before putting a question or decision to the user | [references/research-before-asking.md](references/research-before-asking.md) |
| Before writing a helper, a test helper or a fixture step | [references/reuse-before-writing-a-helper.md](references/reuse-before-writing-a-helper.md) |
| Before adding a test | [references/one-test-per-failure.md](references/one-test-per-failure.md) |

A repository's own instruction file overrides a convention here where the two
disagree, and can add to it; this skill holds only what transfers between
projects.

## Guardrails

- **Do not skip a check because the step looks small.** A one-line install
  or a quick run is where each of these goes wrong.
- **Do not act from memory of a convention.** Read its reference file at the
  moment it applies; the table only says when.
- **Do not launch, install or ask first and check afterwards.** Each check is
  worth something only before the step it guards.
- **Do not turn a check into a reason to change the system.** Updating
  system software, rotating credentials or changing a guardrail is the user's
  call, proposed, never done.

## Adding a convention

One convention is one file under `references/` and one row in the table above.
Write it in general terms: no machine, hardware totals, path, person or dated
incident, because the skill is shared and those are facts about one setup, not
conventions. Give it a *why* that says what goes wrong without it.
