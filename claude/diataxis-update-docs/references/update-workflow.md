# Update workflow details

## Incremental discovery

Verify both commits with Git and confirm ancestry. Inspect changed entrypoints and
their dependencies, then search docs for affected concepts and canonical owners.
Changes in configuration, schemas, security, deployment, and generated contracts
can require documentation updates even when route files did not change.

If revisions are missing, history was rewritten, or the range cannot prove
reachability, record the issue and use full mode. Never advance the baseline from
an unverified range.

## Full baseline

Inspect documentation-relevant public and operational surfaces, existing docs,
navigation, and governance. Record which behavior classes were examined and any
scope-limited failures. Existing failing tests block only the claims they affect.

## Bootstrap minimum

Create:

- A docs landing index that routes by reader need.
- A governance policy defining taxonomy, authorities, and maintenance.
- A documentation-lifecycle ADR.
- Complete reference/how-to/explanation/tutorial pages justified by evidence.
- Category folders even when currently empty, if the approved structure requires
  them; use `.gitkeep` rather than stub pages.

## Finding policy

An unwired implementation is a suspected code finding, not published behavior.
Record file and symbol evidence without fixing it. An official external source
may clarify an external contract, but local runtime behavior remains authoritative.
