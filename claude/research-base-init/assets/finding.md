---
title: <one line — the finding, not the topic>
kind: finding            # must match the kind base.json declares for this layer
regime: living           # living claims the present; frozen describes a moment
status: exploring        # exploring | supported | promoted
confidence: directional  # directional | evidenced | strong
updated: <YYYY-MM-DD>    # moves only when the claim changes
authority: []            # what this is re-verified against; a living record needs one
sources: []              # names in the base's private layer, public URLs, or <repo>@<sha>
informs: []              # the guidance, projects or decisions this shapes
---

# <Question or claim, as a heading>

## Claim

<The finding in one or two sentences. State it as a conclusion someone could act
on. If you cannot write this line yet, the file is `exploring` — say the open
question here instead and fill this in when it resolves.>

## Evidence

<What supports the claim, each point cited to a source by name. Keep verified
evidence and directional reasoning visibly separate — do not let an argument that
merely sounds right sit unmarked next to a checkable fact. Small quoted excerpts
are fine; a whole source is not — that stays in the base's private layer.>

## Caveats and limits

<Where the claim does not hold, what it is often confused with, and what would
lower its confidence. A finding with no stated limits has not been examined hard
enough.>

## Application

<Concretely, how this changes what the repository does. This is the part that
may later become a line in its guidance, so make it actionable — a rule, a
check, a template change — not an observation.>

## Status and graduation

<Whether this is ready to promote into the repository's guidance, and if not,
what is missing: more evidence, a replication, generalization past one case.
When promoted, name the section it landed in.>
