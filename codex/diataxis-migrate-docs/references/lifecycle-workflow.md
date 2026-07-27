# Migration lifecycle workflow

Use this reference for manifest mechanics and write sequencing. Keep all paths
repository-relative and traversal-free.

## Before approval

Perform only read operations. Verify the target's own Git root and `HEAD`; record
the porcelain status, selected documentation domain, locale, exclusions,
repository-native docs tooling, and any pre-existing failing checks. Hash every
dirty path that does not overlap the proposed work.

Build the plan from section-level inventory, not whole-file moves. Section IDs and
fingerprints must match `scripts/check_coverage.py`: meaningful content before
the first section is `__preamble__`; ATX or Setext headings are occurrence-
qualified (`setup`, `setup-2`); fenced-code headings are ignored. Run coverage
with both `--archive-root` and `--repository-root` so migrated destination files
and anchors are verified.
including the heading and content through the next heading of equal or higher
rank, normalized to LF, stripped, terminated by one LF, and SHA-256 encoded as
`sha256:<lowercase hex>`.

## First approved write

Copy `assets/manifest.yaml` to `.docs-migration/manifest.yaml` and fill it against
`references/manifest.schema.yaml`. Set:

- `run.id` to `<UTC YYYYMMDDTHHMMSSZ>-<short HEAD>`;
- `run.mode` to `migrate`, status to `in_progress`, and start time to UTC;
- repository revisions from the target repository itself;
- all pre-existing dirty paths;
- one `scope.docs_domain`, one locale, and explicit exclusions;
- `approved_policies.write_approved` true only for the exact accepted plan;
- archive retention to `retain`;
- one authority entry per material claim or tightly related claim family.

Create `.docs-migration/archive/<run.id>/`, preserving each source document at its
original repository-relative path. Set `archive.path` and `archive.status:
created`. Never flatten archive paths.

## Ledger and reports

Create one ledger entry per archived level-2-or-deeper section:

- `source_path`: path beneath the run archive, written once (for example
  `docs/LEGACY.md`, not `docs/docs/LEGACY.md`);
- `section_id` and exact source fingerprint;
- disposition and destination path/anchor, or a concise retirement/block reason.

Use `evidence` for inspected sources and baseline commands, `findings` for
contradictions, secrets, defects, and blocked decisions, and `verification` for
command/result records. These records may use repository-appropriate keys but
must not contain secret values.

Write `.docs-migration/reports/<run.id>-plan.md` and update it only with the
approved file list and batch boundaries. Store verification summaries beside it.
The manifest remains the machine-readable authority.

## Resumable batches

Before each batch, verify current status and dirty-path hashes. Limit a batch to a
coherent set of source sections and destinations. After it:

1. Update ledger dispositions and destinations.
2. Update inbound links, navigation, and redirects in that batch's approved scope.
3. Run manifest, coverage, and link checks.
4. Record verification and leave the manifest usable if interrupted.

Never infer approval for a new path from approval of an earlier batch.

## Completion

Completion requires a valid manifest, zero unaccounted or mismatched archived
sections, zero broken local links or redirect destinations, no unresolved
material claim or suspected-secret blocker, and a diff limited to approved paths.
Set `repository.current_revision` to the verified current `HEAD`; do not create a
commit. Set `update_baseline.revision` only when the migration's chosen lifecycle
policy defines it, then set completion time and status.

Keep the archive `retained`. A later clean audit and a separate explicit approval
are required before deletion.
