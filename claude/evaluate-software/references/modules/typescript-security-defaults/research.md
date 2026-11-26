---
sources:
  - id: mdn-math-random
    title: "MDN Web Docs: Math.random()"
    url: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random
    date: 2026-11-26
  - id: node-crypto
    title: "Node.js v26.13.1 documentation: Crypto (randomBytes, randomUUID, timingSafeEqual)"
    url: https://nodejs.org/api/crypto.html
    date: 2026-11-26
  - id: nanoid-readme
    title: "Nano ID README (security, non-secure API)"
    url: https://github.com/ai/nanoid
    date: 2026-11-26
  - id: owasp-forgot-password
    title: "OWASP Cheat Sheet Series: Forgot Password Cheat Sheet"
    url: https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html
    date: 2026-11-26
  - id: rfc-8725
    title: "RFC 8725: JSON Web Token Best Current Practices (BCP 225), February 2020"
    url: https://www.rfc-editor.org/rfc/rfc8725.html
    date: 2026-11-26
  - id: jsonwebtoken-readme
    title: "jsonwebtoken README: jwt.verify options"
    url: https://github.com/auth0/node-jsonwebtoken
    date: 2026-11-26
  - id: jsonwebtoken-v9-notes
    title: "jsonwebtoken wiki: Migration Notes, v8 to v9"
    url: https://github.com/auth0/node-jsonwebtoken/wiki/Migration-Notes:-v8-to-v9
    date: 2026-11-26
  - id: ghsa-qwph-4952-7xr6
    title: "GHSA-qwph-4952-7xr6 (CVE-2022-23540): insecure default algorithm in jwt.verify()"
    url: https://github.com/auth0/node-jsonwebtoken/security/advisories/GHSA-qwph-4952-7xr6
    date: 2022-12-21
  - id: ghsa-hjrf-2m68-5959
    title: "GHSA-hjrf-2m68-5959 (CVE-2022-23541): key retrieval function allows RSA to HMAC forgery"
    url: https://github.com/auth0/node-jsonwebtoken/security/advisories/GHSA-hjrf-2m68-5959
    date: 2022-12-21
  - id: jose-verify-options
    title: "jose documentation: JWTVerifyOptions"
    url: https://github.com/panva/jose/blob/main/docs/jwt/verify/interfaces/JWTVerifyOptions.md
    date: 2026-11-26
  - id: rfc-6238
    title: "RFC 6238: TOTP, Time-Based One-Time Password Algorithm, May 2011"
    url: https://www.rfc-editor.org/rfc/rfc6238.html
    date: 2026-11-26
  - id: otplib-security
    title: "otplib guide: Security"
    url: https://otplib.yeojz.dev/guide/security
    date: 2026-11-26
  - id: otplib-advanced
    title: "otplib guide: Advanced usage (afterTimeStep, replay protection)"
    url: https://otplib.yeojz.dev/guide/advanced-usage
    date: 2026-11-26
  - id: codeql-js-xxe
    title: "CodeQL query help: XML external entity expansion (js/xxe)"
    url: https://codeql.github.com/codeql-query-help/javascript/js-xxe/
    date: 2026-11-26
  - id: owasp-xxe
    title: "OWASP Cheat Sheet Series: XML External Entity Prevention Cheat Sheet"
    url: https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html
    date: 2026-11-26
  - id: libxmljs-types
    title: "libxmljs v1.0.11 source, lib/types.ts (parse options, flags, defaults)"
    url: https://github.com/libxmljs/libxmljs/blob/v1.0.11/lib/types.ts
    date: 2023-10-18
  - id: libxmljs-parse
    title: "libxmljs v1.0.11 source, lib/parse.ts (options mapped to libxml2 flags)"
    url: https://github.com/libxmljs/libxmljs/blob/v1.0.11/lib/parse.ts
    date: 2023-10-18
