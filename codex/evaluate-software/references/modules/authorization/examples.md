# Examples: authorization

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
nearest correct version, that does not trigger it. The concept is
language-neutral, so the code examples are written in one invented
TypeScript service on an Express-style router, trimmed to the lines the check
reads; the design example quotes an invented design document.

## authorization/route-outside-shared-check

**Bad.** Every admin route is registered on a router that passes through
`requireRole("admin")`, and the delete route is registered on the
application directly, ahead of that router, with no check of its own and no
public marker, so a request to it is answered before the router is reached:

```typescript
// src/routes/admin.ts
app.delete("/admin/users/:id", async (req, res) => {
  await users.remove(req.params.id);
  res.sendStatus(204);
});

const admin = Router();
admin.use(requireRole("admin"));
admin.get("/admin/users", listUsers);
admin.patch("/admin/users/:id", updateUser);
app.use(admin);
```

**Good.** The delete route is registered on the same router, so it passes
through the same check:

```typescript
// src/routes/admin.ts
const admin = Router();
admin.use(requireRole("admin"));
admin.get("/admin/users", listUsers);
admin.patch("/admin/users/:id", updateUser);
admin.delete("/admin/users/:id", async (req, res) => {
  await users.remove(req.params.id);
  res.sendStatus(204);
});
app.use(admin);
```

## authorization/allow-when-no-rule-matches

**Bad.** The decision walks its rules and, when none matches the role and
the action, grants the request:

```typescript
// src/authz/policy.ts
const rules = [
  { role: "editor", action: "article:update", allow: true },
  { role: "viewer", action: "article:update", allow: false },
];

export function isAllowed(role: string, action: string): boolean {
  const rule = rules.find((r) => r.role === role && r.action === action);
  if (rule) return rule.allow;
  return true;
}
```

**Good.** The same rules, and the fall-through refuses, so an action or a
role no rule names is denied:

```typescript
// src/authz/policy.ts
const rules = [
  { role: "editor", action: "article:update", allow: true },
];

export function isAllowed(role: string, action: string): boolean {
  const rule = rules.find((r) => r.role === role && r.action === action);
  return rule?.allow ?? false;
}
```

## authorization/design-without-central-authorization-point

**Bad.** The design has callers with different access, and says only that
each service checks what it needs, naming no point where a request is
authorized:

```text
## API
Customers call the public REST API to place and track orders. Staff use
the same API, through the back-office app, to refund orders and edit
the catalogue.

## Components
The orders, catalogue and refunds services sit behind the load balancer.
Each service checks the caller's permissions as it needs to.
```

**Good.** The same API, and the design names the gateway at which every
request is authorized before it reaches a service. Naming the point is what
the check asks for; the gateway is one acceptable form, and a shared
library every service calls on each request would be another:

```text
## API
Customers call the public REST API to place and track orders. Staff use
the same API, through the back-office app, to refund orders and edit
the catalogue.

## Components
Every request passes through the API gateway, which authorizes it against
the access policy by the caller's role and the operation, and refuses any
operation the policy does not grant. The orders, catalogue and refunds
services sit behind it and accept requests only from it.
```
