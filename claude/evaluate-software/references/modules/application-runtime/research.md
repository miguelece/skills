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
  - id: npm-run-script-signals
    title: "npm/run-script: lib/signal-manager.js"
    url: https://github.com/npm/run-script/blob/main/lib/signal-manager.js
    date: 2026-11-24
  - id: heroku-dyno-shutdown
    title: "Heroku Dev Center: Dyno Shutdown Behavior"
    url: https://devcenter.heroku.com/articles/dyno-shutdown-behavior
    date: 2026-11-24
  - id: posix-kill
    title: "kill(2), Linux manual page"
    url: https://man7.org/linux/man-pages/man2/kill.2.html
    date: 2026-11-24
  - id: windows-process-creation-flags
    title: "Microsoft Learn: Process Creation Flags"
    url: https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags
    date: 2026-11-24
  - id: node-signal-events
    title: "Node.js documentation: process, Signal events"
    url: https://nodejs.org/api/process.html#signal-events
    date: 2026-11-24
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
  - id: startup-limits-cover-the-worst-case
    claim: >-
      A startup limit is set long enough to cover the worst-case startup
      time, so a time documented as typical is not a limit: a slower start
      than usual is not a failure to start.
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
  - id: wrappers-do-not-reliably-forward-a-stop
    claim: >-
      A wrapper does not reliably pass a stop signal on to the application
      beneath it: npm runs a script through a shell and forwards SIGINT and
      SIGTERM only to that shell, whether the shell passes them on depends
      on the shell, and a Procfile runner signals each process it tracks by
      its own process id. A signal sent to the wrapper alone can report the
      wrapper's exit as the application's.
    confidence: evidenced
    sources: [npm-run-script-signals, heroku-dyno-shutdown]
  - id: a-group-stop-reaches-every-process
    claim: >-
      A stop sent to a process group reaches every process in it. On POSIX,
      a signal sent to the negated group id goes to each member; on Windows,
      a process created with CREATE_NEW_PROCESS_GROUP roots a group of all
      its descendants, to which CTRL_BREAK_EVENT is sent, since SIGTERM,
      SIGINT and SIGKILL sent through Node's kill emulation end the target
      unconditionally. A platform sends the stop the same way: Heroku
      signals every process in a dyno, then SIGKILL after 30 seconds.
    confidence: evidenced
    sources:
      - posix-kill
      - windows-process-creation-flags
      - node-signal-events
      - heroku-dyno-shutdown
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

Two readings were settled on 2026-11-24, when the worked run records were
written, because each check's evidence otherwise let two evaluators report
the same run differently. The stop goes to the started command's process
group, not the wrapper's process id: npm's signal forwarding was removed in
May 2023 (npm/run-script pull 142) and restored in January 2024 (pull 188),
so it cannot be relied on, and a group stop is what a terminal's Ctrl+C
and a dyno's shutdown both send. An end by the stop signal's own default
action is a clean stop, by the owner's ruling: the check's rationale names
a process killed mid-request and a port left bound, and with no request in
flight neither shows from outside, so an application that would drop
in-flight work is not caught, as no check sends a request during the stop.
A documented typical time is read as no documented wait rather than as a
limit with a margin, since no source fixes a margin and the module would
otherwise invent a limit the repository never set.

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
