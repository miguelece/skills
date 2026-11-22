---
sources:
  - id: pytest-assert
    title: "pytest: How to write and report assertions in tests"
    url: https://docs.pytest.org/en/stable/how-to/assert.html
    date: 2026-11-21
  - id: pytest-skipping
    title: "pytest: How to use skip and xfail to deal with tests that cannot succeed"
    url: https://docs.pytest.org/en/stable/how-to/skipping.html
    date: 2026-11-21
  - id: pytest-flaky
    title: "pytest: Flaky tests"
    url: https://docs.pytest.org/en/stable/explanation/flaky.html
    date: 2026-11-21
  - id: pytest-goodpractices
    title: "pytest: Good Integration Practices, conventions for Python test discovery"
    url: https://docs.pytest.org/en/stable/explanation/goodpractices.html
    date: 2026-11-21
  - id: pytest-reference
    title: "pytest API reference, 9.0.2 (pytest.approx, the xfail marker)"
    url: https://docs.pytest.org/en/stable/reference/reference.html
    date: 2026-11-21
  - id: pytest-tmp-path
    title: "pytest: How to use temporary directories and files in tests"
    url: https://docs.pytest.org/en/stable/how-to/tmp_path.html
    date: 2026-11-21
  - id: pytest-monkeypatch
    title: "pytest: How to monkeypatch/mock modules and environments"
    url: https://docs.pytest.org/en/stable/how-to/monkeypatch.html
    date: 2026-11-21
  - id: python-unittest-mock
    title: "Python 3.15 documentation: unittest.mock"
    url: https://docs.python.org/3/library/unittest.mock.html
    date: 2026-11-21
  - id: ruff-pt011
    title: "Ruff rule PT011, pytest-raises-too-broad"
    url: https://docs.astral.sh/ruff/rules/pytest-raises-too-broad/
    date: 2026-11-21
  - id: ruff-pt012
    title: "Ruff rule PT012, pytest-raises-with-multiple-statements"
    url: https://docs.astral.sh/ruff/rules/pytest-raises-with-multiple-statements/
    date: 2026-11-21
  - id: ruff-f631
    title: "Ruff rule F631, assert-tuple"
    url: https://docs.astral.sh/ruff/rules/assert-tuple/
    date: 2026-11-21
  - id: ruff-pgh005
    title: "Ruff rule PGH005, invalid-mock-access"
    url: https://docs.astral.sh/ruff/rules/invalid-mock-access/
    date: 2026-11-21
  - id: pylint-e0102
    title: "Pylint 4.1.4 message E0102, function-redefined"
    url: https://pylint.readthedocs.io/en/stable/user_guide/messages/error/function-redefined.html
    date: 2026-11-21
  - id: swe-book-testing-overview
    title: "Software Engineering at Google, chapter 11: Testing Overview (Adam Bender)"
    url: https://abseil.io/resources/swe-book/html/ch11.html
    date: 2026-11-21
  - id: swe-book-unit-testing
    title: "Software Engineering at Google, chapter 12: Unit Testing (Erik Kuefler)"
    url: https://abseil.io/resources/swe-book/html/ch12.html
    date: 2026-11-21
