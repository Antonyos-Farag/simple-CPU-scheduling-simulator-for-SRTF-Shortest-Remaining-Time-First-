# 03 · Code Walkthrough

*Previous: [02 · SRTF Explained](02-srtf-explained.md) ·
Next: [04 · Worked Example](04-worked-example.md)*

This document explains `srtf.py` piece by piece. The simulator is a cleaned-up,
extended version of a widely-copied beginner SRTF program; the final section
catalogues what was changed and **why** — including two genuine bugs in the
original that could hang the program.

---

## 0. The shape of the program

```text
input ──► srtf(processes) ──► SchedulingResult ──► print_gantt_chart()
   ▲              │                       └───────► print_results()
   │              ├─ _validate_processes()        averages, utilisation…
   │              ├─ _pick_next()      (the SRTF rule, one tick)
   └──────────────┴─ while loop        (the clock)
 get_*_int() helpers
```

Everything flows through one data structure, `SchedulingResult`, so the
*algorithm* never prints and the *printing* never computes. That separation
is what makes the algorithm testable (`tests/test_srtf.py` imports `srtf()`
and never touches the terminal).

---

## 1. The data model

A process is just a tuple `(arrival_time, burst_time)`; its identity is its
position — index 0 is displayed as `P1`. (Using an index instead of a name
is why every formula below needs `processes[i][0]` for arrival and
`processes[i][1]` for burst. Keep that mapping in your head: `[0]` =
arrival, `[1]` = burst.)

Parallel lists track one fact per process:

| List | Meaning | Initial value |
|------|---------|---------------|
| `remaining[i]` | CPU time P(i+1) still needs | copy of burst |
| `response[i]` | first-run time − arrival; `−1` = "hasn't run yet" | `−1` (sentinel) |
| `finish[i]` | clock value when P(i+1) completed | `0` (placeholder) |
| `turnaround[i]` | `finish − arrival` | computed at finish |
| `waiting[i]` | `turnaround − burst` | computed at finish |

**Why the `−1` sentinel for response?** Response time is recorded exactly
once — on a process's *first* tick. The sentinel lets the loop distinguish
"has never run" from "ran, and its response time happened to be 0"
(a process that arrives at 0 and runs immediately legitimately has
response 0). Using `0` as "unset" would make those two cases
indistinguishable. Whenever you see a magic value in code, ask *what real
value it must not collide with* — that's the sentinel pattern.

`SchedulingResult` (a `@dataclass`) bundles the five lists plus the Gantt
chart, makespan, idle time and context-switch count, and derives CPU
utilisation as a property. The original program returned four bare lists;
bundling them means the Gantt chart and statistics travel with the metrics
instead of needing a second simulation pass.

---

## 2. Input validation — `get_non_negative_int` / `get_positive_int`

Both helpers share one pattern:

```python
while True:
    try:
        value = int(input(prompt))
    except ValueError:
        print("  Error: Please enter a valid integer.")
        continue          # ask again; never crash on a typo
    if value < LIMIT:     # 0 or 1 depending on the helper
        print("  Error: ...")
        continue
    return value
```

Teaching points:

- **`int()` raises `ValueError`** on input like `"abc"` or `"3.5"`. Catching
  it turns a crash into a re-prompt — the right behaviour for interactive
  tools.
- **Two different limits exist for a reason.** Arrival times and the
  *count* of processes look similar but aren't: an arrival of 0 is normal
  (P1 arrives "now"), while **0 processes** or a **burst of 0** make the
  simulation meaningless — see §6, Bug 1. So the codebase has
  `get_non_negative_int` (≥ 0, for arrivals) and `get_positive_int` (≥ 1,
  for counts and bursts). The original program used one function named
  "positive" that actually accepted 0 — a naming/behaviour mismatch that
  hid the bug.
- The GUI-free `srtf()` function *also* validates (`_validate_processes`
  raises `ValueError`), because library callers (tests, `examples.py`)
  bypass the input helpers. **Validate at every entry point you don't
  control.**

---

## 3. The SRTF rule — `_pick_next()`

