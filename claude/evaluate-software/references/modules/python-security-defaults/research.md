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
  - id: pyjwt-jwt-source
    title: "PyJWT source, jwt/api_jwt.py (decode_complete, _merge_options, _validate_claims)"
    url: https://github.com/jpadilla/pyjwt/blob/master/jwt/api_jwt.py
    date: 2026-11-26
  - id: pyjwt-1-7-1-jwt-source
    title: "PyJWT 1.7.1 source, jwt/api_jwt.py (decode, verify=False)"
    url: https://github.com/jpadilla/pyjwt/blob/1.7.1/jwt/api_jwt.py
    date: 2018-12-07
  - id: authlib-jwt-docs
    title: "Authlib documentation: JSON Web Token (JWT), authlib.jose"
    url: https://docs.authlib.org/en/latest/jose/jwt.html
    date: 2026-11-26
  - id: authlib-jose-source
    title: "Authlib source, authlib/jose/__init__.py (the default jwt instance)"
    url: https://github.com/authlib/authlib/blob/master/authlib/jose/__init__.py
    date: 2026-11-26
  - id: ghsa-5357-c2jx-v7qh
    title: "GHSA-5357-c2jx-v7qh (CVE-2024-37568): Authlib algorithm confusion with asymmetric public keys"
    url: https://github.com/advisories/GHSA-5357-c2jx-v7qh
    date: 2024-06-09
  - id: joserfc-jwt-guide
    title: "joserfc documentation: JSON Web Token guide (decode, JWTClaimsRegistry)"
    url: https://jose.authlib.org/en/guide/jwt/
    date: 2026-11-26
  - id: codeql-py-xml-bomb
    title: "CodeQL query help: XML internal entity expansion (py/xml-bomb)"
    url: https://codeql.github.com/codeql-query-help/python/py-xml-bomb/
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
  - id: authlib-default-instance-accepts-every-algorithm
    claim: >-
      Authlib's default `jwt` instance is built with every supported JWS
      algorithm, HMAC, RSA, ECDSA, RSA-PSS and EdDSA, without `none`, and
      its decode reads the token header's `alg`; the documentation says
      never to combine symmetric and asymmetric schemes, naming the
      signature bypass CVE-2016-10555, and below 1.3.1 an HMAC
      verification accepted any asymmetric public key as its secret when
      the call named no algorithm, as CVE-2024-37568. `authlib.jose` is
      deprecated since 1.7, for removal in 2.0, in favour of `joserfc`.
    confidence: evidenced
    sources: [authlib-jwt-docs, authlib-jose-source, ghsa-5357-c2jx-v7qh]
  - id: unverified-jwt-must-be-rejected
    claim: >-
      All cryptographic operations used in a JWT must be validated, and the
      entire JWT rejected if any of them fails to validate.
    confidence: strong
    sources: [rfc-8725]
  - id: pyjwt-unverified-decode-skips-every-check
    claim: >-
      PyJWT's `decode` with `verify_signature` set false also defaults the
      expiry, not-before, issued-at, audience, issuer, subject and JWT id
      checks to off unless the caller sets them, and warns of nothing. In
      PyJWT 1.x `verify=False` skipped the signature and every claim check;
      from 2.0.0 the `verify` argument does nothing apart from a
      deprecation warning, and only the option turns verification off.
    confidence: evidenced
    sources: [pyjwt-jwt-source, pyjwt-1-7-1-jwt-source, pyjwt-changelog]
  - id: python-jose-decodes-unverified-when-asked
    claim: >-
      python-jose's `jwt.decode` passes its `verify_signature` option to
      `jws.verify` as the switch for signature checking, and
      `jwt.get_unverified_claims` returns a token's claims without
      verification of any kind.
    confidence: evidenced
    sources: [python-jose-jwt-source]
  - id: jwt-audience-must-be-validated
    claim: >-
      Where the same issuer can issue JWTs for more than one relying party,
      the JWT must carry an audience and the relying party must validate
      that it is among the audiences it accepts.
    confidence: strong
    sources: [rfc-8725]
  - id: authlib-and-joserfc-decode-leaves-claims-unvalidated
    claim: >-
      Authlib's `jwt.decode` returns a `JWTClaims` whose values are
      validated only by a separate `JWTClaims.validate()` call, and
      `joserfc`'s `jwt.decode` checks only that the payload is base64
      JSON, expiry, not-before and other claims being checked by a
      `JWTClaimsRegistry`'s `validate` after the decode.
    confidence: evidenced
    sources: [authlib-jwt-docs, joserfc-jwt-guide]
  - id: pyjwt-checks-exp-only-when-present
    claim: >-
      PyJWT checks `exp` only when the token carries one and `verify_exp`
      is on, a missing `exp` being an error only when listed in `require`,
      and checks the audience whenever `verify_aud` is on.
    confidence: evidenced
    sources: [pyjwt-jwt-source, pyjwt-api]
  - id: plain-equality-is-not-timing-safe
    claim: >-
      Python's `hmac` documentation names `compare_digest` in place of the
      `==` operator when comparing a digest with an externally supplied
      one, to reduce the vulnerability to timing attacks, and `secrets`
      offers the same constant-time comparison; `==` carries no such
      guarantee.
    confidence: evidenced
    sources: [python-hmac, python-secrets]
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
  - id: lxml-limits-stay-on-unless-huge-tree
    claim: >-
      libxml2, from 2.7, imposes hard limits on input documents against
      denial of service by forged input; every lxml version leaves them on
      by default, and the `huge_tree` parser option, from lxml 2.2.1,
      disables them, for really large trusted documents. CodeQL treats an
      lxml parse as safe from XML bombs unless `huge_tree` is set true.
    confidence: strong
    sources: [lxml-faq, codeql-py-xml-bomb]
