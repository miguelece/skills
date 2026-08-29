# Invocation grammar

How a skill takes a parameter on the invocation line. Two families exist here and
they are not interchangeable: one names a thing, the other selects a mode.

Cite this file from a skill that takes a parameter. A skill that takes none does
not carry it, and that is the point of the holder list below.

## The holders, and the list is the enforcement

| Skill | Parameters |
| --- | --- |
| `handoff` | `into <agenda>` |
| `resume-handoff` | `from <path>`, `into <agenda>`, `+question` |
| `post-creation-audit` | `+commit`, `+git`, `+question` |

A skill absent from this table does not take a parameter. Adding one to a skill
that is not listed is a change to this document as well as to that skill.

Nothing mechanical holds that rule, which is exactly why the list is written
down rather than left implied. A grammar defined for three skills and silently
assumed for the rest is the defect this file exists to close.

## Family 1 — word-keyed, and it takes an argument

`from` and `into` each introduce an argument and name a thing. `from` takes one
token, a path. `into` takes the rest of the line, an agenda. The object types
differ, so either order parses unambiguously.

A bare argument is refused rather than guessed. `/resume-handoff next steps`
could be a path or an agenda, and the only way to tell them apart is testing
whether it resolves on disk — a guess that misclassifies a mistyped path in
silence.

`into` means the same thing in both holders: *the agenda is X*. Only the
addressee differs — `handoff` records it for a future session, `resume-handoff`
acts on it in the present one. A keyword whose meaning lives in one skill's
prose is how the two ended up contradicting each other once already.

## Family 2 — modal flags, and they take no argument

The sigil is `+`. It is visibly not an English word, which is the property a
word-keyed parameter lacks, and it transports intact: the argument string
arrives as typed, and the only reserved character is `$`.

### Flags compose as an unordered set

`+git +question` and `+question +git` are the same invocation. Flags are a set
and never a sequence. Order-independence costs nothing to specify, because the
arguments arrive as one string.

### An implication may only ever add

A flag may switch another on. `+git` implies `+commit`, because a flag that
manages merges and pushes but not commits is incoherent.

Two rules keep that from compounding. Every implication is stated where the
flags are stated, never only in a body nobody reads. And every implication
carries the reason it exists, so a later reader can tell a designed implication
from an accumulated one.

An implication that switched a flag *off* is forbidden. That would reintroduce
the hidden subtraction the next rule exists to prevent.

### `+` never subtracts

A flag may change a shipped default — `post-creation-audit` no longer commits
unless asked. But the subtraction is a one-time redefinition of the base, not
something the flag does. Once the base is redefined, `+` only ever adds to it.

The obligation that comes with redefining a base: it is visible in the skill's
`description`, not only in its body. Someone who invokes the skill the way they
always have must be able to see that it now stops short.

### A flag means the same thing in every holder

`+question` is held by `post-creation-audit` and `resume-handoff` and means the
same in both: stop and ask about the items that need a decision, rather than
only listing them. This mirrors `into`, whose meaning is fixed across its two
holders while only the addressee differs.

What it does not control is whether those items are surfaced. Both skills
separate them under their own heading on every run, flagged or not. The flag
adds the interruption and never the separation — `+` never subtracting, applied
to a flag that arrived after the behaviour it modifies.

## Where a parameter is taught

Tersely in `description`, fully in the body.

`description` is the retrieval signal and it is what a listing shows. Listings
are length-capped and the trigger must come first, so a grammar clause at the
end of a long description is exactly what a truncating listing drops. Keep the
clause short enough to survive rather than long enough to explain.

The body is neither the retrieval signal nor length-capped, so the full
semantics belong there. Do not attempt worked examples of every flag in a
`description`.

Put the clause in `description` and not in `when_to_use`: the Codex adapter
emits `name` and `description` alone, so a grammar taught in `when_to_use` is
invisible on one of the two platforms and outside every description contract.
