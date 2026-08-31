# Report form

How to shape a report to the user in chat. Skills that end in a report already
fix *what* to say and *in what order*; this file covers the form that result
takes — emphasis, headings, and what must survive being made shorter.

Cite this file from the step where your skill reports, not from its preamble.
The rules are worth loading at the moment a report is about to be written and
cost nothing before that.

## Two subjects this does not govern

Kept apart by name, because conflating them has already wrecked this subject
twice.

- Conciseness of skill prose — how a `SKILL.md` is written for an agent to read.
  That is `standards/skill-authoring-guide.md`'s subject and is settled there.
- The shape of a document a skill writes to disk — a handoff, a task, a finding.
  Those carry their own prescribed structure, and the rules below do not apply
  to them. A handoff's nine headings are not subject to a heading threshold.

What is left is the third thing: a report a skill emits into the conversation.

## The two tiers are marked, and the marking is load-bearing

Two rules ship here and they are not equally supported. One is measured on this
lab's own material across two independent corpora; the other is argued from a
mechanism and has been exercised but never given a pre-registered threshold. A
reader who cannot tell them apart will treat both as measured, so the tier is
written into each heading rather than left for the prose to imply.

## Measured — ration emphasis

Use bold rarely. Where you would reach for it to mark something important, use a
heading instead.

That is the wording that was measured, reproduced rather than paraphrased. It
carries no numeric target on purpose: a stated bold percentage can be complied
with into a better score without the reply improving.

**What the evidence is.** Against a one-line request for clarity, this rule cut
bold word share from 9.03% to 0.14% — a margin of 8.89pp against a run-to-run
noise floor of 2.50pp measured on that same prompt set. It replicated on a
second, independently written set at 8.97pp against that set's own floor of
1.39pp. Replies did not get shorter and their caveat layer did not thin; the
movement was confined to the emphasis channel.

**The counting rule behind those figures, and the date they were taken.** Bold
word share is bold words over total words under `measure_discourse.py:words` as
it stood before 2026-08-24 — a whitespace-delimited token carrying a letter or a
digit. The first pair was measured 2026-08-20 and the second 2026-08-23. **A
later change to that rule, on 2026-08-24, stopped counting a list marker as a
word**, which moves this first pair to 9.10% and 0.14% and the margin to 8.96pp.
**The values above are not re-issued and are correct as measured** — naming the
rule and the date is what makes them readable, and re-stating them would put two
counting rules inside one passage. See the register of counting rules in the
finding named below.

**What the defect is.** This lab's own replies measured 10.52% of words bolded
against 0.41% for professionally edited technical documentation — roughly
twenty-six times the density. The comparison corpus is genre-mismatched and was
chosen rather than sampled, so read the multiple as indicative. The direction is
not in doubt.

**Both figures in that pair were measured 2026-08-18 under
`measure_discourse.py:words`**, and the two are directly comparable because the
same script counted both. The 10.52% cannot be re-derived — its corpus is frozen
as unreproducible — while the 0.41% can be and reproduces exactly.

**What it does not show.** Every metric here is a proxy. Nothing measured
whether the result is easier to understand, which is the actual target.

## Directional — add headings by length

If the reply runs past roughly 150 words, break it into sections under short
headings. Below that, use none.

This ships as a guard attached to the emphasis rule rather than as a result in
its own right, and that framing is the reason it ships at all. Rationing
emphasis alone carries a known way to do harm: if bold is doing part of the
headings' work, removing it without supplying structure takes away navigation
rather than decoration.

**Why this is not marked measured.** The rule demonstrably acts — where a
control produced no headings at all past 150 words, the instrument produced a
median of three, agreeing across two runs. What is missing is a threshold fixed
in advance to read that against. The 150-word figure is edited prose's measured
heading density, about one per 160 words, rounded down; it is a reasonable
number, not a validated one.

**One caution, and it is the reason the tier did not move.** Heading density
varies by corpus more than the emphasis channel does. The same directive
produced heading medians of 0.0 and 3.5 on one prompt set and 4.0 and 4.0 on
another. A heading floor measured on one body of material says nothing about
another, so no figure here should be carried across corpora.

## Always — the four preservation guardrails

These are not structuring rules and they are not in tiers. They hold whenever a
report is made shorter, by any means, and they cost nothing. The fourth holds
even where nothing was shortened, because a question can be folded into prose on
the first pass.

1. Never drop `not`, `never`, `no`, `only` or `except`. On this material the
   inversion risk is about eleven times the hedge surface, and a dropped
   negation flips meaning rather than trimming it.
2. Never compress a security warning, an irreversible-action confirmation, or a
   multi-step sequence where fragment order changes what the reader does.
3. Never strip a hedge to sound more certain than the evidence supports.
   Verbosity tracks uncertainty, so deleting the hedge hides the signal without
   improving the answer.
4. Never fold an open question into the prose around it. An item the reader has
   to decide something about goes under its own heading, carrying what was
   observed, what was deliberately not done about it, and the decision being
   asked for. Absorbed into a paragraph it reads as an observation, and an
   observation asks nothing of anyone.

The third is the one that fails quietly. In a measured round trip, every item
carrying a modal marker lost it while purely factual items survived intact — an
assumption the writer had gone on to overturn came back as a current belief.
Expansion cannot restore a distinction that deletion destroyed.

The fourth is the newest, and it is the only one of the four that rests on a
report rather than a measurement. It sits in this untiered category rather than
beside the two rules above because those are tiered by evidence and this one has
none to declare — and because the failure it guards is the second guardrail's
shape rather than a new one: a category of content whose meaning does not
survive being absorbed into a paragraph.

What qualifies is narrow on purpose. The test is whether the reader would have
to decide something, not whether the session happened to notice something.
Applied to anything noticed, this either captures nothing or captures the whole
report, and both failures look like compliance.

## Not shipped — answer-first ordering

Opening with the conclusion is the third transformation of the instrument these
rules come from. It is deliberately not a rule here.

It was measured and it acts: qualifiers move later in the document under both
instrument runs. That prices nothing. Its cost is invisible to any metric taken
on the output, because every word survives — the damage falls on a reader who
stops at the answer, and about half of all qualifiers sit in the top half of a
reply where moving the conclusion up pushes them below it.

Ordering a report well is still worth doing, and several skills already fix an
order that is answer-first in effect. What is withheld is a stated rule
recommending it, until there is evidence it helps rather than evidence it
happens.

## This file rations its own emphasis, deliberately

The runs these rules come from used no bold in their own text, and that was a
confound control rather than a style choice: an instrument that rations emphasis
while demonstrating it primes the behaviour it forbids. The same reasoning
applies to a reference an agent loads immediately before writing a report. Where
this file marks something, it uses a heading.

## Where the figures come from

`research/findings/output-compression-technique-package.md`, whose
discourse-level half is marked `evidenced`. Its overall confidence is
`directional` because a different half of it — a six-item, self-scored round
trip — is unchanged, and the two must not be read as one.

Every figure above is quoted with the corpus it was measured on, and since
2026-08-31 with the counting rule and the date as well. A figure from this
research line is not portable without the counting rule and the corpus that
produced it, and a noise floor never transfers between corpora at all.

That finding's *Register of counting rules* is the labelled source for every
figure quoted here: it names the rule behind each live figure the finding
carries, which of the three word-counting rules in this research line produced
it, and whether the arm can be re-measured today. **Check it before quoting any
figure from this file beside one from another corpus.**
