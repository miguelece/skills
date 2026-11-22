---
sources:
  - id: ts-tsconfig
    title: "TypeScript: TSConfig Reference (strict, noImplicitAny, strictNullChecks, noUncheckedIndexedAccess, useUnknownInCatchVariables, skipLibCheck)"
    url: https://www.typescriptlang.org/tsconfig/
    date: 2026-11-21
  - id: ts-6-0
    title: "TypeScript 6.0 release notes: changed defaults"
    url: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html
    date: 2026-11-21
  - id: ts-everyday-types
    title: "TypeScript Handbook: Everyday Types (any, type assertions, the non-null assertion operator)"
    url: https://www.typescriptlang.org/docs/handbook/2/everyday-types.html
    date: 2026-11-21
  - id: ts-narrowing
    title: "TypeScript Handbook: Narrowing (type predicates, discriminated unions, exhaustiveness checking)"
    url: https://www.typescriptlang.org/docs/handbook/2/narrowing.html
    date: 2026-11-21
  - id: ts-3-7
    title: "TypeScript 3.7 release notes: assertion functions"
    url: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-7.html
    date: 2026-11-21
  - id: ts-lib-es5
    title: "TypeScript v5.9.3 standard library declarations, es5.d.ts (JSON.parse)"
    url: https://github.com/microsoft/TypeScript/blob/v5.9.3/src/lib/es5.d.ts
    date: 2026-11-21
  - id: ts-lib-dom
    title: "TypeScript v5.9.3 DOM library declarations, dom.generated.d.ts (Body.json)"
    url: https://github.com/microsoft/TypeScript/blob/v5.9.3/src/lib/dom.generated.d.ts
    date: 2026-11-21
  - id: tse-configs
    title: "typescript-eslint 8.73.0: Shared Configs"
    url: https://typescript-eslint.io/users/configs/
    date: 2026-11-21
  - id: tse-typed-linting
    title: "typescript-eslint: Linting with Type Information"
    url: https://typescript-eslint.io/getting-started/typed-linting/
    date: 2026-11-21
  - id: tse-no-explicit-any
    title: "typescript-eslint rule no-explicit-any"
    url: https://typescript-eslint.io/rules/no-explicit-any/
    date: 2026-11-21
  - id: tse-no-unsafe-assignment
    title: "typescript-eslint rule no-unsafe-assignment"
    url: https://typescript-eslint.io/rules/no-unsafe-assignment/
    date: 2026-11-21
  - id: tse-no-unsafe-member-access
    title: "typescript-eslint rule no-unsafe-member-access"
    url: https://typescript-eslint.io/rules/no-unsafe-member-access/
    date: 2026-11-21
  - id: tse-no-unsafe-type-assertion
    title: "typescript-eslint rule no-unsafe-type-assertion"
    url: https://typescript-eslint.io/rules/no-unsafe-type-assertion/
    date: 2026-11-21
  - id: tse-consistent-type-assertions
    title: "typescript-eslint rule consistent-type-assertions"
    url: https://typescript-eslint.io/rules/consistent-type-assertions/
    date: 2026-11-21
  - id: tse-no-non-null-assertion
    title: "typescript-eslint rule no-non-null-assertion"
    url: https://typescript-eslint.io/rules/no-non-null-assertion/
    date: 2026-11-21
  - id: tse-ban-ts-comment
    title: "typescript-eslint rule ban-ts-comment"
    url: https://typescript-eslint.io/rules/ban-ts-comment/
    date: 2026-11-21
  - id: tse-unknown-in-catch-callback
    title: "typescript-eslint rule use-unknown-in-catch-callback-variable"
    url: https://typescript-eslint.io/rules/use-unknown-in-catch-callback-variable/
    date: 2026-11-21
  - id: tse-switch-exhaustiveness
    title: "typescript-eslint rule switch-exhaustiveness-check"
    url: https://typescript-eslint.io/rules/switch-exhaustiveness-check/
    date: 2026-11-21
  - id: google-ts-style
    title: "Google TypeScript Style Guide (type assertions, non-null assertions, any, ts-ignore)"
    url: https://google.github.io/styleguide/tsguide.html
    date: 2026-11-21
  - id: tse-no-unsafe-type-assertion-source
    title: "typescript-eslint v8.73.0 no-unsafe-type-assertion rule source and tests (type-parameter targets)"
    url: https://github.com/typescript-eslint/typescript-eslint/blob/v8.73.0/packages/eslint-plugin/src/rules/no-unsafe-type-assertion.ts
    date: 2026-11-22
