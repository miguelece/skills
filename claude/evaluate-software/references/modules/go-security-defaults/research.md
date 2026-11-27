---
sources:
  - id: go-math-rand
    title: "Go go1.27.4 standard library: math/rand (Seed, NewSource)"
    url: https://pkg.go.dev/math/rand
    date: 2026-11-26
  - id: go-math-rand-v2
    title: "Go go1.27.4 standard library: math/rand/v2"
    url: https://pkg.go.dev/math/rand/v2
    date: 2026-11-26
  - id: go-crypto-rand
    title: "Go go1.27.4 standard library: crypto/rand"
    url: https://pkg.go.dev/crypto/rand
    date: 2026-11-26
  - id: go-blog-chacha8rand
    title: "The Go Blog: Secure Randomness in Go 1.22"
    url: https://go.dev/blog/chacha8rand
    date: 2024-05-02
  - id: go-toolchains
    title: "Go documentation: Go Toolchains (the go and toolchain lines)"
    url: https://go.dev/doc/toolchain
    date: 2026-11-26
  - id: go-math-rand-source
    title: "Go source at tag go1.27.4: src/math/rand/rand.go (randautoseed, globalRand)"
    url: https://raw.githubusercontent.com/golang/go/go1.27.4/src/math/rand/rand.go
    date: 2026-11-26
  - id: go-math-rand-v2-source
    title: "Go source at tag go1.27.4: src/math/rand/v2/rand.go (the top-level generator)"
    url: https://raw.githubusercontent.com/golang/go/go1.27.4/src/math/rand/v2/rand.go
    date: 2026-11-26
  - id: go-godebug
    title: "Go documentation: Go, Backwards Compatibility, and GODEBUG"
    url: https://go.dev/doc/godebug
    date: 2026-11-26
  - id: go-modules-reference
    title: "Go Modules Reference: the godebug directive of go.mod and go.work"
    url: https://go.dev/ref/mod
    date: 2026-11-26
  - id: owasp-forgot-password
    title: "OWASP Cheat Sheet Series: Forgot Password Cheat Sheet"
    url: https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html
    date: 2026-11-26
  - id: x-crypto-bcrypt
    title: "golang.org/x/crypto v0.59.0: bcrypt (GenerateFromPassword, ErrPasswordTooLong)"
    url: https://pkg.go.dev/golang.org/x/crypto/bcrypt
    date: 2026-11-26
  - id: x-crypto-bcrypt-commit
    title: "x/crypto commit bc7d1d1: bcrypt: reject passwords longer than 72 bytes"
    url: https://go.googlesource.com/crypto/+/bc7d1d1eb54b3530da4f5ec31625c95d7df40231
    date: 2022-12-21
  - id: x-crypto-v0-5-0
    title: "x/crypto tag v0.5.0 (parent commit bc7d1d1)"
    url: https://go.googlesource.com/crypto/+/refs/tags/v0.5.0
    date: 2023-01-04
  - id: owasp-password-storage
    title: "OWASP Cheat Sheet Series: Password Storage Cheat Sheet"
    url: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
    date: 2026-11-26
  - id: go-crypto-subtle
    title: "Go go1.27.4 standard library: crypto/subtle (ConstantTimeCompare)"
    url: https://pkg.go.dev/crypto/subtle
    date: 2026-11-26
  - id: go-crypto-hmac
    title: "Go go1.27.4 standard library: crypto/hmac (Equal)"
    url: https://pkg.go.dev/crypto/hmac
    date: 2026-11-26
  - id: rfc-6238
    title: "RFC 6238: TOTP, Time-Based One-Time Password Algorithm, May 2011"
    url: https://www.rfc-editor.org/rfc/rfc6238.html
    date: 2026-11-26
  - id: pquerna-otp-totp-docs
    title: "github.com/pquerna/otp v1.5.0: totp (Validate, ValidateCustom)"
    url: https://pkg.go.dev/github.com/pquerna/otp/totp
    date: 2024-12-31
  - id: pquerna-otp-totp-source
    title: "pquerna/otp source, totp/totp.go (Validate, ValidateCustom)"
    url: https://github.com/pquerna/otp/blob/master/totp/totp.go
    date: 2026-11-26
  - id: gosec-rules
    title: "gosec RULES.md: G404, insecure random number source"
    url: https://github.com/securego/gosec/blob/master/RULES.md
    date: 2026-11-26
  - id: gosec-rand-source
    title: "gosec source, rules/rand.go (math/rand and math/rand/v2 functions)"
    url: https://github.com/securego/gosec/blob/master/rules/rand.go
    date: 2026-11-26
  - id: codeql-go-insecure-randomness
    title: "CodeQL query help: go/insecure-randomness"
    url: https://codeql.github.com/codeql-query-help/go/go-insecure-randomness/
    date: 2026-11-26
  - id: rfc-8725
    title: "RFC 8725: JSON Web Token Best Current Practices (BCP 225), February 2020"
    url: https://www.rfc-editor.org/rfc/rfc8725.html
    date: 2026-11-26
  - id: golang-jwt-docs
    title: "github.com/golang-jwt/jwt v5.3.1 documentation (WithValidMethods, UnsafeAllowNoneSignatureType)"
    url: https://pkg.go.dev/github.com/golang-jwt/jwt/v5
    date: 2026-01-28
  - id: golang-jwt-parser
    title: "golang-jwt/jwt source, parser.go (signing method from the header's alg)"
    url: https://github.com/golang-jwt/jwt/blob/main/parser.go
    date: 2026-11-26
  - id: golang-jwt-hmac
    title: "golang-jwt/jwt source, hmac.go (SigningMethodHMAC.Verify)"
    url: https://github.com/golang-jwt/jwt/blob/main/hmac.go
    date: 2026-11-26
  - id: golang-jwt-rsa
    title: "golang-jwt/jwt source, rsa.go (SigningMethodRSA.Verify)"
    url: https://github.com/golang-jwt/jwt/blob/main/rsa.go
    date: 2026-11-26
  - id: go-jose-v3-jwt
    title: "github.com/go-jose/go-jose/v3 v3.0.5: jwt (ParseSigned)"
    url: https://pkg.go.dev/github.com/go-jose/go-jose/v3/jwt
    date: 2026-03-31
  - id: go-jose-v3-signing
    title: "go-jose source, v3 branch, signing.go (newVerifier)"
    url: https://github.com/go-jose/go-jose/blob/v3/signing.go
    date: 2026-11-26
  - id: go-jose-v3-asymmetric
    title: "go-jose source, v3 branch, asymmetric.go (RSA verifier algorithms)"
    url: https://github.com/go-jose/go-jose/blob/v3/asymmetric.go
    date: 2026-11-26
  - id: go-jose-v4-jwt
    title: "github.com/go-jose/go-jose/v4 v4.1.9: jwt (ParseSigned)"
    url: https://pkg.go.dev/github.com/go-jose/go-jose/v4/jwt
    date: 2026-11-05
  - id: jwx-v3-jws
    title: "github.com/lestrrat-go/jwx/v3 v3.4.0: jws (Verify, WithKey)"
    url: https://pkg.go.dev/github.com/lestrrat-go/jwx/v3/jws
    date: 2026-10-23
