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
  - id: jsonwebtoken-verify-source
    title: "jsonwebtoken v9.0.3 source, verify.js (nbf, exp and aud checks)"
    url: https://github.com/auth0/node-jsonwebtoken/blob/v9.0.3/verify.js
    date: 2025-12-04
  - id: jose-decode-jwt
    title: "jose documentation: decodeJwt"
    url: https://github.com/panva/jose/blob/main/docs/util/decode_jwt/functions/decodeJwt.md
    date: 2026-11-26
  - id: codeql-js-decode-jwt
    title: "CodeQL experimental query help: JWT decoded without verification (CWE-347, JavaScript)"
    url: https://github.com/github/codeql/blob/main/javascript/ql/src/experimental/Security/CWE-347/decodeJwtWithoutVerification.qhelp
    date: 2026-11-26
  - id: rfc-7519
    title: "RFC 7519: JSON Web Token (JWT), May 2015"
    url: https://www.rfc-editor.org/rfc/rfc7519.html
    date: 2026-11-26
  - id: google-verify-id-token
    title: "Google for Developers: Verify the Google ID token on your server side"
    url: https://developers.google.com/identity/gsi/web/guides/verify-google-id-token
    date: 2026-11-26
  - id: github-webhook-validation
    title: "GitHub Docs: Validating webhook deliveries"
    url: https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries
    date: 2026-11-26
  - id: cloudflare-timing-attacks
    title: "Cloudflare Workers examples: Using timingSafeEqual (protect against timing attacks)"
    url: https://developers.cloudflare.com/workers/examples/protect-against-timing-attacks/
    date: 2026-04-23
  - id: libxmljs2-types
    title: "libxmljs2 v0.37.0 source, index.d.ts (ParserOptions)"
    url: https://github.com/marudor/libxmljs2/blob/v0.37.0/index.d.ts
    date: 2025-06-01
  - id: libxmljs2-document
    title: "libxmljs2 v0.37.0 source, src/xml_document.cc (options mapped to libxml2 flags)"
    url: https://github.com/marudor/libxmljs2/blob/v0.37.0/src/xml_document.cc
    date: 2025-06-01
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
  - id: unverified-jwt-must-be-rejected
    claim: >-
      All cryptographic operations used in a JWT must be validated, and the
      entire JWT rejected if any of them fails to validate.
    confidence: strong
    sources: [rfc-8725]
  - id: jwt-decode-functions-do-not-verify
    claim: >-
      `jsonwebtoken`'s `decode` returns the payload without verifying the
      signature and is not to be used for untrusted messages, `verify`
      being named instead; `jose`'s `decodeJwt` validates neither the
      signature nor the claims' types and values, `jwtVerify` being named
      for signed tokens; and CodeQL's experimental JavaScript query reports
      a JWT only decoded, never verified, as CWE-347.
    confidence: strong
    sources: [jsonwebtoken-readme, jose-decode-jwt, codeql-js-decode-jwt]
  - id: jwt-expiry-must-be-enforced
    claim: >-
      A JWT must not be accepted for processing on or after the time its
      `exp` claim names, nor before the time its `nbf` claim names.
    confidence: strong
    sources: [rfc-7519]
  - id: jsonwebtoken-ignore-options-skip-the-check
    claim: >-
      `jsonwebtoken`'s `verify` checks `nbf` and `exp` whenever the token
      carries them, unless `ignoreNotBefore` or `ignoreExpiration` is set,
      which skips that check; the README defines `ignoreExpiration` as not
      validating the token's expiration.
    confidence: evidenced
    sources: [jsonwebtoken-readme, jsonwebtoken-verify-source]
  - id: audience-is-checked-only-when-named
    claim: >-
      `jsonwebtoken`'s `verify` checks the audience only when an `audience`
      option is given, the README saying to provide one to check `aud`;
      `jose`'s `audience` option names the expected value and requires the
      claim, and its verify options hold no audience check without it.
    confidence: evidenced
    sources: [jsonwebtoken-readme, jsonwebtoken-verify-source, jose-verify-options]
  - id: jwt-audience-must-be-validated
    claim: >-
      Where the same issuer can issue JWTs for more than one relying party,
      the JWT must carry an audience and the relying party must validate
      it; Google's server-side guide calls the `aud` check necessary, so
      that an ID token issued to a malicious app cannot be used to reach
      the same user's data on another app's backend.
    confidence: strong
    sources: [rfc-8725, google-verify-id-token]
  - id: plain-equality-is-not-timing-safe
    claim: >-
      Node names `crypto.timingSafeEqual` as suitable for comparing HMAC
      digests and secret values such as authentication cookies; GitHub's
      webhook guide says never to use a plain `==` for the signature and
      names `crypto.timingSafeEqual`; and Cloudflare's example says a `==`
      or `===` comparison ends at the first mismatched character.
    confidence: strong
    sources: [node-crypto, github-webhook-validation, cloudflare-timing-attacks]
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
  - id: libxmljs2-sets-the-flags-only-when-asked
    claim: >-
      The `libxmljs2` fork declares `noent` and `dtdload` among its parse
      options, and maps them to the same libxml2 flags,
      `XML_PARSE_NOENT` to substitute entities and `XML_PARSE_DTDLOAD` to
      load the external subset, setting each only when the option is given
      true, so its default parse sets neither.
    confidence: evidenced
    sources: [libxmljs2-types, libxmljs2-document]
