# Examples: Go testing

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
nearest correct version, that does not trigger it. The code is invented for
the purpose and trimmed to the lines the check reads. Unlike the other Go
modules' examples, the code shown is test code: test functions, subtests,
helpers, benchmarks, fuzz tests and examples in a `_test.go` file, unless a
section says a line comes from the code under test. Where a check turns on
the `go` line of `go.mod`, the example names the version it assumes.

## go-testing/fatal-from-goroutine

**Bad.** `t.Fatalf` is called from a goroutine the test starts, so it stops
only that goroutine:

```go
func TestFetchAll(t *testing.T) {
    var wg sync.WaitGroup
    for _, url := range urls {
        wg.Add(1)
        go func(url string) {
            defer wg.Done()
            if _, err := fetch(url); err != nil {
                t.Fatalf("fetch %s: %v", url, err) // not the test's goroutine
            }
        }(url)
    }
    wg.Wait()
}
```

**Good.** The goroutine reports with `t.Errorf`, which is safe from any
goroutine and lets the others finish:

```go
func TestFetchAll(t *testing.T) {
    var wg sync.WaitGroup
    for _, url := range urls {
        wg.Add(1)
        go func(url string) {
            defer wg.Done()
            if _, err := fetch(url); err != nil {
                t.Errorf("fetch %s: %v", url, err)
            }
        }(url)
    }
    wg.Wait()
}
```

## go-testing/parallel-subtest-captures-loop-variable

**Bad.** The module's `go.mod` reads `go 1.21`, so `tc` is one variable for
the whole loop, and every parallel subtest reads its last value:

```go
// go.mod: go 1.21
func TestParse(t *testing.T) {
    for _, tc := range cases {
        t.Run(tc.name, func(t *testing.T) {
            t.Parallel()
            if got := Parse(tc.in); got != tc.want {
                t.Errorf("Parse(%q) = %v, want %v", tc.in, got, tc.want)
            }
        })
    }
}
```

**Good.** Still on `go 1.21`, a per-iteration copy before the subtest gives
each one its own case. Raising the `go` line to 1.22 or later is the other
acceptable fix:

```go
// go.mod: go 1.21
func TestParse(t *testing.T) {
    for _, tc := range cases {
        tc := tc
        t.Run(tc.name, func(t *testing.T) {
            t.Parallel()
            if got := Parse(tc.in); got != tc.want {
                t.Errorf("Parse(%q) = %v, want %v", tc.in, got, tc.want)
            }
        })
    }
}
```

## go-testing/teardown-before-parallel-subtests

**Bad.** The deferred `Close` runs when the parent returns, which is before
its parallel subtests start, so they all call a closed server:

```go
func TestHandlers(t *testing.T) {
    srv := httptest.NewServer(newRouter())
    defer srv.Close()
    for _, path := range []string{"/health", "/users"} {
        t.Run(path, func(t *testing.T) {
            t.Parallel()
            resp, err := http.Get(srv.URL + path)
            if err != nil {
                t.Fatal(err)
            }
            resp.Body.Close()
        })
    }
}
```

**Good.** `t.Cleanup` runs the teardown after every subtest has finished:

```go
func TestHandlers(t *testing.T) {
    srv := httptest.NewServer(newRouter())
    t.Cleanup(srv.Close)
    for _, path := range []string{"/health", "/users"} {
        t.Run(path, func(t *testing.T) {
            t.Parallel()
            resp, err := http.Get(srv.URL + path)
            if err != nil {
                t.Fatal(err)
            }
            resp.Body.Close()
        })
    }
}
```

## go-testing/process-state-in-parallel-test

**Bad.** A parallel test sets an environment variable; the deferred restore
does not stop another parallel test reading it meanwhile:

```go
func TestRegionFromEnv(t *testing.T) {
    t.Parallel()
    os.Setenv("APP_REGION", "eu-west")
    defer os.Unsetenv("APP_REGION")
    if got := Region(); got != "eu-west" {
        t.Errorf("Region() = %q, want %q", got, "eu-west")
    }
}
```

**Good.** The test no longer runs in parallel, and `t.Setenv` restores the
variable when it ends:

```go
func TestRegionFromEnv(t *testing.T) {
    t.Setenv("APP_REGION", "eu-west")
    if got := Region(); got != "eu-west" {
        t.Errorf("Region() = %q, want %q", got, "eu-west")
    }
}
```

## go-testing/state-leaks-out-of-test

**Bad.** The test replaces the package-level clock of the code under test
and never puts it back, so every later test in the package sees a fixed
time:

```go
// in the code under test: var now = time.Now
func TestTokenExpired(t *testing.T) {
    now = func() time.Time { return time.Date(2030, 1, 1, 0, 0, 0, 0, time.UTC) }
    if !tok.Expired() {
        t.Error("token issued in 2025 not expired in 2030")
    }
}
```