findings:
  - id: math-rand-is-not-for-secrets
    claim: >-
      Go's documentation says `math/rand/v2` should not be used for
      security-sensitive work, that its outputs might be easily predictable
      regardless of how it is seeded, and both `math/rand` and
      `math/rand/v2` name `crypto/rand`, a cryptographically secure
      generator, for security-sensitive random numbers.
    confidence: strong
    sources: [go-math-rand-v2, go-math-rand, go-crypto-rand]
  - id: seeded-generators-are-predictable
    claim: >-
      A `math/rand` source is seeded with the value it is given, seeds with
      the same remainder modulo 2^31-1 generate the same sequence, and
      before Go 1.20 the top-level generator was seeded as `Seed(1)` at
      program startup.
    confidence: evidenced
    sources: [go-math-rand]
  - id: top-level-math-rand-is-chacha8-from-1-22
    claim: >-
      From Go 1.22 the top-level `math/rand` functions, when `rand.Seed` has
      not been called, and `math/rand/v2`'s, draw from ChaCha8Rand, so that
      accidentally using `math/rand` is no longer a security catastrophe,
      though `crypto/rand` is still better; a call to `rand.Seed` falls back
      to the Go 1 generator, and from Go 1.24 `rand.Seed` is a no-op unless
      `GODEBUG=randseednop=0` restores it.
    confidence: evidenced
    sources: [go-blog-chacha8rand, go-math-rand]
  - id: randautoseed-zero-seeds-math-rand-with-one
    claim: >-
      When the `randautoseed` setting is `0`, the top-level `math/rand`
      generator is built on its first use from a locked source seeded with
      `Seed(1)`, by a branch that reads no Go version, while `math/rand/v2`'s
      top-level generator reads no such setting. No `go` line defaults the
      setting to `0`; a program sets it with a `godebug` directive of the
      main module's `go.mod`, on one line or in a block, or of `go.work`,
      which replaces those directives in a workspace, or with a `//go:debug`
      directive before the `package` clause of a main package's file, and
      the environment's `GODEBUG` can set it at run time.
    confidence: evidenced
    sources: [go-math-rand-source, go-math-rand-v2-source, go-math-rand, go-godebug, go-modules-reference]
  - id: chacha8-is-weaker-than-crypto-rand
    claim: >-
      The Go project says `crypto/rand` is still better than the ChaCha8
      generator behind the top-level `math/rand` functions, because the
      kernel keeps its values secret from more kinds of prying eyes and
      keeps adding entropy, while a compromise of the process's memory
      exposes the generator's values since its last rekey.
    confidence: evidenced
    sources: [go-blog-chacha8rand]
  - id: scanners-report-math-rand-at-any-version
    claim: >-
      `gosec`'s rule G404 reports the functions of `math/rand` and
      `math/rand/v2` as an insecure random number source by package and
      name alone, reading no Go version, and CodeQL's
      `go/insecure-randomness`, at precision high and security severity
      7.8, reports `math/rand` flowing to a security-sensitive value such
      as a password or key, naming no Go version either.
    confidence: evidenced
    sources: [gosec-rules, gosec-rand-source, codeql-go-insecure-randomness]
  - id: go-line-is-the-minimum-toolchain
    claim: >-
      Since Go 1.21 the `go` line of `go.mod` is the minimum Go version
      required to build the module, and a toolchain older than it refuses
      the module, while any newer toolchain may build it.
    confidence: evidenced
    sources: [go-toolchains]
  - id: secrets-need-a-csprng
    claim: >-
      `crypto/rand` implements a cryptographically secure generator, with
      `rand.Text` returning a cryptographically random string from Go 1.24;
      password reset tokens are to be generated with a cryptographically
      secure random number generator.
    confidence: strong
    sources: [go-crypto-rand, owasp-forgot-password]
  - id: bcrypt-reads-only-72-bytes
    claim: >-
      bcrypt uses only the first 72 bytes of a password, and most
      implementations, the reference one included, silently ignore the
      input past them; OWASP names 72 bytes as bcrypt's maximum input
      length and advises enforcing it.
    confidence: strong
    sources: [x-crypto-bcrypt-commit, x-crypto-bcrypt, owasp-password-storage]
  - id: x-crypto-bcrypt-rejects-long-input-from-0-5-0
    claim: >-
      `x/crypto`'s `bcrypt.GenerateFromPassword` rejects a password longer
      than 72 bytes with `ErrPasswordTooLong` from the commit tagged in
      v0.5.0, released 2023-01-04, and silently truncated it before;
      `CompareHashAndPassword` still accepts such input, so hashes already
      stored keep working.
    confidence: evidenced
    sources: [x-crypto-bcrypt-commit, x-crypto-v0-5-0, x-crypto-bcrypt]
  - id: constant-time-compare-covers-only-the-call
    claim: >-
      `subtle.ConstantTimeCompare` takes time that depends on the slices'
      length and not on their contents, and returns 0 at once when the
      lengths differ; `hmac.Equal` compares two MACs without leaking timing
      information. Each protects only the comparison it performs.
    confidence: evidenced
    sources: [go-crypto-subtle, go-crypto-hmac]
  - id: plain-equality-is-not-timing-safe
    claim: >-
      `crypto/hmac` tells receivers to compare MACs with `Equal` to avoid
      timing side-channels, and `crypto/subtle`'s `ConstantTimeCompare` and
      `hmac.Equal` are the standard library's comparisons documented to
      take time independent of the contents; `==`, `bytes.Equal` and
      `strings.Compare` carry no such guarantee.
    confidence: evidenced
    sources: [go-crypto-hmac, go-crypto-subtle]
  - id: jwt-header-names-its-own-algorithm
    claim: >-
      A signed JWT carries its own algorithm in its header, an attacker can
      change it, as from `RS256` to `HS256` or to `none`, and some libraries
      trust it; libraries must let the caller specify the algorithms it
      supports and must use no other, and each key is used with exactly one
      algorithm.
    confidence: strong
    sources: [rfc-8725]
  - id: golang-jwt-header-chooses-unless-restricted
    claim: >-
      `golang-jwt/jwt` v5's parser looks the signing method up from the
      token header's `alg` and checks it against an allowed list only when
      the `WithValidMethods` option is set, which the caller is strongly
      encouraged to do; `none` is accepted only when the key function
      returns `UnsafeAllowNoneSignatureType`.
    confidence: evidenced
    sources: [golang-jwt-parser, golang-jwt-docs]
  - id: golang-jwt-binds-each-method-to-a-key-type
    claim: >-
      In `golang-jwt/jwt`, the HMAC method's `Verify` requires a `[]byte`
      key and the RSA method's an `*rsa.PublicKey`, each returning an
      invalid key type error for any other, so a header naming another
      family fails unless the key function hands back a key of that family.
    confidence: evidenced
    sources: [golang-jwt-hmac, golang-jwt-rsa]
  - id: go-jose-v3-chooses-the-verifier-by-key-type
    claim: >-
      `go-jose` v3's `jwt.ParseSigned` takes no list of algorithms; the
      verifier is picked by the Go type of the key given to verification, a
      `[]byte` selecting the HMAC verifier, and the RSA verifier refuses an
      HMAC `alg` as unsupported.
    confidence: evidenced
    sources: [go-jose-v3-jwt, go-jose-v3-signing, go-jose-v3-asymmetric]
  - id: go-jose-v4-requires-an-algorithm-list
    claim: >-
      `go-jose` v4's `jwt.ParseSigned` takes the list of allowed signature
      algorithms, which must be non-empty, and a token whose `alg` is not
      in it is a parse error.
    confidence: evidenced
    sources: [go-jose-v4-jwt]
  - id: jwx-names-the-algorithm-with-the-key
    claim: >-
      `lestrrat-go/jwx` v3's `jws.WithKey(alg, key)` names the algorithm
      with each verification key, and `Verify` uses the algorithm given
      with the key rather than the header's.
    confidence: evidenced
    sources: [jwx-v3-jws]
  - id: otp-must-be-refused-after-use
    claim: >-
      The TOTP verifier must not accept the second attempt of an OTP after
      the first has been validated, which is what makes it one-time.
    confidence: strong
    sources: [rfc-6238]
  - id: pquerna-otp-validate-is-stateless
    claim: >-
      `pquerna/otp`'s `totp.Validate(passcode, secret)` and
      `totp.ValidateCustom` are functions of the passcode, the secret, the
      time and the options alone, accepting any code in the skew window
      and keeping no record of codes accepted, and the documentation names
      no replay protection, so refusing a code already used is the
      application's.
    confidence: evidenced
    sources: [pquerna-otp-totp-source, pquerna-otp-totp-docs]
  - id: reset-tokens-are-single-use
    claim: >-
      A password reset token is single use and is invalidated after it has
      been used.
    confidence: evidenced
    sources: [owasp-forgot-password]
