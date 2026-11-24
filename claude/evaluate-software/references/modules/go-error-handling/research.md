---
sources:
  - id: go-errors-pkg
    title: "Go standard library: package errors, go1.27.4"
    url: https://pkg.go.dev/errors
    date: 2026-11-23
  - id: go-fmt-errorf
    title: "Go standard library: package fmt, func Errorf, go1.27.4"
    url: https://pkg.go.dev/fmt#Errorf
    date: 2026-11-23
  - id: go-blog-errors-1-13
    title: "The Go Blog: Working with Errors in Go 1.13 (Damien Neil, Jonathan Amsterdam, 2019-10-17)"
    url: https://go.dev/blog/go1.13-errors
    date: 2026-11-23
  - id: go-effective-go
    title: "Effective Go: Errors, Panic and Recover"
    url: https://go.dev/doc/effective_go
    date: 2026-11-23
  - id: go-spec-panics
    title: "The Go Programming Language Specification: Handling panics"
    url: https://go.dev/ref/spec#Handling_panics
    date: 2026-11-23
  - id: go-faq-nil-error
    title: "Go FAQ: Why is my nil error value not equal to nil?"
    url: https://go.dev/doc/faq#nil_error
    date: 2026-11-23
  - id: go-wiki-code-review
    title: "Go Wiki: Go Code Review Comments"
    url: https://go.dev/wiki/CodeReviewComments
    date: 2026-11-23
  - id: google-go-best-practices
    title: "Google Go Style Guide: Best Practices, Error handling"
    url: https://google.github.io/styleguide/go/best-practices#error-handling
    date: 2026-11-23
  - id: errcheck
    title: "errcheck (kisielk/errcheck), README"
    url: https://github.com/kisielk/errcheck
    date: 2026-11-23
  - id: go-vet
    title: "Go command documentation: cmd/vet, go1.27.4"
    url: https://pkg.go.dev/cmd/vet
    date: 2026-11-23
  - id: vet-errorsas
    title: "golang.org/x/tools analyzer errorsas, v0.53.0"
    url: https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/errorsas
    date: 2026-11-23
  - id: vet-printf
    title: "golang.org/x/tools analyzer printf, v0.53.0"
    url: https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/printf
    date: 2026-11-23
  - id: vet-httpresponse
    title: "golang.org/x/tools analyzer httpresponse, v0.53.0"
    url: https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/httpresponse
    date: 2026-11-23
  - id: vet-unusedresult
    title: "golang.org/x/tools analyzer unusedresult, v0.53.0"
    url: https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/unusedresult
    date: 2026-11-23
