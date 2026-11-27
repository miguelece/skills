---
sources:
  - id: saltzer-schroeder
    title: "The Protection of Information in Computer Systems, 1975, section on basic principles (Saltzer and Schroeder)"
    url: https://web.mit.edu/Saltzer/www/publications/protection/Basic.html
    date: 2026-11-26
  - id: owasp-authorization-cheat-sheet
    title: "Authorization Cheat Sheet (OWASP Cheat Sheet Series)"
    url: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
    date: 2026-11-26
  - id: owasp-top10-2025-a01
    title: "A01:2025 Broken Access Control (OWASP Top 10:2025)"
    url: https://top10.owasp.org/2025/A01_2025-Broken_Access_Control
    date: 2026-11-26
  - id: cwe-862
    title: "CWE-862: Missing Authorization (CWE 5.0)"
    url: https://cwe.mitre.org/data/definitions/862.html
    date: 2026-10-28
  - id: owasp-asvs-5-v8
    title: "ASVS 5.0, V8 Authorization (OWASP Application Security Verification Standard)"
    url: https://github.com/OWASP/ASVS/blob/master/5.0/en/0x17-V8-Authorization.md
    date: 2026-11-26
  - id: django-login-required-middleware
    title: "Middleware reference, LoginRequiredMiddleware (Django 5.2 documentation)"
    url: https://docs.djangoproject.com/en/5.2/ref/middleware/
    date: 2026-11-26
  - id: aspnetcore-fallback-policy
    title: "Policy-based authorization in ASP.NET Core (Microsoft Learn)"
    url: https://learn.microsoft.com/en-us/aspnet/core/security/authorization/policies
    date: 2026-09-18
findings:
  - id: every-access-is-checked
    claim: >-
      Every access to every resource is checked for authority, on every
      request; checking most requests is not enough, because a single missed
      check exposes the resource, and a missing check is a weakness of its
      own.
    confidence: strong
    sources: [saltzer-schroeder, owasp-authorization-cheat-sheet, cwe-862]
  - id: one-mechanism-applied-everywhere
    claim: >-
      Access control is implemented once and reused throughout the
      application, configured globally, as a framework's filter or
      middleware, rather than applied to each route by hand, so that an
      endpoint added later is covered without anyone remembering it.
    confidence: strong
    sources:
      - owasp-top10-2025-a01
      - owasp-authorization-cheat-sheet
      - aspnetcore-fallback-policy
  - id: public-routes-are-marked
    claim: >-
      Where frameworks apply a check to every route by default, a route meant
      to be public is declared so explicitly, by a decorator or an attribute
      such as Django's login_not_required or ASP.NET Core's AllowAnonymous,
      so a public route is distinguishable by reading from one that was
      missed.
    confidence: strong
    sources: [django-login-required-middleware, aspnetcore-fallback-policy]
  - id: deny-by-default
    claim: >-
      Access decisions are based on permission rather than exclusion: the
      default is no access, the rules name the conditions under which access
      is granted, and anything they do not name is refused, except resources
      deliberately public.
    confidence: strong
    sources:
      - saltzer-schroeder
      - owasp-authorization-cheat-sheet
      - owasp-top10-2025-a01
      - cwe-862
  - id: design-states-where-authorization-is-enforced
    claim: >-
      An application's authorization documentation defines its rules for
      function-level and data-level access, and the application enforces
      them at a trusted service layer rather than in anything an untrusted
      caller controls. The standard does not itself say "central"; that
      word comes from the reuse finding above.
    confidence: evidenced
    sources: [owasp-asvs-5-v8]
---

# Research: authorization

Read on 2026-11-26 at each source's own page: the basic-principles section
of Saltzer and Schroeder's paper, OWASP's Authorization Cheat Sheet, the
Broken Access Control entry of the OWASP Top 10:2025, CWE-862, the
authorization chapter of ASVS 5.0, Django's middleware reference and
Microsoft's page on ASP.NET Core authorization policies. Each `date` is the
page's own date where it gives one, CWE's release date and the Microsoft
page's revision date, and the reading date otherwise; the Saltzer and
Schroeder page carries no date of its own, so the paper's year is in its
title.

The three principles are old and agree across fifty years of sources:
complete mediation and fail-safe defaults in Saltzer and Schroeder, deny by
default and checks on every request in OWASP's cheat sheet and Top 10, and
default deny in CWE-862's mitigations. Two framework pages show what the
principles look like in code: Django's `LoginRequiredMiddleware` and ASP.NET
Core's fallback policy each apply one check to every route, with a marker for
the routes meant to be public. Microsoft's page also shows the opposite
default, which is why the first check exists: without a fallback policy, an
endpoint with no authorization metadata requires no authorization at all.

## Whether a reading can verify each candidate

Three candidates were put to this module. All three are kept, each narrowed
until a finding can quote what it rests on.

- **A route that bypasses the shared check its siblings use.** Whether a
  route is protected turns on how the whole application routes requests,
  which no single line shows. The check is therefore bounded to what a
  reading can trace: a shared point that siblings visibly pass through, a
  route visibly registered outside it, and no check or public marker of its
  own. Everything a reading cannot trace, routes built from data or by
  reflection, and checks a gateway or a framework configuration may apply
  outside the code read, is named unresolved rather than reported, so the
  check never reports a route as open on the strength of what was not read.
  A route with no siblings to compare against is out of its scope.
- **A decision that allows when no rule matches.** This one is a property
  of one function or one rule table, read whole: its fall-through path is
  quoted. A decision handed to a policy engine whose policies are not in the
  repository is unresolved.
- **A design that names no central authorization point.** A design document
  is read whole, so the absence of a named point is a property of the
  document, quotable as the sections describing how requests arrive. The
  check is limited to designs whose callers have different access, since a
  design with one kind of caller has nothing to authorize.

## What this does not cover

- **Object-level authorization**, a caller reaching another user's record by
  changing an identifier. The sources treat it under the same heading, but
  telling whether a query is scoped to its caller turns on the data model,
  not on where the check sits, and this module was scoped to the central,
  deny-by-default point.
- **A framework whose default leaves unmarked routes open**, such as ASP.NET
  Core with no fallback policy, where no route is protected and so no
  sibling shows the shared point. The first check needs a sibling to compare
  against; a check that reads a framework's global configuration would be
  per framework, and belongs in a module for that framework.
- **Deny by default in a design.** A design that names its authorization
  point but not what that point does with a request no rule covers is not
  reported: the design check asks only for the point, the one candidate put
  to this module for designs.
- **Authentication**, the identity a decision rests on, and the strength of
  the rules themselves. These checks find where authorization is missing or
  fails open, never a rule that grants the wrong role.
- **Probing a running application** for an unprotected route. The static
  phase runs nothing, so a scanner or a request replayed as another user is
  a reference, never the mechanism.