**Good.** The test saves the original and restores it with `t.Cleanup`:

```go
// in the code under test: var now = time.Now
func TestTokenExpired(t *testing.T) {
    orig := now
    t.Cleanup(func() { now = orig })
    now = func() time.Time { return time.Date(2030, 1, 1, 0, 0, 0, 0, time.UTC) }
    if !tok.Expired() {
        t.Error("token issued in 2025 not expired in 2030")
    }
}
```

## go-testing/helper-without-t-helper

**Bad.** The helper can fail the test but does not mark itself, so each
caller's failure is reported at the `t.Fatalf` line inside it:

```go
func mustLoad(t *testing.T, name string) Config {
    cfg, err := Load(filepath.Join("testdata", name))
    if err != nil {
        t.Fatalf("load %s: %v", name, err)
    }
    return cfg
}

func TestDefaults(t *testing.T) {
    cfg := mustLoad(t, "defaults.yaml")
    // ...
}
```

**Good.** `t.Helper()` makes the failure point at the caller's line:

```go
func mustLoad(t *testing.T, name string) Config {
    t.Helper()
    cfg, err := Load(filepath.Join("testdata", name))
    if err != nil {
        t.Fatalf("load %s: %v", name, err)
    }
    return cfg
}

func TestDefaults(t *testing.T) {
    cfg := mustLoad(t, "defaults.yaml")
    // ...
}
```

## go-testing/fatal-ends-table-loop

**Bad.** `t.Fatalf` on a mismatch inside the case loop, with no subtest,
stops the run at the first failing case:

```go
func TestRound(t *testing.T) {
    for _, tc := range []struct{ in, want float64 }{
        {1.4, 1}, {1.5, 2}, {-1.5, -2},
    } {
        if got := Round(tc.in); got != tc.want {
            t.Fatalf("Round(%v) = %v, want %v", tc.in, got, tc.want)
        }
    }
}
```

**Good.** `t.Errorf` records the mismatch and the loop goes on to the rest.
Running each case in its own `t.Run` is the other acceptable form:

```go
func TestRound(t *testing.T) {
    for _, tc := range []struct{ in, want float64 }{
        {1.4, 1}, {1.5, 2}, {-1.5, -2},
    } {
        if got := Round(tc.in); got != tc.want {
            t.Errorf("Round(%v) = %v, want %v", tc.in, got, tc.want)
        }
    }
}
```

## go-testing/fuzz-target-misuses-f

**Bad.** The target calls `Errorf` on the outer `*testing.F` instead of the
`*testing.T` it is given:

```go
func FuzzParseQuery(f *testing.F) {
    f.Add("a=1&b=2")
    f.Fuzz(func(t *testing.T, s string) {
        q, err := ParseQuery(s)
        if err != nil {
            return
        }
        if _, err := ParseQuery(q.Encode()); err != nil {
            f.Errorf("re-parse of %q: %v", q.Encode(), err) // outer F
        }
    })
}
```

**Good.** The target reports through its own `t`:

```go
func FuzzParseQuery(f *testing.F) {
    f.Add("a=1&b=2")
    f.Fuzz(func(t *testing.T, s string) {
        q, err := ParseQuery(s)
        if err != nil {
            return
        }
        if _, err := ParseQuery(q.Encode()); err != nil {
            t.Errorf("re-parse of %q: %v", q.Encode(), err)
        }
    })
}
```

## go-testing/fuzz-target-depends-on-shared-state

**Bad.** A counter captured from outside the target is written on each call
and decides whether strict mode is on, so a saved failing input, run alone,
may run in the other mode and pass:

```go
func FuzzDecode(f *testing.F) {
    f.Add([]byte(`{"a":1}`))
    calls := 0
    f.Fuzz(func(t *testing.T, data []byte) {
        calls++
        d := NewDecoder(Options{Strict: calls%2 == 0})
        if _, err := d.Decode(data); err != nil && !IsSyntaxError(err) {
            t.Errorf("Decode(%q): unexpected error %v", data, err)
        }
    })
}
```

**Good.** The mode is a fuzzed argument, so it is part of the saved input and
every call depends only on its arguments:

```go
func FuzzDecode(f *testing.F) {
    f.Add([]byte(`{"a":1}`), false)
    f.Fuzz(func(t *testing.T, data []byte, strict bool) {
        d := NewDecoder(Options{Strict: strict})
        if _, err := d.Decode(data); err != nil && !IsSyntaxError(err) {
            t.Errorf("Decode(%q): unexpected error %v", data, err)
        }
    })
}
```