---

# Research: Go security defaults

Read on 2026-11-26, at each source's own page: the Go standard library's
documentation and the source of `math/rand` and `math/rand/v2` at
go1.27.4, and the Go project's own documentation and module reference
first, then `golang.org/x/crypto`'s documentation and history,
`pquerna/otp`'s documentation and source, and the documentation and source
of the JWT
libraries `golang-jwt/jwt`, `go-jose` and `lestrrat-go/jwx`, with OWASP's
cheat sheets, RFC 8725 and the `gosec` and CodeQL rules as the independent
published guidance. Each `date` is the reading date, except for the Go blog
post, dated as published, the `x/crypto` commit, dated as committed, the
v0.5.0 tag, dated as tagged, and the `pquerna/otp`, `golang-jwt/jwt`,
`go-jose` and `jwx` documentation, each dated as the release the page shows.
The RFCs carry only a month, given in their titles, so they are dated as
read. The one dated post is the Go
project's own blog, cited for what the package pages do not say: since when
the top-level generator is ChaCha8.

The subject is a defect class that passes every functional test: each
mistake behaves like the secure version until someone attacks it. Of the
five candidates the module was scoped with, four were kept, because each has
a quotable call and a reading rule that decides it, and the fifth was
dropped, because the Go standard library cannot show the defect. Three
checks were added after the module was published, each approved on its own
before it was drafted: the ChaCha8 random secret, the JWT algorithm and the
comparison by plain equality. The predictable random secret was corrected
after publishing, also on its own approval, to read a `randautoseed=0`
setting.