---

# Research: TypeScript security defaults

Read on 2026-11-26, at each source's own page: the platform documentation
first (MDN, Node.js v26.13.1, the RFCs), then each library's own
documentation, source and advisories, with OWASP's cheat sheets and CodeQL's
query help as the independent published guidance, and GitHub's,
Cloudflare's and Google's guides beside them. Each `date` is the reading
date, except for the two advisories, dated as published; the sources cited
at a release tag, dated as that release: the `libxmljs` source at
`v1.0.11`, `jsonwebtoken`'s `verify.js` at `v9.0.3` and the `libxmljs2`
source at `v0.37.0`, each the latest release on npm when read; and
Cloudflare's example, dated as its page was last modified. The RFCs carry
only a month, given in their titles, so they are dated as read. No source is
a dated blog post. The checks added after the module was published were
drafted on 2026-11-26 from sources re-read that day.

The subject is a defect class that passes every functional test: each
mistake behaves like the secure version until someone attacks it. The five
candidates the module was scoped with were each kept, because each has a
quotable call and a reading rule that decides it. Three checks were added
after the module was published, and one widened, each approved before it
was drafted: a JWT decoded and never verified, a JWT's expiry or audience
left unchecked, plain equality on a secret, and the `libxmljs2` fork added
to the XML check. How each was narrowed is below.

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
- **A JWT decoded and never verified.** `jsonwebtoken`'s `decode` and
  `jose`'s `decodeJwt` are quotable calls, but reading a header's `kid` or
  the `iss` claim to choose the key before a verify is legitimate, so the
  `evidence` follows the claims to an identity or authorization decision
  and requires no verify of the same token on the path. A service behind a
  gateway that verified the token is the common legitimate case the code
  cannot confirm, so it is named unresolved, as the Python module's check
  of the same name does. **Severity `critical`**, matching that check and
  `jwt-algorithm-not-pinned`: a token the attacker wrote is accepted with
  any identity they chose, with no algorithm trick needed. The TypeScript
  type-safety module's check on untrusted data reads a type given to
  unchecked data, not whether a signature was checked, so the two may both
  report the same decode, each for its own defect.
