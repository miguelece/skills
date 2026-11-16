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
from `account_attempt.py --match-rate`>. A rate near zero means the price
table is stale. "Not applicable: no supervisor ran" for any other batch.

### Remediation commits

| Commit | Kind | Findings | Suite | Test check | Kept |
| --- | --- | --- | --- | --- | --- |
| <sha> | consolidation | F<n>, F<n> | passed | clean | yes |
| <sha> | removal | F<n> | failed: <summary> | - | reverted by <sha> |

### Findings

| ID | Item | Task | `file:line` | Finding | Class | Status |
| --- | --- | --- | --- | --- | --- | --- |
| F<n> | D<n> | <task> | <path>:<line> | <one line> | structural | committed <sha> |
| F<n> | D5 | <task> | <path>:<line> | <one line> | report | patch: .tranche-gate/patches/F<n>.patch |
| F<n> | D6 | <task> | <path>:<line> | <one line> | report | reported |

- At most 32 rows. Verified findings not reported: <n>, by item.
- Dropped on verification: <n>.
- Findings per changed line: <findings / changed lines>; raw: <n>.
- Not checked: no criteria: D5 and D7 for <task ids>, or "none".

### Guidance candidates

- D<n>, found in two or more tasks: <task ids>; <file:line, file:line>.

### Proposals

- <a defect outside D1 to D12>: <evidence, file:line>. For the owner to add to
  the checklist or not; never remediated.
```

Write "None" under a heading with nothing in it rather than dropping the
heading: the owner, and anything that later collects gate reports, reads the
same parts in the same place every time.
