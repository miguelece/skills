---
name: diataxis-render-docs
description: Use when asked to render, convert, or export existing Diataxis Markdown documentation as interactive, readable HTML pages, either as a zero-token script build into a git-ignored directory or, on request, as hybrid pages enriched by the model and committed beside their Markdown, with a check that reports when an enriched HTML page has drifted from its source.
---

# Render Diataxis documentation as HTML

Render existing Diataxis Markdown pages as interactive HTML for reading. The
Markdown stays the source: this skill never edits it, and never edits
`.gitignore`. Two outputs exist, and the script render is the default:

- **Script render.** `scripts/render_html.py` turns a docs tree, or one page,
  into self-contained HTML in a git-ignored build directory. It spends no model
  tokens, is byte-reproducible, and is regenerated rather than committed.
- **Hybrid render, on request only.** The same script writes each page beside
  its Markdown with empty marked slots, and the model fills only those slots
  with a summary, callouts and inline SVG diagrams. The user commits the page.
  It costs model tokens, so it waits for a go-ahead.

Every page carries a table of contents, collapsible sections, a copy button on
each code block, light and dark themes, navigation across the four page types,
and a search index embedded in the page, so a page opened from disk fetches
nothing over the network.

## Boundaries

- Require the target's own Git repository and an existing docs tree. Writing,
  restructuring, verifying or synchronizing the Markdown belongs to the other
  Diataxis skills; when a request needs one of those, say which and stop.
- Never reword, drop or reorder source content in the HTML. The model's only
  writing surface is the marked slots of a hybrid page.
- Never reference anything over the network: no external script, stylesheet,
  font or image, and no `fetch`. Diagrams are inline SVG.
- Do not record HTML pages in `.docs-migration/manifest.yaml`; the embedded
  fingerprint is the hybrid page's record.
- Never commit target changes. Committing a hybrid page is the user's step.

## Script render

Run from the target repository:

```text
python scripts/render_html.py render <docs-root>
python scripts/render_html.py render <docs-root>/<type>/<page>.md
```

- The default build directory is `build/docs-html/` at the repository root;
  `--out <dir>` names another. Before writing, the script confirms with
  `git check-ignore` that git ignores it. **When it refuses (exit 2), report the
  line it names for `.gitignore` and stop**; adding the line is the user's
  decision, not this skill's.
- A page render takes its navigation from the whole tree (`--root <dir>` names
  the tree when it cannot be inferred) and writes that page only, so links to
  pages not yet rendered resolve after the next tree render.
- Page types come from the path: `tutorials/`, `how-to/`, `reference/`,
  `explanation/` and their common variants. Pages that match none are listed
  under *Other pages*.
- No go-ahead is needed: a script render spends no model tokens. Report the
  pages written and the build directory.

## Hybrid render

Only when the user asks for an enriched, summarized or illustrated page or
tree. Before rendering, **state the page count and a token estimate, then wait
for a go-ahead.** There is no fixed ceiling; the estimate and the go-ahead
replace one. Estimate per page from the measured hybrid medians, net of the
invocation's own overhead:

| Page size | Measured pages | Tokens per page |
| --- | --- | --- |
| Small, under about 1 KB | 138 to 194 bytes | 549 to 1,751 |
| Large, about 4 KB and over | 4 to 14 KB | 3,491 to 8,878 |

Give the tree's total as the sum of the per-page ranges. A page between the
tiers takes the span of both; a page far beyond 14 KB is outside what was
measured, so say so beside its estimate.

On the go-ahead:

1. Render with slots, per page or per tree:

   ```text
   python scripts/render_html.py render --slots <docs-root-or-page>
   ```

   Each page is written as `<page>.html` beside its Markdown, carrying the
   source's fingerprint in a `<meta name="diataxis-source-fingerprint">`
   element, computed by the same rule as `scripts/check_pages.py`. Its
   navigation links to sibling hybrid pages that exist, and otherwise to the
   sibling Markdown, so it never points into the ignored build directory.
2. Fill only the slots, each between its `<!-- BEGIN SLOT name -->` and
   `<!-- END SLOT name -->` markers: `summary` (two to four sentences of what
   the page already says), `diagram` (one inline SVG, or nothing when the page
   has no structure worth drawing) and `callouts:<section>` (a note or warning
   the section's own text supports). Leave a slot empty rather than add a
   claim the page does not make. Leave every marker and everything outside the
   slots exactly as the script wrote it.
3. Run the check and report its result:

   ```text
   python scripts/render_html.py check <docs-root>
   ```

A re-render of a hybrid page replaces its slots, so the model fills them again;
treat it as a new hybrid render, with its estimate and go-ahead.

## Hybrid drift

`check` reads every committed hybrid page under the docs root (a page whose
fingerprint `<meta>` is present) and fails, exit 1, on any of:

- **fingerprint drift**: the Markdown changed after the render;
- **a missing heading**: a source heading, `scripts/check_coverage.py`'s
  reading of the Markdown, is absent from the HTML;
- **a network fetch**: a remote script, stylesheet, image or frame, or a script
  that fetches.

Exit 0 means every hybrid page matches its Markdown. On drift, report each page
the check names and offer a fresh hybrid render of it, with its estimate, and
wait. Never edit the embedded fingerprint to make the check pass. Script output
in the build directory is never checked: it is regenerated, not maintained.

## Report

List the pages rendered and where they landed, the build directory's ignore
status or the line the refusal named, and for a hybrid render the estimate
given, the slots filled, and the `check` result with its exit code.
