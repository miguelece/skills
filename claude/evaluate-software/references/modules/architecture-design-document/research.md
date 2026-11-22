---
sources:
  - id: sei-atam-collection
    title: "Architecture Tradeoff Analysis Method Collection (SEI, Carnegie Mellon University)"
    url: https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/
    date: 2026-11-21
  - id: sei-atam-report
    title: "ATAM: Method for Architecture Evaluation (CMU/SEI-2000-TR-004, Kazman, Klein, Clements)"
    url: https://www.sei.cmu.edu/library/atam-method-for-architecture-evaluation/
    date: 2000-08-01
  - id: arc42-quality-requirements
    title: "Specify quality requirements (arc42 Quality Model, revised March 2026)"
    url: https://quality.arc42.org/articles/specify-quality-requirements
    date: 2026-11-21
  - id: nygard-adr
    title: "Documenting Architecture Decisions (Michael Nygard)"
    url: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
    date: 2011-11-15
  - id: madr
    title: "MADR: Markdown Architectural Decision Records, 4.0.0"
    url: https://adr.github.io/madr/
    date: 2024-09-17
  - id: google-design-docs
    title: "Design Docs at Google (Malte Ubl)"
    url: https://www.industrialempathy.com/posts/design-docs-at-google/
    date: 2020-07-06
findings:
  - id: significance-is-structural
    claim: >-
      A decision is architecturally significant when it bears on the system's
      structure, its quality attributes, its dependencies, its interfaces or
      its construction techniques; that is the scope the decision checks
      apply to.
    confidence: evidenced
    sources: [nygard-adr]
  - id: quality-goal-needs-a-measure
    claim: >-
      A quality attribute becomes evaluable only when refined into a concrete
      scenario with a response and a measure of that response; a goal such as
      "fast" cannot be verified and is read differently by each stakeholder.
    confidence: strong
    sources: [sei-atam-collection, sei-atam-report, arc42-quality-requirements]
  - id: decisions-are-weighed-against-alternatives
    claim: >-
      A design records the options it considered and why the chosen one fits
      the goals better: design documents carry an alternatives section, and
      decision records list considered options and justify the outcome.
    confidence: strong
    sources: [google-design-docs, madr]
  - id: rejected-options-carry-reasons
    claim: >-
      Each rejected alternative can be brief, but the reason it was rejected
      is to be clear. MADR makes per-option pros and cons optional, so only
      the design-document practice states this outright.
    confidence: evidenced
    sources: [google-design-docs, madr]
  - id: consequences-include-costs
    claim: >-
      A decision record states its consequences, negative and neutral as well
      as positive, and architecture evaluation looks for exactly those costs,
      as trade-offs where one quality attribute is improved at another's
      expense and as risks.
    confidence: strong
    sources: [nygard-adr, madr, sei-atam-collection]
  - id: non-goals-bound-the-design
    claim: >-
      A design document lists non-goals, reasonable objectives deliberately
      excluded rather than negated goals, to make priorities clear and set
      readers' expectations.
    confidence: evidenced
    sources: [google-design-docs]
---

# Research: architecture in a design document

Read on 2026-11-21 at each source's own page: SEI's pages for the
Architecture Tradeoff Analysis Method, Nygard's post that introduced
architecture decision records, the MADR project page, the arc42 Quality
Model's article on quality requirements, and Malte Ubl's account of design
documents at Google. Each `date` is the source's publication date where the
page gives one, and the reading date otherwise.

The scenario structure, a stimulus, an environment, a response and a
response measure, is SEI's; the SEI collection page names stimulus and
response, and the arc42 article states the measure's role directly. The SEI
technical reports themselves are PDFs linked from their pages and were not
read in full.

## What this does not cover

- **Confirmation.** MADR has an optional section on how compliance with a
  decision is checked. A design written before code has nothing yet to
  confirm against, and the section is optional, so no check here asks for
  it; the code module beside this one reads confirmation where code exists.
- **Cross-cutting concerns.** The design-document practice also asks how a
  design handles security, privacy and observability. Only one source
  supports it here, and it is a concern of its own rather than of
  architecture's decision structure, so it is left for a module on that
  concept.
- **Risk judgement.** An architecture evaluation in the SEI sense judges
  whether a decision is sound for its scenarios, with stakeholders present.
  These checks only test whether the document records what such a judgement
  needs: they find a missing measure, alternative, reason or consequence,
  never a wrong decision.
