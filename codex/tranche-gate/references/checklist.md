# The tranche checklist

Thirteen items, closed for a tranche. The gate looks for these and nothing else.
A defect that fits none of them goes in the report as a proposal to add to the
list, with its evidence; it is not remediated.

*Scan* names a key of `scripts/scan_tranche.py`'s report. *Judged* means the
model decides, reading one task's chunk. The class says what
[remediation.md](remediation.md) does with a verified finding: *structural* is
committed without asking when it preserves behaviour, *report* is listed for
the owner.

| ID | Defect | How the gate finds it | Class |
| --- | --- | --- | --- |
| D1 | Churn: the same files or lines changed by several tasks, or lines added then removed inside the tranche | Scan `churn`: `files` two or more units changed, and `rewritten` lines | Structural, when condensing keeps behaviour |
| D2 | Reinvention: new code re-implementing a helper the repository already has, often in different syntax | Judged: each function the tranche added, matched against existing ones by name, signature and docstring | Structural, when every caller is in the repository |
| D3 | Copy-paste duplication across tasks, in code or Markdown | Scan `clones`: `python` groups and `text` windows of five meaningful lines | Structural |
| D4 | Dead or deprecated code: unused functions, arguments, modules, unreachable branches | Scan `dead_code`, each candidate tagged `private` or `check published use` | Structural if private; report if published |
| D5 | Surplus verification: tests, fixtures, checkers or scripts beyond the tasks' acceptance criteria | Judged against the criteria: test-to-source lines per task, and new test tooling no criterion names | Report, with its removal prepared as an unapplied patch |
| D6 | Weakened, skipped or deleted tests whose subject remains | `scripts/check_test_changes.py` over the range, always, with the merged attempts' declarations | Report, always |
| D7 | Over-building: one-use helpers, unrequested features, options or abstractions, a change far larger than its criteria | Judged against the criteria; a helper with one call site is a candidate | Inlining is structural; removing a feature is report |
| D8 | Defensive or error-masking code for cases that cannot happen: broad or bare `except`, fallbacks, needless validation | Judged: whether the guarded case is reachable | Report, since a failure path changes |
| D9 | Leftovers: scratch scripts, temporary files, debug output, commented-out code | Scan `leftovers`: `unreferenced_files` and `print_calls` | Structural, even in a published skill's files, when the tranche introduced it |
| D10 | Documentation and comments that contradict the code, restate it, or carry unresolved TODOs | Scan `markers`; judged: each changed document against the changed code | Comments structural; published skill text report |
| D11 | Drift from the repository's conventions, including a bad local pattern copied | The repository's own linters and contract tests; judged against its agent instructions and standards | Structural, even in a published skill's files, when the tranche introduced it; a recurring one is also a guidance candidate |
| D12 | Dependency and hard-coded-value hygiene: new or unpinned dependencies, absolute paths | The diff of every manifest and lockfile; a search of added lines for absolute home paths | Report |
| D13 | Task references: a task id in code, tests, manifests or skill text, or an opaque label (one or two capitals and one or two digits) used outside the document that defines it | Scan `task_refs`: `id` and `label` hits on added lines | Comments and docstrings structural, rewritten to state the reason the reference carried; published skill text report |

**D5 and D7 need criteria.** For a task with no `## Acceptance criteria`
section, write "not checked: no criteria" against both.

## Known false positives

Each was measured on real history when the scan was built. Expect them, and
dismiss each with its reason in the chunk notes, not in the report:

- **Print calls** in a command-line helper not named `main`; the scan
  recognises only `main` and the `__main__` block as entry points.
- **Unreferenced files** that are loaded by a glob, such as test scenario
  files, which no other file names.
- **Task labels** that are another kind of short code, such as an eval
  prompt id or a model name, in prose or a data file other than JSON; and
  this checklist's own item ids, cited from the gate's other files and
  scripts, which the scan reads as defined only here.
- **Clone groups** of shared boilerplate: the same imports, signatures or
  table headers in files that are meant to look alike.

One known miss goes the other way: a dead name that also appears in unrelated
text is not reported, because the scan searches for it as a token.

## Out of the list

- **Style and formatting.** Linters own them, and an unscoped reviewer
  manufactures work.
- **Correctness bugs.** Each stream was verified when it was integrated, and a
  bug review is a different tool's job.
- **Anything else found.** A proposal in the report, for the owner to add to
  the list or not.
