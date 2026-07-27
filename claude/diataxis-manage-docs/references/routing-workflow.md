# Routing workflow details

## Delegation contract

Pass the selected Git root, docs domain, locale, current manifest path, explicit
exclusions, baseline failures, and user-approved phase intent to the phase skill.
Do not pass conclusions that replace its evidence gathering.

Each phase writes its own report under `.docs-migration/reports/` and updates the
same manifest. The orchestrator reads the result before continuing.

## Resume precedence

1. A valid incomplete manifest outranks folder-shape inference.
2. A retained archive with unresolved coverage routes to audit.
3. A clean audit without an update baseline routes to a full update.
4. A verified update baseline permits incremental mode.
5. Invalid or missing incremental history falls back to a full update.

## Approval model

The orchestrator receives approval for domain and phase sequence. Every mutating
phase separately presents exact path changes and waits for approval. Archive
deletion always has its own final approval after a clean audit.