- **A JWT's expiry or audience left unchecked.** Named as the Python
  module's claims check is, and at its severity, **`high`**, one below the
  forged-token checks: the attacker needs a token once validly issued, so
  the defect extends a captured credential's life or reach rather than
  minting one. It holds two forms. The first is literal: `jsonwebtoken`'s
  `ignoreExpiration` and `ignoreNotBefore` turn off a check RFC 7519 says
  must hold, and the token is traced to the request, since a test or a
  refresh flow that reissues only after a separate check reads an expired
  token on purpose. `jose` has no such option, so only `jsonwebtoken` is
  read. The second, the audience, is narrowed: RFC 8725 requires the check
  only where one issuer serves more than one relying party, which one
  repository rarely shows, so an absent `audience` is reported only on a
  verify against a third-party identity provider's key set. That issuer
  serves many applications by design, and Google's guide states the harm:
  a token issued to another, possibly malicious, app is accepted as the
  user it names. The audience is `high` like the expiry, not lower,
  because the harm is the same, a validly issued token accepted where it
  was not meant to be; it is not `critical`, because the attacker still
  needs a token the provider issued for that user. A token the
  repository's own service issues and verifies is excluded, since there
  the issuer serves only this one party. A key-set URL read from
  configuration does not show whose provider it is, so it is unresolved.
- **A secret compared by plain equality.** `===` on strings is everywhere,
  so the `evidence` traces each side, one to a secret the server holds and
  one to the request, and excludes a digest looked up by hash and a
  password-hashing library's own verify. Its wording is shared with the Go
  and Python modules' checks of the same name, sentence for sentence, with
  only the calls changed, so the three read the defect the same way.
  **Severity `medium`**, matching `timing-safe-compare-undone` here and the
  two siblings: a timing attack over a network needs many requests, and no
  primary source read quantifies how exploitable a JavaScript string
  comparison is.
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
  `libxmljs`, whose defaults are safe and whose options and flags turn
  substitution on, and its `libxmljs2` fork, whose source maps its `noent`
  and `dtdload` options to the same libxml2 flags and sets neither by
  default. The fork's release 0.37.0 is from 2025-06-01, and its
  repository was still pushed to in 2026 and not archived when read. The
  check names those two libraries and the options their sources define,
  and reports nothing for another parser or fork whose options were not
  read. Of the fork's options only `noent` and `dtdload` are read: its
  `dtdvalid` reaches libxml2's validation flag too, but no source read for
  the fork states what it loads. The check also requires the
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
- **An absent audience on a token from any other issuer.** RFC 8725 makes
  the check conditional on an issuer serving more than one relying party,
  which a single repository rarely shows, so only a third-party identity
  provider's key set is read.
- **A `jose` verify whose expiry check is weakened** by a large
  `clockTolerance` or a `currentDate` in the past. Neither turns the check
  off by name, and no source read says what value would be a defect.
- **`xml2js` and `@xmldom/xmldom`.** Neither resolves an external entity:
  `xml2js` parses with `sax`, which handles only the five predefined
  entities and does nothing with those a DTD defines
  ([sax README](https://github.com/isaacs/sax-js), read 2026-11-26), and
  `@xmldom/xmldom` fixes its entity map to the predefined XML or HTML
  entities and ignores the SAX entity resolver
  ([dom-parser.js](https://github.com/xmldom/xmldom/blob/master/lib/dom-parser.js),
  read 2026-11-26). An external-entity check on them would report nothing.
- **`fast-xml-parser`'s entity expansion.** Its `processEntities` defaults
  to `true`, and its *Entities* page recommends `false` for untrusted XML,
  but the same page says external entities are not supported and calls
  the default limits safe for trusted XML
  ([Entities](https://github.com/NaturalIntelligence/fast-xml-parser/blob/master/docs/v4%2C%20v5/5.Entities.md),
  v5.12.1, read 2026-11-26). The harm left is expansion within those
  limits, and the library's 2026 entity advisories, one for expansion with
  no limit and several bypassing the limits added since, are each fixed in
  a later release, which a dependency audit reports from the lockfile
  better than a reading of the call does. It was proposed as a check and
  declined for that reason.
- **Authorization**, which turns on how an application routes every
  request rather than on one call, and is the subject of a module of its
  own.
- **Data typed without validation**, covered by the TypeScript type-safety
  module's check on untrusted data, which this module does not repeat.
- **JavaScript files.** The checks read JavaScript as well as TypeScript,
  but the module's language is TypeScript and its triggers match
  TypeScript sources only.
