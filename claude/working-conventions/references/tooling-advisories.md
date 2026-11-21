# Check tooling against current security advisories

Applies before running a runtime, a package manager or a fetched tool (a
language runtime, its package manager, a one-off tool runner, and the like),
in any project.

1. **Check the runtime once per session** against the vendor's current
   security releases, and say whether the installed version is affected.
2. **Before installing or fetching a package, check current supply-chain
   compromise reports for it.** Prefer a pinned exact version or the
   project's existing lockfile. Never install `@latest`, and never run an
   unpinned one-off fetch.
3. **Prefer a package manager with guardrails, and keep them on.** A minimum
   release age, which refuses a version until it has been public for some
   days, and a block on dependency build scripts unless they are listed, both
   stop the common worm patterns. Never turn a guardrail off, or lower a
   release age, to get a fresh release. Where a project already uses another
   package manager with a lockfile, ask before switching it. Check the package
   manager itself against advisories too.
4. **If something is flagged, do not run it in a way that reaches the
   vulnerable path.** Tell the user, name the fixed version, and propose the
   update. Never update system software, or rotate credentials, without
   asking.

## Why

Package registries are a live attack surface: compromised releases of popular
packages appear, spread through install scripts and transitive dependencies,
and are pulled within days. An unpinned fetch takes whatever was published
most recently, which is exactly the window a compromise lives in, and a
runtime with an open high-severity advisory is reachable from any code it runs.
Checking first costs a search; skipping it can hand a credential or the
machine to whoever published the bad release. The advisories themselves are
dated facts that go stale, so the convention is to look them up each time,
not to remember them.
