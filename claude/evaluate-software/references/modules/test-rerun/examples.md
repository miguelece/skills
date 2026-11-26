# Examples: test rerun

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example that
does not trigger it. The check is dynamic, so each example is a run record
rather than code: the declared test command with the manifest line that
declares it, the revision and working tree read before each run, and every
run with its exact command, its time and its result. Every record runs the
same invented service, `orders-api/`, whose `package.json` declares
`"test": "jest"`, with a clean working tree. Times are counted from the
first launch.

## test-rerun/test-is-flaky

**Bad.** The first run fails one test, and a later rerun of that test alone,
on the same revision with nothing changed, passes. Jest has no repeat flag,
so the same-process rerun is named as out of reach, as the rerun on another
host always is:

```text
manifest  orders-api/package.json: "test": "jest"
revision  4f2c9e1, working tree clean, read before each run
isolation none added; the run approved none
run 1     0 s    npm test
          FAIL  src/orders.test.js
            orders > ships an order placed before the cutoff
            Expected: "shipped"  Received: "pending"
run 2     95 s   npm test -- src/orders.test.js -t "ships an order placed before the cutoff"
          PASS  src/orders.test.js (1 test)
same process  out of reach: Jest has no repeat flag
another host  out of reach
result    flaky: failed in run 1, passed in run 2
location  src/orders.test.js, "orders > ships an order placed before the cutoff"
suggested-owner
          src/orders.test.js  A. Tester  9b1d2e7
          src/orders.js       B. Coder   3c4f5a6
          (git log -1 --format="%H %an" 4f2c9e1 -- <file>)
```

**Good.** The test no longer reads the wall clock: it passes a fixed time to
the code under test, committed as `7d8e9f0`, so the first run passes and
nothing is rerun. One acceptable fix among several; what matters is that
every run gives the same result:

```text
manifest  orders-api/package.json: "test": "jest"
revision  7d8e9f0, working tree clean, read before each run
isolation none added; the run approved none
run 1     0 s    npm test
          PASS  src/orders.test.js (12 tests)
result    no test failed, so none was rerun
```

A test that failed in run 1 and again in each rerun is not this check's
finding either: it goes in `unresolved` at its location, since no local
rerun passed and the rerun on another host is out of reach.