## How each check was decided

- **A predictable random secret.** The candidate was a secret from
  `math/rand` rather than `crypto/rand`. Every function of `math/rand` is a
  quotable call, but the package is used legitimately everywhere, so the
  `evidence` requires the value to be followed to a use as a secret, and a
  name alone does not decide it. The harder question was the version. Go's
  documentation still says the package is not for security-sensitive work,
  but from Go 1.22 its unseeded top-level functions draw from ChaCha8, which
  the Go project calls no longer a security catastrophe. A finding of high
  severity on those calls would overstate it, so the check reports what is
  predictable: a generator the code seeds itself, in any version, and a
  top-level call on a `go` line that admits a toolchain older than 1.22, or
  one that `rand.Seed` returns to the Go 1 generator. A `randautoseed=0`
  setting returns the top-level generator to `Seed(1)` at any version, since
  the branch that builds it reads only the setting, so a top-level call in a
  program holding one is reported whatever its `go` line. The setting is
  read where `randseednop` is, in the program's `godebug` and `//go:debug`
  lines, and also in `go.work` and a one-line `godebug`, which Go's
  reference accepts too. The `go` line is the
  minimum toolchain, not the one that builds, so a line below 1.22 is
  reported because the module accepts the predictable generator, not because
  it certainly gets it. A top-level call on a newer line is left to the
  check of lower severity below.
