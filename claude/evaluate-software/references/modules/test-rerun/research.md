---
sources:
  - id: github-flaky-builds
    title: "GitHub Blog: Reducing flaky builds by 18x"
    url: https://github.blog/engineering/infrastructure/reducing-flaky-builds-by-18x/
    date: 2020-12-16
  - id: pytest-flaky
    title: "pytest documentation: Flaky tests"
    url: https://docs.pytest.org/en/stable/explanation/flaky.html
    date: 2026-11-26
  - id: go-testflag
    title: "Go documentation: cmd/go, Testing flags"
    url: https://pkg.go.dev/cmd/go#hdr-Testing_flags
    date: 2026-11-26
  - id: pytest-usage
    title: "pytest documentation: How to invoke pytest"
    url: https://docs.pytest.org/en/stable/how-to/usage.html
    date: 2026-11-26
  - id: jest-cli
    title: "Jest documentation: Jest CLI Options"
    url: https://jestjs.io/docs/cli
    date: 2026-11-26
  - id: pytest-rerunfailures
    title: "PyPI: pytest-rerunfailures"
    url: https://pypi.org/project/pytest-rerunfailures/
    date: 2026-11-26
  - id: git-log
    title: "Git documentation: git-log"
    url: https://git-scm.com/docs/git-log
    date: 2026-11-26
findings:
  - id: a-flaky-test-passes-and-fails-on-the-same-code
    claim: >-
      A flaky test is one that shows both a passing and a failing result on
      the same code, failing intermittently for no reason the code shows, so
      only running it again finds it: reading the code does not.
    confidence: strong
    sources: [github-flaky-builds, pytest-flaky]
  - id: reruns-sort-flaky-failures-by-cause
    claim: >-
      Retrying a failed test in ways that each vary one condition finds most
      flaky failures automatically: GitHub retries in the same process (same
      VM, database and host), in the same process with the clock shifted
      forward by test helpers, and on a different host, and identifies about
      90 percent of flaky failures this way, against about 25 percent
      before. A pass under same conditions points at randomness or a race, a
      pass only on another host at order dependence or shared state.
    confidence: evidenced
    sources: [github-flaky-builds]
  - id: runners-select-and-repeat-one-test
    claim: >-
      Test runners select one test from their own command line, and some
      repeat it in one process: `go test -run` selects by name and `-count n`
      runs each test n times, `-count=1` also bypassing the result cache;
      pytest selects a test by its node id, `file::name`; Jest selects by
      file pattern and by `-t` name pattern, and takes arguments through
      `npm test --`. pytest and Jest have no repeat flag of their own; a
      rerun plugin such as pytest-rerunfailures adds `--reruns` only where
      it is installed.
    confidence: strong
    sources: [go-testflag, pytest-usage, jest-cli, pytest-rerunfailures]
  - id: the-last-change-names-whom-to-ask
    claim: >-
      The people who most recently changed a flaky test's files or the code
      it exercises are the ones to ask about it: GitHub assigns a flaky test
      whose impact passes a threshold to them, from failure history and git
      blame. `git log -1` limited
      to a path gives the last commit that changed it, with its author name
      and hash by the `%an` and `%H` placeholders.
    confidence: evidenced
    sources: [github-flaky-builds, git-log]
---

# Test rerun: research

The findings above back the one check of the library's dynamic module on
test stability. Each source was read on the date it records, except
GitHub's post, which carries its publication date.

## How the findings were reached

The definition GitHub uses, a test with both a passing and a failing result
on the same code, is the one the check reports on, and pytest's own page on
flaky tests describes the same intermittent failure; the two are independent
and agree, so the definition is marked `strong`. The rerun method follows
GitHub's three retries as far as a local run can follow them:

- **The same process** is reached only through a runner's own repeat flag,
  which Go has and pytest and Jest do not. A rerun plugin the repository
  already installs counts as the runner's; the module installs none, by the
  dynamic phase's rules.
- **Later in time** is reached as a fresh launch after the first run ended.
  GitHub shifts the clock forward with test helpers, inside the test
  process; a rerun by the declared command cannot, so it reproduces only
  the wall-clock interval, and a test that fails only at some future date
  is not found. The interval is stated so a reader can judge it.
- **Another host** is out of reach of a run on the user's machine, and is
  always named as such. A test that failed on every local rerun may still
  be flaky in the way GitHub's third retry finds, so it is recorded as
  unresolved, never as passed or as a plain failure.

Reruns are capped at three, GitHub's number, because each is a launch the
user is asked to approve.

The suggested owner follows GitHub's assignment: the people who last
changed the test's files or the code it exercises. The module reads it from
`git log -1` per file rather than from blame, since blame names the author
of each line, and the record wants one name per file. It is a suggestion of
whom to ask, not an assignment: the module cannot see the history GitHub
uses to find the commit that made the test flaky.

## What this does not cover

- **Order dependence.** Randomising test order, which pytest's page and
  `go test -shuffle` offer, changes the conditions rather than rerunning
  under them, so it is not a rerun; a check that shuffles would be a
  candidate of its own.
- **Quarantine.** pytest's page names marking a test as an expected failure
  as a manual quarantine, and warns against keeping it; quarantining is the
  owner's decision on a finding, not something an evaluation does.
- **Tests no manifest declares.** A repository that runs its tests only by
  a toolchain command no file declares, such as a bare `go test ./...`,
  matches no trigger, since the dynamic phase runs only declared commands.
