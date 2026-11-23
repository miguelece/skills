# Search for an existing helper before writing one

Applies before writing a function, a test helper or a fixture step that
reads, lists, parses or sets something up, in any project.

1. **Search by what it does, not by a name you would give it.** Grep for the
   call it would wrap (the subprocess command, the parser, the file walk) and
   for the data it returns, across the code and the tests.
2. **Use what exists.** Import it, or extend it with a parameter where it
   differs only in a filter or a path. A copy that differs in one argument is
   still a copy.
3. **Where the existing helper cannot be reused** (it lives in code the task
   may not change, or importing it would couple two things that should stay
   apart), write the new one and say in the change why the old one did not
   serve, so a later cleanup can join them.

## Why

A second helper that does what the first already does doubles the places a
fix must reach, and the two drift: one gets the error handling or the edge
case the other lacks. Copies are cheap to write and expensive to find later,
because a review of one change sees only the new copy, never the old one it
repeats.