findings:
  - id: errors-are-checked
    claim: >-
      A returned error is handled, returned or, in a truly exceptional case,
      turned into a panic, and is not discarded by assigning it to `_`.
      `errcheck` reports a call whose error result is neither assigned nor
      explicitly discarded, and with `-blank` one assigned to `_`, skipping
      a built-in list of standard library calls documented never to fail,
      and `fmt` by default.
    confidence: strong
    sources: [go-wiki-code-review, errcheck]
  - id: constructed-errors-are-used
    claim: >-
      `fmt.Errorf` and `errors.New` return a value and have no side effect,
      so discarding the result is always a mistake; `go vet`'s
      `unusedresult` analyzer reports it for both by default.
    confidence: evidenced
    sources: [vet-unusedresult, go-vet]
  - id: is-walks-the-chain
    claim: >-
      `==` against a sentinel error matches only an unwrapped error, while
      `errors.Is` matches the target anywhere in the error's tree and is to
      be used in preference to equality; a function documented to return an
      error wrapping a sentinel leaves callers to check it with `errors.Is`.
    confidence: strong
    sources: [go-errors-pkg, go-blog-errors-1-13, google-go-best-practices]
  - id: as-walks-the-chain
    claim: >-
      A type assertion or type switch on an error checks only the outermost
      error, while `errors.As`, and from Go 1.26 `errors.AsType`, finds the
      first error of the type in the chain; the errors package prefers them
      to a direct type assertion. Effective Go's type assertion example
      predates wrapping.
    confidence: strong
    sources: [go-errors-pkg, go-blog-errors-1-13, go-effective-go]
  - id: as-target-must-be-pointer
    claim: >-
      `errors.As` panics unless its target is a non-nil pointer to a type
      implementing `error` or to an interface type; `go vet`'s `errorsas`
      analyzer reports a target that is not, and a `*error` target.
    confidence: strong
    sources: [go-errors-pkg, vet-errorsas, go-vet]
  - id: wrap-verb-decides-inspection
    claim: >-
      `%w` in `fmt.Errorf` makes the result unwrap to its operand, so
      `errors.Is` and `errors.As` see it, while `%v` keeps only the text.
      The choice is whether callers get programmatic access: wrap with `%w`
      when callers should inspect the cause, and use `%v` to keep an
      implementation detail or a system boundary out of the API, since
      wrapping makes the wrapped error part of the API.
    confidence: strong
    sources: [go-blog-errors-1-13, google-go-best-practices, go-fmt-errorf]
  - id: wrap-verb-rules
    claim: >-
      `%w` is supported only by `fmt.Errorf` and functions that wrap it, and
      its operand must implement `error`; `go vet`'s `printf` analyzer
      reports `%w` in a `Printf`-like call, and, in files at Go 1.27 or
      later, a `%w` operand that is a pointer to an error type rather than
      the error type, which defeats `errors.Is`.
    confidence: strong
    sources: [go-fmt-errorf, vet-printf]
  - id: errors-not-matched-by-text
    claim: >-
      Callers should not tell errors apart by matching their string form;
      information a caller needs programmatically belongs in a sentinel or
      a structured error type, checked with `errors.Is` or `errors.As`.
    confidence: evidenced
    sources: [google-go-best-practices]
  - id: typed-nil-is-not-nil-error
    claim: >-
      An interface value is nil only when both its type and value are unset,
      so a nil pointer of a concrete error type returned as `error` is a
      non-nil error and the caller sees a failure that did not happen; a
      function returns an explicit `nil`, and declares `error` rather than a
      concrete type as its result.
    confidence: evidenced
    sources: [go-faq-nil-error]
  - id: check-error-before-using-result
    claim: >-
      The result returned beside an error is not valid until the error is
      checked; `go vet`'s `httpresponse` analyzer reports the common case,
      deferring `resp.Body.Close()` before the error check, as a latent nil
      dereference.
    confidence: evidenced
    sources: [vet-httpresponse, go-vet]
  - id: panic-is-not-error-handling
    claim: >-
      Ordinary error handling uses `error` results, not `panic`, and real
      library functions avoid it. A panic is acceptable to report API
      misuse, to mark unreachable code, during package initialization or in
      a `Must` function, and inside a package whose public API recovers it
      and returns an error.
    confidence: strong
    sources: [go-effective-go, go-wiki-code-review, google-go-best-practices]
  - id: recover-keeps-panics-inside-and-re-panics
    claim: >-
      A package that panics internally converts the panic into an error at
      its public API and re-panics any value that is not its own panic type;
      recovering every panic to avoid a crash is advised against, because
      the program's state may be corrupted.
    confidence: strong
    sources: [go-effective-go, google-go-best-practices]
  - id: recover-only-in-deferred-call
    claim: >-
      `recover` returns nil unless the goroutine is panicking and it is
      called directly by a deferred function; called anywhere else,
      including from a helper the deferred function calls, it stops nothing.
    confidence: strong
    sources: [go-spec-panics, go-effective-go]
  - id: do-not-log-and-return
    claim: >-
      A function that returns an error should not also log it, leaving the
      caller to decide; logging and returning produces duplicate log lines
      for one failure.
    confidence: evidenced
    sources: [google-go-best-practices]
  - id: no-in-band-errors
    claim: >-
      A function should not signal an error or a missing result with an
      in-band value such as `-1`, `""` or `nil`, which callers forget to
      check, but return an extra `error` or `ok` result. The source names
      the standard library's `strings` package, whose in-band values
      simplify string code, as an accepted trade-off against that general
      rule.
    confidence: evidenced
    sources: [go-wiki-code-review]
  - id: error-types-expose-their-cause
    claim: >-
      A custom error type that holds an underlying error exposes it to
      `errors.Is` and `errors.As` by implementing `Unwrap`, which builds the
      chain they walk; without it the cause is invisible to them.
    confidence: evidenced
    sources: [go-blog-errors-1-13, go-errors-pkg]
