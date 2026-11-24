# Examples: Go concurrency

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
nearest correct version, that does not trigger it. The code is invented for
the purpose and trimmed to the lines the check reads; every file shown is
production code, not a `_test.go` file. Where a check turns on the `go` line
of `go.mod`, the example names the version it assumes.

## go-concurrency/shared-variable-unsynchronized

**Bad.** The refresh goroutine writes the map while any caller can read it,
and nothing orders the two:

```go
type Cache struct {
    entries map[string]string
}

func (c *Cache) Refresh(load func() map[string]string) {
    go func() {
        for k, v := range load() {
            c.entries[k] = v // write, in the refresh goroutine
        }
    }()
}

func (c *Cache) Get(k string) string {
    return c.entries[k] // read, in the caller's goroutine
}
```

**Good.** A mutex is held at both accesses:

```go
type Cache struct {
    mu      sync.RWMutex
    entries map[string]string
}

func (c *Cache) Refresh(load func() map[string]string) {
    go func() {
        fresh := load()
        c.mu.Lock()
        defer c.mu.Unlock()
        for k, v := range fresh {
            c.entries[k] = v
        }
    }()
}

func (c *Cache) Get(k string) string {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.entries[k]
}
```

## go-concurrency/goroutine-captures-loop-variable

**Bad.** The module's `go.mod` reads `go 1.21`, so every iteration shares one
`u`, and the goroutine reads it while the loop moves on:

```go
// go.mod: go 1.21
func notifyAll(users []User) {
    for _, u := range users {
        go func() {
            send(u.Email) // the loop's own u, shared by every iteration
        }()
    }
}
```

**Good.** Under the same `go 1.21`, the value is passed as a parameter, so
each goroutine has its own copy:

```go
// go.mod: go 1.21
func notifyAll(users []User) {
    for _, u := range users {
        go func(u User) {
            send(u.Email)
        }(u)
    }
}
```

At `go 1.22` or later the bad form is not reported either: each iteration
declares its own `u`.

## go-concurrency/busy-wait-on-plain-variable

**Bad.** The loop polls a plain flag the worker goroutine sets, so it may
never see the write, or see it before the work's own writes:

```go
var done bool

func run() {
    go func() {
        work()
        done = true
    }()
    for !done {
    }
    report()
}
```

**Good.** The worker closes a channel and the caller blocks on it; an
`atomic.Bool` would also synchronize, but would still spin:

```go
func run() {
    done := make(chan struct{})
    go func() {
        work()
        close(done)
    }()
    <-done
    report()
}
```

## go-concurrency/unsynchronized-fast-path

**Bad.** The flag is read outside the `Once`, so a caller that sees it set
can still read `config` before `load`'s writes reach it:

```go
var (
    config      *Config
    initialized bool
    once        sync.Once
)

func Get() *Config {
    if !initialized { // plain read, outside the Once
        once.Do(func() {
            config = load()
            initialized = true
        })
    }
    return config
}
```

**Good.** Every caller goes through `once.Do`, which is cheap once done, and
the flag is gone:

```go
var (
    config *Config
    once   sync.Once
)

func Get() *Config {
    once.Do(func() { config = load() })
    return config
}
```

## go-concurrency/atomic-access-mixed

**Bad.** `Hit` updates the counter atomically, but `Requests` reads it
plainly while `Hit` can run:

```go
type Stats struct{ requests int64 }

func (s *Stats) Hit() { atomic.AddInt64(&s.requests, 1) }

func (s *Stats) Requests() int64 {
    return s.requests // plain read of an atomically updated field
}
```

**Good.** Every access goes through `sync/atomic`:

```go
type Stats struct{ requests int64 }

func (s *Stats) Hit() { atomic.AddInt64(&s.requests, 1) }

func (s *Stats) Requests() int64 {
    return atomic.LoadInt64(&s.requests)
}
```

## go-concurrency/lock-copied

**Bad.** `Value` has a value receiver, so each call copies the mutex, and its
lock does not exclude `Inc`'s:

```go
type Counter struct {
    mu sync.Mutex
    n  int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.n++
}

func (c Counter) Value() int { // copies c.mu on every call
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.n
}
```

**Good.** Both methods take a pointer receiver, so they lock the one mutex:

```go
func (c *Counter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.n
}
```

## go-concurrency/waitgroup-add-inside-goroutine

**Bad.** `Add` runs inside the goroutine, so `Wait` can return before any
goroutine has counted itself:

```go
func processAll(items []Item) {
    var wg sync.WaitGroup
    for _, it := range items {
        go func(it Item) {
            wg.Add(1)
            defer wg.Done()
            process(it)
        }(it)
    }
    wg.Wait()
}
```

**Good.** `Add` runs before the `go` statement:

```go
func processAll(items []Item) {
    var wg sync.WaitGroup
    for _, it := range items {
        wg.Add(1)
        go func(it Item) {
            defer wg.Done()
            process(it)
        }(it)
    }
    wg.Wait()
}
```

## go-concurrency/cancel-func-not-called

**Bad.** The early return leaves before `cancel` is deferred:

```go
func lookup(parent context.Context, name string) (string, error) {
    ctx, cancel := context.WithTimeout(parent, 5*time.Second)
    req, err := newRequest(ctx, name)
    if err != nil {
        return "", err // cancel is never called on this path
    }
    defer cancel()
    return query(req)
}
```

**Good.** `cancel` is deferred straight after the call, so every path
releases the context:

```go
func lookup(parent context.Context, name string) (string, error) {
    ctx, cancel := context.WithTimeout(parent, 5*time.Second)
    defer cancel()
    req, err := newRequest(ctx, name)
    if err != nil {
        return "", err
    }
    return query(req)
}
```

## go-concurrency/context-key-of-builtin-type

**Bad.** The key is a `string`, which any other package can repeat:

```go
func WithUser(ctx context.Context, u *User) context.Context {
    return context.WithValue(ctx, "user", u)
}
```

**Good.** The key is of a type the package defines and does not export:

```go
type userKey struct{}

func WithUser(ctx context.Context, u *User) context.Context {
    return context.WithValue(ctx, userKey{}, u)
}
```

## go-concurrency/goroutine-has-no-exit

**Bad.** The loop never ends, and the caller has nothing to stop it with or
wait on:

```go
func StartRefresher(c *Cache) {
    go func() {
        for {
            c.Refresh()
            time.Sleep(time.Minute)
        }
    }()
}
```

**Good.** The goroutine ends when the context is canceled, and closes a
channel the caller can wait on:

```go
func StartRefresher(ctx context.Context, c *Cache) <-chan struct{} {
    done := make(chan struct{})
    go func() {
        defer close(done)
        for {
            c.Refresh()
            select {
            case <-ctx.Done():
                return
            case <-time.After(time.Minute):
            }
        }
    }()
    return done
}
```

## go-concurrency/ticker-never-stopped

**Bad.** The module's `go.mod` reads `go 1.22`, so the ticker each call
creates is never recovered once the function returns:

```go
// go.mod: go 1.22
func waitReady(s *Server) {
    t := time.NewTicker(100 * time.Millisecond)
    for range t.C {
        if s.Ready() {
            return // the ticker is never stopped
        }
    }
}
```

**Good.** Under the same `go 1.22`, the ticker is stopped on every path out:

```go
// go.mod: go 1.22
func waitReady(s *Server) {
    t := time.NewTicker(100 * time.Millisecond)
    defer t.Stop()
    for range t.C {
        if s.Ready() {
            return
        }
    }
}
```

At `go 1.23` or later the bad form is not reported, unless a `godebug`
setting restores `asynctimerchan=1`.

## go-concurrency/send-blocks-after-receiver-returns

**Bad.** When the context ends first, nothing receives from the unbuffered
channel, and the sender blocks for good:

```go
func run(ctx context.Context, q Query) (Result, error) {
    ch := make(chan Result)
    go func() { ch <- q.Exec() }()
    select {
    case r := <-ch:
        return r, nil
    case <-ctx.Done():
        return Result{}, ctx.Err() // the sender is left blocked
    }
}
```

**Good.** The channel buffers the one send, so the sender finishes whether
or not anyone receives:

```go
func run(ctx context.Context, q Query) (Result, error) {
    ch := make(chan Result, 1)
    go func() { ch <- q.Exec() }()
    select {
    case r := <-ch:
        return r, nil
    case <-ctx.Done():
        return Result{}, ctx.Err()
    }
}
```

## go-concurrency/goroutine-error-lost

**Bad.** Each goroutine only logs its error, and `SyncAll` reports success
regardless:

```go
func SyncAll(stores []Store) error {
    var wg sync.WaitGroup
    for i := range stores {
        s := stores[i]
        wg.Add(1)
        go func() {
            defer wg.Done()
            if err := s.Sync(); err != nil {
                log.Printf("sync %s: %v", s.Name(), err)
            }
        }()
    }
    wg.Wait()
    return nil
}
```

**Good.** An `errgroup.Group` carries the first error back through `Wait`:

```go
func SyncAll(stores []Store) error {
    var g errgroup.Group
    for i := range stores {
        s := stores[i]
        g.Go(func() error {
            if err := s.Sync(); err != nil {
                return fmt.Errorf("sync %s: %w", s.Name(), err)
            }
            return nil
        })
    }
    return g.Wait()
}
```

## go-concurrency/errgroup-context-not-passed

**Bad.** The derived context is discarded, so one failed fetch cancels none
of the others:

```go
func fetchAll(ctx context.Context, urls []string) error {
    g, _ := errgroup.WithContext(ctx)
    for i := range urls {
        u := urls[i]
        g.Go(func() error {
            return fetch(ctx, u) // the parent context
        })
    }
    return g.Wait()
}
```

**Good.** Each function uses the group's context:

```go
func fetchAll(ctx context.Context, urls []string) error {
    g, gctx := errgroup.WithContext(ctx)
    for i := range urls {
        u := urls[i]
        g.Go(func() error {
            return fetch(gctx, u)
        })
    }
    return g.Wait()
}
```

## go-concurrency/channel-closed-while-sends-possible

**Bad.** Each sender closes the shared channel when it finishes, while the
others may still send, and the second `close` panics too:

