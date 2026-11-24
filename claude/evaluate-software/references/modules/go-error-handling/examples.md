# Examples: Go error handling

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
nearest correct version, that does not trigger it. The code is invented for
the purpose and trimmed to the lines the check reads; every file shown is
production code, not a `_test.go` file. Where a check turns on the `go` line
of `go.mod`, the example names the version it assumes.

## go-error-handling/error-discarded

**Bad.** `Close` on a file being written reports a failed flush, and the call
discards it. The signature read is `func (f *os.File) Close() error`:

```go
func writeReport(path string, data []byte) error {
    f, err := os.Create(path)
    if err != nil {
        return err
    }
    if _, err := f.Write(data); err != nil {
        f.Close()
        return err
    }
    f.Close() // error result discarded: a failed flush is lost
    return nil
}
```

**Good.** The success path returns `Close`'s error; the discard on the
failure path carries a comment saying why it cannot matter:

```go
func writeReport(path string, data []byte) error {
    f, err := os.Create(path)
    if err != nil {
        return err
    }
    if _, err := f.Write(data); err != nil {
        _ = f.Close() // the write error is the one reported
        return err
    }
    return f.Close()
}
```

## go-error-handling/constructed-error-dropped

**Bad.** The error is built as an expression statement, and the function
goes on to withdraw a non-positive amount:

```go
func (a *Account) Withdraw(amount int) error {
    if amount <= 0 {
        fmt.Errorf("withdraw: amount %d must be positive", amount)
    }
    a.balance -= amount
    return nil
}
```

**Good.** The error is returned:

```go
func (a *Account) Withdraw(amount int) error {
    if amount <= 0 {
        return fmt.Errorf("withdraw: amount %d must be positive", amount)
    }
    a.balance -= amount
    return nil
}
```

## go-error-handling/sentinel-compared-with-equality

**Bad.** The module's `go.mod` reads `go 1.21`. The store wraps its sentinel
with `%w`, so the caller's `==` never matches:

```go
// go.mod: go 1.21
var ErrNotFound = errors.New("not found")

func (s *Store) User(id string) (User, error) {
    u, ok := s.users[id]
    if !ok {
        return User{}, fmt.Errorf("user %s: %w", id, ErrNotFound)
    }
    return u, nil
}

func handleGet(s *Store, id string) int {
    _, err := s.User(id)
    if err == ErrNotFound { // false for the wrapped error
        return http.StatusNotFound
    }
    ...
}
```

**Good.** Under the same `go 1.21`, `errors.Is` walks the chain:

```go
// go.mod: go 1.21
func handleGet(s *Store, id string) int {
    _, err := s.User(id)
    if errors.Is(err, ErrNotFound) {
        return http.StatusNotFound
    }
    ...
}
```

## go-error-handling/error-type-asserted

**Bad.** The module's `go.mod` reads `go 1.21`. `loadTemplate` wraps the
`*fs.PathError` that `os.ReadFile` returns, so the assertion fails:

```go
// go.mod: go 1.21
func loadTemplate(name string) ([]byte, error) {
    b, err := os.ReadFile(name)
    if err != nil {
        return nil, fmt.Errorf("template %s: %w", name, err)
    }
    return b, nil
}

func render(name string) error {
    _, err := loadTemplate(name)
    if pe, ok := err.(*fs.PathError); ok { // sees only the outer wrap
        log.Printf("missing template file %s", pe.Path)
        return nil
    }
    return err
}
```

**Good.** Under the same `go 1.21`, `errors.As` walks the chain:

```go
// go.mod: go 1.21
func render(name string) error {
    _, err := loadTemplate(name)
    var pe *fs.PathError
    if errors.As(err, &pe) {
        log.Printf("missing template file %s", pe.Path)
        return nil
    }
    return err
}
```

## go-error-handling/errors-as-invalid-target

**Bad.** The target is `pe`, of type `*fs.PathError`: a pointer to
`fs.PathError`, which does not implement `error` (its `Error` method has a
pointer receiver) and is not an interface, so the call panics:

```go
func isPathError(err error) bool {
    var pe *fs.PathError
    return errors.As(err, pe) // panics: target must point to an error type
}
```

