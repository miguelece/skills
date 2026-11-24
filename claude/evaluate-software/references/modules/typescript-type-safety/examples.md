# Examples: TypeScript type safety

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
nearest correct version, that does not trigger it. The code is invented for
the purpose and trimmed to the lines the check reads, with the declarations
it uses shown where the check reads them and the rest assumed imported. A
check read from configuration is shown as the `tsconfig.json` excerpt, with
no `extends`, so the excerpt is the whole resolved setting. Unless a section
says otherwise, the code compiles under TypeScript 6.0 with `strict` set
true and `noUncheckedIndexedAccess` unset.

## typescript-type-safety/strict-checks-disabled

**Bad.** The manifest pins a compiler older than 6.0, where an absent
`strict` defaults to false, and the configuration sets neither `strict` nor
`strictNullChecks` nor `noImplicitAny`:

```json
// package.json
{ "devDependencies": { "typescript": "5.9.3" } }

// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext"
  }
}
```

**Good.** `strict` is set true, which holds on every compiler version, and no
member of its family is turned back off:

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "strict": true
  }
}
```

## typescript-type-safety/unchecked-index-read

**Bad.** The configuration does not set `noUncheckedIndexedAccess`, which
TypeScript 4.1 added outside the `strict` family, so `limits[plan]` is typed
`number` and an unknown plan throws at `toFixed`:

```json
// tsconfig.json
{ "compilerOptions": { "strict": true } }
```

```typescript
const limits: Record<string, number> = { free: 10, pro: 100 };

function describeLimit(plan: string): string {
  return limits[plan].toFixed(0);
}
```

**Good.** The read is checked for presence before its value is used:

```typescript
function describeLimit(plan: string): string {
  const limit = limits[plan];
  if (limit === undefined) {
    throw new Error(`unknown plan: ${plan}`);
  }
  return limit.toFixed(0);
}
```

## typescript-type-safety/explicit-any

**Bad.** The parameter is `any[]`, with no comment saying why, so a caller
passing prices as strings, or items with no `price`, compiles cleanly:

```typescript
function orderTotal(items: any[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

**Good.** The parameter names the shape the function reads:

```typescript
interface LineItem {
  price: number;
}

function orderTotal(items: readonly LineItem[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

## typescript-type-safety/untrusted-data-typed-without-validation

**Bad.** The response body, typed `any` by `json()`, is asserted to `User`
and used with nothing checked between, so a body missing `email` fails
inside `toLowerCase`:

```typescript
interface User {
  id: string;
  email: string;
}

async function loadEmail(url: string): Promise<string> {
  const response = await fetch(url);
  const user = (await response.json()) as User;
  return user.email.toLowerCase();
}
```

**Good.** The body is held as `unknown` and passes a type guard that checks
every member `User` declares before it is used as one:

```typescript
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    typeof value.id === "string" &&
    "email" in value &&
    typeof value.email === "string"
  );
}

async function loadEmail(url: string): Promise<string> {
  const response = await fetch(url);
  const body: unknown = await response.json();
  if (!isUser(body)) {
    throw new Error("response is not a user");
  }
  return body.email.toLowerCase();
}
```

## typescript-type-safety/narrowing-assertion-without-check

**Bad.** `shape` is declared as the union, and the assertion narrows it to
`Circle` with no check and no comment, so a square yields `NaN`:

```typescript
interface Circle {
  kind: "circle";
  radius: number;
}

interface Square {
  kind: "square";
  side: number;
}

function area(shape: Circle | Square): number {
  const circle = shape as Circle;
  return Math.PI * circle.radius ** 2;
}
```

**Good.** The discriminant is checked, and the compiler narrows on the check
with no assertion:

```typescript
function area(shape: Circle | Square): number {
  if (shape.kind === "circle") {
    return Math.PI * shape.radius ** 2;
  }
  return shape.side ** 2;
}
```

## typescript-type-safety/double-assertion

**Bad.** The compiler refuses `order.id as number`, since `string` and
`number` are unrelated, and the chain through `unknown` goes around the
refusal with no comment, so a string reaches code typed for a number:

```typescript
interface Order {
  id: string;
}

