---
name: task-board-init
description: Set up a file-based task board in a repository, or adopt an existing pile of planning and handoff documents into one by backfilling frontmatter and filing each by its blocker. Use when asked to "set up a task board", "initialize the board", "start tracking tasks in the repo", or to convert scattered task, spec, or planning markdown files into a structured board.
---

# Initialize a task board

Stand up a file-based task board inside a repository, or adopt an existing pile of
planning documents into one without losing what they already say.

Read [references/board-model.md](references/board-model.md) first. It defines the
frontmatter contract, the derived folder mapping, and the gate/status rule that
every other skill in this suite depends on. Do not invent a different state model
here.

## Boundaries

- The board lives inside the repository it describes, in scratch/planning space
  (`.scratch/task_board` by default). Confirm the location with the user before
  creating it. It is working material, not shipped documentation — check that the
  chosen path is gitignored, or ask whether it should be committed.
- Adoption is a **migration, not a rewrite**. Preserve every existing task's prose.
  You are adding frontmatter and moving files, not re-authoring specs.
- Never invent a task's history. If `created` cannot be recovered from the file, git
  log, or the document itself, ask rather than guessing a date.
- Do not set `status: scoped` on an adopted document just because it reads as
  finished. A document with unresolved questions is `draft` no matter how polished.
- One board per repository. If one already exists, this is a triage job — use
  `task-board-triage` instead.

## Fresh board

1. Confirm the board path and whether it is gitignored.
2. Create the board root plus the six derived folders: `completed/`,
   `manual-blocked/`, `owner-deferred/`, `task-blocked/`, `revisit/`,
   `superseded/`.
3. Write `README.md` with a short hand-written orientation section explaining what
   this board is for and where its conventions live, then the two index markers:

   ```text
   <!-- BEGIN GENERATED INDEX -->
   <!-- END GENERATED INDEX -->
   ```

   `ARCHIVE.md` is created by the generator the first time a task completes; it
   carries the same markers and holds the history, so the README stays about live
   work however long the board runs.

4. Copy [assets/task.md](assets/task.md) to the board as `_template.md`. Both board
   scripts skip that name, so the copy costs nothing and is not indexed as a task.
   Do it rather than pointing at the bundled copy: the bundle lives at a
   machine-specific path outside the repository, so a board that only points at it
   stops describing its own format the moment someone else opens the repo.
5. Run both scripts to prove the empty board is valid:

   ```text
   scripts/validate_board.py --board <board>
   scripts/generate_index.py --board <board>
   ```

## Adopting existing documents

1. **Inventory first, change nothing.** List every candidate document, and for each
   record: its apparent state; what blocks it, classified as an action someone must
   perform (`manual`), a decision someone must make (`owner`), or another task on
   this board (`blocked-by`); and whether it has been replaced by a later document.
   Present this inventory and get it confirmed before writing.

   Expect a pile of legacy documents to carry ad-hoc status labels the board's
   vocabulary has no slot for. Those are usually a real distinction someone needed
   and had nowhere to put — read what each one meant before mapping it, rather than
   forcing it into the nearest bucket.
2. Recover dates from `git log --follow --format=%ad --date=short -- <file>` (first
   commit for `created`, last for `updated`). State which dates came from git and
   which the user must supply.
3. For each document, add frontmatter without touching its prose. Derive `status` and
   `gate` from the inventory, not from the document's own self-description — a
   `Status:` line that says "ready for implementation" while four questions are open
   is exactly the drift this board exists to remove.
4. Normalize the required headings (`Why this exists`, `Plan`, `Open questions`,
   `Owner`). Map existing sections onto them by renaming; add a heading with an
   explicit `_None recorded._` only where the document genuinely has nothing.
5. Mark each already-answered question in place with the literal token `RESOLVED`
   plus the date, rather than deleting it. The record of what was decided is worth
   more than a short list.
6. Give every finished document a one-line `outcome:`. Take it from what the
   document already says it did — this is a summarizing pass, not a fresh
   assessment, and it is what lets the archive index be generated rather than
   hand-maintained.
7. Move each file into the folder its frontmatter derives, using `git mv` so history
   survives.
8. Wire up cross-references: set `parent` (lineage) on anything split off another
   document, `blocked-by` on anything waiting for another task rather than a person,
   and both sides of every supersedes pair. Where the pile already has design docs
   with implementation slices under them, set `kind: spec` on the design doc and
   `part-of` on each slice (composition) — but do not manufacture a decomposition the
   source material does not already have.
9. Run the validator and fix findings until clean, then generate the indexes.

If the source material had a hand-maintained summary of finished work, that content
is now generated from `outcome`. Delete the hand-written per-task lines once the
archive index reproduces them — leaving both is how the drift starts again. Keep
the surrounding narrative: session retrospectives and the reasoning behind a
decision are not per-task lines and are not generated.

## Guardrails

- Do not create the board and populate it in one unreviewed pass. The inventory in
  step 1 is a checkpoint — present it and wait.
- Do not move a file with `mv` when the repository tracks it. Use `git mv`.
- Do not delete a superseded document. Set `status: superseded`, write
  `superseded-by`, and let it move to `superseded/`.
- Do not hand-write anything between the index markers. It will be overwritten.
- Do not report the board as initialized until `validate_board.py` exits clean. A
  board that does not validate on day one will not be trusted on day thirty.

## Resources

- The state model, folder mapping, and required sections:
  [references/board-model.md](references/board-model.md)
- Field-by-field contract: [references/task.schema.yaml](references/task.schema.yaml)
- Task template: [assets/task.md](assets/task.md)
