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
documentation at go1.27.4 and the Go project's own documentation first, then
`golang.org/x/crypto`'s documentation and history and `pquerna/otp`'s
documentation and source, with OWASP's cheat sheets as the independent
published guidance. Each `date` is the reading date, except for the Go blog
post, dated as published, the `x/crypto` commit, dated as committed, the
v0.5.0 tag, dated as tagged, and the `pquerna/otp` documentation, dated as
its v1.5.0 release, the version the page shows. The RFC carries only a month,
given in its title, so it is dated as read. The one dated post is the Go
project's own blog, cited for what the package pages do not say: since when
the top-level generator is ChaCha8.

The subject is a defect class that passes every functional test: each
mistake behaves like the secure version until someone attacks it. Of the
five candidates the module was scoped with, four were kept, because each has
a quotable call and a reading rule that decides it, and the fifth was
dropped, because the Go standard library cannot show the defect.

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
  one that `rand.Seed` returns to the Go 1 generator. The `go` line is the
  minimum toolchain, not the one that builds, so a line below 1.22 is
  reported because the module accepts the predictable generator, not because
  it certainly gets it. A top-level call on a newer line is left out; it
  still goes against the documentation, which an owner may judge worth a
  check of lower severity of its own.
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

- **A top-level `math/rand` or `math/rand/v2` call on a `go` line of 1.22
  or later with no `rand.Seed`**, for the reason above.
- **A secret compared with `==` or `bytes.Equal` and no constant-time call
  at all.** It is the commoner timing defect, but this module was scoped to
  the comparison undone by the code around it.
- **XML parsed through a cgo binding to libxml2** or another third-party
  parser, whose entity handling no source read states.
- **A `GenerateFromPassword` error that is discarded**, which the Go error
  handling module reads, and **pre-hashing before bcrypt**, for the reason
  above.
- **JWT verification**, which the sibling modules check for their
  languages; it was not among the candidates this module was scoped with.
- **Authorization**, which turns on how an application routes every
  request rather than on one call, and is the subject of a module of its
  own.