**Good.** The target is a pointer to the `*fs.PathError` variable:

```go
func isPathError(err error) bool {
    var pe *fs.PathError
    return errors.As(err, &pe)
}
```

## go-error-handling/inspected-cause-not-wrapped

**Bad.** `readConfig` wraps with `%v`, and its caller `loadOrDefault` tests
the result for `fs.ErrNotExist`, which can never match:

```go
func readConfig(path string) ([]byte, error) {
    b, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("read config %s: %v", path, err)
    }
    return b, nil
}

func loadOrDefault(path string) ([]byte, error) {
    b, err := readConfig(path)
    if errors.Is(err, fs.ErrNotExist) { // always false
        return defaultConfig, nil
    }
    return b, err
}
```

**Good.** `readConfig` wraps with `%w`, so the cause stays in the chain:

```go
func readConfig(path string) ([]byte, error) {
    b, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("read config %s: %w", path, err)
    }
    return b, nil
}
```

## go-error-handling/wrap-verb-misused

**Bad.** `%w` in `log.Printf`, which does not forward to `fmt.Errorf`, prints
`%!w(...)` and wraps nothing:

```go
func (q *Queue) ack(id string) {
    if err := q.client.Ack(id); err != nil {
        log.Printf("ack %s: %w", id, err)
    }
}
```

**Good.** The log call formats the error with `%v`; `%w` belongs only in
`fmt.Errorf`:

```go
func (q *Queue) ack(id string) {
    if err := q.client.Ack(id); err != nil {
        log.Printf("ack %s: %v", id, err)
    }
}
```

## go-error-handling/error-matched-by-text

**Bad.** A production branch is decided on the error's message, which a
reworded or wrapped error changes:

```go
func handleGet(s *Store, id string) int {
    _, err := s.User(id)
    if err != nil && strings.Contains(err.Error(), "not found") {
        return http.StatusNotFound
    }
    ...
}
```

**Good.** The store exports a sentinel and the caller tests for it:

```go
var ErrNotFound = errors.New("not found")

func handleGet(s *Store, id string) int {
    _, err := s.User(id)
    if errors.Is(err, ErrNotFound) {
        return http.StatusNotFound
    }
    ...
}
```

## go-error-handling/typed-nil-error-returned

**Bad.** `Validate` declares an `error` result and returns `verr`, a
`*ValidationError` that is nil on success, so callers see a non-nil error:

```go
type ValidationError struct{ Field string }

func (e *ValidationError) Error() string { return "invalid " + e.Field }

func Validate(u User) error {
    var verr *ValidationError
    if u.Name == "" {
        verr = &ValidationError{Field: "name"}
    }
    return verr // a nil *ValidationError is a non-nil error
}
```

**Good.** The success path returns a literal `nil`:

```go
func Validate(u User) error {
    if u.Name == "" {
        return &ValidationError{Field: "name"}
    }
    return nil
}
```

## go-error-handling/result-used-before-error-check

**Bad.** The `Close` is deferred before the error is checked, so on failure
it dereferences a nil `resp` and panics:

```go
func fetch(url string) ([]byte, error) {
    resp, err := http.Get(url)
    defer resp.Body.Close()
    if err != nil {
        return nil, err
    }
    return io.ReadAll(resp.Body)
}
```

**Good.** The `Close` is deferred after the check:

```go
func fetch(url string) ([]byte, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    return io.ReadAll(resp.Body)
}
```

## go-error-handling/panic-for-expected-failure

**Bad.** An exported loader, neither `init` nor a `Must` function, panics on
a missing or malformed file, a runtime failure its caller should handle:

```go
func LoadConfig(path string) Config {
    data, err := os.ReadFile(path)
    if err != nil {
        panic(err)
    }
    var c Config
    if err := json.Unmarshal(data, &c); err != nil {
        panic(err)
    }
    return c
}
```

**Good.** The loader returns the failure as an error:

```go
func LoadConfig(path string) (Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return Config{}, fmt.Errorf("load config: %w", err)
    }
    var c Config
    if err := json.Unmarshal(data, &c); err != nil {
        return Config{}, fmt.Errorf("load config %s: %w", path, err)
    }
    return c, nil
}
```

