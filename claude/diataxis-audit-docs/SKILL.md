---
name: diataxis-audit-docs
description: Use when asked to audit, verify, or check migrated or structured Diataxis documentation against authoritative code and archived sources for section coverage, migrated/retired/blocked dispositions, factual drift or contradictions, a broken link, and a suspected secret or credential.
---

# Audit Diataxis documentation

Prove that one structured documentation domain is accurate, complete, navigable,
and safe. Audit discovery is read-only. Present a concrete remediation plan and
receive explicit approval before changing docs, reports, manifests, or archives.

Read [references/audit-workflow.md](references/audit-workflow.md) before starting.
Use the bundled manifest schema and helper scripts. Never treat a passing parser
or a plausible explanation as proof of audit completion.

## Boundaries

- Require the target's own Git repository and select one docs domain and locale.
- Preserve non-overlapping dirty files; stop if planned writes overlap them.
- If `.docs-migration/manifest.yaml` exists, resume it. Never replace an
  incomplete run with a fresh history. If no manifest exists, propose a baseline
  audit manifest and obtain approval before creating it.
- Audit documentation only. Report suspected code defects with evidence; do not
  edit application code or commit target-repository changes.
- Use claim-specific authorities. Code, schemas, configuration, tests, generated
  contracts, and official external sources may own different claims. Local
  behavior wins over external documentation.
- Treat any credential-shaped value in published docs as a blocking
  suspected-secret finding even when labeled fake. Record only its location and
  category; never reproduce the value in plans or reports.
- Unreachable proposals and pending specs are not shipped behavior.
- Do not reorganize the taxonomy during an audit unless the approved remediation
  explicitly includes a separately justified migration.

## Read-only audit plan

1. Capture Git root, revision, status, docs tooling, navigation, redirects,
   configured checks, baseline failures, and the selected domain.
2. Validate the manifest when present. Confirm archive state, run status,
   approved policies, evidence, findings, verification history, and section
   ledger semantics.
3. Build or verify the authority map by claim category. Never choose a value by
   majority agreement between stale pages.
4. With an archive, run section coverage and require every meaningful section to
   be `migrated`, `retired` with reason, or `blocked` with reason. Verify migrated
   destination files and anchors. Without an archive, inventory the current docs
   as the audit baseline.
5. Check dominant Diataxis intent, canonical factual ownership, harmful
   duplication, factual contradictions, pending-feature leakage, unsafe
   commands, suspected secrets, all repository-local links, navigation, and
   supported redirects.
6. Run repository-native docs checks when safe. If a configured check is missing
   or already failing, record its exact scope and run an applicable bundled
   check instead; do not claim broader verification.
7. Present findings and a concrete remediation plan listing every affected path,
   proposed claim resolution, ledger disposition, verification command, dirty
   path protection, and whether any blocker requires user evidence.
8. Wait for explicit approval before any write.

## Remediate and verify

- Update only approved documentation, navigation, redirects, manifest fields,
  and reports. Do not guess unresolved facts.
- Keep material unknowns, credential exposure, unaccounted sections, failed
  checks, broken links, and destination mismatches as blocking findings.
- Record evidence and resolution for each finding. Brief repeated context is
  allowed, but designate one canonical owner for each factual contract.
- Run:

```text
scripts/validate_manifest.py --schema references/manifest.schema.yaml --manifest <manifest>
scripts/check_coverage.py --manifest <manifest> --archive-root <archive-run> --repository-root <repo>
scripts/check_links.py --root <repo> --docs <docs-domain> [--redirects <file>]
```

- Re-run applicable native docs checks, inspect the final diff, confirm unrelated
  dirty-file hashes, and require every verification result to pass.
- Mark an audit complete only with no blocking/open findings and complete
  evidence and verification records.

## Archive decision

A clean audit makes the archive eligible for a second, explicit decision. Ask
whether to delete or retain it. Retention is the default. Before deletion,
resolve the absolute archive path and prove it is inside
`.docs-migration/archive/`; record deletion approval and outcome. Never infer
deletion approval from the original migration request.

## Baseline failure counters

- Findings are not a remediation plan. List exact writes and wait for approval.
- A fake sentinel in published docs is still a suspected-secret blocker.
- "Audit complete" is false while any material claim is unresolved.
- A dirty worktree is not automatically fatal; isolate non-overlapping changes.
- Markdown link success is not enough when navigation, redirects, commands,
  destination anchors, or native docs checks remain unverified.
