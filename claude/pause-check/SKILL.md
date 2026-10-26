---
name: pause-check
description: Judge whether this session should continue or stop at a clean boundary — read the context window's occupancy on demand, check the observable proxies a good pause point needs, and answer "keep going" or "this is a good pause point", naming close-out with the next agenda. Read-only. Use when deciding whether to keep going before the next item of a queue, when a long session may be due a fresh one, or when asked "should we stop here", "is this a good stopping point", "pause check" or "how full is the context".
---

# Pause check

Decide whether this session should keep going or stop at a clean boundary, and
say which in a few lines. Read-only: it reads one figure and the state of the
work, and changes nothing.

Two inputs, with different jobs. **The occupancy figure sets the urgency.**
**The proxies choose where to stop.** A full window never justifies stopping
mid-deliverable, and an empty one never makes a bad boundary good.

The criteria for a good boundary are not restated here. They are in
[references/session-queue.md](references/session-queue.md), under *Choosing a
boundary* and *What a boundary must buy*. Read both before judging.

## 1. Read the channel

Call the tool `mcp__context-occupancy__occupancy`, once, with no arguments. Some
harnesses list it as a deferred tool, so load it first if it has to be loaded.
It answers JSON with a `status`:

- **`ok`**: `tokens`, `window`, `percent`, and `autoCompactThreshold`, which is
  `null` when auto-compaction is off. Report the figure and the threshold
  together.
- **`off`**: the person switched it off. Say so in one line, and say that
  `/occupancy on` switches it back on. Do not switch it on yourself.
- **`unavailable`**, with a `reason`: `subagent`, `no-response-yet`
  (a fresh session, or one just compacted), or `usage-failed`. Say so in one
  line, naming the reason.
- **No such tool**: the channel is not installed, which is always the case on
  Codex today. Report it as *unavailable (not installed)*.

**Never estimate a figure the channel did not give.** A token count a harness
shows the model, such as a remaining-tokens line, is a session budget, not the
window's occupancy. It can be ample while the window is nearly full, and the
reverse. Do not read one as the other.

## 2. Place the figure in a band

Only with an `ok` answer. When `autoCompactThreshold` is a number, measure
against it rather than the window, as `tokens` over the threshold: compaction,
not the window's edge, is where context is lost. Otherwise use `percent`.

| Band | Urgency |
| --- | --- |
| below 35% | No pressure. Keep going. |
| 35% to 60% | Prefer to stop at the next clean boundary. |
| above 60% | Stop at the nearest clean boundary. |

These edges are starting values, tunable, and they live only here.
`session-queue.md` deliberately states no figure, because the skills that read
it never see one.

## 3. Check the proxies

The four observable proxies from `session-queue.md`. Report each one with what
was observed, or as *not checked*. Never drop one silently.

- **Mid-edit**: is any change half-applied, or any file written and not yet
  verified?
- **Next item already committed**: can the next item start from material that is
  already committed, or does it need state only this session holds?
- **Premises verified this session**: were the next item's premises checked in
  this session, so they are cheaper to act on now than later?
- **Items to a verified close**: how many items has this session taken to a
  verified close?

Then judge the current point against *Choosing a boundary*: it is a clean
boundary only if every condition there holds.

## 4. Give the verdict

One of four, in one line, followed by the figure line and the proxies:

- **Keep going.** The band shows no pressure, or the band asks for the next
  clean boundary and this point is not one. Name what has to finish first.
- **Keep going: no signal.** No figure, and the proxies argue neither way. This
  is a real answer, not silence. Say whether the current point is a clean
  boundary, in case the user wants to stop anyway.
- **This is a good pause point.** The band asks for a boundary and the current
  point is a clean one. Name what the boundary buys, from *What a boundary must
  buy*. Suggest the user run `close-out` with `into <next>`, where `<next>` is
  the next item of work. Without one, suggest a bare `close-out`.
- **Stop at the nearest boundary.** The band is above 60% and the current point
  is not clean. Name the shortest path to the next clean boundary: finish the
  edit, run the verification, or record the decision. Never stop part-way to
  save context.

Without a figure, judge from the proxies alone. A clean boundary with nothing
pressing is still *keep going: no signal*, not a stop: always recommending a
stop when blind would make this check noise in every session without a
channel.

## When `close-out` runs this first

Typed bare, `close-out` runs this skill before anything else, to propose the
next session's agenda. The user has already decided to stop, so the verdict
does not decide anything there. What `close-out` needs is `<next>`: the next
item of work, or none. Report it and stop. `close-out` puts the proposal to
the user.

## Guardrails

- Do not edit, commit or write anything, and do not push. This skill reads and
  reports.
- Do not run `close-out` or `handoff` yourself. `close-out` is user-only, and
  this skill only suggests it.
- Do not estimate, extrapolate or invent a figure when the channel gives none,
  and do not read a session budget as occupancy.
- Do not switch the channel on or off.
- Do not recommend stopping part-way through a deliverable, before a pending
  verification, or before a reached decision is recorded.
- Do not omit a proxy. Report it as *not checked* instead.

## Resources

- Where a boundary belongs, and what it must buy:
  [references/session-queue.md](references/session-queue.md)