findings:
  - id: coverage-is-not-verification
    claim: >-
      Executing code is not testing it: line coverage records what a test
      ran, not whether it checked the result, so a test that verifies
      nothing still counts toward coverage. Test quality is judged by which
      behaviours are verified.
    confidence: evidenced
    sources: [swe-book-testing-overview]
  - id: return-values-are-ignored
    claim: >-
      pytest ignores a test's return value, so a test that returns False
      instead of asserting passes; a non-None return raises a warning,
      and the documented fix is to assert.
    confidence: evidenced
    sources: [pytest-assert]
  - id: some-assertions-cannot-fail
    claim: >-
      Some assertion forms are always true: an assert whose condition is a
      non-empty tuple, and a mock assertion method named but never called,
      which reads an attribute instead of checking an interaction. Linters
      flag both as mistakes.
    confidence: strong
    sources: [ruff-f631, ruff-pgh005, python-unittest-mock]
  - id: raises-block-holds-one-statement
    claim: >-
      A `pytest.raises` block with several statements can pass when it
      should fail: once an earlier statement raises the expected exception,
      the later ones never run. Setup belongs outside the block.
    confidence: evidenced
    sources: [ruff-pt012, pytest-assert]
  - id: raises-should-be-constrained
    claim: >-
      `pytest.raises` matches the exception type and its subclasses, so a
      broad type passes on an unrelated failure; `match` constrains the
      message and is the documented way to pin it.
    confidence: evidenced
    sources: [ruff-pt011, pytest-assert]
  - id: collection-is-by-name
    claim: >-
      pytest collects by name: `test_*.py` or `*_test.py` files, `test`
      functions, and `Test` classes only when they have no `__init__`,
      unless the configuration changes the patterns. A test outside these
      conventions is not run.
    confidence: evidenced
    sources: [pytest-goodpractices]
  - id: redefinition-hides-the-first
    claim: >-
      Redefining a function in the same scope is reported as an error by
      Pylint (E0102), and the later definition replaces the earlier one, so
      of two tests with one name in a module or class only the last is
      collected.
    confidence: evidenced
    sources: [pylint-e0102, pytest-goodpractices]
  - id: skips-carry-reasons
    claim: >-
      pytest's skip and xfail markers take a reason, and a conditional xfail
      requires one; by default neither an xfail nor an unexpected pass fails
      the suite, and `strict=True` or the strict-xfail option makes an
      unexpected pass fail it. pytest calls a permanent non-strict xfail
      dangerous.
    confidence: evidenced
    sources: [pytest-skipping, pytest-reference, pytest-flaky]
  - id: floats-compare-with-tolerance
    claim: >-
      Exact equality on computed floats fails on rounding, so pytest
      provides `pytest.approx` and names overly strict float comparison as a
      cause of flaky tests.
    confidence: strong
    sources: [pytest-reference, pytest-flaky]
  - id: tests-are-isolated
    claim: >-
      Tests that depend on state other tests leave behind, or on the
      environment outside their control, fail by order and environment;
      pytest's `tmp_path` gives each test its own directory and
      `monkeypatch` undoes every change after the test, and hermetic tests
      set up and tear down all they need.
    confidence: strong
    sources:
      - pytest-flaky
      - pytest-tmp-path
      - pytest-monkeypatch
      - swe-book-testing-overview
  - id: sleeping-tests-are-slow-and-flaky
    claim: >-
      Small tests are kept from sleeping and from blocking calls so that
      they stay fast and deterministic; timing is one of the causes pytest
      names for flaky tests.
    confidence: directional
    sources: [swe-book-testing-overview, pytest-flaky]
  - id: tests-hold-no-logic
    claim: >-
      Tests should be straight-line code without conditionals or loops,
      because logic in a test can hide a bug in the test itself, and a test
      should be correct by inspection.
    confidence: evidenced
    sources: [swe-book-unit-testing]
---

# Research: Python test quality

Read on 2026-11-21 at each source's own page, pytest's documentation first.
Each `date` is the reading date: the documentation pages are living and carry
no publication date, and the two book chapters are the online edition of a
book published in 2020, whose pages give no day. The pytest pages document
the 9.0 series, Python's the 3.15 series.

## Reading, not running

The linters cited flag several of these mechanically. This module runs none
of them, because it serves the static phase: each check is applied by
reading the test code, and a linter rule is a check's reference, never its
mechanism. Three checks depend on the test configuration as well as the
test, because the configuration can change the default they rest on:
collection patterns, the strict-xfail option, and the flags a helper passes.
For a diff, the finding is in the changed lines, but the configuration is
read where it lives, inside or outside the diff.

## What this does not cover

Each of these was considered and left out, for the reason given.

- **Coverage numbers and mutation scores.** Both need the suite run, which
  is the dynamic phase. The finding on coverage is used here only as the
  reason an assertion-free test is a defect.
- **Testing through private members.** Testing through the public API is
  well supported, but Python marks privacy only by convention, and tests
  often import an underscore helper deliberately, so a reading cannot tell
  a defect from a choice without the project's own rule.
- **Interaction-heavy mocking and mocks without a spec.** The sources prefer
  state checks and auto-speccing, but say when a mock is right only as a
  preference, not as a defect a reading can quote; an assertion method
  never called is kept, under `assertion-that-cannot-fail`.
- **Test naming and one behaviour per test.** These are advice on
  readability with no evidence rule a finding could be verified against.
- **Loops that assert on every item.** The logic finding covers them, but a
  loop that asserts on every pass cannot pass without asserting, so only
  an assertion a branch can skip is a check.
