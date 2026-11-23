---
sources:
  - id: go-memory-model
    title: "The Go Memory Model, version of June 6, 2022"
    url: https://go.dev/ref/mem
    date: 2026-11-23
  - id: go-race-detector
    title: "Go documentation: Data Race Detector"
    url: https://go.dev/doc/articles/race_detector
    date: 2026-11-23
  - id: go-spec
    title: "The Go Programming Language Specification, language version go1.27"
    url: https://go.dev/ref/spec
    date: 2026-11-23
  - id: go-sync
    title: "Go standard library: package sync, go1.27.4"
    url: https://pkg.go.dev/sync
    date: 2026-11-23
  - id: go-context
    title: "Go standard library: package context, go1.27.4"
    url: https://pkg.go.dev/context
    date: 2026-11-23
  - id: go-os-signal
    title: "Go standard library: package os/signal, func Notify, go1.27.4"
    url: https://pkg.go.dev/os/signal#Notify
    date: 2026-11-23
  - id: go-vet
    title: "Go command documentation: cmd/vet, go1.27.4"
    url: https://pkg.go.dev/cmd/vet
    date: 2026-11-23
  - id: vet-loopclosure
    title: "golang.org/x/tools analyzer loopclosure, v0.53.0"
    url: https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/loopclosure
    date: 2026-11-23
  - id: vet-atomic
    title: "golang.org/x/tools analyzer atomic, v0.53.0"
    url: https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/atomic
    date: 2026-11-23
  - id: vet-copylock
    title: "golang.org/x/tools analyzer copylock, v0.53.0"
    url: https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/copylock
    date: 2026-11-23
  - id: vet-waitgroup
    title: "golang.org/x/tools analyzer waitgroup, v0.53.0"
    url: https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/waitgroup
    date: 2026-11-23
  - id: vet-lostcancel
    title: "golang.org/x/tools analyzer lostcancel, v0.53.0"
    url: https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/lostcancel
    date: 2026-11-23
  - id: staticcheck
    title: "Staticcheck: Checks (SA1, SA2 and SA5 groups)"
    url: https://staticcheck.dev/docs/checks/
    date: 2026-11-23
  - id: go-wiki-code-review
    title: "Go Wiki: Go Code Review Comments"
    url: https://go.dev/wiki/CodeReviewComments
    date: 2026-11-23
  - id: google-go-decisions
    title: "Google Go Style Guide: Style Decisions"
    url: https://google.github.io/styleguide/go/decisions
    date: 2026-11-23
  - id: uber-go-guide
    title: "Uber Go Style Guide (uber-go/guide, style.md)"
    url: https://github.com/uber-go/guide/blob/master/style.md
    date: 2026-11-23
  - id: go-blog-pipelines
    title: "The Go Blog: Go Concurrency Patterns: Pipelines and cancellation (Sameer Ajmani, 2014-03-13)"
    url: https://go.dev/blog/pipelines
    date: 2026-11-23
  - id: x-sync-errgroup
    title: "golang.org/x/sync package errgroup, v0.25.0"
    url: https://pkg.go.dev/golang.org/x/sync/errgroup
    date: 2026-11-23
