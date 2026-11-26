# Climb the reuse ladder before writing new code

Applies before writing any new code, in any project: a function, a test
helper, a fixture step, or a branch added to code that exists.

Climb the rungs in order, and stop at the first one that works.

1. **Skip the work.** Ask whether the code is needed at all: the task may
   not ask for it, the case may not arise, or the behaviour may already be
   there.
2. **Reuse what exists.**
   - **Search by what it does, not by a name you would give it.** Grep for
     the call it would wrap (the subprocess command, the parser, the file
     walk) and for the data it returns, across the code and the tests.
   - **Use what you find.** Import it, or extend it with a parameter where it
     differs only in a filter or a path. A copy that differs in one argument
     is still a copy.
   - **Where it cannot be reused** (it lives in code the task may not change,
     or importing it would couple two things that should stay apart), go on
     down the ladder, and say in the change why the existing one did not
     serve, so a later cleanup can join them.
3. **Use the standard library or the platform.** A language or runtime
   facility already does most parsing, path handling, date arithmetic and
   collection work.
4. **Use an installed dependency.** One the project already declares. Adding
   a dependency is not this rung; it is a decision with its own checks.
5. **Write one line.** An expression or a call in place, where a named
   helper would wrap nothing worth naming.
6. **Write the minimum.** The least code that does what the task asks, with
   nothing for a case the task does not have.

**Never cut these to stop on a higher rung:** validation at trust
boundaries, error handling that prevents data loss, security, and
accessibility. A rung that would drop one of them has not worked.

**A shortcut names what it skipped.** Where a rung leaves out something a
fuller version would hold, say in the change and in the reply what was
skipped, and ship the shortcut with the check that shows it still works.

## Why

In one author's benchmark on one model, an instruction to stop at the first
option that works roughly halved the code an agent delivered while its
checked pass rates held. That result is directional, not settled, but the
cost it points at is not: each line is a place a later fix must reach. A
second helper that does what the first already does doubles those places,
and the two drift: one gets the error handling or the edge case the other
lacks. Copies are cheap to write and expensive to find later, because a
review of one change sees only the new copy, never the old one it repeats.
Stopping at the first rung that works cuts the code without cutting the
checks, which is why the exceptions are named and a shortcut says what it
left out.
