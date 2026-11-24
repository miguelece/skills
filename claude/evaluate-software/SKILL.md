---
name: evaluate-software
description: Evaluate code or a design against a library of modules loaded per language, framework and concept -- a diff, a whole repository, a design read from a codebase or a design document -- in a static phase that reads without running anything and a dynamic phase that starts the application by its own declared command, asked first, and confirms its behaviour, and write one report of verified findings. Use when asked to "evaluate this code", "review this repository", "assess this design", "run a static evaluation", "stand the app up and check it", or to check code or a design against language and concept best practice.
allowed-tools: Read Grep Glob Bash(python ${CLAUDE_SKILL_DIR}/scripts/validate_report.py *)
---

# Evaluate software

Evaluate code or a design by loading only the modules it calls for. The
library is a set of modules, each a directory under `references/modules/`,
each declaring which languages, concepts, input kinds and phases it serves,
which checks it runs and the research those checks rest on. This body is the
router; the knowledge lives in the modules.

## When this applies

- The input is one of four kinds: a **diff**, a whole **repository**, a
  design read from a codebase (**design-from-code**), or a **design document**
  written before any code exists.
- The run has a **static phase**, which reads code, tests or a design without
  running anything, and a **dynamic phase**, which stands the application up
  and confirms its behaviour. Each is a complete evaluation on its own.

## The contracts

- **What a module is**: `references/module-contract.md`. Read it before
  loading a module, and never load a file a module's header does not reach.
- **What a run writes**: `references/report.schema.yaml`, one report per run.
  Readers of an evaluation read that report and nothing else, so every module
  loaded or skipped, and why, goes in it.
- **The report is a JSON file, and it is validated before it is handed on.**
  After writing it, run
  `python ${CLAUDE_SKILL_DIR}/scripts/validate_report.py <report.json>`,
  where `${CLAUDE_SKILL_DIR}` is this skill's own directory, which a Codex
  agent resolves itself. Fix every problem it prints, and run it again; hand
  the report on only when it exits `0`.
- **Where the contract comes from**: `references/prior-art.md`, the rule
  metadata of established analysers and the SARIF result format.

## Plan

### 1. Classify the request

Decide the input kind and the phases before reading any module.

- **The input kind**, recorded in `input.kind`:
  - `diff`: a change between two revisions, a patch, or a pull request.
  - `repository`: a whole codebase at one revision, asked about as code.
  - `design-from-code`: a codebase asked about as a design, its
    architecture, boundaries or structure rather than its lines.
  - `design-document`: a written design, with or without code beside it.

  If the request fits two kinds, ask which one is meant rather than guess:
  the kind decides which modules can load.
- **The scope**, in `input.scope`, exact enough to repeat the run: the
  revision range, the root path and revision, or the document path. Anything
  left out on purpose goes in `input.excluded`.
- **The phases asked for**, in `phases.requested`. A request that names no
  phase asks for `static`.
- **A request for the dynamic phase** runs at step 4, after the static phase
  when both are asked for. It runs nothing for a design input, which has
  nothing to start, nor for a `diff` whose head is not the checked-out
  working tree, since the phase never checks a revision out: then `dynamic`
  stays out of `phases.run`, and an entry in `phases.not-run` gives its
  `phase` `dynamic` and its `reason`.

### 2. Select modules

1. Read `references/modules/index.yaml`. It lists every module the library
   holds, and every one of them is accounted for in the report.
2. For each listed id, read the header of
   `references/modules/<id>/module.yaml`: `languages`, `concept`, `triggers`,
   `inputs` and `phases`. Do not act on its `checks`, and do not open its
   `research.md` or any other file of it, until the module is chosen.
3. Choose a module only when all three hold:
   - the run's input kind is in its `inputs`;
   - a phase of this run is in its `phases`, as `phases.requested` holds
     it after step 1;
   - a trigger matches the scope: a `files` glob matches a path in it (for a
     diff, a changed path); a `manifests` entry names a file present in it
     (for a diff, a file present in the repository at the diff's head,
     whether or not the diff changes it), with its marker inside that file
     when one is written; or, for the two design kinds, a `design-markers`
     entry appears anywhere in the design read, as a word or a heading, or a
     `design-headings` entry appears there only as a heading, never as a word
     in the prose.
4. Record each chosen module in `modules.loaded`, its reason the trigger that
   matched, quoted. Record every other listed module in `modules.skipped`,
   its reason the header field that ruled it out: the input kind, the phase,
   or that no trigger matched. No module appears in both lists.

### 3. Run the static phase

For each loaded module, now read its `checks`, and open any other file of
the module only when a check needs it.

1. Look for each check's defect within the scope, by reading. Run nothing.
   For a `diff`, a finding sits in the changed lines, and what it rests on
   may be read anywhere in the repository at the new revision, unless the
   check narrows this in its own `evidence`.
2. **Verify before recording.** Reopen the code at the location, or the
   design document at the section, and confirm that what is there meets the
   check's `evidence` rule. A candidate that does not meet it is dropped, not
   recorded at a lower confidence.
3. Record each verified finding in `findings`:
   - `findings.module` and `findings.check`, the check id as the module
     declares it;
   - `findings.phase`: `static`;
   - `findings.location`: a `file`, with a `symbol` or a `line` where one
     applies, or a design document's `section`, never both;
   - `findings.evidence`: what the check's `evidence` asks for, quoted or
     described from the source;
   - `findings.severity`: the check's own severity;
   - `findings.confidence`: how sure this run is of this one detection,
     after verifying it, as `high`, `medium` or `low`;
   - `findings.dynamic`: null.