findings:
  - id: data-race-definition
    claim: >-
      A data race is a write to a memory location concurrent with another
      read or write of it, unless every access is atomic through
      `sync/atomic`; such access must be serialized with channels or the
      `sync` and `sync/atomic` primitives. Programs with races are
      incorrect, and a race on a multiword value, an interface, map, slice
      or string, can yield a value no single write produced and can in turn
      lead to arbitrary memory corruption.
    confidence: strong
    sources: [go-memory-model, go-race-detector]
  - id: races-the-detector-documents
    claim: >-
      The race detector's documentation names the typical races: a loop
      counter read by a goroutine, a variable such as `err` accidentally
      shared between goroutines, a map used from several goroutines without
      a mutex ("Concurrent reads and writes of the same map are not safe"),
      a primitive variable written and read unprotected, and unsynchronized
      send and close on one channel. The detector finds only races that
      happen at run time, on executed paths.
    confidence: evidenced
    sources: [go-race-detector]
  - id: no-busy-wait-on-plain-variable
    claim: >-
      A loop waiting for another goroutine to set an ordinary variable has
      no synchronization with the write, so it may never observe it and is
      not guaranteed to finish, and observing it does not imply observing
      the writes made before it. Staticcheck SA5002 reports the empty loop
      and names unsynchronized waiting a data race.
    confidence: strong
    sources: [go-memory-model, staticcheck]
  - id: double-checked-locking-is-a-race
    claim: >-
      Testing a plain flag outside a `sync.Once` or a lock, to skip the
      synchronization once setup is done, gives no guarantee that observing
      the flag implies observing the setup's writes, so the reader can see
      uninitialized data; the memory model's fix is explicit
      synchronization.
    confidence: evidenced
    sources: [go-memory-model]
  - id: loop-variable-per-iteration
    claim: >-
      Before Go 1.22 the iterations of a `for` loop share one set of
      iteration variables, so a goroutine started in the loop that refers
      to the variable races with the loop's update and observes a later
      value; from Go 1.22 each iteration has its own variables. `go vet`'s
      `loopclosure` reports the reference from `go` statements and
      `errgroup.Group.Go`, for Go 1.21 and earlier.
    confidence: strong
    sources: [go-spec, vet-loopclosure, go-race-detector]
  - id: atomic-access-is-all-or-nothing
    claim: >-
      An access is exempt from being a race only when every access to the
      location is atomic, so a variable updated through `sync/atomic` and
      also read or written plainly is raced. `go vet`'s `atomic` analyzer
      reports `x = atomic.AddUint64(&x, 1)`, an assignment that is not
      atomic.
    confidence: strong
    sources: [go-memory-model, vet-atomic]
  - id: sync-values-not-copied
    claim: >-
      `sync.Mutex`, `RWMutex`, `WaitGroup`, `Once`, `Cond` and `Map` must
      not be copied after first use; a receiver holding one must be a
      pointer, and `go vet`'s `copylocks` reports locks passed by value.
    confidence: strong
    sources: [go-sync, vet-copylock, go-wiki-code-review, google-go-decisions]
  - id: waitgroup-add-before-go
    claim: >-
      `WaitGroup.Add` with a positive delta from zero must happen before
      `Wait`, and should execute before the statement creating the
      goroutine; calling it inside the goroutine creates a race between
      `Add` and `Wait`. `WaitGroup.Go`, from Go 1.25, is preferred, and
      `go vet`'s `waitgroup` and Staticcheck SA2000 report the misuse.
    confidence: strong
    sources: [go-sync, vet-waitgroup, staticcheck]
  - id: cancel-func-must-be-called
    claim: >-
      The cancel function returned by `context.WithCancel`, `WithTimeout`,
      `WithDeadline` and their variants must be called: failing to call it
      leaks the child and its children until the parent is canceled.
      `go vet`'s `lostcancel` reports a cancel function that is not used
      on all paths, in its diagnostic's words.
    confidence: strong
    sources: [go-context, vet-lostcancel]
  - id: context-key-own-type
    claim: >-
      A `context.WithValue` key should not be a `string` or other built-in
      type, to avoid collisions between packages using context; users
      define their own key types (Staticcheck SA1029).
    confidence: evidenced
    sources: [staticcheck]
  - id: goroutines-must-exit
    claim: >-
      Goroutines are not garbage collected and must exit on their own; one
      blocked forever on a send or receive leaks. A spawned goroutine needs
      a predictable stop or a way to be told to stop, and a way to wait for
      its exit; `init` should not spawn goroutines, and a package needing a
      background one exposes an object whose `Close` or `Stop` ends it.
    confidence: strong
    sources: [go-wiki-code-review, google-go-decisions, uber-go-guide, go-blog-pipelines]
  - id: blocked-sender-leaks
    claim: >-
      When a receiver stops reading early, the goroutines still sending to
      it block and leak; a stage keeps receiving until its inbound channels
      are closed or the senders are unblocked, for instance by closing a
      shared `done` channel as a broadcast.
    confidence: strong
    sources: [go-blog-pipelines, go-wiki-code-review]
  - id: errgroup-propagates-first-error
    claim: >-
      `errgroup` provides synchronization, error propagation and context
      cancellation for a group of goroutines: `Wait` blocks until every
      function passed to `Go` has returned and returns the first non-nil
      error.
    confidence: evidenced
    sources: [x-sync-errgroup]
  - id: errgroup-context-cancels-on-first-error
    claim: >-
      The context `errgroup.WithContext` returns is canceled the first time
      a function passed to `Go` returns a non-nil error, or `Wait` returns;
      the parent context is not.
    confidence: evidenced
    sources: [x-sync-errgroup]
  - id: close-belongs-to-the-sender
    claim: >-
      Sending on or closing a closed channel, and closing a nil channel,
      cause a run-time panic. A pipeline stage closes its outbound channel
      when all its sends are done, and several senders are closed for by
      one goroutine that waits on a `WaitGroup` for them, which prevents a
      send on a closed channel; unsynchronized send and close is a race.
    confidence: strong
    sources: [go-spec, go-blog-pipelines, go-race-detector]
  - id: deferred-lock-is-a-typo
    claim: >-
      Deferring `Lock` immediately after locking is almost always a typo
      for deferring `Unlock`; it does not strictly guarantee a deadlock but
      is highly likely a mistake (Staticcheck SA2003).
    confidence: evidenced
    sources: [staticcheck]
  - id: empty-critical-section-is-usually-a-typo
    claim: >-
      A `Lock` immediately followed by `Unlock` is very often a typo for a
      deferred `Unlock`; it is occasionally a deliberate signal, which
      should then be amply commented (Staticcheck SA2001).
    confidence: evidenced
    sources: [staticcheck]
  - id: no-recursive-read-lock
    claim: >-
      `RWMutex.RLock` should not be used for recursive read locking: a
      blocked `Lock` call excludes new readers from acquiring the lock.
    confidence: evidenced
    sources: [go-sync]
  - id: once-do-reentry-deadlocks
    claim: >-
      No call to `Once.Do` returns until the one call to `f` returns, so if
      `f` causes `Do` to be called on the same `Once`, it deadlocks.
    confidence: evidenced
    sources: [go-sync]
  - id: signal-channel-needs-buffer
    claim: >-
      `signal.Notify` will not block sending to its channel, so the caller
      must give the channel enough buffer for the expected signal rate, one
      for a single signal value; `go vet`'s `sigchanyzer` and Staticcheck
      SA1017 report an unbuffered one.
    confidence: strong
    sources: [go-os-signal, go-vet, staticcheck]
  - id: select-default-spins
    claim: >-
      A `select` with an empty `default` inside an unconditional loop does
      not block, so the loop spins, consuming CPU while waiting for work
      (Staticcheck SA5004).
    confidence: evidenced
    sources: [staticcheck]
  - id: guarded-state-copied-at-boundary
    claim: >-
      A method that returns a map or slice the type guards with a mutex
      hands the caller a reference no longer protected by the mutex, so
      any access to it is subject to data races; the method should return
      a copy.
    confidence: evidenced
    sources: [uber-go-guide]
