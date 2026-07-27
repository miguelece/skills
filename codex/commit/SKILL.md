---
name: commit
description: Split the working tree into a clean series of conventional commits, each one coherent and revertible on its own, following this repository's type vocabulary and authorship rules. Use when asked to "commit", "commit this", "chunk the work into commits", or to write commit messages for the current changes.
---

# Commit

Split the working tree into a clean series of commits that each say exactly what
they changed.

The format, the type vocabulary, the splitting rules, and the authorship rule are
in [references/commit-convention.md](references/commit-convention.md). Read it and
follow it exactly; do not restate or reinterpret it here.

## Boundaries

- **Commit only. Never push.** Publishing is the user's call, and a push is not
  reversible the way a local commit is.
- Never record an agent as author or co-author. This is absolute — see the
  convention's Authorship section. If the tooling appends such a trailer by
  default, strip it.
- Do not amend or rebase existing commits unless asked. Add new ones.
- Do not commit on the default branch. If `git status` shows `main`, `master`, or
  `trunk`, stop and offer to branch first.
- Do not stage files you have not looked at.
- Never use `--no-verify`. If a hook fails, fix what it caught.

## Steps

1. **See the whole picture before staging anything.**

   ```text
   git status
   git diff
   git diff --staged
   git log --oneline -15
   ```

   Read the recent log for the repository's existing topic vocabulary. Match it
   rather than inventing new topics.
2. **Check for anything that must not be committed.** Credentials, tokens, `.env`
   files, large binaries, personal scratch material, editor state, and build
   output. If a secret is already tracked, stop and report it rather than quietly
   committing around it.
3. **Group the changes** into the smallest set of coherent commits, applying the
   splitting rules from the convention. Write the grouping down before staging.
4. **Stage and commit each group explicitly**, by path. Never `git add -A` a mixed
   tree — that is how unrelated changes get bundled.
5. **Verify.** `git log --oneline` and `git status` afterwards. The tree should
   hold only what you deliberately left uncommitted, and you should be able to say
   why for each remaining file.

## Guardrails

- Do not write a message that describes the session instead of the change. "update
  files after debugging" is not a commit message.
- Do not use `chore` as a catch-all for changes that are actually `fix` or `feat`.
- Do not bundle a refactor with a behavior change to save a commit.
- Do not add a body to a commit that could have been split.
- Do not report the work committed without running `git status` afterwards.
- Do not push, tag, or open a PR as part of this skill.

## Resources

- Format, type vocabulary, splitting rules, authorship:
  [references/commit-convention.md](references/commit-convention.md)