findings:
  - id: math-random-is-not-for-secrets
    claim: >-
      `Math.random()` does not provide cryptographically secure random
      numbers and must not be used for anything related to security; the
      Web Crypto API's `getRandomValues()` is named instead. Nano ID names
      `Math.random()` as the unsafe approach its default avoids, and offers
      a non-secure variant only for environments without a secure source.
    confidence: strong
    sources: [mdn-math-random, nanoid-readme]
  - id: secrets-need-a-csprng
    claim: >-
      Node's `crypto.randomBytes` generates cryptographically strong
      pseudorandom data and `crypto.randomUUID` uses a cryptographic
      generator, and password reset tokens are to be generated with a
      cryptographically secure random number generator.
    confidence: strong
    sources: [node-crypto, owasp-forgot-password]
  - id: jwt-header-names-its-own-algorithm
    claim: >-
      A signed JWT carries its own algorithm in its header, an attacker can
      change it to `none` or from `RS256` to `HS256`, and some libraries
      trust it; the verifier must specify the algorithms it accepts, use
      no other, check that the header names the same one, and use each key
      with exactly one algorithm.
    confidence: strong
    sources: [rfc-8725]
  - id: jsonwebtoken-defaults-before-9
    claim: >-
      `jsonwebtoken` through 8.5.1 fell back to `none` when no `algorithms`
      were given and the key was falsy, and could verify a token signed
      with HMAC against an RSA public key through a key retrieval function;
      9.0.0 fixed both, refuses unsigned tokens unless `none` is listed,
      and derives the default list from the key's type.
    confidence: evidenced
    sources: [ghsa-qwph-4952-7xr6, ghsa-hjrf-2m68-5959, jsonwebtoken-v9-notes, jsonwebtoken-readme]
  - id: jose-defaults-to-the-key
    claim: >-
      `jose`'s verify defaults its accepted algorithms to those applicable
      to the key or secret and never accepts `alg: "none"`, so an absent
      `algorithms` there does not let the header choose a weaker check.
    confidence: evidenced
    sources: [jose-verify-options]
  - id: timing-safe-equal-covers-only-the-call
    claim: >-
      `crypto.timingSafeEqual` compares in constant time and throws when
      its inputs differ in byte length, and Node's documentation states
      that it does not make the surrounding code timing-safe, which must be
      kept from introducing timing vulnerabilities; it names HMAC digests
      as suitable inputs.
    confidence: evidenced
    sources: [node-crypto]
  - id: otp-must-be-refused-after-use
    claim: >-
      The TOTP verifier must not accept the second attempt of an OTP after
      the first has been validated, which is what makes it one-time.
    confidence: strong
    sources: [rfc-6238]
  - id: otp-libraries-are-stateless
    claim: >-
      `otplib` is stateless and does not track which tokens it has
      verified, so by default a TOTP code can be reused within its
      validity window; replay protection is the application's, by storing
      the time step of each successful verification and passing it back as
      `afterTimeStep`, or by advancing the HOTP counter.
    confidence: evidenced
    sources: [otplib-security, otplib-advanced]
  - id: reset-tokens-are-single-use
    claim: >-
      A password reset token is single use and is invalidated after it has
      been used.
    confidence: evidenced
    sources: [owasp-forgot-password]
  - id: entity-substitution-enables-xxe
    claim: >-
      Parsing untrusted XML with external entity handling enabled lets the
      document read files, cause denial of service or make server-side
      requests, even when the result is not returned; the remedy is to
      disable entity handling or DTDs, and `libxmljs` called with `noent`
      set true is the JavaScript case CodeQL reports.
    confidence: strong
    sources: [codeql-js-xxe, owasp-xxe]
  - id: libxmljs-substitutes-only-when-asked
    claim: >-
      `libxmljs` 1.x parses with no flags by default; `replaceEntities`, its
      deprecated alias `noent`, and `validateEntities` default to false and
      load DTDs to resolve externally defined entities when set, and the
      `XML_PARSE_NOENT` and `XML_PARSE_DTDLOAD` flags substitute entities
      and load the external subset. `parseXml` maps `replaceEntities` and
      `noent` to `XML_PARSE_NOENT`, and `validateEntities` and `dtdvalid`
      to `XML_PARSE_DTDVALID`.
    confidence: evidenced
    sources: [libxmljs-types, libxmljs-parse]
---

# Research: TypeScript security defaults