```python
def _pick_next(processes, remaining, time):
    idx = -1
    shortest = float("inf")
    for i in range(len(processes)):
        arrival = processes[i][0]
        if arrival <= time and 0 < remaining[i] < shortest:
            shortest = remaining[i]
            idx = i
    return idx
```

This one chained condition encodes the whole algorithm from
[doc 02](02-srtf-explained.md):

- `arrival <= time` — only processes that exist yet;
- `0 < remaining[i]` — only unfinished processes. Without this, finished
  processes (remaining exactly 0) would win every comparison and the
  simulation would "run" a dead process forever;
- `remaining[i] < shortest` — strictly smaller beats the current champion.

Details worth noticing:

- **`float("inf")` as the initial champion** guarantees the first eligible
  process always replaces it. Initialising `shortest` to, say, 9999 would
  silently break for a burst of 10000. Infinity is the honest "no value yet".
- **Strict `<` implements the tie-break.** The first process achieving the
  minimum is never displaced by an equal one later in the scan, so the
  lowest index wins ties. Change `<` to `<=` and ties flip to the *highest*
  index — a one-character change to scheduling policy. Try it in the
  tie example `[(0, 3), (0, 3)]` and watch the Gantt chart swap.
- **`idx = −1` means "nobody".** The caller treats −1 as an idle tick.
  Again a sentinel — and safe here because −1 is never a valid list index
  result we could confuse it with... in Python `list[-1]` *is* valid (last
  element!), which is exactly why the caller checks `idx == -1` **before**
  ever using it as an index. Sentinels demand discipline at the use site.

Cost: one scan is O(n). The main loop calls this every tick, giving the
overall complexity analysed in [doc 06](06-complexity-limitations-next-steps.md).

---

## 4. The simulation loop — `srtf()`

```text
while complete != n:                 # until everyone is done
    idx = _pick_next(...)            # who deserves the CPU now?
    if idx == -1:  idle one tick     # nobody has arrived
    else:
        record response (first tick only)
        remaining[idx] -= 1          # run for exactly 1 tick
        time += 1
        if remaining[idx] == 0:      # finished?
            record finish / turnaround / waiting
```

Four ideas do all the work:

### 4.1 One tick at a time = preemption

The loop body grants **exactly one** time unit, then loops back to
re-decide. Nothing in the code says "preempt" — preemption *emerges* from
re-deciding every tick. A newcomer with smaller remaining time simply wins
the next `_pick_next` call; the previous runner's `remaining` value
preserves its progress. This is the single most important insight in the
file: **in a tick simulation, preemptive algorithms are not harder than
non-preemptive ones — you just decide more often.**

### 4.2 The clock advances in both branches

Idle ticks increment `time` too. If they didn't, a process arriving at
t=100 would appear to arrive at t=0 and every metric would be wrong. Time
passing while nothing happens *is* something happening (to the arrival
schedule).

### 4.3 Metrics are computed at the moment of finishing

```python
finish[idx]     = time                       # already incremented!
turnaround[idx] = finish[idx] - arrival
waiting[idx]    = turnaround[idx] - burst
```

Note the ordering: `time` is incremented *before* the finish check, so a
process whose last tick spans [4, 5) gets `finish = 5` — "it completed at
the instant t=5". This end-exclusive convention is why a lone process
`P1(3, 4)` finishes at 7, not 6. The formulas themselves are derived in
[doc 05](05-metrics-formulas.md).

### 4.4 The loop invariant (why you can trust it)

At the top of every iteration, this statement is true:

> *For every process, `remaining[i]` = burst − (ticks it has run so far),
> and `time` = total ticks elapsed = ticks run by all processes + idle ticks.*

It holds initially (nothing has run, time = 0) and each branch preserves it
(one tick is added either to some process's progress or to the elapsed
total). When the loop exits, `complete == n` means every `remaining` hit 0,
so every process received exactly its burst — the schedule is *valid*.
Checking loop invariants like this is how you reason about simulation code
without running it.

**Termination:** every non-idle tick strictly decreases the sum of all
`remaining` values, and idle ticks strictly increase `time` towards the
next arrival — so with all bursts ≥ 1 (validated!), the loop must end.
Remove the burst ≥ 1 check and termination breaks: that's Bug 1 below.

---

