# Examples: Python testing

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
nearest correct version, that does not trigger it. The code is invented for
the purpose and trimmed to the lines the check reads: test functions,
fixtures and test configuration, with the code under test assumed imported.
Where a check turns on pytest's behaviour or its configuration, the example
names the version it assumes, pytest 9.0.

## python-testing/test-without-assertion

**Bad.** The test calls the code and prints the result, and its name does not
say that completing without raising is the point, so it passes on a broken
parser:

```python
def test_parse_config():
    config = parse_config("retries = 3\n")
    print(config)
```

**Good.** The test asserts the value the parser should produce:

```python
def test_parse_config():
    config = parse_config("retries = 3\n")
    assert config.retries == 3
```

## python-testing/test-returns-instead-of-asserting

**Bad.** The test returns the result of its check, which pytest 9.0 ignores
apart from a warning, so the test passes when `is_valid` returns False:

```python
def test_valid_email():
    return is_valid("someone@example.com")
```

**Good.** The test asserts the value instead of returning it:

```python
def test_valid_email():
    assert is_valid("someone@example.com")
```

## python-testing/assertion-that-cannot-fail

**Bad.** The first assertion's condition is a two-item tuple, which is always
true, and the second names the mock's assertion method without calling it:

```python
def test_notify(mailer):
    sent = notify(mailer, "build failed")
    assert (sent == 1, "one message expected")
    mailer.send.assert_called_once_with
```

**Good.** The message follows a comma outside the condition, and the mock
assertion is called with the arguments it checks:

```python
def test_notify(mailer):
    sent = notify(mailer, "build failed")
    assert sent == 1, "one message expected"
    mailer.send.assert_called_once_with("build failed")
```

## python-testing/assertion-behind-a-condition

**Bad.** The assertion runs only when a user is found, so a regression that
makes `find_user` return None reaches the end of the test with nothing
asserted:

```python
def test_find_user():
    user = find_user("ada")
    if user is not None:
        assert user.name == "ada"
```

**Good.** The test asserts that the user is found, then asserts on it, in
straight-line code:

```python
def test_find_user():
    user = find_user("ada")
    assert user is not None
    assert user.name == "ada"
```

## python-testing/raises-block-with-several-statements

**Bad.** Building the account is inside the block, so a `ValueError` from the
constructor passes the test, and `withdraw`, the call the test names, never
runs:

```python
def test_withdraw_more_than_balance():
    with pytest.raises(ValueError, match="insufficient funds"):
        account = Account(balance=10)
        account.withdraw(50)
```

**Good.** Setup sits before the block, which holds only the call under test:

```python
def test_withdraw_more_than_balance():
    account = Account(balance=10)
    with pytest.raises(ValueError, match="insufficient funds"):
        account.withdraw(50)
```

## python-testing/raises-without-match

**Bad.** `parse_port` raises `ValueError` both for a non-numeric string and
for a number out of range, and the test constrains neither the message nor
the captured exception, so it passes for either cause:

```python
def test_port_out_of_range():
    with pytest.raises(ValueError):
        parse_port("70000")
```

**Good.** `match` pins the message of the cause the test names:

```python
def test_port_out_of_range():
    with pytest.raises(ValueError, match="out of range"):
        parse_port("70000")
```

## python-testing/test-shadowed-by-same-name

**Bad.** Two tests in one module share a name, so the second replaces the
first and the empty-string case never runs:

```python
def test_parse_empty():
    assert parse("") == []


def test_parse_empty():
    assert parse("   ") == []
```

**Good.** Each test has its own name, so both are collected:

```python
def test_parse_empty_string():
    assert parse("") == []


def test_parse_whitespace_only():
    assert parse("   ") == []
```

## python-testing/test-not-collected

**Bad.** The `Test` class defines `__init__`, so pytest skips the whole class
with a collection warning, and the project's configuration sets no
`python_classes` or other pattern that would change that:

