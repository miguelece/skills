# Audit workflow details

## Completion record

Keep the manifest resumable until every blocker is resolved. Add evidence entries
for local source locations, official external URLs with access dates, and
user-confirmed facts. Findings must identify category, severity, blocking state,
affected pages, evidence, resolution, and status. Verification entries must name
the command or inspection, scope, revision, and result.

## Archive coverage

Use the migration run directory as `--archive-root` and the target checkout as
`--repository-root`. The checker accounts for preamble content, ATX and Setext
sections, duplicate headings, fingerprints, dispositions, destination files,
and destination anchors. Retire unverifiable or unsafe legacy guidance with an
explicit reason instead of silently dropping it.

## Claim ownership

Examples of separate authorities:

- Routes and commands: live registration or entrypoint code.
- Request and response shapes: schemas or generated contracts.
- Configuration defaults: runtime configuration code.
- Deployment behavior: CI/CD and infrastructure configuration.
- Public behavior: reachable implementation, strengthened by passing tests.

If the declared authority is absent, keep the claim blocked. Do not ask the user
to decide facts that reachable repository evidence already establishes.

## Reports

Write `<run-id>-audit.md` with scope, baseline state, findings, resolutions,
verification, remaining blockers, and archive eligibility. Write
`<run-id>-code-findings.md` only for suspected implementation defects. Never
include secret values.
