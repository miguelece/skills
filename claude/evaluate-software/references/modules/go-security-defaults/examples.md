# Examples: Go security defaults

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
nearest correct version, that does not trigger it. The code is invented for
the purpose and trimmed to the lines the check reads, with the declarations
it uses shown where the check reads them and the rest assumed declared
elsewhere in the package.

## go-security-defaults/predictable-random-secret

**Bad.** The reset code comes from a `math/rand` generator seeded with the
clock, and is stored and sent as the credential that resets the password:

```go
import (
    "math/rand"
    "time"
)

const alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

var gen = rand.New(rand.NewSource(time.Now().UnixNano()))

func startPasswordReset(email string) error {
    b := make([]byte, 20)
    for i := range b {
        b[i] = alphabet[gen.Intn(len(alphabet))]
    }
    code := string(b)
    if err := resets.Insert(email, code, time.Now().Add(resetTTL)); err != nil {
        return err
    }
    return mailer.Send(email, baseURL+"/reset?code="+code)
}
```

**Good.** The code comes from `crypto/rand`:

```go
import (
    "crypto/rand"
    "time"
)

func startPasswordReset(email string) error {
    code := rand.Text()
    if err := resets.Insert(email, code, time.Now().Add(resetTTL)); err != nil {
        return err
    }
    return mailer.Send(email, baseURL+"/reset?code="+code)
}
```

## go-security-defaults/bcrypt-input-past-72-bytes

**Bad.** The email is joined before the password, and `go.mod` requires a
version of `x/crypto` that truncates silently, so a long enough email leaves
little or none of the password inside the 72 bytes bcrypt reads:

```text
// go.mod
require golang.org/x/crypto v0.4.0
```

```go
import "golang.org/x/crypto/bcrypt"

func hashCredential(email, password string) ([]byte, error) {
    return bcrypt.GenerateFromPassword([]byte(email+":"+password), bcrypt.DefaultCost)
}
```

**Good.** The password is hashed alone, on a version that refuses input past
72 bytes, and the account is found by its email:

```text
// go.mod
require golang.org/x/crypto v0.59.0
```

```go
import "golang.org/x/crypto/bcrypt"

func hashCredential(password string) ([]byte, error) {
    return bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
}
```

## go-security-defaults/timing-safe-compare-undone

**Bad.** A byte-wise loop returns at the first mismatch before the
constant-time call, so the time taken still tracks the guess:

```go
import (
    "crypto/hmac"
    "crypto/sha256"
)

func validSignature(body, got, key []byte) bool {
    mac := hmac.New(sha256.New, key)
    mac.Write(body)
    want := mac.Sum(nil)
    for i := range got {
        if i >= len(want) || got[i] != want[i] {
            return false
        }
    }
    return hmac.Equal(got, want)
}
```

**Good.** The constant-time call alone decides it:

```go
import (
    "crypto/hmac"
    "crypto/sha256"
)

func validSignature(body, got, key []byte) bool {
    mac := hmac.New(sha256.New, key)
    mac.Write(body)
    return hmac.Equal(got, mac.Sum(nil))
}
```

## go-security-defaults/one-time-code-accepted-twice

**Bad.** The TOTP code is checked and the login succeeds, but nothing records
that the code was used, so it works again until its window closes:

```go
import "github.com/pquerna/otp/totp"

func verifySecondFactor(user *User, code string) bool {
    if !totp.Validate(code, user.TOTPSecret) {
        return false
    }
    return true
}
```

**Good.** The time step the code matched is found and stored, and a code
from that step or an earlier one is refused. Storing the step is one
acceptable form; deleting an emailed code on use is another:

```go
import (
    "time"

    "github.com/pquerna/otp"
    "github.com/pquerna/otp/totp"
)

var exact = totp.ValidateOpts{
    Period: 30, Skew: 0, Digits: otp.DigitsSix, Algorithm: otp.AlgorithmSHA1,
}

func verifySecondFactor(user *User, code string) (bool, error) {
    now := time.Now()
    for _, offset := range []int64{-1, 0, 1} {
        at := now.Add(time.Duration(offset) * 30 * time.Second)
        ok, err := totp.ValidateCustom(code, user.TOTPSecret, at, exact)
        if err != nil || !ok {
            continue
        }
        // Atomic: succeeds only when the stored step is earlier than this one.
        return users.AdvanceLastTOTPStep(user.ID, at.Unix()/30)
    }
    return false, nil
}
```