---

# Research: Python security defaults

Read on 2026-11-26, at each source's own page: the platform documentation
first (Python 3.15.2, the RFCs), then each library's own documentation,
source, changelog and advisories, with OWASP's cheat sheets and CodeQL's
query help as the independent published guidance. Each `date` is the reading
date, except for the two advisories, dated as published, and the three
sources cited at a release tag, PyJWT 1.7.1's two files and python-jose
3.5.0, dated as that release. The RFCs carry only a month, given in their
titles, so they are dated as read. No source is a dated blog post.

The subject is a defect class that passes every functional test: each
mistake behaves like the secure version until someone attacks it. The five
candidates the module was scoped with were each kept, because each has a
quotable call and a reading rule that decides it. Four checks were added
after the module was published, and one widened, each approved before it
was drafted: plain equality on a secret, a JWT decoded unverified, a JWT's
claims left unvalidated, lxml's size limits lifted, and Authlib added to
the algorithm check. How each was narrowed is below.

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
  off is a different defect, an unverified token, read by its own check.
  Authlib's default `jwt` instance accepts every algorithm it supports and
  takes the header's `alg`, so a decode by it, or by an instance whose list
  mixes HMAC with an asymmetric algorithm, given one static key, is the
  same defect; it is reported only below 1.3.1, where the advisory shows a
  public key verifying as an HMAC secret, read from the lockfile. Whether
  a mixed list is still exploitable from 1.3.1 no source read states, so
  that case is not reported. `joserfc`, which replaces `authlib.jose`,
  allows only its recommended algorithms by default, and is not read.
- **A JWT decoded unverified.** A decode with signature verification off
  is a quotable option or call, but reading a header or `kid` before a
  verifying decode is legitimate, so the `evidence` follows the claims to
  an identity or authorization decision. A service behind a gateway that
  verified the token is the common legitimate case the code cannot
  confirm, since whether every route passes the gateway is deployment,
  so it is named unresolved rather than reported or excused. PyJWT's
  `verify=False` did something only in 1.x, so that form is gated on the
  lockfile. **Severity `critical`**, matching `jwt-algorithm-not-pinned`
  here and in the TypeScript and Go modules: the consequence is the same,
  a token the attacker wrote accepted with any identity they chose, and
  needs less of them, no algorithm trick at all.
