# Documentation governance

## Purpose

This repository organizes durable documentation by reader intent. Keep each page
focused on one dominant purpose and make factual claims traceable to an
authoritative source.

## Information architecture

- `tutorials/` teaches a newcomer through a complete learning experience.
- `how-to/` or the repository's established equivalent gives task procedures.
- `reference/` provides precise, scan-friendly facts.
- `explanation/` provides context, rationale, and conceptual relationships.
- `adr/` records durable technical and documentation decisions.

Use repository-native names when tooling already defines an equivalent taxonomy.
Do not create pages merely to populate every category.

## Sources of truth

For each material claim, record the code, configuration, schema, test, or
operational source that owns it. Shipped behavior outranks stale documentation.
Pending proposals and unreachable implementation details are not user-facing
behavior.

## Change policy

1. Update the closest canonical page instead of adding a competing summary.
2. Update the documentation index and all tracked-text inbound links after moves.
3. Add redirects when the documentation platform supports them.
4. Keep generated output, vendored material, patch notes, and verification
   transcripts out of the durable taxonomy unless explicitly governed.
5. Never publish secrets. Document variable names and secure setup procedures,
   not credential values.
6. Record durable information-architecture decisions in an ADR.

## Verification

Before declaring documentation work complete, validate links and anchors, verify
material claims against their recorded authorities, and confirm that repository
changes remain inside the approved documentation scope.
