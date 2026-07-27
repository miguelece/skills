# Adopt Diataxis for repository documentation

## Status

Accepted

## Date

Recorded in `.docs-migration/manifest.yaml`.

## Context

The previous documentation mixed learning, task, lookup, and explanatory content.
That made navigation difficult, duplicated facts, and allowed claims to drift from
the implementation.

## Decision

Organize documentation by dominant reader intent using Diataxis or the
repository's existing equivalent taxonomy. Preserve the migration source,
section-level dispositions, claim authorities, approvals, and verification
evidence in `.docs-migration/`.

## Consequences

- Each durable page has one dominant intent and one canonical home.
- Existing site conventions are adapted instead of replaced mechanically.
- Moved paths require updated inbound links and supported redirects.
- Pending specifications and unverified behavior remain unpublished.
- Archived originals remain available through the post-migration audit.

## Related records

- `.docs-migration/manifest.yaml`
- `documentation-governance.md`
