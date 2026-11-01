---
name: research-base-audit
description: Audit a research base by re-verifying each living record against the authority it names — the contract, the code or an external source — and report which claims hold, which are contradicted or drifted, and which could not be checked, asking the user about each one rather than refiling or editing anything. Use when asked to "audit the research base", "re-verify the findings", "are our findings still true", or to check living research claims against their authorities.
allowed-tools: Read Grep Glob WebFetch Bash(python ${CLAUDE_SKILL_DIR}/scripts/validate_base.py *) Bash(python ${CLAUDE_SKILL_DIR}/scripts/index.py *)
disallowed-tools: Edit Write NotebookEdit
---

# Audit a research base

Re-verify every living record in a research base against the authority it
names, and report which claims do not hold for the user to decide.

Read [references/research-base-model.md](references/research-base-model.md)
first. Its *Audit means re-verification, not reconciliation* section is this
skill's charter, and *Citations, and which direction they are pinned in* says
what an `authority` names. Every key a record may carry is in
[references/record.schema.yaml](references/record.schema.yaml).

**The expensive failure is reporting health the audit never established.** A
claim it could not check, reported as holding, is worse than no audit: the next
reader trusts it.

## 1. Check the base with its own tooling

Run `python ${CLAUDE_SKILL_DIR}/scripts/validate_base.py --base <base>` first,
where `${CLAUDE_SKILL_DIR}` is this skill's own directory, which a Codex agent
resolves itself, and read its output, not only its exit code. Both scripts are
pre-approved in exactly the form this step gives, so type each command as
written.

- **A structural refusal stops the audit**: `base-file-missing`,
  `base-file-invalid` or `layer-directory-missing`. With no declared layers there
  is nothing to read. Report the refusal and stop.
- **Any other finding does not stop it.** Carry each into the report beside the
  audit's own results. A living record reported `authority-missing` is the
  contract's *cannot be audited* case: it gets no result of its own.

Then run `python ${CLAUDE_SKILL_DIR}/scripts/index.py --base <base> --check` and
report whether the index is stale. A stale index is reported, never rebuilt here.

## 2. Choose what is audited

The subject is every living record in a tracked layer: `regime: living` in its
frontmatter. **Frozen records are outside the audit's subject entirely.** A
frozen record described a moment and never claimed the present, so re-verifying
one is a category error.

## 3. Re-verify each claim against its authority

Read what the record says is currently true, then check it against each entry
in its `authority`, located by the form it takes:

- **A document in a repository**, such as the contract: read it as it stands
  now, and check the claim against the passage it names. `path:Name` names a
  heading or a symbol, as the contract's *Citations* section defines.
- **Code**: find the symbol or path by name, never by a line number, and check
  the claim against what the code does now.
- **An instrument**, a code entry followed by the inputs it ran on: re-run it
  over those inputs and judge the clause against what it reports. A
  deterministic instrument over committed inputs is re-run without asking
  first. Before a live run, one that spawns an agent or a model, or a run over
  inputs in a private layer, ask the user, once per clause. A declined run
  leaves that clause *not checked*, and its note names the reason; it is never
  *drifted*. No instrument is pre-approved, because none sits at a path this
  skill can know, so a re-run asks permission.
- **An external source**: fetch it when you can, and record the access date
  beside the result. A `WebFetch` read returns a summary of the page, not the
  page: it counts for a passage it returns verbatim that matches the claim, and
  so can support *holds*. A result that rests on what a page does not say, or
  says otherwise, needs a raw read with `curl`, which this skill does not
  pre-approve, so it asks permission. Without one, that part is *not checked*.

**What is judged.** The parts of a record are its *Claim* section and every
section whose level-2 heading begins with *Application*. One part is one
paragraph or one list item. Inside a part, each clause that asserts a fact is
judged. A clause about the record itself, its status, confidence, scope or
provenance, or a decision, is not a claim about the present and is not judged.
A decision is an imperative or a recommendation addressed to the reader; a fact
embedded in one is still judged, and a hypothesis or an argument the record
states is judged as a claim. Provenance means the history of the record's own
wording; a clause saying what this lab has or has not tested, or recounting a
test the record ran, is a fact about the present and is judged.