findings:
  - id: strict-family-is-opt-in
    claim: >-
      The compiler's strongest checks are a family switched on by `strict`,
      which includes `noImplicitAny`, `strictNullChecks` and
      `useUnknownInCatchVariables`, and each member can be turned off
      beneath it. Without `strictNullChecks`, `null` and `undefined` are
      ignored by the type system; without `noImplicitAny`, a type the
      compiler cannot infer silently becomes `any`.
    confidence: evidenced
    sources: [ts-tsconfig]
  - id: strict-default-depends-on-the-compiler
    claim: >-
      TypeScript 6.0 changed the default of `strict` from false to true, so
      a configuration that leaves `strict` unset is strict under 6.0 and
      later and not strict under 5.x. Whether an unset `strict` is a defect
      therefore depends on the compiler version the project resolves.
    confidence: evidenced
    sources: [ts-6-0, ts-tsconfig]
  - id: unchecked-indexing-is-outside-strict
    claim: >-
      `noUncheckedIndexedAccess` is not part of the `strict` family, and
      without it a read through an index signature is typed as present, so
      a missing key reaches code that was never made to handle `undefined`.
    confidence: evidenced
    sources: [ts-tsconfig]
  - id: any-disables-checking
    claim: >-
      `any` turns type checking off for the value it types: any property
      can be read, any call made and any assignment accepted. Current
      guidance is to describe a known shape with a type and an unknown one
      with `unknown`, which must be narrowed before use, keeping `any` as a
      justified, commented last resort.
    confidence: strong
    sources: [ts-everyday-types, tse-no-explicit-any, google-ts-style]
  - id: any-propagates
    claim: >-
      An `any` spreads through assignment, member access, calls and returns,
      including when hidden in a generic argument, so one untyped value
      leaves unchecked code far from where it entered; typescript-eslint's
      `no-unsafe-*` rules exist to make those flows visible and need the
      project's type information to see them.
    confidence: evidenced
    sources: [tse-no-unsafe-assignment, tse-no-unsafe-member-access, tse-typed-linting]
  - id: boundary-apis-return-any
    claim: >-
      The standard declarations type the commonest entry points for outside
      data as `any`: `JSON.parse` returns `any` and the fetch body's
      `json()` returns `Promise<any>`, so data from a request, a file or a
      message is unchecked unless the code checks it.
    confidence: evidenced
    sources: [ts-lib-es5, ts-lib-dom]
  - id: assertions-have-no-runtime-effect
    claim: >-
      A type assertion, `as T`, is erased at compile time and checks
      nothing when the code runs, so a wrong one neither throws nor yields
      `null`; an assertion that narrows a type bypasses the checker, and a
      type guard or a runtime check is the recommended replacement.
    confidence: strong
    sources: [ts-everyday-types, tse-no-unsafe-type-assertion, google-ts-style]
  - id: type-parameter-assertions-are-unsafe
    claim: >-
      typescript-eslint's `no-unsafe-type-assertion` reports an assertion to
      a type parameter on purpose, with one message for an unconstrained
      parameter and one for a value that only meets the constraint, since
      the parameter can be instantiated with a narrower subtype; its tests
      hold such assertions invalid and the rule takes no options. Google's
      guide treats every assertion as unsafe and asks for a comment saying
      why one holds. Neither, nor any source read, exempts a generic helper.
    confidence: evidenced
    sources: [tse-no-unsafe-type-assertion-source, tse-no-unsafe-type-assertion, google-ts-style]
  - id: double-assertion-escapes-the-relation-check
    claim: >-
      The compiler refuses an assertion between unrelated types, and
      asserting through `any` or `unknown` first, `x as unknown as T`, is
      the way around that refusal; Google's guide accepts it only with a
      sound, stated reason.
    confidence: evidenced
    sources: [ts-everyday-types, google-ts-style]
  - id: literal-annotation-over-assertion
    claim: >-
      Asserting an object literal to a type hides errors an annotation would
      report: an annotated literal is checked for missing and excess
      properties, an asserted one is not.
    confidence: strong
    sources: [tse-consistent-type-assertions, google-ts-style]
  - id: non-null-assertion-is-unchecked
    claim: >-
      The postfix `!` removes `null` and `undefined` from a type without any
      check and with no runtime effect, so when the assumption is wrong the
      code fails at run time; the sources prefer a check or optional
      chaining, and a stated reason where the assertion is kept.
    confidence: strong
    sources: [ts-everyday-types, tse-no-non-null-assertion, google-ts-style]
  - id: suppression-directives-hide-errors
    claim: >-
      `@ts-ignore` and `@ts-nocheck` suppress compiler errors and are
      discouraged by both sources. They split on `@ts-expect-error`:
      typescript-eslint's recommended setting allows it with a description,
      while Google's guide avoids it too.
    confidence: strong
    sources: [tse-ban-ts-comment, google-ts-style]
  - id: caught-values-are-unknown
    claim: >-
      A caught value can be anything thrown, so it should be `unknown` and
      narrowed before use; `useUnknownInCatchVariables` does that for a
      `catch` clause under `strict`, but a promise rejection callback's
      parameter stays `any` unless annotated.
    confidence: strong
    sources: [ts-tsconfig, tse-unknown-in-catch-callback, google-ts-style]
  - id: assertion-signatures-are-trusted
    claim: >-
      An assertion function, declared `asserts x is T` or `asserts x`, is
      trusted by the compiler: code after the call relies on the condition,
      and the function must throw when the condition fails for that to be
      true.
    confidence: evidenced
    sources: [ts-3-7]
  - id: type-predicates-are-author-checked
    claim: >-
      A user-defined type predicate, `x is T`, narrows by its return type
      alone, and the check is whatever its body does, so a body that does
      not test what the predicate claims narrows wrongly with no error.
    confidence: directional
    sources: [ts-narrowing]
  - id: exhaustiveness-is-checked-only-when-asked
    claim: >-
      A `switch` meant to cover every member of a union or enum silently
      misses a member added later unless a `never` assignment in its
      `default` or a lint rule makes the gap an error.
    confidence: strong
    sources: [ts-narrowing, tse-switch-exhaustiveness]
