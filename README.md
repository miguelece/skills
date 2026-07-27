# Skills

Published agent skills. This repo is the distribution point — skills are
developed and iterated on in [`skill-lab`](../skill-lab/), then published here
once they are worth using.

## Layout

One directory per skill, under a subtree per agent runtime:

```text
skills/
├── claude/
│   └── <skill>/            # SKILL.md (+ references/, scripts/, assets/)
└── codex/
    └── <skill>/            # same SKILL.md, plus agents/openai.yaml sidecar
```

A skill is authored once, platform-neutrally, in the lab; the build projects it
onto each runtime. The two subtrees hold those projections — the same body with
the frontmatter and sidecars each runtime expects.

## Installing a skill

Copy the skill directory into the runtime's skills directory — for Claude Code,
`claude/<skill>/` into `~/.claude/skills/<skill>/`; for Codex, `codex/<skill>/`
into `~/.codex/skills/<skill>/`. The subtrees keep the two runtimes' variants
from colliding, so the repo is installed from per-runtime, not cloned wholesale.

## Publishing

`skill-lab/tools/publish.py` is the one-way sync from lab to here. For each
skill it builds the requested platform fresh from canonical sources, runs a leak
guard, writes `skills/<platform>/<skill>/`, and commits.

```powershell
python tools/publish.py projects/<project> --yes                 # all platforms
python tools/publish.py projects/<project> --platform claude --yes
```

Building fresh means a publish can never ship a stale or hand-edited bundle.

## Source material

Skills are often built against real, private material. That material never
belongs here. `refs/` and `_private/` are gitignored at any depth as a backstop,
the publish build reads only the skill's own sources (never `refs/`), and the
leak guard refuses a bundle carrying real emails, absolute home paths, or any
term in an optional private denylist. The rule remains: private inputs stay in
the lab.

## What's published

Sourced from these lab projects — see the directory tree for the current set:

- `diataxis-doc-migration` — Diataxis documentation lifecycle skills.
- `task-board-management` — file-based in-repo task board skills.
- `quality-of-life` — dev-workflow conveniences (commit, handoff, spike, audit).
