---
name: diataxis-update-docs
description: Use when asked to update, synchronize, compare, or sync Diataxis documentation with shipped public behavior or live behavior in code since a Git revision or baseline, fill missing or undocumented implementation gaps, or bootstrap sparse documentation from a live API.
---

# Update Diataxis documentation from code

Synchronize one documentation domain with reachable public and operational
behavior. Support a full baseline, a Git-incremental update, and sparse-repository
bootstrap. Discovery and planning are read-only; wait for approval before writes.

Read [references/update-workflow.md](references/update-workflow.md) before
planning. Use the shared manifest and helpers. Document what ships, not what a
proposal hopes will ship.

## Boundaries

- Require the target's own Git repository, one docs domain, and one locale.
- Cover public APIs, CLI/UI flows, configuration, security constraints,
  deployment and operations, extension points, and architecture behavior
  maintainers must understand. Do not document every private helper.
- A feature is eligible only when reachable from a real entrypoint. Tests improve
  confidence but are not mandatory. A schema, proposal, isolated function, or
  diff fragment alone does not prove reachability.
- Use claim-specific authorities and inspect current source, not only a supplied
  diff or handoff. Never ask the user to confirm facts established by reachable
  repository evidence.
- Report suspected code defects in findings; do not edit code.
- Preserve non-overlapping dirty files and never commit target changes.
- Treat suspected credentials as blocking and never reproduce their values.

## Choose the update mode

- **Incremental:** use the manifest's last verified update revision only when
  both revisions resolve and form a valid ancestry range in the target repo.
- **Full:** scan the complete documentation-relevant behavior surface. Use for
  the first baseline, periodic drift control, or whenever incremental history is
  missing, rewritten, invalid, or too incomplete to establish reachability.
- **Bootstrap:** when docs are sparse, perform a full scan and propose the
  minimum useful Diataxis foundation. Create the index, governance policy,
  migration/documentation ADR, and justified category folders. Do not create
  TODO pages or empty content stubs.

## Read-only update plan

1. Capture Git root, status, current revision, manifest state, docs tooling,
   native checks, and selected domain.
2. Validate the recorded baseline. If it is invalid, state the reason and switch
   to a full scan; never substitute an enclosing repository revision.
3. Inventory relevant entrypoints and follow wiring into schemas, configuration,
   services, security, deployment, and side effects. Separate reachable behavior
   from pending or unwired specs.
4. Compare behavior with canonical docs. Identify missing contracts, stale facts,
   affected how-to steps, explanatory gaps, broken references, and ADR-worthy
   decisions.
5. For sparse docs, propose substantive destination pages by reader intent.
   Empty taxonomy folders are allowed; placeholder pages are not.
6. Record probable code defects as durable findings with evidence. Do not write
   documentation that presents uncertain reachability as shipped.
7. Present exact creates/modifications, evidence, excluded proposals, checks,
   dirty-path protections, and baseline advancement rules. Wait for approval.

## Apply and verify

- Change only approved docs, navigation, governance, ADRs, manifest, and reports.
- Keep each factual contract canonically owned in one page; repeat brief context
  only where a procedure needs it.
- Draft architecture ADRs for user confirmation before writing inferred
  rationale. The documentation-lifecycle ADR is mandatory in bootstrap mode.
- Validate the manifest and repository links; run safe native checks. Execute
  non-destructive documented commands when prerequisites exist and inspect
  destructive, credentialed, deployment, production, and migration commands
  statically.
- Record evidence, findings, verification scope, baseline failures, and report
  paths. Do not mark complete while checks fail or blocking findings remain.
- Advance `update_baseline.revision` only to the verified current target-repo
  commit after documentation changes and all applicable checks pass.
- Write `<run-id>-update.md`; write `<run-id>-code-findings.md` when suspected
  implementation defects exist.

## Baseline failure counters

- Sparse bootstrap is not a README-only patch.
- An invalid incremental range triggers a full scan, not a guessed revision.
- A diff is a discovery aid, not the complete public contract.
- Do not document an endpoint while simultaneously saying its reachability is
  unverified.
- A pending proposal stays out of published docs even when it sits beside live
  code.
- Evidence, findings, verification, and next-baseline state are part of the
  update—not optional bookkeeping.
