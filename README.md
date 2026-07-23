# Skills

Published agent skills. This repo is the distribution point — skills are
developed and iterated on in [`skill-lab`](../skill-lab/), then published here
once they are worth using.

## Status

Nothing published yet. The repo is intentionally empty apart from this README
while the structure is decided.

## Intended direction

A multi-platform skills repo: each skill carried in a form that works across
agent runtimes rather than Claude Code alone.

Open questions to settle before the first publish:

- **Layout** — one directory per skill at the root, or grouped by domain.
- **Multi-platform shape** — how per-runtime metadata is carried alongside a
  shared `SKILL.md`. The lab already separates these: a common core plus
  `agents/openai.yaml` for Codex, with `tools/generate_claude.py` emitting the
  Claude Code variant.
- **Publish mechanism** — a script in the lab that syncs built skills here,
  versus this repo pulling from the lab.
- **Install path** — whether the repo is meant to clone straight into
  `~/.claude/skills/`, which constrains the root layout to one dir per skill.

## Candidate first publish

The four Diataxis documentation lifecycle skills in the lab:
`diataxis-migrate-docs`, `diataxis-audit-docs`, `diataxis-update-docs`,
`diataxis-manage-docs`.

## Source material

Skills are often built against real, private material. That material never
belongs here. `refs/` and `_private/` are gitignored at any depth as a
backstop, but the rule is that private inputs stay in the lab.
