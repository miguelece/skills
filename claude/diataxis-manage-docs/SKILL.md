---
name: diataxis-manage-docs
description: Use when asked to diagnose, assess, or decide documentation maturity, lifecycle, or recorded state and manage, orchestrate, or route Diataxis migration, audit or verification, and update or synchronization phases across a repository.
---

# Manage the Diataxis documentation lifecycle

Diagnose one documentation domain and route it through the minimum necessary
phase skills. This skill is a thin orchestrator: do not duplicate migration,
audit, or update implementation logic.

Read [references/routing-workflow.md](references/routing-workflow.md). Begin
read-only, present the proposed domain and phase sequence, and wait for approval.

## Preflight

- Require the target's own Git root and inspect status, instructions, docs roots,
  docs tooling, `.docs-migration/manifest.yaml`, archives, and reports.
- Discover every plausible documentation domain and canonical locale. When
  multiple coherent audiences exist, require the user to select exactly one.
  Never choose a monorepo domain merely because it has the clearest defect.
- Preserve non-overlapping dirty changes and record baseline failures.
- Treat suspected credential locations as blockers without copying values.
- Use repository evidence for discoverable facts. Do not escalate a code-explicit
  configuration value to an owner decision.
- Never write, edit code, commit, delete archives, or start a phase before the
  user approves the diagnosis and phase sequence.

## Diagnose state

Classify the selected domain:

- **Messy:** mixed/flat legacy docs, overlapping intent, stale source files, or no
  approved lifecycle manifest.
- **Migration in progress:** manifest/archive exists and migration or audit is
  incomplete.
- **Structured but unbaselined:** coherent Diataxis-style docs without a clean
  accuracy audit and full code-to-doc baseline.
- **Sparse:** little or no durable documentation.
- **Maintained:** valid manifest with clean audit and verified update baseline.

Repository folder names alone do not establish maturity. Manifest state,
archives, evidence, findings, and verification take precedence.

## Route phases

Use these exact routes:

| State | Sequence |
| --- | --- |
| Messy | `diataxis-migrate-docs` → `diataxis-audit-docs` → full `diataxis-update-docs` |
| Archive or incomplete audit | Resume `diataxis-audit-docs` → full `diataxis-update-docs` |
| Structured but unbaselined | `diataxis-audit-docs` → full `diataxis-update-docs` |
| Sparse | bootstrap `diataxis-update-docs` |
| Maintained | incremental `diataxis-update-docs`, or requested periodic full update |

Do not invent intermediate lifecycle phases. Do not advance past a blocking
finding. Unsafe or unverifiable archived guidance may be retired with an explicit
reason; it does not always require an owner decision.

## Plan and orchestration

1. Present selected domain, locale, maturity evidence, exclusions, baseline
   failures, blockers, proposed phase sequence, and approval gates. Shape that
   presentation, and every later phase report, per
   [references/report-form.md](references/report-form.md).
2. Wait for approval.
3. Invoke or instruct the applicable phase skill using the same
   `.docs-migration/manifest.yaml`. The phase skill performs its own read-only
   analysis and exact write-plan approval.
4. After each phase, validate manifest state and reports before routing the next.
   Never recreate the manifest or lose authorities, evidence, findings,
   verification, section ledger, archive state, or update baseline.
5. Stop when a phase is blocked. Report the blocker and required evidence rather
   than routing around it.
6. Finish with the current lifecycle state, completed reports, remaining
   periodic update recommendation, and archive outcome.

## Baseline failure counters

- Route messy docs through migration; do not append more facts to mixed pages.
- Resume an incomplete audit instead of restarting migration.
- A structured domain without a code baseline needs a full update after audit,
  not merely a targeted correction.
- Domain selection belongs to the user when multiple audiences are plausible.
- Use the shared manifest, not an issue, PR comment, or informal run record.
- A pre-existing test failure can be scope-limited; it neither justifies fixing
  code nor automatically blocks unrelated documentation planning.