---

# Research: Go concurrency

The findings above were read from the Go project's own documentation, the
memory model, the race detector article, the specification, the `sync`,
`context` and `os/signal` packages and the pipelines post, from five `go vet`
analyzers at golang.org/x/tools v0.53.0 and the `cmd/vet` analyzer list,
from Staticcheck's check list, from the Code Review Comments wiki, the
Google Go style guide's decisions, the Uber Go style guide and the `errgroup`
package at golang.org/x/sync v0.25.0. Every page was read on 2026-11-23
against Go 1.27.4. A finding is `strong` where the language's documentation
and an independent source agree, or a specification states it, and
`evidenced` where one source states it directly.

## Reading, not running

The race detector, `go vet` and Staticcheck carry several of these checks
mechanically, and the race detector finds only races on paths a run
executes. This module runs none of them, because it serves the static
phase: each check is applied by reading the code, and a tool is a check's
reference, never its mechanism. A reading reaches paths no test executes,
but it can report only a race whose two accesses and missing
synchronization it can quote; a check's `evidence` asks for both.

## Production code only

The checks read files not ending in `_test.go`. The Go testing module reads
the test files and already checks the concurrency defects particular to
tests: `Fatal` from a goroutine, a parallel subtest capturing a loop
variable, teardown before parallel subtests and process state changed by a
parallel test. A race inside a test is a defect of the test, and reading
test files here too would let one line be reported by both modules. The
Go error handling module reads error handling in production code and left
errors lost from goroutines to this module; the check on them excludes a
call whose error is discarded as a statement or assigned to `_` inside the
goroutine, which that module's discard check already reports.

## Four consequences derived, not quoted

The `sync` package says its types must not be copied after first use, and
the copy check's rationale adds why: a copied `Mutex` is a separate value
with its own state, so code locking the copy does not exclude code locking
the original. That follows from Go's value semantics rather than from a
sentence in the sources. The recursive read lock's deadlock is likewise
derived from the one sentence the package gives, that a blocked `Lock`
excludes new readers: the second `RLock` waits for the writer, which waits
for the first.

Two more rationales go past their sources' wording. The lost goroutine
error's "reports success for work that failed" follows from the caller
having no path to learn of the error; the `errgroup` package describes how
an error is carried back, not what losing one costs. The empty critical
section's "runs unguarded" follows from the lock being released before the
code that follows it; Staticcheck says only that such a section is very
often a typo for a deferred `Unlock`.

## Version

One check rests on the Go version a package is built with, read from the
`go` line of its `go.mod`: a goroutine capturing a loop variable is a race
only before Go 1.22. `WaitGroup.Go`, from Go 1.25, is named as the
preferred form and decides nothing.

## What this does not cover

Each of these was considered and left out, for the reason given.

- **`time.Tick` and unstopped timers leaking.** Staticcheck SA1015 and the
  `time` package ([package time](https://pkg.go.dev/time#Tick)) record that
  since Go 1.23 the garbage collector recovers unreferenced tickers and
  timers, stopped or not; how the toolchain and the `go.mod` line together
  select the old behaviour was not confirmed from a primary page, so no
  check could state when it applies.
- **A context stored in a struct, or not passed first.** The `context`
  package and both style guides advise against it, but none names a
  failure a finding could be verified against.
- **Passing a nil context.** The `context` package prohibits it and
  Staticcheck SA1012 reports it, but the sources state no consequence
  beyond the prohibition.
- **An embedded mutex, a pointer to a mutex, and channel sizes other than
  zero or one.** API shape and scrutiny advice from the Uber guide, with no
  defect behind it.
- **Unbuffered channels against buffered ones in general, and preferring
  channels to locks.** Design guidance; neither choice is a defect alone.
- **Concurrency inside tests.** The Go testing module reads it.