function orderKey(order: Order): number {
  return order.id as unknown as number;
}
```

**Good.** The value is converted, not asserted, and a failed conversion is
an error at the point it happens:

```typescript
function orderKey(order: Order): number {
  const key = Number.parseInt(order.id, 10);
  if (Number.isNaN(key)) {
    throw new Error(`order id is not numeric: ${order.id}`);
  }
  return key;
}
```

## typescript-type-safety/object-literal-asserted-not-annotated

**Bad.** The literal is asserted to `RetryPolicy`, which declares a required
`backoffMs` the literal lacks, and the compiler accepts it:

```typescript
interface RetryPolicy {
  attempts: number;
  backoffMs: number;
}

const policy = { attempts: 3 } as RetryPolicy;
```

**Good.** The variable is annotated, so the literal is checked for missing
and excess properties, and it supplies both:

```typescript
const policy: RetryPolicy = { attempts: 3, backoffMs: 200 };
```

## typescript-type-safety/non-null-assertion-without-check

**Bad.** `find` returns `User | undefined`, and the `!` removes `undefined`
with no check and no comment, so an unknown id fails at `user.name`:

```typescript
interface User {
  id: string;
  name: string;
}

function userName(users: readonly User[], id: string): string {
  const user = users.find((candidate) => candidate.id === id)!;
  return user.name;
}
```

**Good.** The missing case is checked, and the compiler narrows on the check:

```typescript
function userName(users: readonly User[], id: string): string {
  const user = users.find((candidate) => candidate.id === id);
  if (user === undefined) {
    throw new Error(`no user with id ${id}`);
  }
  return user.name;
}
```

## typescript-type-safety/type-check-suppressed

**Bad.** `@ts-ignore` silences the error that a `string | undefined` is not
a `number`, and every later error on the line with it:

```typescript
function listenPort(env: Record<string, string | undefined>): number {
  // @ts-ignore
  const port: number = env.PORT;
  return port;
}
```

**Good.** The value is parsed into the type the code needs, and the
directive is gone:

```typescript
function listenPort(env: Record<string, string | undefined>): number {
  const port = Number.parseInt(env.PORT ?? "8080", 10);
  if (Number.isNaN(port)) {
    throw new Error(`PORT is not a number: ${env.PORT}`);
  }
  return port;
}
```

## typescript-type-safety/caught-value-used-as-typed

**Bad.** The rejection callback's parameter is left unannotated, so it is
typed `any` even under `strict`, whose `useUnknownInCatchVariables`, added in
TypeScript 4.4, covers only a `catch` clause; a rejection with a string
logs `undefined`:

```typescript
function save(record: Record<string, string>): Promise<void> {
  return store.put(record).catch((error) => {
    log.error(error.message);
  });
}
```

**Good.** The parameter is annotated `unknown` and narrowed before its
members are read:

```typescript
function save(record: Record<string, string>): Promise<void> {
  return store.put(record).catch((error: unknown) => {
    log.error(error instanceof Error ? error.message : String(error));
  });
}
```

## typescript-type-safety/type-guard-does-not-check

**Bad.** The predicate casts and checks only `name`, an optional member
that `Dog` carries too, so a named dog is narrowed to `Cat` and `meow`
throws:

```typescript
interface Cat {
  kind: "cat";
  name?: string;
  meow(): void;
}

interface Dog {
  kind: "dog";
  name?: string;
  bark(): void;
}

function isCat(pet: Cat | Dog): pet is Cat {
  return (pet as Cat).name !== undefined;
}
```

**Good.** The predicate tests `kind`, the member that distinguishes `Cat`
from the rest of the union:

```typescript
function isCat(pet: Cat | Dog): pet is Cat {
  return pet.kind === "cat";
}
```

## typescript-type-safety/switch-not-exhaustive

**Bad.** `Status` has three members, the `switch` handles two, there is no
`default`, and the function returns `void`, so a refunded order is silently
ignored:

```typescript
type Status = "pending" | "paid" | "refunded";

function notify(status: Status): void {
  switch (status) {
    case "pending":
      sendReminder();
      break;
    case "paid":
      sendReceipt();
      break;
  }
}
```

**Good.** Every member has a `case`, and a `default` assigning to `never`
makes a member added later a compile error here:

```typescript
function notify(status: Status): void {
  switch (status) {
    case "pending":
      sendReminder();
      break;
    case "paid":
      sendReceipt();
      break;
    case "refunded":
      sendRefundNotice();
      break;
    default: {
      const unhandled: never = status;
      throw new Error(`unhandled status: ${String(unhandled)}`);
    }
  }
}
```
