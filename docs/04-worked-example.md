# 04 · Worked Example — Tracing the Classic Problem by Hand

*Previous: [03 · Code Walkthrough](03-code-walkthrough.md) ·
Next: [05 · Metrics & Formulas](05-metrics-formulas.md)*

The best way to learn a scheduling algorithm is to **be** the scheduler:
simulate it with pencil and paper, then let the program check you. This
document does exactly that for the classic textbook example (the one
`python srtf.py --demo` runs).

---

## The problem

| Process | Arrival | Burst |
|---------|---------|-------|
| P1 | 0 | 8 |
| P2 | 1 | 4 |
| P3 | 2 | 9 |
| P4 | 3 | 5 |

Total work: 8 + 4 + 9 + 5 = **26 ticks**. If the CPU never idles, the last
process finishes at t=26. Keep that in mind as a sanity check.

## How to trace

Keep a table of *remaining times*. At each decision point, list the ready
processes (arrived, unfinished), pick the smallest remaining, and run it
until either it finishes or a new arrival forces a re-check. (In the
tick-by-tick simulator a re-check happens every tick, but nothing can
change *between* arrivals, so hand traces only need the arrival and finish
instants. Convince yourself of that — it's why hand tracing is feasible.)

---

## The trace

**t = 0 — P1 arrives.** Ready: {P1 (8)}. Nothing to choose.
→ P1 runs. At t=1 it will have 7 left.

**t = 1 — P2 arrives (burst 4).** Ready: P1 (7), P2 (4). 4 < 7 →
**P2 preempts P1.** ⭐ *This is the defining SRTF moment: P1 did nothing
wrong; a shorter job simply showed up.*
P2 runs. Next arrival is P3 at t=2, so re-check then.

**t = 2 — P3 arrives (burst 9).** Ready: P1 (7), P2 (3, it ran 1 tick),
P3 (9). Smallest is still P2 → no preemption. Arrivals alone don't cause
switches; being *shorter* does.
P2 continues. Next arrival: P4 at t=3.

**t = 3 — P4 arrives (burst 5).** Ready: P1 (7), P2 (2), P3 (9), P4 (5).
P2 still smallest → P2 continues, and with no arrivals left, it runs to
completion.

**t = 5 — P2 finishes** (it ran 1–5, four ticks ✓). Ready: P1 (7), P3 (9),
P4 (5). Smallest: **P4**. → P4 runs to completion (nobody new can arrive).

**t = 10 — P4 finishes** (5 ticks, 5–10 ✓). Ready: P1 (7), P3 (9).
Smallest: **P1** — the original process finally resumes, still needing 7
of its 8 ticks.

**t = 17 — P1 finishes** (1 tick before preemption + 7 now = 8 ✓).
Ready: P3 (9) alone.

**t = 26 — P3 finishes** (9 ticks, 17–26 ✓). All done — and 26 matches the
total-work prediction, confirming zero idle time.

### Tick-level summary

| Interval | Running | Remaining after the interval: P1 · P2 · P3 · P4 | Event at the end |
|----------|---------|--------------------------------------------------|------------------|
| 0–1 | P1 | 7 · – · – · – | P2 arrives, preempts |
| 1–5 | P2 | 7 · **0** · 9 · 5 | P2 finishes |
| 5–10 | P4 | 7 · – · 9 · **0** | P4 finishes |
| 10–17 | P1 | **0** · – · 9 · – | P1 finishes |
| 17–26 | P3 | – · – · **0** · – | P3 finishes |

### The Gantt chart

```text
| P1 (0–1) | P2 (1–5) | P4 (5–10) | P1 (10–17) | P3 (17–26) |
0          1          5           10            17            26
```

*(Dashes mark processes not yet arrived or already finished in a column.
Remaining values are shown at decision instants.)*

---

## Computing the metrics by hand

Formulas (derived properly in [doc 05](05-metrics-formulas.md)):

```text
turnaround = finish − arrival
waiting    = turnaround − burst
response   = first time the process ran − arrival
```

| Process | Arrival | Burst | Finish | Turnaround = F−A | Waiting = T−B | First ran | Response |
|---------|---------|-------|--------|------------------|---------------|-----------|----------|
| P1 | 0 | 8 | 17 | 17 | **9** | 0 | 0 |
| P2 | 1 | 4 | 5 | 4 | **0** | 1 | 0 |
| P3 | 2 | 9 | 26 | 24 | **15** | 17 | 15 |
| P4 | 3 | 5 | 10 | 7 | **2** | 5 | 2 |

**Averages:**

```text
Average waiting    = (9 + 0 + 15 + 2) / 4  = 26/4 = 6.50
Average turnaround = (17 + 4 + 24 + 7) / 4 = 52/4 = 13.00
Average response   = (0 + 0 + 15 + 2) / 4  = 17/4 = 4.25
```

**Cross-checks** (always do these — they catch most hand errors):

- ✔ Last finish (26) = total burst (26) ⇒ no idle time.
- ✔ Every process's segments on the Gantt chart sum to its burst:
  P1 = 1 + 7 = 8 ✓, P2 = 4 ✓, P4 = 5 ✓, P3 = 9 ✓.
- ✔ Waiting = ticks a process was ready but not running. P3 arrived at 2
  and first ran at 17 = 15 ticks of pure waiting, and it was never
  preempted afterwards, so waiting = response = 15 ✓. (Whenever a process
  runs to completion without preemption after its first tick,
  waiting = response + 0 further waits... in general waiting ≥ response,
  with equality iff the process is never preempted *after first running* —
  check P1: response 0 but waiting 9, because it was preempted for 9 ticks.)
- ✔ Context switches: P1→P2, P2→P4, P4→P1, P1→P3 = 4.

## Now let the program check you

```bash
python srtf.py --demo
```

Its output table matches the hand computation cell-for-cell
(and `tests/test_srtf.py::TestClassicExample` pins these numbers down so
the program can never silently drift away from this document).

## Two "what if" questions to test your feel for SRTF

1. **What if P3 arrived at t=2 with burst 3 instead of 9?**
   At t=2, ready remaining times are P1 (7), P2 (3), P3 (3) — a tie between
   P2 and P3, broken for P2 (lower index). P2 runs one tick → 2 left, now
   strictly smallest, finishes at 5. Then P3 (3) beats P4 (5) and P1 (7):
   P3 5–8, P4 8–13, P1 13–20. New average waiting:
   P1: 20−0−8=12, P2: 0, P3: 8−2−3=3, P4: 13−3−5=5 → (12+0+3+5)/4 = 5.00.
   *Verify: change `DEMO_PROCESSES` — or run the interactive mode.*
2. **What if all four processes arrived at t=0?**
   No arrivals remain after t=0, so no preemption can ever be triggered:
   SRTF degenerates to SJF — P2 (4) 0–4, P4 (5) 4–9, P1 (8) 9–17,
   P3 (9) 17–26. Average waiting = (9 + 0 + 17 + 4)/4 = 7.50 — *worse* than
   6.50, because arrivals staggered in time gave SRTF chances to reorder.
   Interesting: the same bursts, a different arrival pattern, a different
   optimum value. (The optimum *claim* still holds — it's optimal among
   schedules for *that* arrival pattern.)

Next: [05 · Metrics & Formulas →](05-metrics-formulas.md)
