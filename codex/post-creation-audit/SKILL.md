---
name: post-creation-audit
description: 'Close out a work session with a repo hygiene pass — confirm new behavior is tested at the right levels, update every document the change contradicted, and delete mid-development artifacts. Use when asked to "audit the session", "do a post-creation audit", "wrap this up", "run repo hygiene", or before finishing a block of work. It audits and stops by default: "/post-creation-audit +commit" also lands the session as clean commits, and "/post-creation-audit +git" adds merging, pushing, worktrees and pruning stale branches.'
---

# Post-creation audit

Close a work session properly: prove the new work is tested, bring every document
that went stale back into line, and remove what was only ever scaffolding.

## Invocation

The default audits, reports, and stops. The working tree is left exactly as it
was found.

| Flag | Adds |
| --- | --- |
| `+commit` | step 4 — splits the session into commits |
| `+git` | implies `+commit`, and adds step 5 — merge, push, worktrees, pruning |

`+git` implies `+commit` because a mode that merges and pushes but does not
commit is incoherent. An implication only ever adds; no flag ever switches
another off. Flags are an unordered set, so their order on the line means
nothing. The full rules, and the list of which skills take a parameter at all,
are in [references/invocation-grammar.md](references/invocation-grammar.md).

**The default changed, and this is the sentence that says so.** This skill used
to commit every time it ran. It no longer does. `+commit` asks for what an
unflagged invocation used to give you.

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

## 4. Commit — only with `+commit` or `+git`

Without one of those flags, stop after step 3. Report what the audit found and
leave the working tree as it is; the user commits at a moment they choose.

With the flag, split the session into commits following
[references/commit-convention.md](references/commit-convention.md). Read it and
follow it exactly.

Order matters: the audit's own corrections (tests, docs, cleanup) are part of the
work and get committed alongside it, grouped by kind rather than dumped into one
"address review" commit.

## 5. The rest of the git work — only with `+git`

`+git` covers five operations and no others: commit, merge, push, worktree
management, and pruning stale branches. **Rebases, tags, remote management,
stashes and submodules are out of scope by name** — a flag called `git` reads as
covering all of it unless the boundary is written down.

- **Merge.** Merge the session's branch into the branch it was headed for, and
  only when that is genuinely where it was headed. Fast-forward where the
  history allows it.
- **Push.** Push the branch to its remote. **Never force-push.** A push rejected
  as non-fast-forward is reconciled by fetching and integrating what is already
  there — never by overriding it.
- **Worktrees.** Remove a worktree that is finished with, then run
  `git worktree prune` to clear the administrative records of directories that
  no longer exist. Pruning those records deletes no work.
- **Prune stale branches.** Two different operations wear that name and only one
  is safe to do without asking:
  - **Remote-tracking refs whose upstream is gone** — `git fetch --prune`.
    This deletes no commits and no local branch. Do it.
  - **Local branches** — propose them and **ask before deleting any of them**,
    listing what you would remove and why each is safe.

**What a branch delete must never touch:** the current branch, the integration
branch, a branch checked out in another worktree, and any branch holding commits
that are not already contained in the integration branch. Use `git branch -d`,
which refuses an unmerged branch. **Never `git branch -D`**, which does not.

**Two ways the safe check misleads, both worth knowing before trusting it.**

`git branch --merged` answers relative to `HEAD` unless a base is named. Run it
as `git branch --merged <integration branch>`, or the answer changes with
wherever the session happens to be standing.

A branch that was **squash-merged** does not appear in `git branch --merged` at
all, so `-d` refuses it even though its work has landed. **Report it and leave
it.** Reaching for `-D` to get past that case is exactly how a branch with
genuinely unmerged work gets deleted by the same keystroke.

## Reporting the audit

Shape the report per [references/report-form.md](references/report-form.md).
The honesty rules below govern what may be claimed; that file governs the form
the claim takes — and its guardrails matter here, because a shortened audit
report is exactly where a "not checked" turns into silence.

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
- Do not commit without `+commit` or `+git`. The unflagged default audits and
  stops, and committing anyway is the subtraction working in reverse.
- Do not push without `+git`. Committing is not publishing, and the default does
  neither.
- Do not force-push, under any flag. `+git` adds a push, never an override of
  what is already on the remote.
- Do not delete a branch without proposing it and getting an answer, even under
  `+git`. It is the one operation here that can lose work.
- Do not turn that confirmation into a confirm-everything mode. Commit, merge
  and push do not ask; only deletion does, and the reason is that only deletion
  is irreversible.

## Resources

- What `+commit` and `+git` mean, how flags compose, and which skills take a
  parameter at all:
  [references/invocation-grammar.md](references/invocation-grammar.md)
- Commit format, type vocabulary, splitting rules, authorship:
  [references/commit-convention.md](references/commit-convention.md)
- Emphasis, headings, and what must survive a shortened report:
  [references/report-form.md](references/report-form.md)
