---
sources:
  - id: python-random
    title: "Python 3.15.2 documentation: random, Generate pseudo-random numbers"
    url: https://docs.python.org/3/library/random.html
    date: 2026-11-26
  - id: python-secrets
    title: "Python 3.15.2 documentation: secrets, Generate secure random numbers for managing secrets"
    url: https://docs.python.org/3/library/secrets.html
    date: 2026-11-26
  - id: owasp-forgot-password
    title: "OWASP Cheat Sheet Series: Forgot Password Cheat Sheet"
    url: https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html
    date: 2026-11-26
  - id: rfc-8725
    title: "RFC 8725: JSON Web Token Best Current Practices (BCP 225), February 2020"
    url: https://www.rfc-editor.org/rfc/rfc8725.html
    date: 2026-11-26
  - id: pyjwt-api
    title: "PyJWT documentation: API Reference (jwt.decode, get_unverified_header)"
    url: https://pyjwt.readthedocs.io/en/stable/api.html
    date: 2026-11-26
  - id: pyjwt-changelog
    title: "PyJWT documentation: Changelog (v2.0.0, algorithms required)"
    url: https://pyjwt.readthedocs.io/en/stable/changelog.html
    date: 2026-11-26
  - id: pyjwt-jws-source
    title: "PyJWT source, jwt/api_jws.py (decode_complete, _verify_signature)"
    url: https://github.com/jpadilla/pyjwt/blob/master/jwt/api_jws.py
    date: 2026-11-26
  - id: pyjwt-1-7-1-jws-source
    title: "PyJWT 1.7.1 source, jwt/api_jws.py (algorithms optional, header selects)"
    url: https://github.com/jpadilla/pyjwt/blob/1.7.1/jwt/api_jws.py
    date: 2018-12-07
  - id: ghsa-ffqj-6fqr-9h24
    title: "GHSA-ffqj-6fqr-9h24 (CVE-2022-29217): PyJWT key confusion through non-blocklisted public key formats"
    url: https://github.com/jpadilla/pyjwt/security/advisories/GHSA-ffqj-6fqr-9h24
    date: 2022-05-12
  - id: python-jose-jws-source
    title: "python-jose 3.5.0 source, jose/jws.py (verify, _verify_signature)"
    url: https://github.com/mpdavis/python-jose/blob/3.5.0/jose/jws.py
    date: 2025-05-28
  - id: python-jose-jwt-source
    title: "python-jose source, jose/jwt.py (decode passes algorithms through)"
    url: https://github.com/mpdavis/python-jose/blob/master/jose/jwt.py
    date: 2026-11-26
  - id: python-hmac
    title: "Python 3.15.2 documentation: hmac, Keyed-Hashing for Message Authentication (compare_digest)"
    url: https://docs.python.org/3/library/hmac.html
    date: 2026-11-26
  - id: rfc-6238
    title: "RFC 6238: TOTP, Time-Based One-Time Password Algorithm, May 2011"
    url: https://www.rfc-editor.org/rfc/rfc6238.html
    date: 2026-11-26
  - id: pyotp-docs
    title: "PyOTP documentation (verify is stateless, replay prevention)"
    url: https://pyauth.github.io/pyotp/
    date: 2026-11-26
  - id: codeql-py-xxe
    title: "CodeQL query help: XML external entity expansion (py/xxe)"
    url: https://codeql.github.com/codeql-query-help/python/py-xxe/
    date: 2026-11-26
  - id: owasp-xxe
    title: "OWASP Cheat Sheet Series: XML External Entity Prevention Cheat Sheet"
    url: https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html
    date: 2026-11-26
  - id: lxml-faq
    title: "lxml FAQ: How do I use lxml safely as a web-service endpoint?"
    url: https://lxml.de/FAQ.html
    date: 2026-11-26
  - id: lxml-changes
    title: "lxml CHANGES.txt (5.0.0, LP#1742885; 6.1.0, LP#2146291)"
    url: https://github.com/lxml/lxml/blob/master/CHANGES.txt
    date: 2026-11-26
  - id: python-xml
    title: "Python 3.15.2 documentation: XML Processing Modules, XML security"
    url: https://docs.python.org/3/library/xml.html
    date: 2026-11-26
  - id: python-sax-handler
    title: "Python 3.15.2 documentation: xml.sax.handler (feature_external_ges)"
    url: https://docs.python.org/3/library/xml.sax.handler.html
    date: 2026-11-26
