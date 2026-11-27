---
sources:
  - id: martin-clean-architecture-adp
    title: "Clean Architecture, chapter 14: Component Coupling (Robert C. Martin)"
    url: https://www.oreilly.com/library/view/clean-architecture-a/9780134494272/ch14.xhtml
    date: 2026-11-21
  - id: archunit-guide
    title: "ArchUnit User Guide, 1.5.1"
    url: https://www.archunit.org/userguide/html/000_Index.html
    date: 2026-11-21
  - id: import-linter-contracts
    title: "Import Linter: contract types"
    url: https://import-linter.readthedocs.io/en/stable/contract_types/
    date: 2026-11-21
  - id: import-linter-layers
    title: "Import Linter: layers contract"
    url: https://import-linter.readthedocs.io/en/stable/contract_types/layers/
    date: 2026-11-21
  - id: dependency-cruiser-rules
    title: "dependency-cruiser: rules reference"
    url: https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md
    date: 2026-11-21
  - id: go-arch-lint
    title: "go-arch-lint: Golang architecture linter"
    url: https://github.com/fe3dback/go-arch-lint
    date: 2026-11-21
  - id: madr
    title: "MADR: Markdown Architectural Decision Records, 4.0.0"
    url: https://adr.github.io/madr/
    date: 2024-09-17
  - id: thoughtworks-fitness-function
    title: "Technology Radar: Architectural fitness function (Thoughtworks)"
    url: https://www.thoughtworks.com/radar/techniques/architectural-fitness-function
    date: 2017-11-30
  - id: ousterhout-aposd
    title: "A Philosophy of Software Design, second edition (John Ousterhout)"
    url: https://web.stanford.edu/~ouster/cgi-bin/aposd.php
    date: 2026-11-26
  - id: ousterhout-martin-discussion
    title: "A Philosophy of Software Design vs Clean Code (John Ousterhout and Robert Martin)"
    url: https://github.com/johnousterhout/aposd-vs-clean-code
    date: 2026-11-26
  - id: orosz-aposd-review
    title: "A Philosophy of Software Design: My Take (Gergely Orosz)"
    url: https://blog.pragmaticengineer.com/a-philosophy-of-software-design-review/
    date: 2023-10-27
  - id: fowler-remove-middle-man
    title: "Refactoring catalog: Remove Middle Man (Martin Fowler)"
    url: https://refactoring.com/catalog/removeMiddleMan.html
    date: 2026-11-26
  - id: refactoring-guru-middle-man
    title: "Refactoring.Guru: Middle Man"
    url: https://refactoring.guru/smells/middle-man
    date: 2026-11-26
  - id: fowler-legacy-seam
    title: "Legacy Seam (Martin Fowler)"
    url: https://martinfowler.com/bliki/LegacySeam.html
    date: 2024-01-04
