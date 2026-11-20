# The gate report

The report is a section appended to the tranche record, after everything the
supervisor wrote and before the execution log, which stays last. With no
board it is the whole of `.tranche-gate/report.md` instead, opening with the
line `Uncommitted: this repository has no board.`

Fill it in this order. The owner reads the open entries first because they
block the next tranche; the rest is reviewed at leisure.

```markdown
## Gate report

- Gated: <date>; base <sha>, tip <sha>; gate commits <sha>..<sha>, or none.
- Size: <n> changed lines, against a declared limit of 4,000 (unmeasured).
- Record: <the supervisor's | filed by the gate | none, uncommitted>.

### Open escalation entries

- E<n>: <title>. <What it waits for, in one line.>
  Blocking first, oldest first. "None" when there are none.

### Candidate precedents

- E<n>: <the rule its answer set, in the owner's words>, applying to <tasks>.
  An answered entry whose answer sets a rule for more than one task.

### Match rate

<the record's `Match rate:` line, which the supervisor wrote at its close
from `account_attempt.py --match-rate`>: each called model's median ratio of
priced over billed cost. A median outside 0.90 to 1.02 means the price table
is stale; a billed model no transcript called is listed apart and flags
nothing. "Not applicable: no supervisor ran" for any other batch.

### Session costs

| Session | Attempts | Priced | Harness total | Ratio |
| --- | --- | --- | --- | --- |
| <session id> | <task> <n>, ... | <`priced_usd`> | <`recorded_usd` \| absent> | <`ratio` \| absent> |

Copied from the record's session table, which the supervisor printed at its
close with one `account_attempt.py --sessions <run-dir>/leases.md --project
<dir>` run over the lease table: each session's transcript-priced cost, the
harness total Claude Code recorded for it, and the ratio of the first over the
second. Attempt costs stay transcript-priced, not scaled. A session still
running at the close reads `absent`. "Not applicable: no supervisor ran" for
any other batch.

### Remediation commits

| Commit | Kind | Findings | Suite | Test check | Kept |
| --- | --- | --- | --- | --- | --- |
| <sha> | consolidation | F<n>, F<n> | passed | clean | yes |
| <sha> | removal | F<n> | failed: <summary> | - | reverted by <sha> |

### Findings

| ID | Item | Task | `path:name` | Finding | Class | Status |
| --- | --- | --- | --- | --- | --- | --- |
| F<n> | D<n> | <task> | <path>:<name> | <one line> | structural | committed <sha> |
| F<n> | D5 | <task> | <path>:<name> | <one line> | report | patch: .tranche-gate/patches/F<n>.patch |
| F<n> | D6 | <task> | <path> | <one line> | report | reported |

- At most 32 rows. Verified findings not reported: <n>, by item.
- Dropped on verification: <n>.
- Findings per changed line: <findings / changed lines>; raw: <n>.
- Not checked: no criteria: D5 and D7 for <task ids>, or "none".
- D6 declared: <test>, <change>, declared by <task>: <reason>; or "none".
- D6 declared, nothing matched: <each `declared_unmatched` entry>, or "none".

### Guidance candidates

- D<n>, found in two or more tasks: <task ids>; <path:name, path:name>.

### Proposals

- <a defect outside D1 to D12>: <evidence, path:name>. For the owner to add to
  the checklist or not; never remediated.
```

D6 comes from `scripts/check_test_changes.py` over base..tip. A deleted or
marked test a declaration matched is listed with the declaring task and its
reason, which its task-id prefix carries: one task's declaration matches by
test id, so it can explain a flag another task caused, and naming the task
lets the owner see that. An unmatched one is a finding, reported as
undeclared. Changed tests are the gate's to judge for weakening, as the
integrator judges them; a verdict's prose is context, not a pass. Every
`declared_unmatched` entry is listed, since it is a planned change that did
not happen as declared.

A finding cites `path:name`, or the bare file where no single name encloses
it, and never a line number: the report lands in a board task, which
`validate_board.py` checks under
[*Citations name things, never line ranges*](board-model.md#citations-name-things-never-line-ranges),
because a line number rots as soon as the gate's own commits move the code.

Write "None" under a heading with nothing in it rather than dropping the
heading: the owner, and anything that later collects gate reports, reads the
same parts in the same place every time.