---

# Research: TypeScript type safety

Read on 2026-11-21 at each source's own page, the TypeScript handbook and
TSConfig reference first, then typescript-eslint's rule pages, with Google's
TypeScript style guide as the independent published guidance. Each `date` is
the reading date: the documentation pages are living and carry no
publication date. The TSConfig reference documents options up to TypeScript
6.0; typescript-eslint's pages are the 8.73.0 documentation. The two library
declaration files are cited at the `v5.9.3` tag, so the signatures quoted
stay where they were read.

## Reading, not running

The compiler and typescript-eslint report most of these mechanically, and
several of the rules need the project's type information to do it. This
module runs neither, because it serves the static phase: each check is
applied by reading, a compiler option or a lint rule is its reference and
never its mechanism, and a check that depends on a type reads the
declaration of that type wherever it lives. Whether a value can be `null`,
which members a union has, or what a called function returns is often
declared outside the changed lines, so for a diff the finding sits in the
changed lines while the declarations and the `tsconfig.json` chain it rests
on are read where they are.

## What this does not cover

Each of these was considered and left out, for the reason given.

- **`exactOptionalPropertyTypes`, `noImplicitOverride`,
  `noFallthroughCasesInSwitch` and `noImplicitReturns`.** The reference
  documents them, but their absence is a project's choice of strictness,
  not a defect a reading can quote; the module reports only the `strict`
  family, whose members the reference names, and the indexed read that
  `noUncheckedIndexedAccess` would catch, as a code finding.
- **`skipLibCheck`.** The reference marks it recommended and states its cost
  as a trade-off, so its presence is not a defect.
- **Unnecessary assertions.** typescript-eslint's rule flags them as clutter;
  an assertion that changes nothing does not make code less safe.
- **Assertion style, `as` against angle brackets.** A stylistic rule, with no
  safety consequence.
- **Method parameter bivariance.** `strictFunctionTypes` deliberately leaves
  method-syntax types bivariant, and the reference gives the DOM's types as
  the reason, so a method signature is not reported.
- **Runtime validation libraries.** The sources recommend a check at the
  boundary, not any one library, so the module accepts any visible check:
  a type guard, an assertion function or a schema parse.
- **Separate checks for each `no-unsafe-*` flow.** Calls, member access and
  returns on an `any` are the spread one `any` causes; the module reports
  where the `any` enters, under `explicit-any` or
  `untrusted-data-typed-without-validation`, rather than each use.
