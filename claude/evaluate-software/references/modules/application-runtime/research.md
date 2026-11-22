---
sources:
  - id: veracode-sast-dast
    title: "Veracode: SAST vs. DAST for Security Testing, Unveiling the Differences"
    url: https://www.veracode.com/blog/sast-vs-dast-security-testing-unveiling-differences/
    date: 2026-11-22
  - id: gitlab-sast-dast
    title: "GitLab: SAST vs. DAST"
    url: https://about.gitlab.com/topics/devsecops/sast-vs-dast/
    date: 2026-11-22
  - id: npm-start
    title: "npm documentation: npm start"
    url: https://docs.npmjs.com/cli/v10/commands/npm-start
    date: 2026-11-22
  - id: heroku-procfile
    title: "Heroku Dev Center: The Procfile"
    url: https://devcenter.heroku.com/articles/procfile
    date: 2026-11-22
  - id: k8s-probes
    title: "Kubernetes: Configure Liveness, Readiness and Startup Probes"
    url: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
    date: 2026-11-22
  - id: turing-way-smoke
    title: "The Turing Way: Smoke testing"
    url: https://book.the-turing-way.org/reproducible-research/testing/testing-smoketest/
    date: 2026-11-22
  - id: twelve-factor-disposability
    title: "The Twelve-Factor App, IX: Disposability"
    url: https://12factor.net/disposability
    date: 2026-11-22
findings:
  - id: running-the-application-finds-what-reading-misses
    claim: >-
      Dynamic testing exercises a running application from outside, with no
      access to its source, and finds defects that only show at run time,
      where static analysis reads the code without running it. The two are
      complementary, not substitutes.
    confidence: evidenced
    sources: [veracode-sast-dast, gitlab-sast-dast]
  - id: start-commands-are-declared
    claim: >-
      Ecosystems give an application a declared start command in a manifest:
      `npm start` runs the `start` script of `package.json`, and a Procfile
      declares each process type and the command it runs, the `web` type
      being the one that receives HTTP traffic. A runner uses that
      declaration rather than composing a command of its own.
    confidence: evidenced
    sources: [npm-start, heroku-procfile]
  - id: readiness-is-its-own-signal
    claim: >-
      A started process is not yet ready to serve: orchestrators separate a
      startup or readiness signal from the process merely running, and send
      no traffic until it reports ready.
    confidence: evidenced
    sources: [k8s-probes]
  - id: smoke-checks-are-shallow-gates
    claim: >-
      A smoke test is a quick, shallow check of an application's most basic
      behaviour, run first; when it fails, deeper testing is not worth
      running.
    confidence: directional
    sources: [turing-way-smoke]
  - id: processes-stop-gracefully-on-a-signal
    claim: >-
      A well-behaved process starts quickly and shuts down gracefully on
      SIGTERM: a web process stops accepting requests, finishes those in
      flight and exits.
    confidence: evidenced
    sources: [twelve-factor-disposability]
---

# Application runtime: research

The findings above back the three checks of the library's first dynamic
module. Each source was read on the date it records.

## How the findings were reached

The module takes the shape of dynamic application security testing, which
tests the running application from outside and needs no source language,
so one module serves every language the library covers. The vendor pages
compared for that shape agree on the split between the phases: static
analysis reads code at rest, and dynamic testing probes a running
application. Industry dynamic testing runs against a deployed test
instance, not a developer's workstation, so it gives no precedent for
running unattended on the user's own machine; that is why the router asks
before each launch.

The triggers are the manifests that declare a start or serve command: a
`package.json` start script, a `[project.scripts]` table in
`pyproject.toml`, a compose file and a Procfile. A compose file is itself a
container command, so it runs as the repository declares it; the router
adds no container to any other command.

Readiness, the smoke check and shutdown follow the lifecycle an
orchestrator imposes on a process: wait for a readiness signal before
traffic, then stop it with a signal and expect a prompt, clean exit.

## What this does not cover

- **Security probing.** The module borrows dynamic testing's shape, not its
  attacks: no check sends hostile input, and none is a scanner's rule.
- **Analysers.** No analyser runs in this phase; analysis belongs to the
  static phase, by the split the vendor pages draw.
- **Isolation.** Claude Code's own sandbox does not cover native Windows,
  and its documentation recommends a container or a virtual machine for
  untrusted code. The module's targets are the user's own repositories, so
  it adds no isolation, and the per-launch ask carries that review.
- **Flaky tests.** Rerunning a test suite to find unstable tests is a
  candidate for a later dynamic module of its own; it confirms tests, not
  the application.