---

# Research: Go error handling

The findings above were read from the Go project's own documentation, the
errors and fmt packages, the specification, the FAQ, Effective Go, the Go
1.13 errors post and the Code Review Comments wiki, from the Google Go style
guide's error handling section, from the `errcheck` README and from four
`go vet` analyzers at golang.org/x/tools v0.53.0. Every page was read on
2026-11-23 against Go 1.27.4. A finding is `strong` where the language's
documentation and an independent source agree, or a specification states it,
and `evidenced` where one source states it directly.

## Reading, not running

`errcheck` and `go vet` carry several of these checks mechanically:
`errorsas`, `printf`, `httpresponse` and `unusedresult`. This module runs
none of them, because it serves the static phase: each check is applied by
reading the code, and a linter is a check's reference, never its mechanism.
The checks read production code, files not ending in `_test.go`; test code
is read by the Go testing module, which checks error comparisons in tests
itself. For a diff, a finding is in the changed lines, while the function a
call resolves to, a sentinel's declaration or a caller that inspects an
error is read where it lives, inside or outside the diff.

Two checks rest on the version of Go a package is built with, read from the
`go` line of the `go.mod` that holds it: equality against a sentinel and a
type assertion on an error are defects only where `errors.Is` and
`errors.As` exist, from Go 1.13. `errors.AsType`, from Go 1.26, is named as
an alternative and decides nothing. `go vet` reports a pointer `%w` operand
only in files at Go 1.27 or later, but the defect that operand causes does
not depend on the version, so that check reads none.

## Choosing between `%w` and `%v`

The Go 1.13 post and the Google guide agree that neither verb is the
default: `%w` makes the wrapped error part of the API, and `%v` is right at
a system boundary or for an implementation detail. A reading cannot tell
from one `fmt.Errorf` which the author meant, so the check on this finding
reports only the case with a visible consequence: a `%v` wrap whose cause a
caller then inspects with `errors.Is` or `errors.As`, which can never match.
Wrapping an implementation detail with `%w` is left out, because whether
the detail is meant to be API is the author's decision.

## What this does not cover

Each of these was considered and left out, for the reason given.

- **Error string form**, lowercase and without trailing punctuation, as the
  Code Review Comments and Effective Go advise. A style rule: a capitalised
  message misbehaves nowhere, so there is no defect a finding could be
  verified against.
- **Messages that repeat the cause or say only "failed to"**, and where
  `%w` sits in the message. Readability advice from the Google guide.
- **Indented error flow.** Layout advice with no defect behind it.
- **`errors.Join` and multiple `%w` operands.** Both are valid since Go
  1.20; no source names a misuse a reading could verify.
- **Returning `errors.ErrUnsupported` unwrapped.** The errors package
  advises wrapping it, but no source names a failure that follows.
- **`log.Fatal` against `log.Exit` at initialization.** Specific to the
  Google logging library.
- **Errors lost from goroutines**, and `errgroup` as the pattern that
  carries them back. A concurrency module reads goroutines and channels.
- **Error checks inside tests.** The Go testing module reads them.
