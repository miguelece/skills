# What the gate changes, and what it reports

A refactoring changes how code does something, never what it does. Structure
changes are easy to reverse and behaviour changes are not, so the gate makes
the first kind alone and leaves the second to the owner. A green suite is not
proof on its own: a measurable share of LLM refactorings change behaviour and
still pass the existing tests.

## Committed without asking

Only behaviour-preserving cleanup of code the tranche introduced, after each
finding is verified against the code:

- **Consolidation**: a duplicate (D2, D3) or churned code (D1) condensed, when
  every caller is in the repository and moves in the same commit. Inlining a
  one-use helper (D7) is a consolidation.
- **Removal**: dead code (D4) tagged `private`, or tagged `check published
  use` in code that nothing published ships; and a test, only together with
  the code it tests.
- **Leftover cleanup**: scratch files, temporary files, debug output and
  commented-out code (D9), and comments that restate or contradict the code
  (D10), and a comment or docstring that cites a task id or an opaque label,
  rewritten to state the reason the reference carried (D13).
- **Convention fixes** (D11) that the repository's own linters or contract
  tests pin.

Leftover cleanup (D9) and convention fixes (D11) of what the tranche
introduced are committed even in a published skill's files, because removing
them restores the behaviour already published. Nothing reaches users before
the owner publishes.

**Where the touched code has thin tests**, pin its behaviour first with a
characterization test in the same commit, or report the change instead of
making it.

## Each commit

1. **Hold one kind of change per commit**: consolidation, removal, leftover
   cleanup or convention fix, never two. Label it with its kind and its finding ids,
   within the repository's commit convention. The gate's commits sit after
   the tranche tip as their own range.
2. **Re-verify it**: run the owning suite, then

   ```text
   scripts/check_test_changes.py --repo <path> --base <tranche tip> --tip HEAD \
       --declared .tranche-gate/declared.json
   ```

   where the declared list names each test a removal deleted with its
   subject, with that reason. A `blocked` verdict means a test changed that
   the commit did not mean to.
3. **On any failure, revert it** with `git revert --no-edit <sha>`, and report
   the finding with what failed. A failing commit is never fixed forward.

## Reported, not done

- Any change to a published skill's behaviour that predates the tranche: its
  `SKILL.md` or references, a bundled script's flags or output, or anything in
  a publish target.
- A task id or opaque label in published skill text (D13).
- A test deleted or weakened while its subject remains (D6).
- Any behaviour change: removing a feature or an option (D7), a changed
  failure path (D8), a dependency (D12).
- Dead code tagged `check published use` (D4) in code a published skill or
  package ships, which someone outside the repository may call.
- A consolidation that reaches into code older than the tranche, reported as
  pre-existing.

## Surplus verification (D5)

Report each surplus test, fixture, checker or script with its removal ready,
not applied:

1. Make the removal in the working tree.
2. Save it with `git diff -- <files> > .tranche-gate/patches/<finding>.patch`.
3. Restore the files with `git restore -- <files>`, and confirm the patch
   still applies with `git apply --check .tranche-gate/patches/<finding>.patch`.

The owner applies the patches they accept. A checker may be the only thing
pinning a behaviour, and removing even redundant tests loses coverage often
enough that the risk is theirs to take.
