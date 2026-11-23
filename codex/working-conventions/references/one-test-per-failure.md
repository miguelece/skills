# Add a test only for a failure nothing else catches

Applies before adding a test, in any project.

1. **Name the failure the test is for**: the input or the change that would
   make it fail.
2. **Check whether the suite already fails on it.** Make that change, or seed
   that input, with the new test left out, and run the suite. If it already
   fails, the new test adds nothing.
3. **Add the test only where the suite stayed green**, or where the new test
   reports the same failure in words the old one does not and that matters to
   whoever reads the failure.

## Why

A test that repeats another's failure costs a second place to update every
time the behaviour changes, and a reader cannot tell which of the two is the
one that guards the behaviour. Suites grow this way when each change adds its
own check without asking what already fails, and the extra tests read as
coverage while covering nothing new.