## 5. From ticks to a Gantt chart

The loop appends one entry per tick to `timeline` (`idx`, or `None` for
idle). `_merge_timeline` then compresses consecutive duplicates:

```text
timeline:  [0, 0, 1, None, None, 2]      (per-tick winners)
segments:  P1: 0–2 · P2: 2–3 · IDLE: 3–5 · P3: 5–6
```

Merging matters because a *segment boundary* is precisely a context switch
(or a transition to/from idle) — the statistics code counts boundaries
instead of re-deriving them. `_count_context_switches` counts only
process→*different*-process boundaries, so waking from idle isn't charged
as a switch (a definitional choice; the tests pin it down).

---

## 6. Bugs in the original version, and their fixes

The program this repo is based on was correct for well-behaved input — but
"well-behaved" was doing heavy lifting. Three issues, in increasing
seriousness:

### Bug 1 — Burst time 0 ⇒ infinite loop *(fixed: burst must be ≥ 1)*

The original accepted `burst = 0` (its validator allowed 0 everywhere).
Such a process starts with `remaining = 0`, so the picker never selects it
(it requires `remaining > 0`... and in the original, a 0-remaining process
could also never be *marked* complete, since completion was only detected
after running a tick). Either way `complete` never reaches `n` and the
`while` loop spins forever. **Fix:** `get_positive_int` for bursts +
`_validate_processes` raising on `burst < 1`.

### Bug 2 — Zero processes ⇒ crash *(fixed: count must be ≥ 1)*

With `n = 0`, the original computed `sum(waiting) / n` → `ZeroDivisionError`
after printing an empty table. **Fix:** the count prompt uses
`get_positive_int`, and `srtf([])` raises a clear `ValueError`.

### Issue 3 — Misleading name *(fixed: two honest helpers)*

`get_positive_int` documented itself as validating a "non-negative integer"
and accepted 0. Not a crash by itself — but the mismatch is what let Bugs 1
and 2 slip in: readers (and the original author) reasonably assumed
"positive" excluded 0. Names are part of correctness.

Other improvements, for clarity rather than correctness: the Gantt chart,
idle/utilisation/context-switch statistics, `--demo` mode, separation of
algorithm from I/O, and a `main()` guarded by
`if __name__ == "__main__":` so the file can be imported by tests.

For reference, the changes at a glance:

| Area | Original | This version |
|------|----------|--------------|
| Burst / count input | 0 accepted → hang or crash | ≥ 1 enforced, with clear errors |
| Return value | 4 parallel lists | `SchedulingResult` dataclass (+ Gantt, stats) |
| Schedule selection | inline in loop | `_pick_next()`, unit-testable, tie-break documented |
| Visualisation | table only | table + Gantt chart + utilisation/switches |
| Entry points | top-level script | `main()`, `--demo`, importable `srtf()` |
| Tests | none | 18 hand-computed tests |

---

## 7. What we'd still change with more space

- A `Process` dataclass instead of raw tuples (readability, at the cost of
  more machinery for beginners).
- Event-driven simulation (jump the clock to the next arrival/finish
  instead of stepping every tick) — much faster; see
  [doc 06](06-complexity-limitations-next-steps.md).
- A priority queue for the ready set instead of a linear scan.

Each is a refactoring exercise: the tests in `tests/` should pass
unchanged, which is exactly what tests are for.

---

## Check your understanding

1. Why must the `idx == -1` check happen *before* `remaining[idx]` is ever
   touched? *(Python negative indexing — `remaining[-1]` is the last
   element and would silently corrupt the simulation.)*
2. Which single character, changed in `_pick_next`, reverses tie-breaking?
   *(`<` → `<=`.)*
3. The response-time code runs *before* `remaining[idx] -= 1`. Would moving
   it after the decrement change anything? *(No for the recorded value —
   it depends only on `time`, which hasn't advanced yet either way — but
   placing it before makes "first tick about to run" read naturally.)*
4. Can `complete` ever *exceed* `n`? *(No: a process is counted only when
   its remaining hits 0, which happens once per process because the picker
   excludes `remaining == 0` afterwards.)*

Next: [04 · Worked Example →](04-worked-example.md)
