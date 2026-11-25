# Module contract

What a module of the evaluation library is, so the router can choose modules
without reading them whole and every module can be checked the same way. The
shape follows the rule metadata of established analysers, recorded in
[prior-art.md](prior-art.md): a rule carries its own rationale, references,
severity and language scope, and a result carries its location and evidence.

## Layout

```text
references/modules/
├── index.yaml              # the router's module index
└── <module-id>/
    ├── module.yaml         # the header and the checks
    ├── research.md         # the module's own findings file
    ├── examples.md         # a bad and a good example per check, read on demand
    └── ...                 # any guidance the checks need, loaded on demand
```

- **`index.yaml`** holds one `modules:` list of module ids. Every id listed
  has a directory, and every directory is listed: the index and the library
  agree in both directions, so the router never offers a module that does not
  exist or misses one that does.
- **A module is self-contained.** Its files link only to each other and to
  the web. It ships inside a public bundle, so it never links into the
  repository it was authored in and never carries an absolute home path.

## The header

`module.yaml` declares each of these fields. Every field is required.

| Field | Value |
| --- | --- |
| `id` | kebab-case, equal to the module's directory name, unique in the library |
| `languages` | a list of kebab-case language names, or exactly `[language-neutral]` |
| `concept` | one kebab-case name for what the module evaluates, such as `testing` |
| `triggers` | a mapping writing all four trigger kinds below; at least one is non-empty |
| `inputs` | the input kinds the module supports, a non-empty subset of the four below |
| `phases` | the phases the module serves, a non-empty subset of the two below |

`language-neutral` is for a module about a concept no language owns, an
architecture or a design practice. It is never listed with a language.

**Triggers** say when the router loads the module. Each kind is a list of
strings, and every header writes all four, as `[]` where empty, so a header
that omits a kind is refused:

- `files`: glob patterns over paths, such as `**/test_*.py`.
- `manifests`: a manifest file, optionally with a marker inside it, written
  `file:marker`, such as `pyproject.toml:[tool.pytest.ini_options]`.
- `design-markers`: words that mark a design document as the module's
  subject, for the two design input kinds. One matches wherever it appears
  in the design read, as a word in the prose or as a heading.
- `design-headings`: plain strings that mark a design document as the
  module's subject, for the two design input kinds, matching only when one
  appears as a heading of the design read, never as a word in the prose.
  Use it where a common word, such as *Decision*, would load the module on
  nearly any design text. An entry is written without a `#` prefix.

**Input kinds**, as the report schema enumerates them:

- `diff`: a change between two revisions. A finding sits in the changed
  lines, while the evidence it rests on, a configuration file, a helper's
  body or a declaration, may be read anywhere in the repository at the new
  revision. A check may narrow this in its own `evidence`, as one reported
  only when the diff changes the setting it reads.
- `repository`: a whole codebase at one revision.
- `design-from-code`: the design a codebase embodies, read from it.
- `design-document`: a design written down, before or without code.

**Phases**: `static`, which reads without running anything, and `dynamic`,
which stands the application up and observes it. A check has no phase of its
own: the router loads a module's checks whole once its header matches a phase
of the run, so dynamic checks live in a module of their own, declaring
`phases: [dynamic]`. Such a module serves neither design input kind, since a
design has nothing to start.

## Checks

`module.yaml` also holds a `checks:` list, at least one entry. Each check
declares every one of these fields:

| Field | Value |
| --- | --- |
| `id` | `<module-id>/<name>`, both halves kebab-case, unique in the library |
| `statement` | the defect, in one sentence, as it would be reported |
| `evidence` | what a finding must show before it is reported |
| `severity` | `critical`, `high`, `medium`, `low` or `info` |
| `rationale` | why the defect matters: what goes wrong if it ships |
| `references` | at least one external http(s) URL the check rests on |
| `findings` | at least one bare id of a finding in this module's `research.md` |

`references` and `findings` sit side by side. `findings` names the research
the check rests on, by the ids the findings file gives it, never prefixed with
the module id, since a finding id is unique only within its module.
`references` keeps the URL in reach of the agent running the check, which
reads `module.yaml` and not the findings file, and it may be a deeper link
than the finding's source records.

The `evidence` field is the check's verification rule: a finding that cannot
show it is not reported. The severity scale is the report schema's, mapped to
SARIF levels there.

A case a check's `evidence` names as unresolved is recorded in the report's
`unresolved` list, with the reason it could not be decided: it is never
reported as a finding, and never read as a pass.

A check whose verdict depends on a tool's version names, in its `evidence`,
where that version is read and what is reported when it cannot be read; a
case it cannot decide is named as unresolved, and goes in `unresolved`.

## The findings file

`research.md` is the module's own research: the findings its checks rest on,
with their sources. A module carries its research with it and depends on no
research held anywhere else. Its YAML frontmatter holds two lists:

- `sources`: each with an `id`, a `title`, an http(s) `url` and a `date`,
  `YYYY-MM-DD`, the date the source was published or read. At least one.
- `findings`: each with an `id`, a `claim`, a `confidence` mark and the
  `sources` it cites by id. At least one.

The confidence mark says how far the cited sources carry the claim:

- `directional`: the sources point this way but do not settle it.
- `evidenced`: a source states or demonstrates it directly.
- `strong`: several independent sources, or a primary specification, agree.

That scale is about a research claim. It is distinct from a report finding's
`confidence`, which says how sure one run is of one detection.

Every finding is cited by at least one check's `findings`. A finding that
supports no check, such as one that only explains why a check is absent,
belongs in the prose body instead.

The body below the frontmatter is free prose: how the findings were reached,
and what they do not cover.

## The examples file

`examples.md` holds worked examples of the module's checks: one section per
check, so a reader can see each defect before judging a finding of it. It is
read on demand, like any other guidance file, when a check's `statement` or
`evidence` leaves a case unclear; the router does not load it with the
checks.

- **One section per check id.** Each section's heading is a level-two
  heading holding the check's full id, `<module-id>/<name>`, and nothing
  else. Every
  check in `module.yaml` has a section, and every section names a check: the
  two agree in both directions, as checks and findings do. The sections
  follow the checks' order in `module.yaml`, so a reader who knows where a
  check sits finds its example in the same place.
- **A bad and a good example in each section.** The bad example shows the
  defect the check's `statement` names and satisfies its `evidence`. The
  good example is the nearest correct version, and does not trigger the
  check. Each is introduced by a line reading `**Bad.**` or `**Good.**`, so
  no heading repeats between sections, and is short, usually one code block.
- **Examples are invented for the purpose.** They quote no real codebase and
  no private material, and they follow the module's link rule: no link out
  of the module and no home path.

A heading inside a fenced code block is code, not a section. Every module
carries the file: a module without it is refused, as one without
`research.md` is.

## How the contract is checked

A static contract suite in the authoring repository checks every module
against this document: each header field present with an allowed value, each
check with a rationale and an external reference, a findings file citing at
least one dated source, checks and findings linked both ways (each check's
`findings` naming only ids its `research.md` records, and each finding there
cited by some check), an examples file with a section for each check, in
the checks' order, and none for anything else, no link out of the module and
no home path, unique module and check ids, and an index that matches the
directories both ways.