Read on 2026-11-26, at each source's own page: the platform documentation
first (MDN, Node.js v26.13.1, the RFCs), then each library's own
documentation, source and advisories, with OWASP's cheat sheets and CodeQL's
query help as the independent published guidance. Each `date` is the reading
date, except for the two advisories, dated as published, and the `libxmljs`
source, cited at its `v1.0.11` tag, the latest release on npm when read,
and dated as that release. The RFCs carry
only a month, given in their titles, so they are dated as read. No source is
a dated blog post.

The subject is a defect class that passes every functional test: each
mistake behaves like the secure version until someone attacks it. The five
candidates the module was scoped with were each kept, because each has a
quotable call and a reading rule that decides it; how each was narrowed is
below.

## How each check was decided

- **A predictable random secret.** `Math.random()` is a quotable call, but
  it is also used legitimately everywhere, so the `evidence` requires the
  value to be followed to a use as a secret, and a variable's name alone
  does not decide it. A helper built on it counts only where its own source
  or documentation says so, as Nano ID's does for its non-secure variant.
- **A JWT algorithm taken from the token.** The literal defect, an
  `algorithms` list or a key chosen from the unverified header, is always
  reported. An absent `algorithms` is reported only for `jsonwebtoken`
  below 9.0.0: from 9.0.0 that library refuses `none` and binds the default
  list to the key's type, and `jose` has always defaulted to the key, so in
  both an absent list does not let the header choose. The version is read
  from the lockfile, and an unreadable one leaves the case unresolved.
  RFC 8725 still asks for each key to carry one algorithm; a module that
  reported every absent list would report the current libraries' documented
  safe default as a defect, so that is left to a reviewer.
- **A timing-safe comparison undone.** The early return is quotable in the
  same function. A length check before the call is common and Node's
  documentation explains why: the call throws on unequal lengths. It leaks
  only the secret's length, so it is reported only where that length is not
  fixed and public; comparing two digests of the same size, which Node names
  as a suitable input, needs no length check and is the good form.
- **A one-time code accepted twice.** The defect is an absence, a missing
  write, so the `evidence` reads the success path to its return. Where that
  path calls code the reading cannot follow, such as a store behind an
  interface, the case is unresolved rather than reported, since the
  consumption may sit there.
- **XML external entities.** Of Node's XML parsers, the sources read name
  only `libxmljs`, whose defaults are safe and whose options and flags turn
  substitution on. The check therefore names that library and the options
  its source defines, and reports nothing for another parser, a fork of it
  included, whose options were not read. It also requires the
  input to come from outside the program, since a document the repository
  ships cannot carry an attacker's entity.

## Reading, not running

The static phase runs nothing, so a scanner such as CodeQL, Semgrep or a
library's own audit is a reference and never the mechanism. Every check is
applied by reading the call, the code around it and, where a library's
behaviour changed with a version, the lockfile. For a diff the finding sits
in the changed lines, while the declarations, the success path and the
lockfile it rests on are read where they are.

## What this does not cover

- **A hash or key derivation that ignores input past a length limit**, such
  as bcrypt's 72 bytes. The scoped candidates for this module did not
  include it; the library that has it in JavaScript is a dependency choice
  this module did not research.
- **A secret compared with `===` and no `timingSafeEqual` at all.** It is
  the commoner timing defect, but this module was scoped to the comparison
  undone by the code around it.
- **A token read with `jwt.decode` and never verified**, or a JWT's claims,
  expiry and audience left unchecked. Neither takes the algorithm from the
  header, the defect this module checks.
- **Other XML parsers**, such as `fast-xml-parser`, `xml2js` and
  `@xmldom/xmldom`, and entity expansion attacks that need no external
  entity. No source read states how they handle entities, so the module
  says nothing about them.
- **Authorization**, which turns on how an application routes every
  request rather than on one call, and is the subject of a module of its
  own.
- **Data typed without validation**, covered by the TypeScript type-safety
  module's check on untrusted data, which this module does not repeat.
- **JavaScript files.** The checks read JavaScript as well as TypeScript,
  but the module's language is TypeScript and its triggers match
  TypeScript sources only.
