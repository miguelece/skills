---
name: advise-from-evaluation
description: Turn an evaluation report into ranked advisories that say what to change, in what order and which findings each change answers -- refactoring advice for an evaluation of code, marking any change that alters observable behaviour as not a refactoring, and implementation advice for an evaluation of a design, answering each finding before the work it affects. Recommends only and files nothing. Use when asked to "turn this evaluation into advice", "what should we refactor", "advise on these findings", "prioritise the evaluation", "how should we build this design", or to plan changes from an evaluate-software report.
allowed-tools: Read Grep Glob Bash(python ${CLAUDE_SKILL_DIR}/scripts/validate_report.py *)
---

# Advise from an evaluation

Turn one evaluation report into advisories: what to change, in what order,
and which findings each change answers. An evaluation is a measurement; an
advisory is a recommendation the owner judges, accepts or rejects on its own
terms. This skill writes the recommendation and stops there.

## When this applies

- The input is **one evaluation report**, in the schema at
  `references/report.schema.yaml`, as `evaluate-software` writes it. Read that
  schema before reading the report, and read the report through it: every
  field this skill relies on is named below, and the report holds nothing
  else this skill may use.
- No report means no advisory. If asked to advise on code with no report,
  say that an evaluation comes first and offer `evaluate-software`; do not
  evaluate the code here.

## Plan

### 1. Read the report and select the mode

1. Check the report before advising on it: run
   `python ${CLAUDE_SKILL_DIR}/scripts/validate_report.py <report.json>`,
   where `${CLAUDE_SKILL_DIR}` is this skill's own directory, which a Codex
   agent resolves itself. It is the validator the evaluation skill runs on
   the report it writes. Exit `0` means the report conforms; read it. Exit
   `1` refuses the report, naming each problem the script printed; exit `2`
   refuses it as unreadable or not JSON. Advice on a malformed report would
   cite what is not there. Do not fix the report: this
   skill did not write it, so hand it back to whoever produced it. A report
   refused for its `schema-version` predates the current schema: do not edit
   it to pass, since an `unresolved` list added by hand would claim every
   check was judged. Say it predates the schema, and ask for the evaluation
   to be re-run.
2. Read `input.kind`. It alone selects the mode:

   | `input.kind`       | Mode                 |
   |--------------------|----------------------|
   | `diff`             | refactoring          |
   | `repository`       | refactoring          |
   | `design-from-code` | implementation       |
   | `design-document`  | implementation       |

3. The refactoring mode is steps 2 and 3; the implementation mode is step 4.
   Do not run one mode's steps on the other's input: the refactoring mode's
   rule about behaviour does not fit a design with no code behind it.
4. Read the phases before the findings. Each entry in `phases.not-run` is a
   requested phase that did not run: name it with its `reason`, whatever
   `findings` holds, since an unrun phase recorded nothing. Name each
   `unresolved` entry too, by its `check`, its location where it has one,
   and its `reason`, whatever `findings` holds: a check it names was neither
   failed nor passed. Then, when `findings` is empty:
   - **`phases.run` is empty**: nothing was evaluated, so the empty list is
     no clean run. Say there is nothing evaluated to advise on, and stop.
   - **`phases.run` is not empty**: it is a clean run of the phases it names,
     and only of the checks no `unresolved` entry names. Name them, say
     there is nothing to advise on, and stop.

### 2. Refactoring mode: group findings into changes

Read each finding's `findings.check`, `findings.location`,
`findings.evidence`, `findings.severity` and `findings.confidence`. Where a
location names a symbol or a line, `findings.location.symbol` and
`findings.location.line` place it exactly.

1. **Group findings that one change answers.** Two findings share a change
   when the same edit, in the same place, removes both: the same check in one
   file or one symbol, or different checks that the same restructuring
   clears. Do not group findings merely because they share a check; a
   change is one edit a reviewer can read as one.
2. **Write each change as an advisory**:
   - **What to change**: the edit, concretely, at the finding's location,
     drawn from the evidence. Not "improve the tests" but which function
     gains which assertion.
   - **The findings it answers**: each cited by its `findings.check` and its
     location, so the owner can trace the advisory back to the report.
   - **The order of its steps**, where the change has more than one: each
     step leaves the code working, so the change can stop after any of them.
   - **Its kind**: a refactoring, or **not a refactoring** (step 3).