### 4. Run the dynamic phase

Only when `dynamic` is in `phases.requested` and a loaded module declares
it. This phase runs code on the user's machine, and on native Windows the
harness runs it unsandboxed, so the ask in item 3 is the one review point
before it runs.

1. **Find the command.** Use only the repository's own declared start, serve
   or test command, the one a loaded module's trigger matched: a
   `package.json` script, a `pyproject.toml` script entry, a compose file's
   services or a `Procfile` process. Run it as declared, with no container
   added; a command that is itself a container command runs as it is
   written. Never compose a command the repository does not declare.
2. **Estimate it.** State the command, what it starts, and its peak memory,
   GPU memory and disk use, with what the estimate rests on, against the
   user's safety budget where one is set. If it does not clearly fit, do
   not launch: say so and ask how to shrink it.
3. **Ask before each launch.** Put the command and its resource estimate to
   the user and wait for a yes before starting it, every launch, even when
   the harness would let it run without a prompt. A declined launch starts
   nothing, and the module chosen for it stays in `modules.loaded`, which
   lists a module the router chose, whether or not its phase ran. `dynamic`
   stays out of `phases.run`, and its entry in `phases.not-run` gives the
   reason, that the user declined the launch; read `phases.not-run`, not
   `modules.loaded`, for whether the module's checks ran.
4. **Install nothing unchecked.** When the command needs its dependencies
   installed first, that install is a launch of its own, asked as above,
   and it runs only after its runtime and its packages are checked against
   current security advisories, from the lockfile, never an unpinned fetch.
5. **Start it and confirm readiness.** Start the declared command as the
   root of its own process group (a new session on POSIX,
   `CREATE_NEW_PROCESS_GROUP` on Windows), so a stop reaches the
   application beneath a wrapper such as `npm start`, which does not
   reliably pass a signal on. Wait for the signal the repository
   documents (a health endpoint, a log line, a listening port) before any
   check runs, and record the process in `dynamic.started`: its `target`,
   its exact `command`, and in `ready` how readiness was confirmed.
6. **Run each loaded dynamic module's checks** against the running
   application, from outside it, as each check's `evidence` asks. Verify
   before recording, as in step 3, then record each finding with
   `findings.phase`: `dynamic`, and in `findings.dynamic` the `command` or
   request that exercised it, what was `observed` and what was `expected`.
7. **Tear down every process** the phase started: stop each by signalling
   its process group, not the wrapper's process id alone, then confirm
   every process in the group has exited and the port is released. A
   process that will not stop is reported to the user at once, by its
   command and process id, not as a finding.

### 5. Report

Write one report by `references/report.schema.yaml`: every required field
present, no field it does not define, and every rule under its `rules:`
held. The reserved dynamic fields are empty in a run without the dynamic
phase.

- **Static ran** when at least one module was loaded and its checks were
  read against the scope: `static` is in `phases.run`, and an empty
  `findings` list is a clean run.
- **No module matched**, because the index lists none or every listed module
  was skipped: say so, and evaluate nothing. Do not evaluate from general
  knowledge in a module's place, because a finding with no check behind it
  has no rationale, no reference and no evidence rule to be verified
  against. The report still accounts for every listed module in
  `modules.skipped`, leaves `modules.loaded` and `findings` empty, and keeps
  `static` out of `phases.run`, so the empty `findings` list cannot read as
  a clean run. It records each requested phase in `phases.not-run`, its
  `reason` that no module matched.
- **Dynamic ran** when its application started, reported ready and its
  checks were run against it: `dynamic` is in `phases.run`.

`phases.not-run` holds every requested phase that is not in `phases.run`,
each with its reason, and is an empty list when every requested phase ran.

In the reply, name where the report is, list the modules loaded and skipped
with their reasons, and repeat why any requested phase did not run.

## Status

The library holds eight modules, listed in `references/modules/index.yaml`;
each module's `module.yaml` header says which input kinds and phases it
supports and what triggers it. Two are on architecture: one for a design
document and one for the design read from a codebase. The static code
modules read a test suite, the type safety, the error handling or the
concurrency of Python, TypeScript or Go code in a `diff` or a
`repository`. A `diff` or a `repository` whose contents trigger no static
module ends at step 5's no-match case. One module is dynamic: it starts an
application whose manifest declares a start or serve command, in any
language, and checks that it reports ready, answers a smoke check and
shuts down cleanly.

## Guardrails

- Do NOT run the code, a test or a server in the static phase.
- Do NOT launch without asking first, every launch of the dynamic phase,
  with the command and its resource estimate.
- Do NOT install anything without the advisory check, and never from an
  unpinned fetch.
- Do NOT add a container the repository does not declare, and do not run a
  command it does not declare.
- Do NOT run an analyser in either phase: the dynamic phase stands the
  application up and observes it, nothing else.
- Do NOT leave a process running: tear down everything the phase started.
- Do NOT report a finding the check's `evidence` rule is not met for.
- Do NOT load a module whose header does not support the input kind and
  phase of this run; record it as skipped, with the reason.
- Do NOT evaluate from general knowledge when no module matched.
- Do NOT add a field the report schema does not define.
