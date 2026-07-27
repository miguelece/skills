---
name: spike
description: Build the smallest throwaway prototype in scratch space that answers one stated question, gather real evidence, then discard or deliberately promote it. Use when asked to "spike this", "prototype it", "try it quickly", "proof of concept", "just test whether this works", or to evaluate an approach before committing to it.
---

# Spike

Build the smallest throwaway thing that answers one question, in scratch space,
and decide deliberately what happens to it.

A spike's deliverable is **an answer, not code**. The code is the instrument; it is
expected to be discarded. Holding that line is what makes a spike cheap — the
moment it has to be production-quality, it stops being a spike.

## Boundaries

- **Name the question first**, in one sentence, with what would count as an answer.
  A spike without a question is just unplanned work.
- **Everything lives in scratch space** — a gitignored scratch directory, a throwaway
  branch, or a temp dir. Never in the production tree, not even briefly.
- **Box it.** State up front how far you will go before stopping and reporting,
  whether the answer arrived or not. Report a spike that ran out of box as
  inconclusive; that is a real result.
- Skip what production needs and a spike does not: error handling, edge cases,
  tests for the throwaway code, naming, abstraction, configurability. Deliberately
  cutting these is the technique, not sloppiness.
- Do **not** modify production code to make the spike work. If the spike needs a
  production change to run, that is itself a finding — record it and stop.

## Steps

1. **Write the question and the answer criteria.** "Can X do Y under constraint Z?"
   plus what evidence would settle it either way.
2. **Choose the scratch location** and confirm it is gitignored or throwaway.
3. **Build the smallest thing that could answer it.** Hardcode freely. Use real
   inputs where the answer depends on them — a spike on synthetic data answers a
   question nobody asked.
4. **Get the evidence.** Measure rather than infer. Record the actual numbers,
   errors, and outputs.
5. **Write down what you learned**, including anything that contradicted the
   premise. A spike that overturns its own question is the most valuable kind, and
   that result evaporates unless it is written down.
6. **Decide the disposition explicitly** — see below. Say which, and do it.

## Disposition — choose one, out loud

- **Discard.** The answer is recorded; the code is deleted. This is the default and
  the most common correct outcome.
- **Promote by rewriting.** The approach is validated, so it gets built properly,
  from scratch, with tests. The spike is still deleted — it was the instrument, not
  a draft.
- **Keep as a tool.** It turned out to be a useful harness. Then it graduates: it
  gets a real home, a real name, and tests, in its own commit.

Never a fourth option where the spike quietly stays where it is and slowly becomes
load-bearing.

## Guardrails

- Do not start without a written question and a box.
- Do not put spike code in the production tree "temporarily".
- Do not import, call, or depend on spike code from production code.
- Do not promote spike code by copy-paste. Promotion means rewriting it.
- Do not report a spike as successful because the code ran. It succeeded if it
  answered the question — including by answering "no".
- Do not let the spike expand into implementing the feature. If the question is
  answered, stop, even if continuing feels efficient.
- Do not delete the spike before its findings are written down.

## Reporting

Report, in this order: the question, what was built and where, the evidence with
real numbers, the answer, anything that contradicted the premise, and the
disposition you took. If the box ran out first, say so and say what would settle
it.