- **A ChaCha8 random secret.** A top-level call on a `go` line of 1.22 or
  later still goes against Go's documentation, and both `gosec` and CodeQL
  report `math/rand` with no version gate, while the Go project's blog calls
  the residual risk small. So it is a check of its own at `low`, not a
  widening of the high one: the value is hard to predict today, and what
  remains is the weaker protection of a user-space generator and the one
  `rand.Seed` that makes it predictable. It reuses the high check's rule
  that the value be followed to a use as a secret, so its false positives
  are that check's, and it reads the same `go` line, so an unreadable one
  leaves a top-level `math/rand` call unresolved rather than low, since it
  may be the high defect.
- **A JWT algorithm the header chooses.** RFC 8725 requires the verifier to
  pin the algorithm, and in `golang-jwt/jwt` the header chooses it unless
  `WithValidMethods` is set. But each Go library read binds the algorithm
  family to the key's Go type: `golang-jwt/jwt`'s methods refuse a key of
  another type, and `go-jose` v3 picks its verifier by the key's type. So a
  call without `WithValidMethods` is safe when its key function returns one
  key of one type, and a check on every such call would report sound code.
  The classic forgery, a public key used as an HMAC secret, needs the key
  function to hand back public material as a `[]byte` or to pick the key
  from the header, and the check reads exactly those two forms. `none` needs
  the explicit `UnsafeAllowNoneSignatureType`, a choice no reading mistakes
  for a default, so it is not a form of its own. `go-jose` v4 and `jwx` make
  the caller name the algorithm, so their calls are not this defect, and
  `gopkg.in/square/go-jose.v2` and any other library were not read, so a
  call through one is unresolved. No source read reports the Go form in real
  code, and `gosec` has no JWT rule; the severity is the sibling modules',
  since the defect, where it occurs, forges any token.
- **bcrypt input past 72 bytes.** The candidate was input that can pass the
  limit, such as a concatenated string. bcrypt reads only 72 bytes, and
  `x/crypto` silently dropped the rest until v0.5.0, which returns
  `ErrPasswordTooLong` from `GenerateFromPassword` instead. A long password
  hashed alone loses only its own tail, which bcrypt's design accepts, so
  the check needs a value joined before the password, where the password is
  what is lost. On v0.5.0 or later such input fails loudly, a usability
  defect rather than this one, so the version, read from `go.mod`, decides
  it, and an unreadable one leaves the case unresolved. OWASP's warning
  about pre-hashing turns on implementations that stop at a NUL byte;
  `x/crypto`'s own source appends a NUL and was not read to stop at one, so
  no check rests on it.
