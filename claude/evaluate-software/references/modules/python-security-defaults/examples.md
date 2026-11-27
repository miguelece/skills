# Examples: Python security defaults

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
nearest correct version, that does not trigger it. The code is invented for
the purpose and trimmed to the lines the check reads, with the declarations
it uses shown where the check reads them and the rest assumed imported.

## python-security-defaults/predictable-random-secret

**Bad.** The reset code comes from `random` and is stored and sent as the
credential that resets the password:

```python
import random
import string


def start_password_reset(email: str) -> None:
    code = "".join(random.choices(string.ascii_letters + string.digits, k=20))
    resets.insert(email=email, code=code, expires_at=now() + RESET_TTL)
    mailer.send(email, f"Your reset link: {BASE_URL}/reset?code={code}")
```

**Good.** The code comes from `secrets`:

```python
import secrets


def start_password_reset(email: str) -> None:
    code = secrets.token_urlsafe(32)
    resets.insert(email=email, code=code, expires_at=now() + RESET_TTL)
    mailer.send(email, f"Your reset link: {BASE_URL}/reset?code={code}")
```

## python-security-defaults/jwt-algorithm-not-pinned

**Bad.** The accepted algorithm is read from the token's own unverified
header, so a token whose header says `HS256` is checked with the public key
as an HMAC secret:

```python
import jwt


def read_session(token: str) -> dict:
    header = jwt.get_unverified_header(token)
    return jwt.decode(token, PUBLIC_KEY_PEM, algorithms=[header["alg"]])
```

**Good.** The verifier pins the one algorithm the issuer signs with:

```python
import jwt


def read_session(token: str) -> dict:
    return jwt.decode(token, PUBLIC_KEY_PEM, algorithms=["RS256"])
```

**Bad, Authlib.** The default `jwt` instance accepts every algorithm it
supports and takes the header's `alg`, with one static public key, while the
lockfile resolves `authlib==1.2.1`, below the 1.3.1 fix:

```python
from authlib.jose import jwt


def read_session(token: str) -> dict:
    claims = jwt.decode(token, PUBLIC_KEY_PEM)
    claims.validate()
    return claims
```

**Good, Authlib.** An instance built with the one algorithm the issuer
signs with:

```python
from authlib.jose import JsonWebToken

rs256_jwt = JsonWebToken(["RS256"])


def read_session(token: str) -> dict:
    claims = rs256_jwt.decode(token, PUBLIC_KEY_PEM)
    claims.validate()
    return claims
```

## python-security-defaults/jwt-signature-not-verified

**Bad.** The claims come from a decode that checks no signature, and the
`sub` they carry picks the user the request acts as:

```python
import jwt


def current_user(request: Request) -> User:
    token = request.headers["Authorization"].removeprefix("Bearer ")
    claims = jwt.decode(token, options={"verify_signature": False})
    return users.get(claims["sub"])
```

**Good.** The signature is verified, with the issuer's key and its one
algorithm, before `sub` is trusted:

```python
import jwt


def current_user(request: Request) -> User:
    token = request.headers["Authorization"].removeprefix("Bearer ")
    claims = jwt.decode(
        token, PUBLIC_KEY_PEM, algorithms=["RS256"], audience="orders-api"
    )
    return users.get(claims["sub"])
```

## python-security-defaults/jwt-claims-not-validated

**Bad.** Authlib verifies the signature, but the claims are used without
`validate()`, so an expired token still names its user:

```python
from authlib.jose import JsonWebToken

rs256_jwt = JsonWebToken(["RS256"])


def current_user(token: str) -> User:
    claims = rs256_jwt.decode(token, PUBLIC_KEY_PEM)
    return users.get(claims["sub"])
```

**Good.** The claims are validated, expiry included, before `sub` is used,
with the audience this service accepts required:

```python
from authlib.jose import JsonWebToken

rs256_jwt = JsonWebToken(["RS256"])


def current_user(token: str) -> User:
    claims = rs256_jwt.decode(
        token,
        PUBLIC_KEY_PEM,
        claims_options={"aud": {"essential": True, "value": "orders-api"}},
    )
    claims.validate()
    return users.get(claims["sub"])
```

## python-security-defaults/secret-compared-by-plain-equality

**Bad.** The webhook's signature header is compared with the MAC the server
computes over the body by `!=`, so the comparison stops at the first wrong
character:

```python
import hashlib
import hmac


def webhook_is_authentic(request: Request) -> bool:
    expected = hmac.new(WEBHOOK_SECRET, request.body, hashlib.sha256).hexdigest()
    if request.headers["X-Signature"] != expected:
        return False
    return True
```

**Good.** The same two values go through `hmac.compare_digest`:

```python
import hashlib
import hmac


def webhook_is_authentic(request: Request) -> bool:
    expected = hmac.new(WEBHOOK_SECRET, request.body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(request.headers["X-Signature"], expected)
```

## python-security-defaults/timing-safe-compare-undone

**Bad.** The prefix test returns before the constant-time call, on the
secret's own content, so the response time shows whether the guess starts
right:

```python
import hmac


def api_key_is_valid(presented: str) -> bool:
    if not presented.startswith(EXPECTED_KEY[:8]):
        return False
    return hmac.compare_digest(presented, EXPECTED_KEY)
```

**Good.** The constant-time call is the only comparison:

```python
import hmac


def api_key_is_valid(presented: str) -> bool:
    return hmac.compare_digest(presented.encode(), EXPECTED_KEY.encode())
```

## python-security-defaults/one-time-code-accepted-twice

**Bad.** The code is checked and accepted, and nothing records that it has
been used, so the same code logs in again while its window lasts:

```python
import pyotp


def verify_second_factor(user: User, code: str) -> bool:
    totp = pyotp.TOTP(user.otp_secret)
    return totp.verify(code)
```

**Good.** The accepted time code is stored, and one not later than the last
accepted is refused, in one conditional update so two concurrent requests
cannot both succeed. That update is one acceptable form; a row lock is
another:

```python
import pyotp
from pyotp.exceptions import OTPVerificationError


def verify_second_factor(user: User, code: str) -> bool:
    totp = pyotp.TOTP(user.otp_secret)
    try:
        timecode = totp.verify_and_get_timecode(code)
    except OTPVerificationError:
        return False
    advanced = db.execute(
        "UPDATE otp_state SET last_timecode = ?"
        " WHERE user_id = ? AND last_timecode < ?",
        (timecode, user.id, timecode),
    ).rowcount
    return advanced == 1
```

## python-security-defaults/xml-external-entities-enabled

**Bad.** An uploaded document is parsed with external entities resolved, so
an entity naming a local file is read into the result:

```python
from lxml import etree


def import_catalogue(upload: bytes) -> etree._Element:
    parser = etree.XMLParser(resolve_entities=True)
    return etree.fromstring(upload, parser=parser)
```

**Good.** The parser keeps entity references unresolved, so the document
cannot load anything:

```python
from lxml import etree


def import_catalogue(upload: bytes) -> etree._Element:
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    return etree.fromstring(upload, parser=parser)
```

## python-security-defaults/xml-size-limits-disabled

**Bad.** An uploaded document is parsed with `huge_tree=True`, so libxml2's
limits against forged input are off for a document anyone can send:

```python
from lxml import etree


def import_catalogue(upload: bytes) -> etree._Element:
    parser = etree.XMLParser(resolve_entities=False, huge_tree=True)
    return etree.fromstring(upload, parser=parser)
```

**Good.** The parser keeps the default limits, and an oversized upload
fails to parse instead of exhausting the worker:

```python
from lxml import etree


def import_catalogue(upload: bytes) -> etree._Element:
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    return etree.fromstring(upload, parser=parser)
```