findings:
  - id: dependencies-are-acyclic
    claim: >-
      The dependency graph between packages or components is to have no
      cycles, and the established structure checkers each offer that rule:
      ArchUnit's cycle check over slices, import-linter's acyclic-siblings
      contract and dependency-cruiser's circular rule.
    confidence: strong
    sources:
      - martin-clean-architecture-adp
      - archunit-guide
      - import-linter-contracts
      - dependency-cruiser-rules
  - id: layering-is-declared-not-inferred
    claim: >-
      Each layer checker judges imports against a layering someone declared:
      import-linter's ordered layers, ArchUnit's named layers and the access
      allowed to each, go-arch-lint's components and what each may depend
      on, dependency-cruiser's forbidden rules. None infers the layering from
      the code, so a layer violation exists only relative to a stated rule.
    confidence: strong
    sources:
      - import-linter-layers
      - archunit-guide
      - go-arch-lint
      - dependency-cruiser-rules
  - id: layers-depend-downward
    claim: >-
      In a layered contract a higher layer may import a lower one and a lower
      layer may not import a higher one; import-linter also counts an
      indirect chain through unlisted modules as a break.
    confidence: evidenced
    sources: [import-linter-layers]
  - id: decisions-name-their-confirmation
    claim: >-
      A decision record can say how compliance with it is confirmed, by
      review or by an automated architecture test, and an architectural
      fitness function is the objective, repeated check that keeps a stated
      characteristic from drifting. MADR makes the confirmation section
      optional, so its absence is a gap in practice, not a breach of a
      format.
    confidence: evidenced
    sources: [madr, thoughtworks-fitness-function]
  - id: forwarding-layers-are-shallow
    claim: >-
      A module is worth its interface when that interface is much simpler
      than what it does, and a method whose implementation is no more than
      its interface hides nothing. Ousterhout names a method that only
      passes its arguments to another with the same signature as a sign of
      a shallow layer; that naming is read here through a review of the
      book, because the book's text is not public.
    confidence: directional
    sources: [ousterhout-aposd, ousterhout-martin-discussion, orosz-aposd-review]
  - id: purposeful-delegation-is-kept
    claim: >-
      A class that only delegates is a middle man, and the refactoring is to
      remove it and call the delegate directly. Delegation is kept where it
      serves a purpose: a middle man that cuts a dependency between classes,
      one a pattern such as Proxy or Decorator creates on purpose, and a
      seam, where a test changes behaviour without editing the code that
      uses it.
    confidence: evidenced
    sources: [fowler-remove-middle-man, refactoring-guru-middle-man, fowler-legacy-seam]
---

# Research: architecture read from code

Read on 2026-11-21 at each source's own page. Each `date` is the source's
publication date where the page gives one, and the reading date for living
documentation pages that carry none. Martin's chapter is behind a login at
that address; its rule is cited there because that is where it is published,
and the tool documentation restates it as a checked rule, which is what
carries the finding to `strong`.

## Reading, not running

The tools above find cycles and layer breaks mechanically. This module runs
none of them, because it serves the static phase, which runs nothing: each
check is applied by reading the import lines, or, for the forwarding-layer
check, the function bodies, and a tool is a check's reference, never its
mechanism. Two consequences follow.

- **A reading sees direct imports.** Import-linter counts an indirect chain
  through unlisted modules as a layer break; a reading reports one only when
  it has followed and quoted every link of the chain.
- **Dynamic imports are not read as edges** unless their target is a literal
  in the line quoted.

## Function bodies, for one check

The module reads imports for every check but one. The forwarding-layer
check also reads the bodies of the functions it quotes, because whether a
layer only forwards is visible in its methods and nowhere in its imports.
Its sources were read on 2026-11-26. The book's page gives only the
edition's month and the joint discussion only the months it ran, so both
are dated by that reading; the discussion was read for its section on
method length.

- **Why the check is narrow.** Many thin layers exist on purpose, as a
  test's seam or a stable public surface, and reading one file cannot tell
  a purposeful layer from an empty one in general. The check survives only
  because its evidence can be shown: every method of the layer, whole,
  passing its own arguments on unchanged and returning the result
  unchanged, and the files read showing that no test substitutes it and
  the repository does not export it. A layer that adds validation,
  translation, error handling or a seam a test uses is no finding.
- **Why `directional`.** Ousterhout's account of pass-through methods is in
  a book whose text is not public, so it is read through a review, and the
  discussion with Martin shows that what counts as too shallow is argued
  over. The refactoring sources carry the narrower claim, that an
  only-delegating class is to be removed unless it serves a purpose, at
  `evidenced`.

## What this does not cover

- **Inferring a layering.** Because every checker works from a declared
  layering, the layer check reports nothing where the repository states
  none, rather than guessing one from directory names.
- **Metrics.** Instability and abstractness measures from the same body of
  component principles are not checks here; they rank designs rather than
  find a defect that can be quoted.
- **Shallowness in general.** A module whose interface is merely close in
  size to what it does, a method that forwards after a little work, and a
  chain of calls through several objects are judgements of degree, not a
  defect a reading can quote, so only the layer that does nothing but
  forward is checked.
- **Languages.** The triggers cover the manifests of Python, JavaScript or
  TypeScript, and Go; another language's repository does not load this
  module.
