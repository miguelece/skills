---
name: synthesize-research
description: Turn raw skill-craft material in research/sources/ into a cited, confidence-marked finding in research/findings/, regenerate the index, and flag anything ready to promote into the standards. Use when working in the skill lab and asked to "synthesize this research", "write this up as a finding", "compile the research", "turn these sources into a finding", or to review whether a finding is ready to promote.
allowed-tools: Read Grep Glob Edit Write Bash(git check-ignore*) Bash(python ${CLAUDE_SKILL_DIR}/scripts/index.py *) Bash(python ${CLAUDE_SKILL_DIR}/scripts/validate_base.py *)
---

# Synthesize research into a finding

Compile raw material into one finding that carries its own evidence, and keep the
research base honest.

Read [references/research-base-model.md](references/research-base-model.md) for
what a research base is: location keyed to kind, state in frontmatter, and the
frozen/living split that decides whether anything re-verifies a record.

Then find the base you are working in — the directory holding its `base.json`,
which names its layers — and read that base's own `README.md`. In this lab the
base is `research/`, and its pipeline runs from `sources/` (raw, private) to
`findings/` (synthesis, committed) to `standards/` (promoted guidance). Do not
restate either document here; follow them.

## When this applies

Synthesizing sources into a finding, sharpening an existing finding with new
evidence, or judging whether a finding is ready to promote. Not for domain research
a single skill needs — in this lab, that belongs in the project's `refs/`.

## Boundaries

- **Confidence is the whole game. Never launder it.** A claim is `directional`
  unless the evidence is concrete and checkable. Do not upgrade `directional` to
  `evidenced` by dropping the caveat — an overstated finding gets promoted and then
  silently steers everything written after it.
- **Never invent evidence.** No fabricated statistics, no citations to sources that
  are not in the base's private layer or a real public URL. "Studies show" with no
  traceable source is a directional claim at best, and usually not even that.
- **Cite private sources by name; do not paste them.** Small quoted excerpts are
  fine. A whole copyrighted article belongs in the private layer, which is
  gitignored — never copy it into a committed finding.
- **Do not promote into the repository's guidance on your own.** Promotion edits
  guidance other work follows. Propose it and get explicit approval; the skill's
  job ends at *recommending* promotion with the evidence.
- **One finding, one claim.** If the material carries two separable conclusions,
  write two findings.

## Procedure

1. **Confirm the material is in the base's private layer** — the untracked layer
   `base.json` declares. If it is not there yet, move it there before working, and
   verify with `git check-ignore <base>/<layer>/<file>`. Working from material
   pasted into the chat loses the provenance the finding needs.
2. **State the claim in one line** before writing anything else. If you cannot, this
   is `status: exploring` — record the open question and what evidence would settle
   it, and stop there.
3. **Read the sources and ground the finding in them.** Separate what a source
   actually establishes from what merely sounds right. Note contradictions between
   sources rather than picking the convenient one. The `authority` step 5 names
   must be one of the sources read here, and you must have checked that it states
   the claim. A source cited for background is not an authority until it does.
4. **Draft from [assets/finding.md](assets/finding.md)** into the base's synthesis
   layer. Keep claim, evidence, caveats, and application in their separate
   sections. The application section is what may later become a line in the
   repository's guidance, so make it an actionable rule, not an observation.
5. **Fill the frontmatter honestly.** `kind` must match the layer's declared kind,
   and a finding that claims the present is `regime: living`, so it names the
   `authority` it is re-verified against. That authority is one step 3 read and
   checked as stating the claim; a first-hand measured claim names its
   instrument, by `path:symbol` and the inputs it ran on. A private input goes in
   `sources`, never in `authority`. Mark `status` and `confidence`, and fill
   `sources` and `informs`. Re-read the evidence section and check every claim in
   it is marked at the confidence the evidence actually supports.
6. **Regenerate the index and check the base.** Run
   `python ${CLAUDE_SKILL_DIR}/scripts/index.py --base <base>`, where
   `${CLAUDE_SKILL_DIR}` is this skill's own directory, which a Codex agent
   resolves itself. Then run the same command with `--check` to confirm it is
   clean. Both scripts are pre-approved in exactly the form this step gives, so
   type each command as written. The index reads every tracked layer the base's
   `base.json` declares and splices the index into its `README.md`; a base with
   no `base.json` is refused with exit 2. Then run
   `python ${CLAUDE_SKILL_DIR}/scripts/validate_base.py --base <base>` and read
   its output, not only its exit code.
7. **Assess promotion.** If the finding is `supported`, `evidenced` or better, and
   generalizes past one case, say so and propose the exact one-line rule and the
   section of the guidance it would join — but do not edit that guidance without
   approval.

## Guardrails

- Do not write a finding whose claim you cannot state in one line — that is notes,
  and it stays `exploring`.
- Do not mark a claim `evidenced` without a source you can point to or a run you can
  reproduce.
- Do not name an authority the synthesis did not read and check against the
  claim.
- Do not copy a whole third-party source into a committed finding.
- Do not edit the repository's guidance to promote a finding without explicit
  approval.
- Do not file domain research here; in this lab it belongs in the relevant
  project's `refs/`.
- Do not leave the index stale — regenerate it, and confirm with `--check`.

## Resources

- What a research base is, and what a record carries:
  [references/research-base-model.md](references/research-base-model.md)
- Every frontmatter key and rule, as a schema:
  [references/record.schema.yaml](references/record.schema.yaml)
- Finding template: [assets/finding.md](assets/finding.md)
- Index generator: `scripts/index.py --base <base> [--check]`
- The base's checker, and the one frontmatter parser the index reads through:
  `scripts/validate_base.py --base <base>`