A dated note, one opening with a date and a verb such as *AMENDED*, *Updated*,
*Rewritten*, *Restated* or *Added*, is judged together with the passage it
names, or else the passage it directly follows, never as a part of its own.
Where a note corrects a sentence, the passage is judged as the note corrects
it, and the original sentence stands only as history. Every other section is
support: read it to judge the parts, never judge it.

**Several entries.** An entry is relevant to a clause when its subject covers
what the clause claims. A clause takes the worst result among its relevant
entries, and a part takes the result of its worst clause. A clause is *drifted*
by silence only when every relevant entry is silent on it, and an entry on
another subject is never counted as silent. A clause no entry is relevant to is
*drifted*, and its note says that nothing the record names can check it. A
clause stays judged where the record itself says its authority cannot check it
and names no instrument for it: it is *drifted*, and its note names that
admission.

Give each record exactly one result, judged against the authority as it stands
now:

- *holds* — the authority says what the record says;
- *contradicted* — the authority says otherwise;
- *drifted* — the authority, as it stands now, weakens the claim without
  reversing it, or says nothing on a part of it;
- *authority missing* — the named document, symbol or source does not exist or
  does not resolve;
- *not checked* — the authority could not be reached or read this run.

**When the disagreement began is not part of a result.** A claim that never
matched its authority and one whose authority has moved since get the same
result, because the audit reads the authority as it stands, not its history.

**The worst part sets the result.** Where a record's claim has several parts,
judge each, and give the record the result of its worst, in this order:
*contradicted*, *authority missing*, *drifted*, *not checked*, *holds*. Every
other part that disagrees is asked about in step 4, as a note on the record's
question. A part with no judged clause takes no result: it does not count toward
the worst part, and the report lists it as having nothing to judge, never as
*holds*.

A result is never better than the evidence read this run. **One failed fetch is
not the contract's retirement case**: *permanently unavailable* is a judgement
about the future, and one run cannot make it. Report *not checked*, and name
retirement to frozen only as a decision the user may take.

## 4. Ask about what needs a decision

On every run, with no parameter, put each finding to the user as its own
answerable question: each *contradicted*, *drifted* or *authority missing*
result, and each validator finding carried into the report. For each *not
checked* authority, ask the user to confirm it or to leave it *not checked*. A
result the user confirms is reported as *confirmed by the owner*, with the date,
and never as *holds*.

Each question about a *contradicted*, *drifted* or *authority missing* result
names both remedies: correct the claim, which moves the record's `updated`, or
re-cite or pin the authority, which does not. Where evidence already read this
run shows the disagreement predates the record's `updated`, the question says
so, as a note. No history is searched for it, and its absence says nothing
about when the disagreement began.

**Never ask what you could read yourself.** A question about a fact the
repository or a reachable source already settles spends the user's attention on
the audit's own work.

State each question as a form, not a tool: where the harness offers a structured
prompt it renders that way, and where it does not, ask in numbered prose.

## 5. Report

Shape the report per [references/report-form.md](references/report-form.md).
Give the count of living records audited and the count in each result, then:

- every finding, with its question;
- whether the index is stale;
- what was not checked, and why.

**An audit reports; it does not refile.** What the user decides about a finding
is theirs to carry out: a corrected claim, a lowered confidence, a record
retired to frozen. None of those is a step of this skill.

## Guardrails

- Do not edit, move or retire a record, and do not write `base.json`.
- Do not audit a frozen record.
- Do not report *not checked* or *confirmed by the owner* as *holds*.
- Do not report a record better than its worst part.
- Do not judge a section other than *Claim* and *Application*.
- Do not judge a clause about the record itself.
- Do not report a part with nothing to judge as *holds*.
- Do not report what a page does not say from a `WebFetch` read alone.
- Do not judge a measured clause *drifted* because a re-run was declined.
- Do not search an authority's history to write a note.
- Do not treat one unreachable source as permanently unavailable.
- Do not regenerate the index; report it stale.
- Do not ask the user a question the repository or a reachable source answers.
- Do not continue past a structural refusal from the validator.
- Do not commit.

## Resources

- What a research base is, and what its audit is for:
  [references/research-base-model.md](references/research-base-model.md)
- Every frontmatter key and rule, as a schema:
  [references/record.schema.yaml](references/record.schema.yaml)
- The base's checker: `scripts/validate_base.py --base <base>`
- Index staleness: `scripts/index.py --base <base> --check`
- How the report is shaped: [references/report-form.md](references/report-form.md)
