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
