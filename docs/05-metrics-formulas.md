# 05 · Metrics & Formulas

*Previous: [04 · Worked Example](04-worked-example.md) ·
Next: [06 · Complexity, Limitations & Next Steps](06-complexity-limitations-next-steps.md)*

Every number the simulator prints is defined here, with the reasoning
behind each formula — because in scheduling, most confusion is not about
the algorithm but about what exactly is being measured.

---

## 1. The timeline of one process

Every process lives through the same four instants:

```text
arrival ────────► first run ────────► (maybe preempted & resumed…) ────────► finish
   │                  │                                                        │
   │◄── response ────►│                                                        │
   │◄──────────────────────── turnaround ────────────────────────────────────►│
   │◄── waiting = all the time inside turnaround NOT spent running ──────────►│
```

| Instant / interval | Definition |
|--------------------|------------|
| **Arrival time** `A` | When the process enters the system (given as input) |
| **Burst time** `B` | Total CPU time the process needs (given as input) |
| **First-run time** | The clock value at which the process first receives the CPU |
| **Finish time** `F` | The clock value at which the process receives its *last* tick |

Note the convention used throughout this repo (and most textbooks): a tick
that runs "during [4, 5)" *ends* at t=5, so a process whose last tick is
[4, 5) has finish time **5**. Time is measured at tick boundaries, and
intervals are start-inclusive / end-exclusive — the same convention as
Python slices, and for the same reason: adjacent intervals then share
endpoints without overlapping or leaving gaps.

## 2. The three per-process metrics

### Turnaround time — "how long was it in the system?"

```text
turnaround = finish − arrival          (T = F − A)
```

This is the total wall-clock time from the process's point of view:
waiting *plus* running. Users experience turnaround — it's "I submitted
the job at 2 and got the result at 17".

### Waiting time — "how long did it sit doing nothing?"

```text
waiting = turnaround − burst           (W = T − B = F − A − B)
```

Inside the turnaround interval, the process spends exactly `B` units
running (that's the definition of burst). Everything else it spent in the
ready queue. Hence waiting needs no separate bookkeeping: subtract what it
*must* have spent running from the total, and the remainder is what it
spent waiting. This is why the simulator computes waiting in one line at
the moment a process finishes — during the simulation, a half-finished
process's waiting time is still growing and isn't final yet.

An equivalent tick-level view, useful for checking by hand on a Gantt
chart: **waiting = number of ticks in [arrival, finish) during which the
process was not running.**

### Response time — "how long until it first reacted?"

```text
response = first-run time − arrival
```

Response measures *initial* delay only. A process preempted ten times after
a quick start still has a small response time; a process that runs
uninterrupted but only after a long wait has a large one. This is why
interactive systems (terminals, games, GUIs) obsess over response time: a
program that reacts instantly and finishes slowly *feels* faster than one
that ignores you and then finishes at the same moment.

### How the three relate

For any process:

```text
0 ≤ response ≤ waiting            (your first wait is part of your total wait)
waiting = turnaround − burst  ⇒    turnaround = waiting + burst
response = waiting   ⇔   the process was never preempted after first running
```

The simulator's tests assert the first two identities for every test case
(`TestInvariants`) — they're excellent hand-checks too.

## 3. Averages

Each headline number is the plain arithmetic mean over all `n` processes:

```text
average waiting    = (W₁ + W₂ + … + Wₙ) / n
average turnaround = (T₁ + T₂ + … + Tₙ) / n
average response   = (R₁ + R₂ + … + Rₙ) / n
```

Two things averages hide, both worth remembering:

1. **Distribution.** `examples.py` Example 6 has an *average* waiting time
   of 1.67 — while P1 personally waits 10. Whenever a result matters,
   look at the maximum as well as the mean.
2. **A shortcut:** since total burst is constant for a given input,
   `average turnaround = average waiting + average burst`. Check with
   [doc 04](04-worked-example.md): 6.50 + 26/4 = 6.50 + 6.50 = 13.00 ✓.
   Optimising one therefore optimises the other — that's why SRTF's
   optimality claim covers both.

## 4. Whole-run statistics

| Statistic | Definition | Notes |
|-----------|------------|-------|
| **Makespan** (total time) | Clock value when the last process finishes | Equals the final `time` in the simulation |
| **Idle time** | Ticks with an empty ready queue | Unavoidable if the first arrival is late |
| **CPU utilisation** | `(makespan − idle) / makespan × 100%` | 100% ⇔ the CPU never lacked work |
| **Context switches** | Boundaries where the CPU passes directly from one process to a *different* one | This repo's definition: starting the first process and resuming after idle don't count. (Definitions vary — always state yours.) |
| **Throughput** | `n / makespan` processes per unit time | Not printed; easy to derive |

## 5. A complete micro-example

One process, `P1` arrives at 3, burst 4 (`srtf([(3, 4)])`):

```text
| IDLE (0–3) | P1 (3–7) |
```

- Finish = 7, turnaround = 7 − 3 = 4, waiting = 4 − 4 = **0** — waiting
  counts only time spent *ready*, and P1 ran the instant it arrived. The 3
  idle ticks happened **before P1 existed**; they hurt utilisation
  (4/7 ≈ 57.1%) but are not charged to P1 as waiting. Mixing those two up
  is the most common beginner mistake with these formulas.
- Response = 3 − 3 = 0. Makespan 7, idle 3, switches 0.

## 6. Common mistakes checklist

- ❌ *"Waiting = finish − burst."* Forgot the arrival. Use `F − A − B`.
- ❌ *"Turnaround includes waiting before arrival."* Nothing exists before
  arrival; turnaround starts *at* arrival.
- ❌ *"Response and waiting are the same thing."* Only if the process is
  never preempted after starting (see P1 in doc 04: response 0, waiting 9).
- ❌ *"A finish time of 5 means it ran until 'during' 5."* End-exclusive:
  its last tick was [4, 5).
- ❌ *"Idle time before my process arrived counts as its waiting."*
  See §5 above.
- ❌ *Comparing averages across different inputs.* Averages are only
  comparable for the *same* process set with the *same* arrival pattern —
  doc 04's what-if #2 shows why.
- ❌ *Assuming the printed average tells the whole story.* See §3 — always
  glance at the worst-off process too.

## 7. Self-test

For `P1(0, 10), P2(1, 4), P3(3, 1)` — trace it yourself first! Then check:
the Gantt chart is `P1 (0–1) | P2 (1–3) | P3 (3–4) | P2 (4–6) | P1 (6–15)`,
giving finishes 15, 6, 4; waiting 5, 1, 0; responses 0, 0, 0; average
waiting 2.00. The interesting process is P2: its response is 0 (it ran the
instant it arrived) yet its waiting is 1, because tiny P3 preempted it at
t=3 and it sat ready — but not running — from 3 to 4. That single tick is
exactly the difference between the response and waiting formulas.

Next: [06 · Complexity, Limitations & Next Steps →](06-complexity-limitations-next-steps.md)
