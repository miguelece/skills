# Examples: TypeScript security defaults

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
nearest correct version, that does not trigger it. The code is invented for
the purpose and trimmed to the lines the check reads, with the declarations
it uses shown where the check reads them and the rest assumed imported.

## typescript-security-defaults/predictable-random-secret

**Bad.** The reset code comes from `Math.random()` and is stored and sent as
the credential that resets the password:

```typescript
async function startPasswordReset(email: string): Promise<void> {
  const code = Math.random().toString(36).slice(2, 10);
  await resets.insert({ email, code, expiresAt: Date.now() + 15 * 60_000 });
  await mailer.send(email, `Your reset link: ${baseUrl}/reset?code=${code}`);
}
```

**Good.** The code comes from Node's cryptographic generator:

```typescript
import { randomBytes } from "node:crypto";

async function startPasswordReset(email: string): Promise<void> {
  const code = randomBytes(32).toString("base64url");
  await resets.insert({ email, code, expiresAt: Date.now() + 15 * 60_000 });
  await mailer.send(email, `Your reset link: ${baseUrl}/reset?code=${code}`);
}
```

## typescript-security-defaults/jwt-algorithm-not-pinned

**Bad.** The accepted algorithm is read from the token's own unverified
header, so a token whose header says `HS256` is checked with the public key
as an HMAC secret:

```typescript
import jwt from "jsonwebtoken";

function readSession(token: string): jwt.JwtPayload {
  const decoded = jwt.decode(token, { complete: true });
  if (decoded === null) {
    throw new Error("malformed token");
  }
  const claims = jwt.verify(token, publicKeyPem, {
    algorithms: [decoded.header.alg as jwt.Algorithm],
  });
  if (typeof claims === "string") {
    throw new Error("unexpected payload");
  }
  return claims;
}
```

**Good.** The verifier pins the one algorithm the issuer signs with:

```typescript
function readSession(token: string): jwt.JwtPayload {
  const claims = jwt.verify(token, publicKeyPem, { algorithms: ["RS256"] });
  if (typeof claims === "string") {
    throw new Error("unexpected payload");
  }
  return claims;
}
```

## typescript-security-defaults/timing-safe-compare-undone

**Bad.** The raw API key is compared in constant time, but the length check
before the call returns early on the secret's length, and the prefix check
returns early on its content:

```typescript
import { timingSafeEqual } from "node:crypto";

function apiKeyMatches(presented: string, stored: string): boolean {
  const a = Buffer.from(presented);
  const b = Buffer.from(stored);
  if (a.length !== b.length) return false;
  if (!presented.startsWith(stored.slice(0, 4))) return false;
  return timingSafeEqual(a, b);
}
```

**Good.** Both sides are reduced to digests of the same fixed size, so the
call needs no check before it and nothing returns early:

```typescript
import { createHash, timingSafeEqual } from "node:crypto";

function apiKeyMatches(presented: string, stored: string): boolean {
  const a = createHash("sha256").update(presented).digest();
  const b = createHash("sha256").update(stored).digest();
  return timingSafeEqual(a, b);
}
```

## typescript-security-defaults/one-time-code-accepted-twice

**Bad.** The TOTP code is verified, and the success path returns without
recording the time step it matched, so the same code logs in again until it
expires:

```typescript
import { verify } from "otplib";

async function checkSecondFactor(user: User, token: string): Promise<boolean> {
  const result = await verify({ secret: user.totpSecret, token });
  return result.valid;
}
```

**Good.** The last accepted time step is passed back as `afterTimeStep`, and
the new one is stored on success. This is one acceptable form; a store of
used codes serves as well:

```typescript
async function checkSecondFactor(user: User, token: string): Promise<boolean> {
  const result = await verify({
    secret: user.totpSecret,
    token,
    afterTimeStep: user.lastTotpTimeStep,
  });
  if (!result.valid) return false;
  await users.update(user.id, { lastTotpTimeStep: result.timeStep });
  return true;
}
```

## typescript-security-defaults/xml-external-entities-enabled

**Bad.** The request body is parsed with entity substitution on, so a
document declaring an entity that names a local file has it read into the
result:

```typescript
import { parseXml } from "libxmljs";

app.post("/import", (req, res) => {
  const doc = parseXml(req.body, { replaceEntities: true });
  res.json({ items: doc.find("//item").length });
});
```

**Good.** The parser keeps its default, with no entity substitution and no
DTD loading:

```typescript
app.post("/import", (req, res) => {
  const doc = parseXml(req.body);
  res.json({ items: doc.find("//item").length });
});
```