## go-error-handling/recover-swallows-every-panic

**Bad.** The parser panics internally to unwind on a syntax error, and its
deferred `recover` converts every panic into an error, a nil dereference in
`parseExpr` included:

```go
func (p *Parser) Parse(src string) (n Node, err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("parse: %v", r)
        }
    }()
    return p.parseExpr(src), nil
}
```

**Good.** The parser panics with its own type, and the `recover` converts
only that type and re-panics the rest:

```go
type syntaxError struct{ err error }

func (p *Parser) fail(format string, args ...any) {
    panic(syntaxError{fmt.Errorf(format, args...)})
}

func (p *Parser) Parse(src string) (n Node, err error) {
    defer func() {
        if r := recover(); r != nil {
            se, ok := r.(syntaxError)
            if !ok {
                panic(r)
            }
            err = se.err
        }
    }()
    return p.parseExpr(src), nil
}
```

## go-error-handling/recover-not-called-directly

**Bad.** `crashWithStack` calls `recover`, but the deferred call is the
function literal, not `crashWithStack`, so `recover` returns nil and the
panic propagates without its stack being logged:

```go
func crashWithStack() {
    if r := recover(); r != nil {
        log.Printf("panic: %v\n%s", r, debug.Stack())
        os.Exit(2)
    }
}

func main() {
    defer func() { crashWithStack() }()
    run()
}
```

**Good.** `crashWithStack` is itself the deferred call. It logs the value
with its stack and ends the process, the form the check for a recover that
swallows every panic also allows:

```go
func main() {
    defer crashWithStack()
    run()
}
```

## go-error-handling/error-logged-and-returned

**Bad.** The same branch logs the error and returns a wrap of it, so each
caller that handles it logs it again:

```go
func (s *Service) Charge(orderID string) error {
    if err := s.gateway.Charge(orderID); err != nil {
        log.Printf("charge order %s: %v", orderID, err)
        return fmt.Errorf("charge order %s: %w", orderID, err)
    }
    return nil
}
```

**Good.** The function returns the wrapped error and leaves the logging to
the caller that handles it:

```go
func (s *Service) Charge(orderID string) error {
    if err := s.gateway.Charge(orderID); err != nil {
        return fmt.Errorf("charge order %s: %w", orderID, err)
    }
    return nil
}
```

## go-error-handling/in-band-error-value

**Bad.** `-1` means an unknown SKU, as the doc comment says, and nothing
makes a caller check for it:

```go
// Price returns the price of sku in cents, or -1 if sku is unknown.
func (c *Catalog) Price(sku string) int {
    p, ok := c.prices[sku]
    if !ok {
        return -1
    }
    return p
}
```

**Good.** A second `ok` result reports whether the SKU was found:

```go
// Price returns the price of sku in cents, and whether sku is known.
func (c *Catalog) Price(sku string) (int, bool) {
    p, ok := c.prices[sku]
    return p, ok
}
```

## go-error-handling/error-type-hides-cause

**Bad.** `QueryError` holds the driver's error with no `Unwrap` method, and
the caller `findUser` tests the result for `sql.ErrNoRows`, which can never
match:

```go
type QueryError struct {
    Query string
    Err   error
}

func (e *QueryError) Error() string { return e.Query + ": " + e.Err.Error() }

func (r *Repo) queryRow(q string, args ...any) (User, error) {
    var u User
    if err := r.db.QueryRow(q, args...).Scan(&u.ID, &u.Name); err != nil {
        return User{}, &QueryError{Query: q, Err: err}
    }
    return u, nil
}

func (r *Repo) findUser(id int) (User, bool, error) {
    u, err := r.queryRow("SELECT id, name FROM users WHERE id = $1", id)
    if errors.Is(err, sql.ErrNoRows) { // stops at QueryError
        return User{}, false, nil
    }
    return u, err == nil, err
}
```

**Good.** `QueryError` exposes its cause through `Unwrap`:

```go
func (e *QueryError) Unwrap() error { return e.Err }
```