- **A JWT's claims left unvalidated.** Narrowed to forms the code states:
  Authlib and `joserfc` leave claim validation to a separate call, so its
  absence before the claims are used is quotable, and PyJWT and
  python-jose expiry and audience checks are on until an option turns
  them off. A PyJWT call that omits `require=["exp"]` is left out: PyJWT
  checks `exp` whenever the token carries one, and whether the issuer
  always sets it is not in the code. **Severity `high`**, one below the
  forged-token checks: the attacker needs a token once validly issued,
  expired or meant for another service, so the defect extends a captured
  credential's life or reach rather than minting one, the same harm as
  `one-time-code-accepted-twice`, which is `high`. The TypeScript module's
  check of the same name reads the same defect at the same severity.
- **A secret compared by plain equality.** `==` on strings is everywhere,
  so the `evidence` traces each side, one to a secret the server holds and
  one to the request, and excludes a digest looked up by hash and a
  password-hashing library's own verify. Its wording is shared with the Go
  module's check of the same name, sentence for sentence, with only the
  calls changed, so the two read the defect the same way. **Severity
  `medium`**, matching `timing-safe-compare-undone` and the Go check: a
  timing attack over a network needs many requests, and no primary source
  read quantifies how exploitable it is.
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
- **lxml's size limits lifted.** libxml2's limits against forged input
  are on in every lxml version unless the code passes `huge_tree=True`, so
  the option is the quotable defect, and the input trace the XXE check
  reads excludes the legitimate use, a large document the program trusts.
  **Severity `medium`**, one below the XXE check: the harm is availability
  alone, a request that exhausts the worker, without the file read or
  request forgery that puts external entities at `high`.

## Reading, not running

The static phase runs nothing, so a scanner such as CodeQL, Bandit or a
dependency audit is a reference and never the mechanism. Every check is
applied by reading the call, the code around it and, where a library's
behaviour changed with a version, the lockfile. For a diff the finding sits
in the changed lines, while the declarations, the success path and the
lockfile it rests on are read where they are.

## What this does not cover

- **A PyJWT decode that only omits `require=["exp"]`.** PyJWT checks `exp`
  whenever the token carries one, so the call is wrong only if the issuer
  can omit it, which the code does not show.
- **An Authlib decode mixing HMAC and asymmetric algorithms from 1.3.1.**
  The documentation still calls it insecure, but no source read shows it
  exploitable once the advisory's fix is in.
- **Entity expansion in the standard library's parsers**, such as the
  billion laughs. The Python 3.15.2 *XML security* section ties it to the
  Expat version, below 2.7.2, and says whether the interpreter uses its
  bundled or the system's Expat depends on how it was built, to be checked
  at run time through `pyexpat.EXPAT_VERSION`
  (<https://docs.python.org/3/library/xml.html>). No code, manifest or
  lockfile records either, so a reading has nothing to quote. CodeQL's
  `py/xml-bomb` reports `xml.etree` regardless of version; the Python
  documentation, the primary source, governs, as it does for lxml's
  default above. lxml's own limits are the decidable case, and are checked.
- **`xmlrpc`'s decompression bomb.** The server decodes gzip under a
  20 MiB default `max_decode` in CPython's `xmlrpc.client.gzip_decode`,
  read in the 3.14 standard library's source
  (<https://github.com/python/cpython/blob/3.14/Lib/xmlrpc/client.py>), so
  the defect there would be an explicit unbounded limit, a form no source
  shows in use. The client's gzip response path sets no limit, but its
  exposure turns on whether the remote server is trusted, which a reading
  cannot decide. Bandit's B411 flags the import itself
  (<https://bandit.readthedocs.io/en/latest/blacklists/blacklist_imports.html>),
  a lint over module choice rather than a default the code gets wrong.
- **`xmltodict` and `untangle`.** Neither has a default a reading would
  report. `xmltodict.parse` defaults `disable_entities=True` and raises on
  an entity declaration (<https://github.com/martinblech/xmltodict>), so an
  explicit `disable_entities=False` exposes only internal expansion, which
  turns on the Expat version as above. `untangle` turns external general
  entities off in 1.2.0 and parses through `defusedxml` from 1.2.1
  (<https://github.com/stchris/untangle>); below that, its plain `xml.sax`
  parser processes no external general entities by default on Python
  3.7.1 and later, so the only defect would be an explicit
  `feature_external_ges=True`, which was not added.
- **Authorization**, which turns on how an application routes every
  request rather than on one call, and is the subject of a module of its
  own.
