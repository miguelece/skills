# Examples: application runtime

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
same run succeeding, that does not trigger it. The checks are dynamic, so
each example is a run record rather than code: what the dynamic phase would
observe, with the declared command and the manifest line that declares it,
the readiness signal waited for or the request or stop signal sent, and the
output observed. Every record runs the same invented service, an HTTP API in
`orders-api/` whose `package.json` declares its start command, on
`localhost`. Times are counted from the launch, or from the signal sent.

## application-runtime/does-not-start-or-report-ready

**Bad.** The declared command exits before the documented readiness signal
answers, so the record gives the exit code and the last lines of output. Had
the process stayed up with no signal, the record would give the 15 seconds
waited instead, a limit the README sets rather than a typical time:

```text
manifest  orders-api/package.json: "start": "node src/server.js"
command   npm start
ready     GET http://localhost:3000/healthz answers 200, within 15 s
          (README.md, "Running": "ready when /healthz answers 200
          within 15 seconds of start")
observed  exit code 1 at 0.4 s; /healthz never answered; last output:
            > orders-api@1.0.0 start
            > node src/server.js
            src/server.js:12
            TypeError: Cannot read properties of undefined (reading 'port')
```

**Good.** The same command stays running and the documented signal answers
inside the documented limit:

```text
manifest  orders-api/package.json: "start": "node src/server.js"
command   npm start
ready     GET http://localhost:3000/healthz answers 200, within 15 s
          (README.md, "Running": "ready when /healthz answers 200
          within 15 seconds of start")
observed  process running; /healthz answered 200 at 2.1 s; last output:
            orders-api listening on port 3000
```

## application-runtime/smoke-check-fails

**Bad.** The README documents a read-only request and its response, and the
running service answers it with a different status and body:

```text
manifest   orders-api/package.json: "start": "node src/server.js"
command    npm start (ready: /healthz answered 200 at 2.0 s)
documented README.md, "Usage": a fresh start seeds order 42, and
             $ curl http://localhost:3000/orders/42
             {"id": 42, "status": "shipped"}
sent       GET http://localhost:3000/orders/42
observed   404, body {"error": "no route for GET /orders/42"}
expected   200, body {"id": 42, "status": "shipped"}
```

**Good.** The same request returns the documented response:

```text
manifest   orders-api/package.json: "start": "node src/server.js"
command    npm start (ready: /healthz answered 200 at 2.0 s)
documented README.md, "Usage": a fresh start seeds order 42, and
             $ curl http://localhost:3000/orders/42
             {"id": 42, "status": "shipped"}
sent       GET http://localhost:3000/orders/42
observed   200, body {"id": 42, "status": "shipped"}
expected   200, body {"id": 42, "status": "shipped"}
```

## application-runtime/shutdown-is-not-clean

**Bad.** `npm start` was started as the root of its own process group, and
the stop goes to that group. The wrapper and its shell end on the signal,
but the service ignores it for the whole wait and keeps its port bound, so
it is stopped by force, and the record says so:

```text
manifest  orders-api/package.json: "start": "node src/server.js"
command   npm start (ready: /healthz answered 200 at 2.0 s)
sent      SIGTERM to process group 4812: npm (4812), sh (4825),
          node src/server.js (4826)
waited    10 s
observed  npm and sh ended by SIGTERM at 0.1 s; node still running and
          port 3000 still listening at 10 s; no output after the signal;
          node stopped by force (SIGKILL) at 10 s
```

**Good.** The same signal to the same group closes the server, which exits
0 well inside the wait and releases its port; the wrapper ends by the
signal's own default action, which is a clean stop:

```text
manifest  orders-api/package.json: "start": "node src/server.js"
command   npm start (ready: /healthz answered 200 at 2.0 s)
sent      SIGTERM to process group 4812: npm (4812), sh (4825),
          node src/server.js (4826)
waited    10 s
observed  node exit code 0 at 0.3 s; sh and npm ended by SIGTERM at
          0.3 s; no process left in the group; port 3000 released; last
          output:
            received SIGTERM, closing server
            server closed
```
