# Create workflow details

## Classifying a page

Diataxis types answer different reader needs, and a page serves one:

| Reader need | Type | Template |
| --- | --- | --- |
| Learn by doing | Tutorial | `assets/tutorial.md` |
| Accomplish a known task | How-to | `assets/how-to.md` |
| Look up a fact | Reference | `assets/reference.md` |
| Understand why | Explanation | `assets/explanation.md` |

A request phrased as one type can need another. "A tutorial listing every
option" is reference; "a how-to explaining our architecture" is explanation.
Propose the type the content needs and say why.

## Anchoring claims

An anchor names the file and symbol that owns the claim, at the current
revision. Prefer the code path a real entrypoint reaches over a test, a schema
or a fixture. A value that only an existing doc states is not anchored: the doc
may be stale, and an existing page that disagrees with the code is reported as a
contradiction for `diataxis-update-docs` rather than corrected here.

Pending proposals, specs and unwired implementations are not shipped behavior.
A page may mention a proposal only as a proposal, and only when the author asks
for it.

## Bootstrap order

The four steps of the fixed order are considered in sequence, and each candidate
is recorded with its outcome:

```text
reference   for each public entrypoint   kept | dropped: <reason>
tutorial    one getting-started path     kept | dropped: <reason>
how-to      each operational task        kept | dropped: <reason>
explanation each recorded decision       kept | dropped: <reason>
```

An entrypoint that nothing reaches is dropped from reference and recorded as a
suspected code finding. A step that keeps nothing is still listed.

## Manifest records

A create run sets `run.mode` to `create`. It writes no `section_ledger` entries
and creates no archive, because it moves no existing material. Record each
claim's owning source under `claim_authorities`, the anchors under `evidence`,
excluded claims and suspected defects under `findings`, and every check under
`verification`.

A bootstrap performs a full scan, so after its pages and checks are verified it
may set `update_baseline.revision` to the verified current commit, giving later
incremental updates a valid start. A single-page run scans only what its page
needs, so it leaves `update_baseline` unchanged.
