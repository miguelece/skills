---
name: diataxis-create-docs
description: Use when asked to create, write, or add new Diataxis documentation, either to bootstrap docs for a sparse repository with little or no documentation, or to add a single new page (a tutorial, how-to, reference, or explanation) to an existing docs tree.
---

# Create Diataxis documentation

Write new Diataxis documentation for one documentation domain: a single
requested page in an existing tree, or the first pages and foundation of a
sparse repository. Discovery and planning are read-only; wait for one approval
of the whole plan before any write.

Read [references/create-workflow.md](references/create-workflow.md) before
planning. Write each page from its template: `assets/tutorial.md`,
`assets/how-to.md`, `assets/reference.md` or `assets/explanation.md`. Use the
shared manifest and helpers.

## Boundaries

- Require the target's own Git repository, one docs domain, and one locale.
- Create new pages and the foundation a sparse domain lacks. Restructuring
  mixed legacy docs belongs to `diataxis-migrate-docs`, verifying them to
  `diataxis-audit-docs`, and synchronizing existing pages with code to
  `diataxis-update-docs`. When a request needs one of those, say which and stop
  rather than doing that phase's work here.
- Use repository-native taxonomy names when the docs tooling already defines
  them. Do not add a Diataxis folder beside an existing equivalent.
- Report suspected code defects in findings; do not edit code.
- Preserve non-overlapping dirty files and never commit target changes.
- Treat suspected credentials as blocking and never reproduce their values.

## What justifies a page

**A page's existence may rest on author intent.** A user asking for the page is
reason enough to write it, and so is a tutorial or explanation chosen for
teaching. Reachable behavior is not required to justify that a page exists.

**Its content may not rest on intent.** Every factual claim about the system
anchors to reachable code: name the file and symbol. Design rationale is
attributed to a recorded decision or explicitly to the author, never stated as
an established fact without one of them.

A claim that cannot be anchored is not written as shipped behavior. Report it
as an excluded claim with its reason, or, when the code looks unwired or wrong,
record it as a suspected code finding with file and symbol evidence. Decide
this from the repository; do not ask the user to settle what the code answers.

## Choose the create mode

- **Single page:** a request names one page or one subject. Classify its type,
  place it, anchor it, and plan it.
- **Bootstrap:** the domain has little or no durable documentation. Perform a
  full scan, choose the first pages by the fixed order below, and propose them
  with the foundation.

A request for one page in a sparse domain is a single page. Mention that the
domain is sparse and that bootstrap exists; do not widen the request into one.

## Single page

1. Capture Git root, status, current revision, manifest state, docs tooling,
   taxonomy, native checks, and selected domain.
2. Classify the page by the reader's need: a lesson is a tutorial, a task is a
   how-to, facts to look up are reference, and understanding is explanation.
   When the request mixes types, propose the dominant one and name the rest as
   separate pages rather than blending them.
3. Place it in the repository's taxonomy. Find the canonical owner of each fact
   the page needs; link to an existing owner rather than restating it.
4. Gather an anchor for every factual claim, and attribute every piece of
   rationale, per *What justifies a page*. Note any existing page that
   contradicts the code.

## Bootstrap

Choose first pages in this order. Consider every candidate in a step before
moving to the next:

1. **A reference page for each public entrypoint** a reader can reach.
2. **One getting-started tutorial** that takes a newcomer through the main path.
3. **How-to pages for operational tasks** the code supports: configuration,
   deployment, recovery.
4. **Explanation pages for recorded decisions**, from ADRs or comments that
   state why.

Each candidate is kept or dropped with a stated reason. The order is fixed; the
count follows the repository. A step can end with no page kept, and that is
recorded with its reason rather than filled.

Propose the foundation alongside the kept pages: a docs landing index that
routes by reader need, a governance policy from
`assets/documentation-governance.md`, and a documentation-lifecycle ADR from
`assets/diataxis-migration-adr.md`. Create a category folder only for a kept
page or when the approved structure requires it, using `.gitkeep` rather than a
stub. Do not create TODO pages or empty content stubs.

## Present the plan

Present exact creates and modifications, each page's type and placement, its
anchors, the excluded claims and dropped candidates with their reasons,
contradictions found in existing pages, findings, checks, dirty-path
protections, and manifest changes. Shape that presentation per
[references/report-form.md](references/report-form.md); the excluded claims,
dropped candidates and their reasons are the part a shortened report loses.

Wait for one approval of the whole plan. Do not ask page by page.

## Apply and verify

- Write only the approved pages, navigation, governance, ADRs, manifest, and
  reports.
- Keep each factual contract canonically owned in one page.
- Draft architecture ADRs for user confirmation before writing inferred
  rationale. The documentation-lifecycle ADR is mandatory in bootstrap mode.
- Validate the manifest with `scripts/validate_manifest.py` and repository
  links with `scripts/check_links.py`; run safe native checks. Execute
  non-destructive documented commands when prerequisites exist.
- Record evidence, claim authorities, findings, and verification in the shared
  manifest. Do not mark complete while checks fail or blocking findings remain.
- Write `<run-id>-create.md`; write `<run-id>-code-findings.md` when suspected
  implementation defects exist.

## Baseline failure counters

- A creation request is not a synchronization run: do not spend it validating
  an update baseline it never asked about.
- Sparse bootstrap is not a README-only patch.
- Reasons for a dropped page belong in the plan, not only in the agent's own
  reasoning.
- An example value the author chose is labelled as the author's choice.
- A question the repository answers is not a question for the user.
- Present the plan before writing, even for one page.