## go-testing/benchmark-result-discarded

**Bad.** `Checksum` has no side effect, and its result is unused, so the
compiler may inline it and remove the call:

```go
// in the code under test: func Checksum(p []byte) uint32, no side effects
func BenchmarkChecksum(b *testing.B) {
    data := make([]byte, 4096)
    for i := 0; i < b.N; i++ {
        Checksum(data)
    }
}
```

**Good.** The result goes to a package-level sink, so the call must be kept.
On `go 1.24` or later, a `for b.Loop()` loop is the other acceptable form:

```go
var sink uint32

func BenchmarkChecksum(b *testing.B) {
    data := make([]byte, 4096)
    for i := 0; i < b.N; i++ {
        sink = Checksum(data)
    }
}
```

## go-testing/benchmark-mixes-loop-and-b-n

**Bad.** The module's `go.mod` reads `go 1.24`. The benchmark sizes and
fills its inputs with a loop over `b.N`, then times with `b.Loop()`:

```go
// go.mod: go 1.24
func BenchmarkParseID(b *testing.B) {
    ids := make([]string, b.N)
    for i := 0; i < b.N; i++ {
        ids[i] = strconv.Itoa(i)
    }
    i := 0
    for b.Loop() {
        ParseID(ids[i])
        i++
    }
}
```

**Good.** The inputs are a fixed set, and only `b.Loop()` drives the
iterations:

```go
// go.mod: go 1.24
func BenchmarkParseID(b *testing.B) {
    ids := make([]string, 1024)
    for i := range ids {
        ids[i] = strconv.Itoa(i)
    }
    i := 0
    for b.Loop() {
        ParseID(ids[i%len(ids)])
        i++
    }
}
```

## go-testing/test-not-run

**Bad.** In `parse_test.go`, the letter after `Test` is lowercase, so
`go test` does not treat the function as a test:

```go
func Testparse(t *testing.T) {
    if _, err := Parse(""); err == nil {
        t.Error("Parse(\"\") returned no error")
    }
}
```

**Good.** The name follows the `Test` prefix with an uppercase letter:

```go
func TestParse(t *testing.T) {
    if _, err := Parse(""); err == nil {
        t.Error("Parse(\"\") returned no error")
    }
}
```

## go-testing/example-output-not-checked

**Bad.** The example prints but has no output comment, so it is compiled
and never run:

```go
func ExampleJoin() {
    fmt.Println(Join([]string{"a", "b", "c"}, "-"))
}
```

**Good.** The `// Output:` comment makes `go test` run the example and
compare what it prints:

```go
func ExampleJoin() {
    fmt.Println(Join([]string{"a", "b", "c"}, "-"))
    // Output: a-b-c
}
```

## go-testing/error-compared-by-string

**Bad.** The code under test returns a sentinel for a missing user, and the
test compares the message instead:

```go
// in the code under test: var ErrNotFound = errors.New("user not found")
func TestUserMissing(t *testing.T) {
    _, err := store.User("nobody")
    if err == nil || err.Error() != "user not found" {
        t.Errorf("User(%q) error = %v, want ErrNotFound", "nobody", err)
    }
}
```

**Good.** The test compares by identity with `errors.Is`, which also holds
if the error is later wrapped:

```go
// in the code under test: var ErrNotFound = errors.New("user not found")
func TestUserMissing(t *testing.T) {
    _, err := store.User("nobody")
    if !errors.Is(err, ErrNotFound) {
        t.Errorf("User(%q) error = %v, want ErrNotFound", "nobody", err)
    }
}
```

## go-testing/golden-file-rewritten-every-run

**Bad.** The test writes the actual output to the golden file and then
compares against it, so the comparison always matches:

```go
func TestRender(t *testing.T) {
    got := Render(page)
    golden := filepath.Join("testdata", "page.golden")
    if err := os.WriteFile(golden, got, 0o644); err != nil {
        t.Fatal(err)
    }
    want, err := os.ReadFile(golden)
    if err != nil {
        t.Fatal(err)
    }
    if !bytes.Equal(got, want) {
        t.Errorf("Render() mismatch with %s", golden)
    }
}
```

**Good.** The write happens only when the test is run with `-update`:

```go
var update = flag.Bool("update", false, "rewrite golden files")

func TestRender(t *testing.T) {
    got := Render(page)
    golden := filepath.Join("testdata", "page.golden")
    if *update {
        if err := os.WriteFile(golden, got, 0o644); err != nil {
            t.Fatal(err)
        }
    }
    want, err := os.ReadFile(golden)
    if err != nil {
        t.Fatal(err)
    }
    if !bytes.Equal(got, want) {
        t.Errorf("Render() mismatch with %s", golden)
    }
}
```
