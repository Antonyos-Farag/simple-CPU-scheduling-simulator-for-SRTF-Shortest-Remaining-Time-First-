# 06 · Complexity, Limitations & Next Steps

*Previous: [05 · Metrics & Formulas](05-metrics-formulas.md) ·
Then: [Exercises](../exercises/exercises.md)*

You've learned what SRTF does and how the simulator implements it. This
final document steps back: how expensive is the simulation, where does the
*model* stop being true, and what would you build next?

---

## 1. Complexity of this simulator

Let `n` = number of processes and `T` = makespan (roughly total burst +
idle time, i.e. the number of ticks simulated).

| Piece | Cost | Why |
|-------|------|-----|
| `_pick_next()` | O(n) per call | Linear scan over all processes |
| Main loop | O(T · n) total | One `_pick_next()` per tick, T ticks |
| `_merge_timeline()` | O(T) | Single pass over the timeline |
| Memory | O(T + n) | The per-tick timeline dominates |

**Reading that table:** for teaching inputs (a handful of processes, tens
of ticks) this is instant. For a stress input — say 1,000 processes with
bursts of 10,000 — `T ≈ 10⁷` and the scan makes it ~10¹⁰ operations:
minutes to hours. The simulator chooses clarity over speed deliberately:
the tick loop *is* the definition of the algorithm, written out loud.

### How a production version gets faster

1. **Fewer decisions.** `_pick_next` can only change its answer when
   (a) the running process finishes, or (b) a new process arrives. Between
   those *events* the winner is stable (its remaining time only shrinks).
   An **event-driven** simulator jumps the clock straight to the next
   event instead of stepping tick by tick: the number of decisions drops
   from `T` (one per tick) to one per Gantt segment — and since segments
   are created only by arrivals, finishes, and preemptions (which
   themselves only happen at arrivals), that's O(n) segments for n
   processes, regardless of how large the bursts or idle gaps are.
2. **A better ready structure.** Keep ready processes in a **min-heap
   keyed by remaining time**: picking the winner becomes O(1) peek,
   insertion/removal O(log n). (The running process's key decreases every
   tick — with event-driven jumps you only reinsert it at events, so the
   "decreasing key" problem disappears.)
3. Combined: **O((n + preemptions) · log n)** — the same answer, computed
   orders of magnitude faster. The output must be *identical* (including
   tie-breaks!), which makes this a perfect refactoring exercise: the
   existing tests are your safety net.

A fair question: if event-driven is strictly faster, why teach the tick
version? Because the tick version cannot hide anything. Every intermediate
state is inspectable, the loop invariant is obvious, and bugs have nowhere
to lurk. Optimise after you understand — in that order.

## 2. Where the model stops being real

SRTF as implemented here (and in textbooks) rests on assumptions real
operating systems cannot make:

### 2.1 "Burst times are known"

The algorithm's input is the one thing a real scheduler never has: the
future. Real systems **predict** the next CPU burst from history, commonly
with exponential averaging:

```text
predictedₙ₊₁ = α · (actualₙ) + (1 − α) · predictedₙ        0 ≤ α ≤ 1
```

`α` near 1 trusts recent behaviour; near 0 trusts the long-run average.
With predictions, "SRTF" becomes *shortest predicted remaining time* — and
its optimality guarantee evaporates, because the proof needs true values.
This is the main reason SRTF is a **benchmark** (the bar other algorithms
are measured against) rather than a shipped scheduler.

### 2.2 "Context switches are free and instant"

Here, switching costs 0 ticks. In reality a switch flushes caches and
saves/restores state. An algorithm that preempts every tick (as SRTF loves
to do with many tiny jobs) can spend a meaningful fraction of CPU on
switching. Real schedulers therefore impose a **minimum runtime** or use
time quanta (Round Robin's core idea) to amortise switch costs.

### 2.3 "Time is discrete; processes never block"

Real processes alternate CPU bursts with I/O waits, have multiple threads,
memory hierarchies, and multiple cores. A process blocked on disk shouldn't
count as "waiting for CPU", yet our single-number model has no way to say
so. Multi-core scheduling adds migration and cache-affinity questions this
model can't even express.

### 2.4 Fairness

As §6 of [doc 02](02-srtf-explained.md) showed, SRTF can starve long
processes indefinitely. Production schedulers (Linux's CFS/EEVDF, Windows'
multilevel feedback queues) are built around **fairness with good response
time**, borrowing SRTF's insight ("favour whoever has received least /
needs least") while guaranteeing everyone progresses. *Aging* — boosting
effective priority the longer a process waits — is the classical patch,
and a great extension exercise.

## 3. So why learn SRTF at all?

- It is the **provable optimum** for average waiting time — the reference
  point every practical scheduler is judged against.
- It teaches **preemption**, ready queues, and the metric vocabulary that
  the entire field uses (and that interviews and exams test).
- Its failure mode (starvation) motivates essentially every fairness
  mechanism in real kernels.

## 4. Next steps, ordered by difficulty

1. **Trace mode** — add a `--trace` flag printing the decision table of
   [doc 04](04-worked-example.md) automatically. (Best first change: pure
   output, no algorithm changes.)
2. **New algorithms** — implement FCFS and non-preemptive SJF as sibling
   functions returning `SchedulingResult`; compare averages on identical
   inputs. Notice how much code (validation, Gantt, printing) is reused.
3. **Round Robin** — add a quantum parameter; observe average response
   time improve and context switches multiply as the quantum shrinks.
4. **Aging for SRTF** — e.g. effective remaining = remaining − (waited /
   k). Measure how Example 6's starvation softens as `k` varies; check
   average waiting time doesn't explode.
5. **Event-driven rewrite** — restructure per §1, prove identical output
   with the current test suite, then benchmark 10,000 processes.
6. **Visualisation** — render the Gantt chart as an image or a small web
   page; animate the ready queue tick by tick.

Whichever you pick: predict the effect *before* you code it, and let the
tests tell you if you were right.

---

## The whole course in five sentences

1. Scheduling decides which ready process gets the CPU, and re-deciding
   that question is the difference between whole algorithm families.
2. SRTF always runs the arrived process with the least remaining time,
   preempting whenever a shorter job appears.
3. That rule minimises average waiting/turnaround time — provably — but
   needs unknowable future knowledge and can starve long jobs.
4. Waiting, turnaround, and response time measure different slices of a
   process's life; their formulas are three lines and worth memorising.
5. A one-tick-at-a-time simulation makes all of this concrete, checkable,
   and extendable — which is why you're holding one.

Now go break things: [Exercises →](../exercises/exercises.md)
