---
name: capture-knowledge
description: Capture one item learned in a session — a claim, a note, or a reference to a committed research finding at its commit — into a central knowledge base's private sources layer, named by date and slug, with its origin repository and record and the evidence it rests on, for a later digest to turn into a finding. Use when asked to "capture this", "file this in the knowledge base", "save this to .knowledge", or to promote a transferable finding from this repository by reference.
allowed-tools: Read Grep Glob Write Bash(python ${CLAUDE_SKILL_DIR}/scripts/capture_path.py *)
---

# Capture knowledge

File one item a session learned into a central knowledge base, on the user's
command: a claim or a note, or a committed research finding by reference. A
later digest turns captures into findings; a capture is its input, not a
finding.

Read [references/research-base-model.md](references/research-base-model.md)
first. *Kind and tracking are independent axes* says why a capture is raw input
and goes in the private layer, *Declaring the layers* says how a base names its
layers, and *Citations, and which direction they are pinned in* gives the one
form for naming a record in another repository.

**The expensive failure is a capture that reaches a commit.** It may quote
another repository's private material, and a commit is removable only by
rewriting history. So the path is never chosen by hand: a script names it, and
only inside the private layer, where git ignores it.

## 1. Find the knowledge base

Read its location from the user's own instructions: a line in their
`CLAUDE.md`, `AGENTS.md` or equivalent naming where the knowledge base lives.
**With none, ask the user where it is**, and stop until they answer. Do not
search the disk for a likely directory, and do not fall back to the current
repository's own research base: knowledge about one repository stays in it.

The base is the directory holding `base.json`. A base without one is refused,
not guessed at.

## 2. Decide what is captured

One capture holds one item. Before writing, settle four things:

- **The claim or note**, in your own words, a sentence or a short paragraph.
  It should hold beyond the repository it was learned in; if it is only about
  that repository, say so to the user and suggest its own research instead.
- **The slug**, kebab-case, naming the claim rather than the session.
- **The origin**, in the cross-store form of *Citations*:
  `<repository>:<path-in-repository>`, with `#<heading>` to name one entry
  inside a file and `@<sha>` last to pin it. `<repository>` is the repository's
  directory name, never a machine path. Name the record the item came from: a
  finding, a task, a source file or a commit.
- **The evidence**: what the claim rests on — a measurement, a passage, a
  commit, a test — each named as the origin is, or by URL with an access date.

**A committed research finding is captured as a reference at its commit, not a
copy.** Pin it to the commit that last changed it
(`git -C <repository> log -1 --format=%h -- <path>`), state its claim in one
sentence, and leave the finding where it is. A short quoted excerpt is fine;
the finding's text is not pasted in. If the record has uncommitted changes, a
pin would name a version that does not say what you read: tell the user, and
capture it only once it is committed or as an unpinned, living reference they
accept.

## 3. Name the path

Run `python ${CLAUDE_SKILL_DIR}/scripts/capture_path.py --base <base> --slug <slug>`,
where `${CLAUDE_SKILL_DIR}` is this skill's own directory, which a Codex agent
resolves itself; the script is
[scripts/capture_path.py](scripts/capture_path.py), and its docstring carries
every refusal. It reads `base.json` through
[scripts/validate_base.py](scripts/validate_base.py)'s reader, picks the one
untracked layer of kind `source`, checks that git ignores the path, and prints
`<base>/<layer>/<date>-<slug>.md`. It writes nothing.

**Write the capture only to the path it prints.** Exit 2 is a refusal with its
rule id in brackets: report it and stop, or, for `capture-exists`, choose
another slug. A refusal is never routed around by writing elsewhere.

## 4. Write the capture

```markdown
---
title: <the claim, as a sentence>
kind: source
regime: frozen
updated: <date>
sources:
  - <origin, in the cross-store form>
---

# <the claim, as a sentence>

## Claim

<the claim or note, in your own words>

## Origin

- <origin>, captured from <repository> on <date>.

## Evidence

- <each piece of evidence, named, with what it shows>
```

A reference capture's *Claim* is the finding's claim in one sentence and its
*Origin* is the pinned reference; nothing more of the finding is carried.

## 5. Confirm it stayed private

Run `git -C <base> status --porcelain`. **Nothing new may appear**: the capture
is ignored, so the status is what it was before. If the capture shows, delete
the file you just wrote, report it, and stop. Then tell the user the capture's
path and that it is not backed up until a digest turns it into a tracked
finding.

## Guardrails

- **Do not commit** anything in the knowledge base or the origin repository.
- **Do not force-add** a capture, or anything under a private layer; it is the
  one command that overrides an ignore rule.
- **Do not write a capture anywhere but the path the script prints**, and do
  not create the private layer's ignore rule yourself to make a refusal pass:
  ask the user.
- **Do not copy a committed finding into a capture**; reference it at its
  commit.
- **Do not put a machine path in a capture.** The origin names a repository by
  its directory name, so the capture means the same on every machine.
- **Do not guess the base's location.** It comes from the user's own
  instructions or from the user.
