# Solutions

Fully worked answers. If your numbers differ, the most likely causes are
(in order): a tie broken the other way, an arrival applied one tick early
or late, or waiting confused with response — see
[doc 05](../docs/05-metrics-formulas.md) §6.

---

## Exercise 1 — Predict the Gantt chart

`P1(0, 5)`, `P2(1, 3)`, `P3(2, 1)`.

- **t=0:** only P1 exists → P1 runs (5→4 by t=1).
- **t=1:** P2 arrives (3) vs P1 (4) → **P2 preempts** (3→2 by t=2).
- **t=2:** P3 arrives (1) vs P2 (2), P1 (4) → **P3 preempts**; P3 finishes
  at t=3.
- **t=3:** P2 (2) vs P1 (4) → P2 resumes, finishes at t=5.
- **t=5:** only P1 (4) remains → runs 5–9.

```text
| P1 (0–1) | P2 (1–2) | P3 (2–3) | P2 (3–5) | P1 (5–9) |
```

| Process | Finish | Turnaround | Waiting | Response |
|---------|--------|------------|---------|----------|
| P1 | 9 | 9 − 0 = 9 | 9 − 5 = **4** | 0 |
| P2 | 5 | 5 − 1 = 4 | 4 − 3 = **1** | 0 |
| P3 | 3 | 3 − 2 = 1 | 1 − 1 = **0** | 0 |

Averages: waiting (4+1+0)/3 ≈ **1.67**, turnaround (9+4+1)/3 ≈ **4.67**,
response **0.00**. Context switches: P1→P2, P2→P3, P3→P2, P2→P1 = **4**.
Note every response is 0 — each process ran in the very tick it arrived —
yet P1 still waited 4 ticks in total (1–5, while others ran). Response
measures only the *first* wait.

## Exercise 2 — Idle time and utilisation

`P1(4, 2)`, `P2(0, 1)`, `P3(6, 2)`.

```text
| P2 (0–1) | IDLE (1–4) | P1 (4–6) | P3 (6–8) |
```

Every process runs the instant it arrives, so **all waiting times are 0**
— including P1's, even though the CPU sat idle from 1 to 4: those ticks
precede P1's existence and belong to *idle time*, not to P1's waiting.
Makespan **8**, idle **3**, utilisation (8−3)/8 = **62.5%**.

## Exercise 3 — The tie that isn't

`P1(0, 4)`, `P2(2, 2)`, `P3(3, 3)`.

1. **No preemption at t=2.** P1's remaining (4 − 2 = 2) *equals* P2's
   burst (2). Preemption needs a strictly smaller remaining time, and the
   scan's strict `<` also keeps the incumbent champion (P1, lower index).
   Next tick P1 drops to 1 and is strictly ahead anyway.
2. P1 runs 0–4 and finishes. At t=4: P2 (2) vs P3 (3) → P2 runs 4–6, then
   P3 runs 6–9.

   ```text
   | P1 (0–4) | P2 (4–6) | P3 (6–9) |
   ```

   Waiting: P1 = **0**, P2 = (6−2) − 2 = **2**, P3 = (9−3) − 3 = **3**.
   Average = 5/3 ≈ 1.67.
3. **Yes.** With newest-wins ties, P2 would take over at t=2, finish at 4;
   P1 (remaining 2) would then beat P3 (3), finish at 6; P3: 6–9.
   Gantt: `P1 (0–2) | P2 (2–4) | P1 (4–6) | P3 (6–9)`, waiting becomes
   P1 = 2, P2 = 0, P3 = 3 — same *average* here (coincidence of this
   input), different per-process results and one extra context switch.
   Moral: tie-breaking is a real policy choice with observable effects,
   exactly as [doc 02](../docs/02-srtf-explained.md) §4 warns.

## Exercise 4 — SRTF vs FCFS

FCFS runs processes to completion in arrival order:

```text
| P1 (0–8) | P2 (8–12) | P3 (12–21) | P4 (21–26) |
```

Waiting: P1 = 0; P2 = 8−1 = 7; P3 = 12−2 = 10; P4 = 21−3 = 18.
Average = 35/4 = **8.75** (vs SRTF 6.50).

Who gains under SRTF? **P2** (7→0), **P4** (18→2), and overall everyone
except **P3**, which *loses* badly (10→15): SRTF sacrifices the long job
to speed up three others — the optimality/starvation trade-off in one
table. The 2.25 difference is bought by preempting P1 at t=1, which no
non-preemptive algorithm can do, and by letting P4 jump ahead of P3.

FCFS could still win in a real system when **context switches are
expensive** relative to job lengths (or when fairness/starvation-freedom
matters more than mean waiting): FCFS here switches 3 times, SRTF 4, and
in switch-heavy workloads the gap widens fast.

## Exercise 5 — Response ≠ waiting

`P1(0, 10)`, `P2(1, 4)`, `P3(3, 1)`:

```text
| P1 (0–1) | P2 (1–3) | P3 (3–4) | P2 (4–6) | P1 (6–15) |
```

**P2**: response 0 (ran at t=1, the tick it arrived), waiting 1 — the
extra tick came from being **preempted by P3 at t=3** and sitting ready
from 3 to 4. **General rule:** response = waiting exactly when the process
runs *continuously* from its first tick to completion (never preempted
after starting). Any later preemption adds waiting that response cannot
see.

## Exercise 6 — Starvation, constructed by you

One valid answer (there are many): `P1(0, 12)` plus short jobs
`P2(1, 2)`, `P3(3, 2)`, `P4(5, 2)`, `P5(7, 2)` — this is Example 6 of
`examples.py` with one short job fewer:

