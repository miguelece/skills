---
name: diataxis-migrate-docs
description: Use when asked to migrate, reorganize, or restructure existing messy, legacy, flat, or mixed documentation into Diataxis while preserving section coverage, source-to-destination traceability, fingerprints, and a durable ledger.
---

# Migrate existing documentation to Diataxis

Restructure one existing documentation domain without losing provenance, inventing
behavior, or touching unrelated work. Discovery and planning are read-only.
Writing starts only after the user approves the exact plan.

Read [references/lifecycle-workflow.md](references/lifecycle-workflow.md) before
planning or writing. Use the bundled manifest, governance, ADR, schema, and helper
scripts exactly as described there.

## Non-negotiable boundaries

- Require a Git repository. Read `git status`, resolve `HEAD` in the target
  repository itself, and record pre-existing test/build failures as baseline
  evidence. Never use an enclosing repository's revision for a nested target.
- Select exactly one documentation domain and one canonical locale per run.
  In a monorepo, stop for domain selection before proposing a write plan. Do not
  blend operator, developer, public-API, or other audiences.
- Exclude generated files, dependencies, vendored docs, build output, archived
  copies, and explicitly out-of-scope domains. Detect the repository's actual
  docs-site configuration before assuming folder names.
- Inventory dirty paths. Continue only when they do not overlap the approved
  migration paths; preserve unrelated dirty files byte-for-byte.
- Treat code, schemas, configuration, tests, and shipped operational definitions
  as claim-specific authorities. Record the authority map. Do not ask owners to
  decide facts already established by repository evidence.
- Exclude pending proposals and unreachable or unshipped behavior from published
  docs. Report suspected implementation defects; never edit application code.
- If a suspected credential appears, record only its location and category.
  Never copy the value into plans, reports, archives outside the protected run
  archive, or generated documentation. Block completion until resolved.
- Never commit target-repository changes.

## Read-only discovery and plan

1. Inspect Git root, revision, status, repository instructions, docs tooling,
   navigation, redirects, tests, source docs, and relevant implementation.
2. Discover all plausible docs domains. Select one, default locale to `en-US`
   when the repository declares no canonical locale, and state exclusions.
3. Build a claim-specific authority map. Resolve contradictions from the
   strongest reachable evidence; mark unresolved material claims blocked.
4. Parse every source Markdown/MDX document into level-two-or-deeper sections.
   Record source path, stable section ID, SHA-256 fingerprint, intended
   disposition (`migrated`, `retired`, or `blocked`), and destination.
5. Classify each destination by dominant reader intent:
   tutorial, how-to, reference, or explanation. Keep ADRs separate. Adapt
   equivalent custom taxonomies such as `learn/recipes/catalog/concepts`; do not
   create a parallel empty tree merely to rename folders.
6. Find tracked-text inbound links, docs navigation, and supported redirect
   configuration affected by each move.
7. Present one concrete plan listing every create, move, modify, retire, archive,
   redirect, and link-update path; baseline failures; blocked claims; dirty-path
   protections; verification commands; and bounded resumable batches. Shape that
   presentation per [references/report-form.md](references/report-form.md); it is
   long, it is what approval is given against, and none of its blockers may be
   compressed away.
8. Ask for explicit approval of that exact plan. Approval is required before
   creating `.docs-migration`, copying originals, changing a non-doc config file,
   or making any other write. A general request to "migrate the docs" is not
   approval of an undisclosed file list.

## Execute the approved migration

1. Create run ID `<UTC YYYYMMDDTHHMMSSZ>-<short HEAD>` and
   `.docs-migration/manifest.yaml`. Copy every in-scope original to
   `.docs-migration/archive/<run-id>/<original-relative-path>` before moving,
   rewriting, or deleting it. Keep originals through the later clean audit.
2. Populate approved policies, verified repository revisions, selected domain and
   locale, exclusions, dirty paths, authorities, section ledger, evidence,
   findings, verification, update baseline, and archive state. Keep status
   resumable after every batch.
3. Create or update the docs index, documentation governance page, taxonomy
   directories, and migration ADR. Empty taxonomy directories are allowed; use
   `.gitkeep` only when Git persistence is required. Never create placeholder
   content pages.
4. Migrate in bounded batches. Preserve useful facts, remove stale duplication,
   and keep brief contextual repetition only when it helps the reader complete
   the page's dominant intent.
5. Update all affected tracked-text inbound links, navigation configuration, and
   supported redirects within the approved scope. Do not silently modify
   application configuration such as `.env.example`; add it to a revised plan and
   obtain approval if a non-doc change is truly required.
6. Mark every archived section migrated, retired with a reason, or blocked with a
   reason. Do not delete source paths until the archive exists and coverage
   records are complete.

## Verify and hand off

- Run `scripts/validate_manifest.py`, `scripts/check_coverage.py`, and
  `scripts/check_links.py`; run safe repository-native docs checks too.
- Recheck Git status/diff, approved path scope, unrelated dirty-file hashes,
  redirects, navigation, suspected-secret blockers, and claim authorities.
- Record commands and results in the manifest. Do not mark the run complete while
  material claims, secrets, broken links/redirects, fingerprint mismatches, or
  unaccounted sections remain.
- Report created, modified, moved, retired, and blocked items plus baseline
  failures. Leave the archive retained and instruct the later audit phase to
  decide whether it is eligible for explicitly approved deletion.

## Baseline failure counters

- A proposed feature does not become explanation content. If code does not ship
  `signup_code` or an equivalent proposal, exclude it from user-facing docs.
- A prose source map or `docs/archive` is not the lifecycle record. Use the
  versioned manifest and `.docs-migration/archive`.
- A mention of "section coverage" is insufficient. Record every fingerprint and
  disposition, then run the checker.
- A custom taxonomy is not missing documentation. Map its intent and preserve
  working site routes.
- Correct domain selection is not enough. Also record `en-US` (or the selected
  locale), archive state, governance, authorities, approvals, and baseline
  evidence.