- **A timing-safe comparison undone.** The early return is quotable in the
  same function. `subtle.ConstantTimeCompare` returns at once on unequal
  lengths, so its timing already reveals the length, and a length check
  before it discloses nothing the call does not, and is not reported.
  `hmac.Equal` is the standard library's named comparison for MACs, so it
  is read the same way.
- **A secret compared by plain equality.** It is the commoner timing defect:
  no constant-time call at all. `crypto/hmac` tells receivers to compare
  MACs with `Equal` to avoid timing side-channels. CodeQL's
  `go/timing-attack`, read 2026-11-26 at
  [Timing.ql](https://github.com/github/codeql/blob/main/go/ql/src/experimental/CWE-203/Timing.ql),
  models `==`, `!=` and `strings.Compare` on values named as secrets, but is
  experimental and outside the default suite, and `gosec` has no rule. The
  check needs both sides traced, one to a secret the server holds and the
  other to the request, because a name such as `token` does not show either.
  A digest looked up by hash leaks nothing an attacker can use, since the
  time tracks the hash of the guess, and a bcrypt or argon2 verify does its
  own comparison, so neither is reported. No source read measures how much
  `==` on Go strings or slices leaks over a network, so the severity is the
  undone comparison's, `medium`, not higher. The rule is worded to hold in
  any language with only the comparison calls changed.
- **A one-time code accepted twice.** The defect is an absence, a missing
  write, so the `evidence` reads the success path to its return. Where that
  path calls code the reading cannot follow, such as a store behind an
  interface, the case is unresolved rather than reported, since the
  consumption may sit there. `pquerna/otp` is named because its
  `totp.Validate` takes only the passcode and the secret, so it cannot
  record a use.
- **XML external entities: dropped.** The hypothesis was that the standard
  `encoding/xml` resolves none, and the reading confirms it. The package
  documentation, read 2026-11-26 at
  [pkg.go.dev/encoding/xml](https://pkg.go.dev/encoding/xml), offers only
  `Decoder.Entity`, a map of non-standard entity names to string
  replacements that the caller supplies, and `HTMLEntity`. The source, read
  the same day at
  [go.dev/src/encoding/xml/xml.go](https://go.dev/src/encoding/xml/xml.go),
  returns a `<!DOCTYPE ...>` as a `Directive` token, accumulated for the
  caller and never parsed for entity declarations, reports an entity
  outside the built-in set and that map as a syntax error in strict mode,
  and imports neither `os` nor `net`, so a document can name a `SYSTEM`
  file or URL but the decoder never opens it. A reading therefore has no
  call that can show the defect in standard Go, and a check would report
  nothing.

## Reading, not running

The static phase runs nothing, so a scanner such as `gosec`, `govulncheck`
or CodeQL is a reference and never the mechanism. Every check is applied by
reading the call, the code around it and, where behaviour changed with a
version, `go.mod`. For a diff the finding sits in the changed lines, while
the `go` line, the required version and the success path it rests on are
read where they are.

## What this does not cover

- **XML parsed through a cgo binding to libxml2** or another third-party
  parser, whose entity handling no source read states.
- **A `GenerateFromPassword` error that is discarded**, which the Go error
  handling module reads, and **pre-hashing before bcrypt**, for the reason
  above.
- **A JWT parsed without verification and its claims trusted**, as with
  `golang-jwt/jwt`'s `ParseUnverified`, and **JWT claims left unchecked**,
  such as no expected audience or no required expiry. Neither was among the
  checks approved for this module.
- **A `GODEBUG` set in the environment at run time**, such as
  `GODEBUG=randautoseed=0` in a deployment file or a shell. It is not part
  of the program the static phase reads and may differ between
  environments, so the random-secret checks read only the settings the code
  and `go.mod` or `go.work` hold.
- **Authorization**, which turns on how an application routes every
  request rather than on one call, and is the subject of a module of its
  own.