```text
| P1 (0–1) | P2 (1–3) | P3 (3–5) | P4 (5–7) | P5 (7–9) | P1 (9–20) |
```

P1 waits 8 ticks (1–9; its waiting time is 20−0−12 = 8); every short job
runs on arrival and waits 0. Check your own construction against the two
conditions: victim's waiting ≥ 8 *and* all others exactly 0.

Why it grows without bound: each short job needs only to arrive *before
the victim becomes the minimum* — and since the victim's remaining time
never decreases while it waits, a new short job every ≤ 2 ticks always
wins. The victim's wait is bounded only by the length of the short-job
stream, which can be infinite.

Prevention: **aging** — e.g. treat a process's effective remaining time as
`remaining − waited/k`, so sufficiently patient processes eventually win
regardless of size. Downside (any correct one): average waiting time
rises (you've deliberately deviated from the optimal rule), and a poorly
chosen aging rate can cause *thrashing* between two long processes or let
long jobs bully short ones — fairness/performance is a dial, not a switch.

## Exercise 7 — Bug hunt

The student's condition is
`remaining[i] <= shortest` — two changes from
`0 < remaining[i] < shortest`, each with its own failure:

**Bug A — dropped `0 <` (finished processes can "win").**
A finished process has `remaining == 0`, which is ≤ everything. Input:
`[(0, 1), (0, 5)]`. P1 finishes at t=1, but from then on P1 (remaining 0)
keeps being selected, `remaining` goes negative forever, P1 is re-marked
"finished" every tick... depending on the surrounding code the loop either
never terminates or corrupts every metric. (In `srtf.py`'s structure:
the picker happily returns the dead P1, whose remaining becomes −1, −2, …
so `remaining[idx] == 0` never fires again and `complete` stalls —
infinite loop.) This is the sneakiest class of bug: every *individual*
line looks plausible.

**Bug B — `<` became `<=` (tie-break reversed, plus worse).**
On ties the *last* process scanned now wins instead of the first: the
tie policy silently flips to highest-index-wins (see Exercise 3 for
observable effects: extra switches, different per-process waiting).
Worse, combined with Bug A, `<=` also admits a 0-remaining process even
when another unfinished process also has remaining 0...0 — the two bugs
compound, which is typical of real debugging: symptoms appear far from
causes.

Neither bug crashes on the classic demo input for Bug B alone — it just
produces a *different valid-looking schedule*. That's why the test suite
pins exact Gantt charts, not just averages.

## Exercise 8 — Change the policy (code)

1. `remaining[i] < shortest` → `remaining[i] <= shortest` makes the last
   minimal process win. For `[(0, 3), (0, 3)]`: at t=0, P2 (later index)
   wins the tie; thereafter P2's remaining is strictly smallest each tick
   so it runs to completion: `P2 (0–3) | P1 (3–6)` — the exact mirror of
   the original chart, waiting swapped between the processes. (Run
   `python examples.py` and look at Example 5.)
2. SJF: only allow the running process to change when the CPU would
   otherwise be free — i.e. call `_pick_next` **only when the current
   process has finished (or none is running)**, and keep running the
   current one otherwise. Equivalently: make the decision at
   arrival/finish *events of the running process only*, never letting a
   mere arrival displace it. In the tick loop: remember `current`; only
   re-pick when `current is None or remaining[current] == 0`.
3. Expected failures: `TestPreemption` (a short newcomer no longer
   preempts — P1 would finish at 10, not 11... precisely: with
   `[(0, 10), (2, 1)]`, SJF gives P1 0–10, P2 10–11, so finish times,
   waiting times, and context-switch count all change), the classic
   example's tests (SJF average waiting is 7.75, not 6.50 — P1 runs 0–8),
   and `TestInvariants` should still *pass* (the formulas hold for any
   valid schedule). The lesson: tests encode *policy*, not just
   arithmetic — changing the algorithm *should* fail the tests that were
   written to specify the old policy, and the ones that still pass were
   specifying something deeper (the invariants).

## Exercise 9 — Complexity thinking

1. Last arrival at 900, burst 5 → makespan **905 ticks**. Busy ticks:
   10 × 5 = 50; idle ticks: **855** (nine gaps of 95, plus none before 0 —
   precisely: gaps 5–100, 105–200, …, 805–900 = 9 × 95 = 855). The
   simulator spends ~94% of its iterations advancing the clock through
   empty time, running an O(n) scan each time to rediscover that nobody
   is ready.
2. Event-driven: one decision per arrival and per finish ≈ **20
   decisions** (10 + 10; no preemptions occur since processes never
   overlap... each arrives after the previous finished: arrivals at
   multiples of 100, finishes 5 later). From 905 iterations to ~20 —
   a ~45× reduction on this input, growing with the idle gaps.
3. Tick simulator: **O(T · n)** time (scan per tick), O(T + n) memory.
   Event-driven with a heap: **O(S · log n)** decisions-side, where
   segments `S ≤ arrivals + finishes` here — in general
   `S = O(n + number of preemptions)` and preemptions only happen at
   arrivals, so `S = O(n)` segments worst-case... more carefully:
   each arrival can create at most one extra segment boundary, so
   `S ≤ 2n + (number of arrivals) = O(n)`; with a linear scan instead of
   a heap it'd be O(S · n) = O(n²) — still independent of idle time and
   burst magnitudes, which is the real win.

---

*All answers verified against the simulator. Found a discrepancy between
a solution and the program? Check the tie-break discussion in Exercise 3,
then open an issue — one of them is a bug, and either way it's worth
reporting.*
