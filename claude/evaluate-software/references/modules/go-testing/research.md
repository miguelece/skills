---
sources:
  - id: go-testing-pkg
    title: "Go standard library: package testing, go1.27.4"
    url: https://pkg.go.dev/testing
    date: 2026-11-23
  - id: go-cmd-go
    title: "Go command documentation: Test packages (go test)"
    url: https://pkg.go.dev/cmd/go
    date: 2026-11-23
  - id: go-wiki-table-driven
    title: "Go Wiki: TableDrivenTests"
    url: https://go.dev/wiki/TableDrivenTests
    date: 2026-11-23
  - id: go-wiki-test-comments
    title: "Go Wiki: Go Test Comments"
    url: https://go.dev/wiki/TestComments
    date: 2026-11-23
  - id: go-blog-subtests
    title: "The Go Blog: Using Subtests and Sub-benchmarks (Marcel van Lohuizen)"
    url: https://go.dev/blog/subtests
    date: 2026-11-23
  - id: go-blog-loopvar
    title: "The Go Blog: Fixing For Loops in Go 1.22 (David Chase, Russ Cox, 2023-09-19)"
    url: https://go.dev/blog/loopvar-preview
    date: 2026-11-23
  - id: go-blog-b-loop
    title: "The Go Blog: More predictable benchmarking with testing.B.Loop (Junyang Shao, 2025-04-02)"
    url: https://go.dev/blog/testing-b-loop
    date: 2026-11-23
  - id: go-fuzz-doc
    title: "Go documentation: Go Fuzzing"
    url: https://go.dev/doc/security/fuzz/
    date: 2026-11-23
  - id: vet-testinggoroutine
    title: "golang.org/x/tools analyzer testinggoroutine"
    url: https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/testinggoroutine
    date: 2026-11-23
  - id: vet-tests
    title: "golang.org/x/tools analyzer tests, v0.53.0"
    url: https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/tests
    date: 2026-11-23
  - id: google-go-best-practices
    title: "Google Go Style Guide: Best Practices, Tests"
    url: https://google.github.io/styleguide/go/best-practices
    date: 2026-11-23
  - id: google-go-decisions
    title: "Google Go Style Guide: Style Decisions, Useful test failures and Test structure"
    url: https://google.github.io/styleguide/go/decisions
    date: 2026-11-23
  - id: gotest-tools-golden
    title: "gotest.tools/v3/golden, v3.5.2"
    url: https://pkg.go.dev/gotest.tools/v3/golden
    date: 2026-11-23
