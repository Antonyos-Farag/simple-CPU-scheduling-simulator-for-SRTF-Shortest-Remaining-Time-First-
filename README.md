# SRTF CPU Scheduling Simulator — An Educational Guide

> **Shortest Remaining Time First (SRTF)** is the preemptive version of
> Shortest Job First. At every moment, the CPU runs the ready process that
> needs the *least time to finish* — and a newly arrived shorter process
> immediately takes the CPU away from whoever is running.
>
> This repository teaches you SRTF from zero: what CPU scheduling is, how
> the algorithm thinks, how every line of the simulator works, and how to
> prove (by hand) that its output is correct.

Pure Python, no dependencies. Python 3.8+ is all you need.

---

## Table of contents

- [Quick start](#quick-start)
- [What you will learn](#what-you-will-learn)
- [The 30-second explanation of SRTF](#the-30-second-explanation-of-srtf)
- [A first run](#a-first-run)
- [Learning path](#learning-path)
- [Repository map](#repository-map)
- [Key terms](#key-terms)
- [Running the tests](#running-the-tests)
- [Exercises](#exercises)
- [Limitations & honest caveats](#limitations--honest-caveats)
- [Ideas to extend this project](#ideas-to-extend-this-project)
- [License](#license)

---

## Quick start

```bash
# 1. Run the classic textbook example (nothing to type)
python srtf.py --demo

# 2. Run all six teaching examples
python examples.py

# 3. Enter your own processes interactively
python srtf.py

# 4. Run the test suite
python -m unittest discover -s tests -v
```

In interactive mode you will be asked for the number of processes, then an
**arrival time** (when the process appears, ≥ 0) and a **burst time** (how
much CPU it needs, ≥ 1) for each one. Bad input (letters, negatives, a zero
burst) is rejected with an explanation and you are asked again.

---

## What you will learn

By working through this repo you will be able to:

1. Explain what the operating system's **scheduler** does and why it matters.
2. State the SRTF rule and predict, on paper, which process runs at any time.
3. Distinguish **preemptive** from **non-preemptive** scheduling.
4. Draw a **Gantt chart** for any small set of processes.
5. Compute **waiting**, **turnaround**, and **response** time — and explain
   how they differ.
6. Read a tick-by-tick simulation loop and reason about its correctness.
7. Spot real bugs (including two in the original version of this program!)
   and understand complexity, starvation, and why real operating systems
   don't schedule exactly this way.

---

## The 30-second explanation of SRTF

Imagine a single CPU and several processes competing for it. Each process
announces when it **arrives** and how much CPU time it **needs in total**
(its burst). The SRTF rule is one sentence:

> **Always run the arrived, unfinished process with the smallest
> _remaining_ time. Re-decide at every time unit.**

Because the decision is re-made constantly, SRTF is **preemptive**: if a new
process arrives needing 1 unit while the running process still needs 7, the
newcomer takes the CPU immediately. The interrupted process keeps its
progress — "remaining time" is burst minus what it has already received.

Two consequences follow, and the whole repo explores them:

- **Short jobs finish fast.** SRTF provably minimises average waiting time
  (for processes whose bursts are known in advance).
- **Long jobs can starve.** A steady stream of short jobs can postpone a
  long job again and again.

---

## A first run

```text
$ python srtf.py --demo

=== SRTF (Shortest Remaining Time First) Scheduling ===

Demo processes (arrival, burst):
  P1: arrival=0, burst=8
  P2: arrival=1, burst=4
  P3: arrival=2, burst=9
  P4: arrival=3, burst=5

Gantt Chart:
  | P1 (0-1) | P2 (1-5) | P4 (5-10) | P1 (10-17) | P3 (17-26) |

===================== RESULTS =====================
Process | Arrival | Burst | Finish | Waiting | Turnaround | Response
---------------------------------------------------------------
P1       |       0 |     8 |     17 |       9 |         17 |        0
P2       |       1 |     4 |      5 |       0 |          4 |        0
P3       |       2 |     9 |     26 |      15 |         24 |       15
P4       |       3 |     5 |     10 |       2 |          7 |        2

Average Waiting Time:     6.50
Average Turnaround Time:  13.00
Average Response Time:    4.25

Total time (makespan):    26
CPU idle time:            0
CPU utilization:          100.0%
Context switches:         4
```

Reading the Gantt chart: **P1** starts at t=0, but at t=1 **P2** arrives
needing only 4 units (P1 still needs 7), so P2 *preempts* it. P2 runs to
completion, then P4 (5 left) beats P1 (7 left) and P3 (9 left), and so on.
Don't worry if the table columns are mysterious for now —
[docs/04-worked-example.md](docs/04-worked-example.md) traces every single
tick of this exact example by hand, and
[docs/05-metrics-formulas.md](docs/05-metrics-formulas.md) defines every
column.

---

## Learning path

Read in order — each document builds on the previous one. Total reading
time is roughly 45–60 minutes, exercises excluded.

| # | Document | What it covers |
|---|----------|----------------|
| 1 | [CPU scheduling basics](docs/01-cpu-scheduling-basics.md) | Processes, the ready queue, preemption, and where SRTF sits among FCFS / SJF / Round Robin / Priority scheduling |
| 2 | [SRTF explained](docs/02-srtf-explained.md) | The rule, why it's optimal, tie-breaking, idle time, starvation |
| 3 | [Code walkthrough](docs/03-code-walkthrough.md) | Every part of `srtf.py`, line by line — plus the bugs fixed from the original version |
| 4 | [Worked example](docs/04-worked-example.md) | The classic 4-process example traced tick by tick with all metrics computed by hand |
| 5 | [Metrics & formulas](docs/05-metrics-formulas.md) | Waiting vs turnaround vs response, averages, utilisation, common calculation mistakes |
| 6 | [Complexity, limitations & next steps](docs/06-complexity-limitations-next-steps.md) | Why the simulation is O(T·n), why real OSes can't use pure SRTF, and how to make it faster/fairer |
| — | [Exercises](exercises/exercises.md) · [Solutions](exercises/solutions.md) | Practice problems (predict → run → compare) with fully worked answers |

**The golden rule of this repo:** always predict the Gantt chart on paper
*first*, then run the program to check yourself. Reading output you already
expected teaches you ten times more than reading output that surprises you.

---

## Repository map

```text
.
├── README.md                  <- you are here
├── srtf.py                    <- the simulator (well-commented, start here in code)
├── examples.py                <- six preset teaching examples:  python examples.py
├── docs/
│   ├── 01-cpu-scheduling-basics.md
│   ├── 02-srtf-explained.md
│   ├── 03-code-walkthrough.md
│   ├── 04-worked-example.md
│   ├── 05-metrics-formulas.md
│   └── 06-complexity-limitations-next-steps.md
├── exercises/
│   ├── exercises.md           <- try these before opening solutions
│   └── solutions.md
└── tests/
    └── test_srtf.py           <- hand-computed expectations; doubles as examples
```

Design choices, made deliberately for learners:

- **Standard library only.** Nothing to install, nothing between you and the algorithm.
- **One tick at a time.** The simulator advances the clock by a single unit
  and re-decides, exactly like the definition of the algorithm. It's not the
  fastest possible implementation — it's the clearest one.
- **The tests are worked examples.** Every expected number in
  `tests/test_srtf.py` is derived in a comment, so a failing test teaches
  you something either way.

---

## Key terms

| Term | One-line meaning |
|------|------------------|
| **Arrival time** | When a process enters the system and becomes eligible to run |
| **Burst time** | Total CPU time a process needs to complete |
| **Remaining time** | Burst time minus CPU time already received |
| **Ready queue** | Processes that have arrived but are waiting for the CPU |
| **Preemption** | Forcibly taking the CPU from a running process to give it to another |
| **Gantt chart** | A timeline diagram showing who held the CPU during each interval |
| **Finish (completion) time** | The clock value when a process receives its last unit of CPU |
| **Waiting time** | Time spent ready-but-not-running (see [docs/05](docs/05-metrics-formulas.md)) |
| **Context switch** | The act of stopping one process and starting a different one |

Full definitions with examples: [docs/01](docs/01-cpu-scheduling-basics.md)
and [docs/05](docs/05-metrics-formulas.md).

---

## Running the tests

```bash
python -m unittest discover -s tests -v
```

18 tests cover the classic example, preemption, idle CPU time, ties,
input validation, and invariants that must hold for *any* input (e.g. the
Gantt chart's busy ticks always add up to the total burst time).

---

## Exercises

Eight exercises live in [exercises/exercises.md](exercises/exercises.md):
predicting Gantt charts, hand-computing metrics, comparing SRTF with FCFS,
hunting a bug, and modifying the code. Worked answers are in
[exercises/solutions.md](exercises/solutions.md) — try first, peek later.

---

## Limitations & honest caveats

This is a *teaching* simulator, and it's important to know where the model
stops matching reality:

- **It assumes burst times are known in advance.** Real operating systems
  don't know the future; they estimate. SRTF is therefore a theoretical
  benchmark more than a deployable scheduler.
- **Time is discrete.** Real preemption happens on timer interrupts and
  context switches themselves cost time; both are ignored here.
- **Long processes can starve** under a stream of short arrivals — the
  simulator will happily demonstrate this (Example 6 in `examples.py`).
- **One CPU, no I/O.** Processes never block waiting for disk or keyboard.

Details and discussion: [docs/06-complexity-limitations-next-steps.md](docs/06-complexity-limitations-next-steps.md).

---

## Ideas to extend this project

In roughly increasing difficulty — each makes a great follow-up project:

1. Print a per-tick trace table (time, ready processes, decision) like the
   one in [docs/04](docs/04-worked-example.md).
2. Add **FCFS** and non-preemptive **SJF** modes and compare average waiting
   times on the same input.
3. Add **Round Robin** with a configurable time quantum.
4. Add **aging** to SRTF so long-waiting processes gradually gain priority —
   measure how it fights starvation.
5. Replace the linear scan in `_pick_next` with a heap and benchmark the
   difference (analysis in [docs/06](docs/06-complexity-limitations-next-steps.md)).
6. Plot the Gantt chart with `matplotlib`, or make a tiny web front-end.

---

## License

Released under the MIT License — free to use, copy, and modify, including
for teaching. See [LICENSE](LICENSE).