```go
func merge(srcs []Source) <-chan Item {
    out := make(chan Item)
    for i := range srcs {
        src := srcs[i]
        go func() {
            for _, it := range src.Items() {
                out <- it
            }
            close(out) // other senders may still be sending
        }()
    }
    return out
}
```

**Good.** One goroutine closes the channel after every sender is done:

```go
func merge(srcs []Source) <-chan Item {
    out := make(chan Item)
    var wg sync.WaitGroup
    for i := range srcs {
        src := srcs[i]
        wg.Add(1)
        go func() {
            defer wg.Done()
            for _, it := range src.Items() {
                out <- it
            }
        }()
    }
    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}
```

## go-concurrency/deferred-lock-after-lock

**Bad.** The deferred call locks the mutex a second time instead of
releasing it:

```go
func (s *Store) Put(k, v string) {
    s.mu.Lock()
    defer s.mu.Lock()
    s.data[k] = v
}
```

**Good.** The deferred call is `Unlock`:

```go
func (s *Store) Put(k, v string) {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.data[k] = v
}
```

## go-concurrency/empty-critical-section

**Bad.** The lock is released at once, so the write it was meant to guard
runs unguarded:

```go
func (s *Store) Put(k, v string) {
    s.mu.Lock()
    s.mu.Unlock()
    s.data[k] = v // outside the lock
}
```

**Good.** The `Unlock` is deferred:

```go
func (s *Store) Put(k, v string) {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.data[k] = v
}
```

## go-concurrency/recursive-read-lock

**Bad.** `Describe` holds the read lock and calls `Count`, which takes it
again; a writer waiting between the two deadlocks both:

```go
func (r *Registry) Describe(name string) string {
    r.mu.RLock()
    defer r.mu.RUnlock()
    return name + ": " + strconv.Itoa(r.Count())
}

func (r *Registry) Count() int {
    r.mu.RLock() // the second read lock, while Describe holds the first
    defer r.mu.RUnlock()
    return len(r.items)
}
```

**Good.** An unexported helper reads under the caller's lock, and only the
exported methods lock:

```go
func (r *Registry) Describe(name string) string {
    r.mu.RLock()
    defer r.mu.RUnlock()
    return name + ": " + strconv.Itoa(r.count())
}

func (r *Registry) Count() int {
    r.mu.RLock()
    defer r.mu.RUnlock()
    return r.count()
}

// count requires r.mu held.
func (r *Registry) count() int { return len(r.items) }
```

## go-concurrency/once-do-reentered

**Bad.** The function passed to `once.Do` reaches `Settings` again through
`validate`, so the inner `Do` waits on the outer one:

```go
var (
    once sync.Once
    conf *Config
)

func Settings() *Config {
    once.Do(initSettings)
    return conf
}

func initSettings() {
    conf = parse(os.Getenv("APP_CONFIG"))
    validate()
}

func validate() {
    if Settings().Port == 0 { // once.Do again, on the same Once
        log.Fatal("port is required")
    }
}
```

**Good.** `validate` takes the config it checks, and never calls back into
`Settings`:

```go
func initSettings() {
    conf = parse(os.Getenv("APP_CONFIG"))
    validate(conf)
}

func validate(c *Config) {
    if c.Port == 0 {
        log.Fatal("port is required")
    }
}
```

## go-concurrency/signal-channel-unbuffered

**Bad.** The channel has no buffer, so a signal that arrives before the
receive is dropped:

```go
func waitForInterrupt() {
    sig := make(chan os.Signal)
    signal.Notify(sig, os.Interrupt)
    <-sig
}
```

**Good.** A buffer of one holds the signal until it is received:

```go
func waitForInterrupt() {
    sig := make(chan os.Signal, 1)
    signal.Notify(sig, os.Interrupt)
    <-sig
}
```

## go-concurrency/select-default-spins

**Bad.** The empty `default` makes the `select` return at once, so the loop
spins while no job is ready:

```go
func drain(jobs <-chan Job, quit <-chan struct{}) {
    for {
        select {
        case j := <-jobs:
            j.Run()
        case <-quit:
            return
        default:
        }
    }
}
```

**Good.** Without `default`, the `select` blocks until a channel is ready:

```go
func drain(jobs <-chan Job, quit <-chan struct{}) {
    for {
        select {
        case j := <-jobs:
            j.Run()
        case <-quit:
            return
        }
    }
}
```

## go-concurrency/guarded-state-escapes-lock

**Bad.** `Members` returns the guarded slice itself, which callers then read
while `Add` appends under the lock:

```go
type Roster struct {
    mu      sync.Mutex
    members []string
}

func (r *Roster) Add(name string) {
    r.mu.Lock()
    defer r.mu.Unlock()
    r.members = append(r.members, name)
}

func (r *Roster) Members() []string {
    r.mu.Lock()
    defer r.mu.Unlock()
    return r.members // the caller uses it outside the lock
}
```

**Good.** `Members` returns a copy made under the lock:

```go
func (r *Roster) Members() []string {
    r.mu.Lock()
    defer r.mu.Unlock()
    return append([]string(nil), r.members...)
}
```