findings:
  - id: fatal-only-on-test-goroutine
    claim: >-
      `FailNow`, and so `Fatal` and `Fatalf`, must be called from the
      goroutine running the test; calling it does not stop other goroutines.
      The Google guide calls a `t.Fatal` from any other goroutine incorrect
      and advises `t.Error` and a return instead, and the `testinggoroutine`
      analyzer reports a `Fatal` called from a goroutine a test starts.
    confidence: strong
    sources: [go-testing-pkg, google-go-best-practices, vet-testinggoroutine]
  - id: loop-variable-per-iteration-since-1-22
    claim: >-
      Before Go 1.22 a `for` loop's variable was shared by every iteration,
      so parallel subtests that capture it all see its final value and the
      test passes without checking the cases it lists; the fix was a
      per-iteration copy, `tc := tc`. Go 1.22 gives each iteration its own
      variable, but only in packages of modules whose `go.mod` declares
      `go 1.22` or later, and a `//go:build` line can set it per file.
    confidence: strong
    sources: [go-blog-loopvar, go-blog-subtests, go-wiki-table-driven]
  - id: parallel-subtests-run-after-parent-returns
    claim: >-
      A subtest that calls `t.Parallel` is suspended until its parent test
      function returns, so code after the parent's loop and the parent's
      deferred calls run before the parallel subtests do. Teardown belongs
      after a wrapping `t.Run` group, which does not return until its
      parallel subtests complete, or in `t.Cleanup`, which runs once the
      test and all its subtests complete.
    confidence: strong
    sources: [go-blog-subtests, go-testing-pkg]
  - id: process-state-and-parallel-tests
    claim: >-
      Tests interact through global state, which makes them order-dependent
      and keeps them from running in parallel or being sharded, so a test
      resets any global state it modifies. Because the environment and the
      working directory are process-wide, `t.Setenv` and `t.Chdir`, which
      restore them, cannot be used in parallel tests or tests with parallel
      ancestors.
    confidence: strong
    sources: [google-go-best-practices, go-testing-pkg]
  - id: helpers-mark-themselves
    claim: >-
      `t.Helper` marks a function as a test helper, so a failure is
      reported at the caller's line rather than inside the helper; the
      Google guide and the Go Test Comments advise it for helpers that can
      fail a test, and not for one that cannot.
    confidence: strong
    sources: [go-testing-pkg, google-go-best-practices, go-wiki-test-comments]
  - id: keep-going
    claim: >-
      A test should generally report every mismatch rather than stop at the
      first: prefer `t.Error`, and in a table loop without subtests use
      `t.Error` and `continue`; `t.Fatal` fits setup failures, or inside a
      subtest, where it ends only that case.
    confidence: strong
    sources: [google-go-best-practices, google-go-decisions, go-wiki-test-comments]
  - id: fuzz-target-rules
    claim: >-
      A fuzz test is `FuzzXxx(f *testing.F)` in a `_test.go` file with
      exactly one `f.Fuzz` target, whose function takes a `*testing.T` and
      then arguments of the listed primitive types. `*F` methods may be
      called only before `F.Fuzz`; inside the target only `*T` methods, and
      of `*F` only `Failed` and `Name`, may be used.
    confidence: strong
    sources: [go-testing-pkg, go-fuzz-doc]
  - id: fuzz-targets-are-deterministic
    claim: >-
      A fuzz target should be fast and deterministic and should not depend
      on shared or global state, nor keep state past the end of each call,
      so that new failures and their coverage can be reproduced. A failing
      input is written under `testdata/fuzz/<Name>` and is then run by plain
      `go test` as a regression test.
    confidence: strong
    sources: [go-testing-pkg, go-fuzz-doc]
  - id: b-loop-keeps-the-benchmark-honest
    claim: >-
      In a `b.N` loop the compiler may eliminate a call whose result is
      unused, so the benchmark measures an empty loop, and setup before the
      loop is timed unless the timer is reset. `B.Loop`, from Go 1.24, keeps
      the loop body's values alive and excludes setup from timing, and is
      now preferred; a benchmark uses `B.Loop` or a `b.N` loop, not both.
    confidence: strong
    sources: [go-blog-b-loop, go-testing-pkg]
  - id: tests-are-found-by-name-and-signature
    claim: >-
      `go test` runs functions named `TestXxx`, where `Xxx` does not start
      with a lowercase letter, taking one `*testing.T`, in `_test.go` files;
      the `tests` analyzer, which `go test` runs by default, reports
      malformed names and wrong signatures of tests, benchmarks, fuzz tests
      and examples.
    confidence: strong
    sources: [go-testing-pkg, vet-tests, go-cmd-go]
  - id: examples-run-only-with-output
    claim: >-
      An example function is executed by `go test` and its standard output
      compared only when it carries an output comment; without one it is
      compiled but not executed.
    confidence: evidenced
    sources: [go-testing-pkg]
  - id: errors-compared-by-meaning
    claim: >-
      A test does not compare error strings to decide which error it got;
      it uses `errors.Is`, or `cmp` with `cmpopts.EquateErrors`, and when an
      error is not meant to be inspected, a non-nil check is enough. A
      substring check that the message names a parameter is allowed.
    confidence: strong
    sources: [google-go-decisions, go-wiki-test-comments]
  - id: golden-files-update-behind-a-flag
    claim: >-
      Golden files live under the package's `testdata` directory, which the
      go tool ignores, and are rewritten only when the test is run with an
      `-update` flag the package defines; the old and new expected values
      are then compared by diff to check the update is correct.
    confidence: directional
    sources: [gotest-tools-golden, go-cmd-go]
---

# Research: Go test quality

Read on 2026-11-23 at each source's own page, the Go project's own
documentation first. Each `date` is the reading date: the package and
command documentation and the wiki pages are living and carry no
publication date, and the three blog posts' own dates are in their titles.
The `testing` and `cmd/go` pages document go1.27.4.

## Reading, not running

`go vet`'s `tests` analyzer and the `testinggoroutine` analyzer flag two of
these mechanically. This module runs neither, because it serves the static
phase: each check is applied by reading the test code, and an analyzer is a
check's reference, never its mechanism. One check depends on the module's
Go version, read from the `go` line of the `go.mod` that holds the package
and from any `//go:build` line of the file: the loop-variable capture is a
defect only below Go 1.22. For a diff, a finding is in the changed lines,
but `go.mod`, a helper's body or the parent test of a subtest is read where
it lives, inside or outside the diff.

## Golden files

No Go project page states a golden-file practice; the convention is
documented by the libraries that implement it, here `gotest.tools`, and by
the `cmd/go` rule that `testdata` is ignored by the go tool. The finding is
therefore `directional`, and the one check on it reads only the defect
that makes a golden comparison vacuous: a test that rewrites the file it
compares against on every run.

## What this does not cover

Each of these was considered and left out, for the reason given.

- **Assertion libraries and `reflect.DeepEqual`.** The Google guide and the
  Go Test Comments advise against both, but as a style preference: neither
  makes a test pass on broken code, so there is no defect a finding could
  be verified against.
- **Failure message form**, got before want, naming the function and the
  input, and printing a diff. Readability advice with no evidence rule.
- **Table-driven tests with branching logic per row.** The Google guide
  prefers separate test functions when cases need different logic, as a
  matter of readability; a reading cannot tell where branching starts to
  hide a defect.
- **A test with no failure call.** A Go test with no `t.Error`, `t.Fatal`
  or `t.Fail` still fails on a panic, which is often what it checks, and no
  source read names it a defect.
- **Sleeps and timing.** No Go source read names a fixed sleep as a cause
  of flaky tests; the Google guide links a tip on parallel flakiness but
  does not state it.
- **Race detection, coverage and fuzzing runs.** `-race`, `-cover`,
  `-shuffle` and `-fuzz` need the suite run, which is the dynamic phase.
- **Concurrency in the code under test.** Data races and goroutine leaks in
  production code belong to a concurrency module; this one reads tests
  only, including the goroutines a test itself starts.