3. **Mark each advisory by what it does to behaviour.** A refactoring changes
   the code's structure without changing what it does: every input gives the
   same output, the same errors and the same side effects as before. A change
   that alters any of that, even to fix a defect, is **not a refactoring**,
   and says so in its own line, for the owner: name the behaviour that
   changes, from what to what, so the owner decides it as a behaviour change
   rather than accepting it as cleanup. When unsure, mark it **not a
   refactoring**; the owner can relabel it, and a mislabelled behaviour change
   cannot be taken back after it ships.
4. **Carry the confidence through.** An advisory resting on a finding of
   `low` confidence says so, and says what would confirm the finding before
   the change is made.

### 3. Rank the advisories

Order the advisories so the first is the one to do first:

1. **By severity**: an advisory ranks at the highest `findings.severity` of
   the findings it answers, `critical` first, then `high`, `medium`, `low`
   and `info`.
2. **Then by reach**: among advisories of equal severity, the one that
   answers more findings ranks higher.
3. **Then by confidence**: among the rest, the one whose findings carry the
   higher `findings.confidence` ranks higher.

Where one advisory must land before another, because the second edits code
the first restructures, say so and keep that order even against the rank.

### 4. Implementation mode: answer the findings before the build

Read the same finding fields as step 2. A design document's finding is placed
by `findings.location.section`; a design read from code, by
`findings.location.file` and, where one applies, `findings.location.symbol`.

1. **Lay out the build** the design describes, from the design `input.scope`
   names: one step per piece a reviewer can read as one, such as a component,
   an interface or a storage choice, in the order the design's own
   dependencies require. Where the design leaves a step unstated, say so
   rather than invent it.
2. **Answer each finding before the work it affects.** A finding against a
   design is a gap in it: a decision with no alternative, a quality attribute
   with no measure, a structure the code contradicts. Write it as an advice
   item placed before the first build step resting on the part of the design
   it was found in, so the gap is closed before anything is built on it. A
   finding bearing on the whole design, such as missing non-goals, comes
   before the first step.
3. **Write each advice item**:
   - **What to do**: the decision to weigh, the measure to set or the step to
     build, concretely, at its section or file, drawn from the evidence.
   - **The findings it answers**: each cited by its `findings.check` and its
     location, so the owner can trace the item back to the report. A build
     step no finding bears on cites none, and says so.
   - **The work it holds back**: the build steps that wait on it.
4. **Order items that affect the same work** by `findings.severity`, then by
   `findings.confidence`, as step 3 ranks. Carry the confidence through as
   step 2 does.
5. **For a `design-from-code` input**, an item that edits existing code is
   marked as step 2 marks it: a refactoring, or **not a refactoring**.

### 5. Report

Write the advisories in the reply, in rank order, or for the implementation
mode in the order step 4 fixed, each with a number the owner can answer by.
Open with the report's `input.kind` and `input.scope`, the phases in
`phases.run`, each `phases.not-run` entry with its `reason`, the count of
findings read and the count of `unresolved` entries, so advice resting on
one phase, or on the checks that were judged, does not read as complete.
End with any finding no advisory answers, with why: a finding is never
dropped silently.

## Hand-off

An advisory, in either mode, is a recommendation, not work. The owner
accepts, rejects or amends each one by its number. **An advisory the owner
accepts is filed through `to-task`**, by the session that took the
acceptance, with the advisory and the findings it cites as the task's input.
This skill files nothing itself, before or after the owner answers.

## Guardrails

- **Recommend only.** Do not edit code, open a branch, run a fix, or file a
  task. Filing goes through `to-task`, after the owner accepts, in the session
  that took the acceptance.
- **Cite the report, not memory.** Every advisory answers findings the report
  holds, cited by check and location. Do not add an advisory for a problem the
  report does not record; if you notice one, say it is outside the report and
  suggest a re-evaluation.
- **Never label a behaviour change a refactoring.** A change that alters
  observable behaviour is marked **not a refactoring**, whatever its size.
- **Never build on an open finding.** In the implementation mode, no build
  step comes before the item answering a finding against the part of the
  design it rests on.
- **Read only fields the schema defines.** A field the report carries that the
  schema does not define is a malformed report, not extra input.
