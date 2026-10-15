# Exercises

Work these **on paper first**, then use the simulator to check yourself:

```bash
python srtf.py          # interactive mode — type the exercise's processes in
```

Worked answers are in [solutions.md](solutions.md). No peeking — the
learning happens in the gap between your prediction and the program's
output. (If your answer differs, check tie-breaking and arrival instants
before assuming you — or the program — are wrong. See
[doc 02](../docs/02-srtf-explained.md) §4.)

Notation: `P1(0, 5)` means P1 arrives at time 0 with burst time 5.

---

## Exercise 1 — Predict the Gantt chart ⭐

Processes: `P1(0, 5)`, `P2(1, 3)`, `P3(2, 1)`.

1. Draw the Gantt chart.
2. Compute finish, turnaround, waiting, and response time for each process.
3. Compute the three averages and the number of context switches.

*Hint: something new arrives at t=1 and again at t=2. Re-decide at both
instants.*

## Exercise 2 — Idle time and utilisation ⭐

Processes: `P1(4, 2)`, `P2(0, 1)`, `P3(6, 2)`.

1. Draw the Gantt chart, including IDLE blocks.
2. What is each process's waiting time? (Careful — see
   [doc 05](../docs/05-metrics-formulas.md) §5 before answering.)
3. Compute the makespan, idle time, and CPU utilisation.

## Exercise 3 — The tie that isn't ⭐⭐

Processes: `P1(0, 4)`, `P2(2, 2)`, `P3(3, 3)`.

At t=2, P2 arrives with burst 2 — exactly equal to P1's remaining time at
that moment.

1. Does P2 preempt P1? Why, or why not?
2. Draw the full Gantt chart and compute all waiting times.
3. Would the answer change if ties were broken in favour of the *newest*
   process instead of the lowest process number? What exactly changes?

## Exercise 4 — SRTF vs FCFS ⭐⭐

Using the classic processes `P1(0, 8)`, `P2(1, 4)`, `P3(2, 9)`, `P4(3, 5)`:

1. Schedule them with **FCFS** (arrival order, non-preemptive) and compute
   the average waiting time.
2. Compare with SRTF's 6.50. Where do the 2.25 units of difference come
   from — which processes gain, which lose, relative to FCFS?
3. FCFS has *fewer* context switches. Name a real-world cost that could
   make FCFS preferable anyway in some system.

## Exercise 5 — Response ≠ waiting ⭐

Processes: `P1(0, 10)`, `P2(1, 4)`, `P3(3, 1)`.

Find a process whose response time and waiting time differ. Explain, in
one or two sentences, *where the extra waiting came from*. Also state the
general rule: for which processes are the two numbers always equal?

## Exercise 6 — Starvation, constructed by you ⭐⭐

1. Construct a set of at most 5 processes in which one process waits at
   least 8 time units under SRTF while every other process waits 0.
   (Verify with the simulator.)
2. Explain why adding *more* short processes makes the victim's wait grow
   without bound.
3. Describe one mechanism (not in the simulator) that prevents this, and
   one downside of that mechanism.

## Exercise 7 — Bug hunt ⭐⭐⭐

A student modified `_pick_next` and produced this version:

```python
for i in range(n):
    if processes[i][0] <= time and remaining[i] <= shortest:
        shortest = remaining[i]
        idx = i
```

Their program now misbehaves. Identify **two** distinct bugs relative to
the original:

```python
if arrival <= time and 0 < remaining[i] < shortest:
```

For each bug: describe a concrete input that exposes it, and what the
program does (wrong winner? crash? infinite loop?) on that input.

## Exercise 8 — Change the policy (code) ⭐⭐⭐

1. In `srtf.py`, change the tie-break in `_pick_next` from "lowest index
   wins" to "highest index wins" (one character changes). Predict — before
   running — what happens to Example 5 (`[(0, 3), (0, 3)]`) in
   `examples.py`. Then run it and confirm.
2. Restore the original. Now suppose you wanted **non-preemptive SJF**
   instead of SRTF. Describe (in words or code) the smallest change to the
   simulation loop that achieves it: *when* should `_pick_next` be allowed
   to change the running process?
3. Run the full test suite after each change
   (`python -m unittest discover -s tests`). Which tests fail for the SJF
   variant, and why are those failures *expected* — what do they tell you
   about what the tests were really specifying?

## Exercise 9 — Complexity thinking ⭐⭐⭐

1. Processes arrive at times 0, 100, 200, …, 900 (10 processes), each with
   burst 5. Roughly how many *ticks* does the simulator execute? How many
   of those ticks are idle? What does that tell you about what the
   simulation spends its time doing?
2. The event-driven idea in [doc 06](../docs/06-complexity-limitations-next-steps.md)
   jumps the clock between arrivals/finishes. For this input, roughly how
   many *decisions* would an event-driven simulator make?
3. State the simulator's time complexity in terms of `n` (processes) and
   `T` (ticks), and the event-driven version's in terms of `n` and the
   number of Gantt segments `S`.

---

*Difficulty: ⭐ warm-up · ⭐⭐ core understanding · ⭐⭐⭐ stretch.*

*Finished? The [next-steps list](../docs/06-complexity-limitations-next-steps.md#4-next-steps-ordered-by-difficulty)
has project-sized continuations of Exercises 7–9.*
