# Check the hardware before a heavy run

Applies before running a GPU model, a large batch job, a big build, or anything
else that can use a large share of the machine.

1. **Estimate the job's peak VRAM, RAM and disk use.** Base it on the
   hardware the paper or project reports, the model size, the input length,
   the batch size and the attention type (flash or plain).
2. **Compare it against a safety budget of three quarters of the machine's
   total**, not the total itself. Read the totals from the machine, or from
   the project's or user's own instruction file where one records them; for
   disk, take three quarters of the free space as measured now.
3. **State the estimate, and whether it fits the budget, before launching.**
4. **If it does not clearly fit, shrink the job first, or ask.** Shorter
   inputs, smaller windows, a smaller batch, running on CPU, or flash attention
   all shrink it.
5. **Never launch a job just to see whether it fits.**

## Why

Out-of-memory is not always a clean failure. Some GPU drivers spill to system
memory instead of raising an error, and some hosts are unstable under
sustained load, so an oversized job can hang or crash the whole machine and
lose every other piece of work on it. A reported hardware figure is the
cheapest warning available: a model that its authors ran on a far larger GPU
will not fit a smaller one by luck. The quarter held back covers the error in
the estimate and everything else the machine is running.