findings:
  - id: random-is-not-for-secrets
    claim: >-
      The `random` module's generators are completely deterministic and
      must not be used for security purposes; Python's documentation names
      the `secrets` module for security and cryptographic uses, and says
      `randbytes` should not be used to generate security tokens.
    confidence: strong
    sources: [python-random, python-secrets]
  - id: secrets-need-a-csprng
    claim: >-
      `secrets` generates cryptographically strong random numbers for
      passwords, account authentication and security tokens, and is to be
      used in preference to `random`; password reset tokens are to be
      generated with a cryptographically secure random number generator.
    confidence: strong
    sources: [python-secrets, owasp-forgot-password]
  - id: jwt-header-names-its-own-algorithm
    claim: >-
      A signed JWT carries its own algorithm in its header, an attacker can
      change it to `none` or from `RS256` to `HS256`, and some libraries
      trust it; the verifier must be able to specify the algorithms it
      accepts, and each key is used with exactly one algorithm. PyJWT's
      documentation warns against computing `algorithms` from the token's
      own `alg`, and says the unverified header is not to be trusted
      before the signature is verified.
    confidence: strong
    sources: [rfc-8725, pyjwt-api]
  - id: pyjwt-requires-algorithms-from-2
    claim: >-
      PyJWT 1.x accepted a `decode` with no `algorithms`, warning only, and
      used the header's `alg` to choose the algorithm; 2.0.0, released
      2020-12-22, requires an explicit `algorithms` by default, and its
      current source refuses a verifying decode without one unless the key
      is a `PyJWK`, which binds the key's own algorithm. Before 2.4.0,
      passing every default algorithm let an HMAC algorithm verify against
      an asymmetric public key.
    confidence: evidenced
    sources: [pyjwt-changelog, pyjwt-jws-source, pyjwt-1-7-1-jws-source, ghsa-ffqj-6fqr-9h24]
  - id: python-jose-accepts-any-algorithm-by-default
    claim: >-
      python-jose's `jwt.decode` defaults `algorithms` to `None` and passes
      it through to `jws.verify`, whose allow-list check is skipped when it
      is `None`, so the token header's `alg` builds the key and selects the
      verification, as of 3.5.0, the latest release when read.
    confidence: evidenced
    sources: [python-jose-jws-source, python-jose-jwt-source]
  - id: compare-digest-covers-only-the-call
    claim: >-
      `hmac.compare_digest` avoids content-based short-circuiting, and for
      inputs of different lengths may reveal their types and lengths but
      not their values; it is named in place of `==` for comparing a
      digest to an externally supplied one. It protects only the
      comparison it performs.
    confidence: evidenced
    sources: [python-hmac]
  - id: otp-must-be-refused-after-use
    claim: >-
      The TOTP verifier must not accept the second attempt of an OTP after
      the first has been validated, which is what makes it one-time.
    confidence: strong
    sources: [rfc-6238]
  - id: pyotp-verify-is-stateless
    claim: >-
      PyOTP's `verify` and `verify_and_get_timecode` are stateless and can
      accept the same code repeatedly while it remains valid; replay
      prevention is the application's, by persisting the last accepted
      time code or HOTP counter per credential, atomically, and rejecting
      one that is not later.
    confidence: evidenced
    sources: [pyotp-docs]
  - id: reset-tokens-are-single-use
    claim: >-
      A password reset token is single use and is invalidated after it has
      been used.
    confidence: evidenced
    sources: [owasp-forgot-password]
  - id: entity-resolution-enables-xxe
    claim: >-
      Parsing untrusted XML with external entity handling enabled can
      expose local files, cause server-side request forgery or exhaust
      resources; the remedy is to disable external entity handling, with
      `defusedxml` recommended for Python, and CodeQL reports an
      `lxml.etree` parse whose parser resolves external entities.
    confidence: strong
    sources: [codeql-py-xxe, owasp-xxe]
  - id: lxml-resolves-only-internal-entities-from-5
    claim: >-
      From lxml 5.0.0, released 2023-12-29, parsers no longer expand
      external entities by default, the default being
      `resolve_entities='internal'`, and `resolve_entities=True` enables
      them again; `iterparse` and `ETCompatXMLParser` still defaulted to
      `True` until 6.1.0, released 2026-04-17, as CVE-2026-41066.
    confidence: evidenced
    sources: [lxml-changes, lxml-faq]
  - id: stdlib-parsers-resolve-only-when-asked
    claim: >-
      Python's built-in XML parsers rely on Expat, which by default does
      not access local files or create network connections; enabling
      `xml.sax`'s `feature_external_ges` includes external general
      entities, which the documentation warns opens external entity
      attacks on user-provided XML.
    confidence: evidenced
    sources: [python-xml, python-sax-handler, owasp-xxe]
