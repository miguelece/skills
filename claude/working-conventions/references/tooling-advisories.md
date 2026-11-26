# Check tooling against current security advisories

Applies before running a runtime, a package manager or a fetched tool (a
language runtime, its package manager, a one-off tool runner, and the like),
and before installing or loading agent tooling: a skill, an MCP server, a
plugin or mod, or an agent config file that wires one in, in any project.
Agent tooling reaches the agent's context and tools the same way a package
does, so it is supply chain too: pin each by exact version, commit or hash,
never by a branch, a tag that can move or a "latest".

1. **Check the runtime once per session** against the vendor's current
   security releases, and say whether the installed version is affected.
   For a runtime packaged by an operating system distribution, read the
   distribution's own advisory data rather than comparing version strings:
   distributions backport fixes without changing the version, so the string
   alone can report a fixed build as vulnerable.
2. **Before installing or fetching a package or a component, check current
   supply-chain compromise reports for it.** Prefer a pinned exact version or
   the project's existing lockfile. Never install `@latest`, and never run an
   unpinned one-off fetch.
3. **Prefer a package manager with guardrails, and keep them on.** A minimum
   release age, which refuses a version until it has been public for some
   days, and a block on dependency build scripts unless they are listed, both
   stop the common worm patterns. Never turn a guardrail off, or lower a
   release age, to get a fresh release. Where a project already uses another
   package manager with a lockfile, ask before switching it. Check the package
   manager itself against advisories too.
4. **Vet the first fetch where no credentials are reachable.** Put the first
   fetch or run of a component not yet pinned or vetted in a container or VM
   where the host has one, so an install-time payload finds nothing to take.
   A pinned version already in use needs no repeat. Skills, MCP servers and
   plugins must run on the host in the end, so the isolation covers
   inspecting them, not running them: read what they install, execute and
   connect to before they reach the host.
5. **Review a change to agent config as code.** A change to settings, hooks
   or MCP wiring is reviewed as a code change before it takes effect: read
   the diff, and name what it lets run, read or reach that it did not before.
   A config change can grant a tool or a network endpoint as surely as new
   code can.
6. **If something is flagged, do not run it in a way that reaches the
   vulnerable path.** Tell the user, name the fixed version, and propose the
   update. Never update system software, or rotate credentials, without
   asking.

## Why

Package registries are a live attack surface: compromised releases of popular
packages appear, spread through install scripts and transitive dependencies,
and are pulled within days. An unpinned fetch takes whatever was published
most recently, which is exactly the window a compromise lives in, and a
runtime with an open high-severity advisory is reachable from any code it runs.
Agent tooling is the same surface with a shorter path: a skill, an MCP server
or a plugin loads straight into the agent's context and tools, and a payload
that runs at install harvests whatever credentials the session can reach,
which is why the first fetch is vetted away from them. A version string is a
lead, not proof, because a distribution's fix does not always move it.
Checking first costs a search; skipping it can hand a credential or the
machine to whoever published the bad release. The advisories themselves are
dated facts that go stale, so the convention is to look them up each time,
not to remember them.
