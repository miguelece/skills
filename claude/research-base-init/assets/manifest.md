---
title: <one line — what these files pre-register, not where they sit>
kind: pre-registration   # must match the kind base.json declares for this layer
regime: frozen           # the files describe a moment, and are never edited
updated: <YYYY-MM-DD>    # the date this manifest is written
sources:                 # each commit that froze a covered file, pinned as repo@sha
  - <repo>@<sha>
informs: []              # the guidance, projects or decisions the run shaped
covers:                  # every file that binds the run, one per entry, never a directory
  - <path>
---

# <What was pre-registered, as a heading>

<Which run these files bind, and what it measured. Name the work item that
commissioned it by its id, never as a link: a work item moves when it closes.>

## What these files are

<One line per file or group of files: what each holds. Each is described here
because it cannot carry frontmatter, and none is edited — adding frontmatter to
a frozen file after its run is the one change a pre-registration cannot
survive.>