---

# Research: Python security defaults

Read on 2026-11-26, at each source's own page: the platform documentation
first (Python 3.15.2, the RFCs), then each library's own documentation,
source, changelog and advisories, with OWASP's cheat sheets and CodeQL's
query help as the independent published guidance. Each `date` is the reading
date, except for the advisory, dated as published, and the two sources cited
at a release tag, PyJWT 1.7.1 and python-jose 3.5.0, dated as that release.
The RFCs carry only a month, given in their titles, so they are dated as
read. No source is a dated blog post.

The subject is a defect class that passes every functional test: each
mistake behaves like the secure version until someone attacks it. The five
candidates the module was scoped with were each kept, because each has a
quotable call and a reading rule that decides it; how each was narrowed is
below.

## How each check was decided

- **A predictable random secret.** Every function of `random` is a quotable
  call, but the module is used legitimately everywhere, so the `evidence`
  requires the value to be followed to a use as a secret, and a variable's
  name alone does not decide it. `random.SystemRandom` draws from the
  operating system's source, the one `secrets` uses, so it is excluded.
- **A JWT algorithm taken from the token.** The literal defect, an
  `algorithms` list or a key chosen from the unverified header, is always
  reported, as is a list that admits `none` or every algorithm. An absent
  `algorithms` turns on the library. python-jose's source skips the
  allow-list when none is given, in the latest release, so it is reported
  in any version. PyJWT refuses such a call from 2.0.0, so it is reported
  only below that version, read from the lockfile; an unreadable version
  leaves the case unresolved. A decode that turns signature verification
  off is a different defect, an unverified token, and is left out.
- **A timing-safe comparison undone.** The early return is quotable in the
  same function. Unlike Node's equivalent, `compare_digest` does not throw
  on inputs of different lengths, and its documentation says that it may
  reveal their lengths but not their values, so a length check before it
  discloses nothing the call does not, and is not reported.
- **A one-time code accepted twice.** The defect is an absence, a missing
  write, so the `evidence` reads the success path to its return. Where that
  path calls code the reading cannot follow, such as a store behind an
  interface, the case is unresolved rather than reported, since the
  consumption may sit there.
- **XML external entities.** The scoped candidate named the standard
  library and `lxml`. The standard library's parsers rely on Expat, which
  does not load files or the network by default, so only an explicit
  `feature_external_ges` on an `xml.sax` parser is reported. `lxml`'s
  default changed with its version, and differently for `iterparse` and
  `ETCompatXMLParser`, so an unset `resolve_entities` is reported only on a
  version the lockfile shows to be below the fix, and an explicit
  `resolve_entities=True` on any. CodeQL's example still describes the
  default parser as resolving local entities; lxml's own changelog, the
  primary source, governs for 5.0 and later. The input must come from
  outside the program, since a document the repository ships cannot carry
  an attacker's entity.

## Reading, not running

The static phase runs nothing, so a scanner such as CodeQL, Bandit or a
dependency audit is a reference and never the mechanism. Every check is
applied by reading the call, the code around it and, where a library's
behaviour changed with a version, the lockfile. For a diff the finding sits
in the changed lines, while the declarations, the success path and the
lockfile it rests on are read where they are.

## What this does not cover

- **A secret compared with `==` and no `compare_digest` at all.** It is the
  commoner timing defect, but this module was scoped to the comparison
  undone by the code around it.
- **A token decoded with signature verification off**, or a JWT's claims,
  expiry and audience left unchecked. Neither takes the algorithm from the
  header, the defect this module checks.
- **Other JWT libraries**, such as Authlib's `jose`, whose defaults no
  source read states.
- **Entity expansion attacks that need no external entity**, such as the
  billion laughs, which Python's documentation ties to the Expat version
  rather than to a call the code makes, and **`xmlrpc`'s decompression
  bomb**.
- **Other XML parsers**, such as `xmltodict` or `untangle`, whose entity
  handling no source read states.
- **Authorization**, which turns on how an application routes every
  request rather than on one call, and is the subject of a module of its
  own.
