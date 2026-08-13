# Skills

Agent skills for Claude Code and Codex — 16 of them, covering three workflows:
turning work into tracked tasks and running them, keeping documentation honest
against the code, and the daily loop of committing, handing off, and cleaning up.

A skill is a folder of instructions an agent loads when a task matches it. It
does not run code on its own or change how the agent is configured; it tells the
agent how to do one job carefully, and it is inert until something invokes it.

## Layout

One directory per skill, under a subtree per runtime:

```text
skills/
├── claude/
│   └── <skill>/        # SKILL.md + references/, scripts/, assets/
└── codex/
    └── <skill>/        # same SKILL.md, plus agents/openai.yaml
```

Both subtrees hold the same skill bodies. They differ only in the frontmatter
and sidecar metadata each runtime expects, so install from the one that matches
your agent rather than cloning the repo wholesale.

## Installing

Copy the skill directory you want into your runtime's skills directory:

```bash
# Claude Code
cp -r claude/<skill> ~/.claude/skills/<skill>

# Codex
cp -r codex/<skill> ~/.codex/skills/<skill>
```

For Claude Code, `~/.claude/skills/` makes a skill available everywhere;
`<project>/.claude/skills/` scopes it to one repository. Copy the whole
directory — `references/`, `scripts/`, and `assets/` are part of the skill, and
a `SKILL.md` on its own will fail partway through.

Every skill triggers on description match, so you can simply describe the job
("audit the task board", "write a handoff"). The one exception is **commit**,
which is deliberately invocation-only — call it as `/commit` in Claude Code or
`$commit` in Codex, so it never fires on its own against a live working tree.

## The skills

### Task board

A file-based task board that lives in the repository, so the plan and the code
travel together and survive losing a session. Start with **task-board-init**;
the rest operate on the board it creates.

| Skill | What it does |
| --- | --- |
| `task-board-init` | Create a board, or adopt scattered planning docs into one |
| `to-task` | Write a grounded, self-contained task spec onto the board |
| `task-interview` | Grill a draft task until its open questions become decisions |
| `focused-implementation` | Take one scoped task to done, in tested slices |
| `orchestrate-implementation` | Group several non-interfering tasks and run them together |
| `to-follow-on` | Carve work off an in-flight task into its own task |
| `task-board-triage` | Reconcile board state with what the repo actually shows |

### Diataxis documentation

Restructure and maintain documentation under the
[Diataxis](https://diataxis.fr) framework, treating existing docs as something
to migrate with an audit trail rather than rewrite. **diataxis-manage-docs**
diagnoses which of the others a repository needs.

| Skill | What it does |
| --- | --- |
| `diataxis-manage-docs` | Diagnose doc maturity and route to the right phase |
| `diataxis-migrate-docs` | Migrate legacy docs into Diataxis, preserving coverage |
| `diataxis-audit-docs` | Check migrated docs for drift, gaps, and coverage |
| `diataxis-update-docs` | Sync docs with shipped behavior since a baseline |

### Daily workflow

Independent of the other two families. Each is useful on its own except
**handoff** and **resume-handoff**, which are the two halves of one cycle —
one writes the document at a context boundary, the other picks it up on the
far side.

| Skill | What it does |
| --- | --- |
| `commit` | Split the working tree into clean, revertible commits |
| `handoff` | Write a handoff doc a fresh session can resume from |
| `post-creation-audit` | Test, document, clean up, and land a block of work |
| `resume-handoff` | Resume from a handoff: verify, check in, then act |
| `spike` | Throwaway prototype in scratch space to answer one question |

## Conventions these skills assume

Several skills encode opinions. They are stated in each skill's `references/`
so you can see and change them:

- **Commit format** — `type(topic): summary` over a four-type vocabulary
  (`fix`, `feat`, `test`, `chore`). Used by `commit`, `post-creation-audit`,
  `handoff`, and `spike`.
- **Authorship** — the commit convention defaults to recording no agent as
  author or co-author. It is a stated default with its reasoning, not a mandate;
  invert that section if your project requires AI-contribution disclosure.
- **Task frontmatter** — the board skills share one task schema and filing
  rule. Changing it means changing it for all of them.

Read the skill before installing it. These are instructions your agent will
follow on your repository, and they are short enough to review.

## About these bundles

The directories here are generated from a separate authoring repository, where
each skill is written once and projected onto both runtimes. That is why the
two subtrees are identical apart from frontmatter, and it means edits made
directly to a bundle here would be overwritten by the next publish — adjust
your installed copy instead.

## License

[MIT](LICENSE). Use, adapt, and redistribute these skills freely; keep the
copyright notice.