```python
# pyproject.toml: [tool.pytest.ini_options] sets only testpaths = ["tests"]
class TestCart:
    def __init__(self):
        self.cart = Cart()

    def test_add_item(self):
        self.cart.add("apple")
        assert self.cart.count() == 1
```

**Good.** The setup moves into a fixture and the class keeps no `__init__`,
so its tests are collected:

```python
class TestCart:
    @pytest.fixture
    def cart(self):
        return Cart()

    def test_add_item(self, cart):
        cart.add("apple")
        assert cart.count() == 1
```

## python-testing/skip-without-reason

**Bad.** The marker and the call skip with no reason given, so nothing says
when the tests could run again:

```python
@pytest.mark.skip
def test_export_pdf():
    assert export_pdf(report()).startswith(b"%PDF")


def test_import_legacy():
    pytest.skip()
```

**Good.** Each skip says why, so it can be re-judged later:

```python
@pytest.mark.skip(reason="PDF export needs the renderer, not in CI yet")
def test_export_pdf():
    assert export_pdf(report()).startswith(b"%PDF")


def test_import_legacy():
    pytest.skip("legacy format dropped; delete with the importer")
```

## python-testing/xfail-not-strict

**Bad.** On pytest 9.0, the marker gives a reason but no `strict=True`, and
the configuration does not set the strict-xfail option, so when the rounding
bug is fixed the test passes as XPASS and the suite stays green:

```python
# pyproject.toml: [tool.pytest.ini_options] sets no xfail_strict or strict_xfail
@pytest.mark.xfail(reason="rounding bug in invoice totals")
def test_invoice_total():
    assert invoice_total(["19.99", "5.01"]) == Decimal("25.00")
```

**Good.** Strict mode makes an unexpected pass fail the suite, so the marker
cannot outlive the bug. Setting `xfail_strict = true` in the configuration is
the other acceptable fix:

```python
@pytest.mark.xfail(strict=True, reason="rounding bug in invoice totals")
def test_invoice_total():
    assert invoice_total(["19.99", "5.01"]) == Decimal("25.00")
```

## python-testing/float-compared-exactly

**Bad.** `mean` sums and divides in float arithmetic, and the expected side
is a non-integral float literal, so rounding fails the test: the mean it
computes of 0.1 and 0.2 is 0.15000000000000002:

```python
def test_mean():
    assert mean([0.1, 0.2]) == 0.15
```

**Good.** `pytest.approx` compares within a relative tolerance:

```python
def test_mean():
    assert mean([0.1, 0.2]) == pytest.approx(0.15)
```

## python-testing/state-leaks-out-of-test

**Bad.** The test sets an environment variable and never restores it, so
every test that runs after it in the same process sees debug mode:

```python
def test_debug_logging(caplog):
    os.environ["APP_DEBUG"] = "1"
    start_app()
    assert "debug logging on" in caplog.text
```

**Good.** `monkeypatch` sets the variable for this test only and restores it
afterwards:

```python
def test_debug_logging(caplog, monkeypatch):
    monkeypatch.setenv("APP_DEBUG", "1")
    start_app()
    assert "debug logging on" in caplog.text
```

## python-testing/sleep-in-test

**Bad.** The test waits a fixed two seconds for the worker to finish the job,
the condition the sleep stands in for, so it is slow on a fast machine and
fails on a slow one:

```python
def test_worker_processes_job(queue, worker):
    queue.put(Job("resize"))
    time.sleep(2)
    assert queue.empty()
```

**Good.** The test polls the condition it needs, with a deadline, so it
returns as soon as the job is done and fails clearly if it never is:

```python
def test_worker_processes_job(queue, worker):
    queue.put(Job("resize"))
    deadline = time.monotonic() + 5
    while not queue.empty():
        assert time.monotonic() < deadline, "job not processed in 5s"
        time.sleep(0.01)
```
