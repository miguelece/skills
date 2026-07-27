---
name: post-creation-audit
description: Close out a work session with a repo hygiene pass — confirm new behavior is tested at the right levels, update every document the change contradicted, delete mid-development artifacts, and land it all as clean commits. Use when asked to "audit the session", "do a post-creation audit", "wrap this up", "run repo hygiene", or before finishing a block of work.
---

# Post-creation audit

Close a work session properly: prove the new work is tested, bring every document
that went stale back into line, remove what was only ever scaffolding, and land it
all as clean commits.

## Boundaries

- This audits **what this session produced**. Establish that scope first with
  `git status` and `git diff`, and stay inside it. A session audit that turns into
  a repo-wide cleanup buries the work under unrelated churn.
- Audit before committing. The commit step is last because it is the record of
  everything the earlier steps corrected.
- Do not "fix" pre-existing problems you happen to notice. Note them, offer to
  raise them as tasks, and leave them alone.
- Do not delete anything you cannot prove is an artifact.

## 1. Tests

For every behavior this session added or changed:

- Is there a test that **fails without the change**? If it has never failed, it has
  proved nothing — make it fail deliberately, once, and confirm the reason.
- Are the levels right? Unit tests for logic and edge cases; integration tests for
  the seams the unit tests stub out. A feature covered only at one level has an
  untested half.
- Are the error paths covered, not just the happy path?
- Run the **full suite**, not the files you touched. Report the actual numbers.

State plainly what is untested and why, rather than implying uniform coverage.

## 2. Documentation

Walk this list explicitly and say which items needed no change — a silent list is
indistinguishable from a skipped one.

- **Architecture decisions** — did this session make one? A choice between real
  alternatives, with consequences, belongs in an ADR while the reasoning is fresh.
- **Explanations, how-tos, references** — anything the change contradicts.
- **`README.md`** — commands, structure, prerequisites.
- **`CLAUDE.md` / `AGENTS.md`** — facts and boundaries only. If a section has grown
  into a procedure, that is a signal it wants to be a skill instead.
- **`.gitignore`** — new artifact directories, scratch space, local config. After
  any change, re-check the tracked file count: a broad rule silently swallowing a
  needed fixture is a classic and invisible failure.
- **Config files** — `.yaml`, `.json`, `.toml`, lockfiles, CI workflows.
- **Follow-on work** — anything discovered and deliberately not done. Raise it as a
  task rather than leaving it in the conversation, where it dies.

## 3. Cleanup

Remove what was scaffolding for the session and is not scaffolding for the repo:

- Throwaway scripts, probe files, one-off fixtures, sample outputs.
- Commented-out code left "just in case". Git remembers it.
- Debug logging, temporary timeouts, hardcoded test values, skipped tests.
- Stray `__pycache__`, `.pytest_cache`, build output, editor backups.

For each candidate, confirm it is genuinely an artifact before deleting — check
whether anything imports or references it. When unsure, ask.

## 4. Commit

Split the session into commits following
[references/commit-convention.md](references/commit-convention.md). Read it and
follow it exactly.

Order matters: the audit's own corrections (tests, docs, cleanup) are part of the
work and get committed alongside it, grouped by kind rather than dumped into one
"address review" commit.

## Guardrails

- Do not report the audit passed on a section you did not actually walk. Say "not
  checked".
- Do not claim coverage you did not run. Paste the real result.
- Do not skip the full-suite run because the touched files pass.
- Do not update docs by asserting the new behavior without reading what the doc
  currently says — the contradiction you need to fix is usually a sentence you did
  not expect.
- Do not delete a file because it looks temporary. Prove it.
- Do not fold unrelated fixes into this session's commits.
- Do not push. Committing is in scope; publishing is the user's call.

## Resources

- Commit format, type vocabulary, splitting rules, authorship:
  [references/commit-convention.md](references/commit-convention.md)
