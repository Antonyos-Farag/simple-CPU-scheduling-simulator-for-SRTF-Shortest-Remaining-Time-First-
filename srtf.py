"""
SRTF (Shortest Remaining Time First) CPU Scheduling Simulator
==============================================================

An educational, dependency-free simulator for the preemptive
Shortest Remaining Time First scheduling algorithm.

New to the topic? Read the learning material in this order:

    1. docs/01-cpu-scheduling-basics.md
    2. docs/02-srtf-explained.md
    3. docs/03-code-walkthrough.md      <- explains this file, step by step
    4. docs/04-worked-example.md        <- a full hand-traced example

Quick start
-----------
Interactive mode (the program asks you for the processes):

    python srtf.py

Demo mode (runs a classic textbook example, no typing needed):

    python srtf.py --demo

Only the Python standard library is used. Python 3.8+ is required.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
# A process is entered as a plain tuple:  (arrival_time, burst_time)
#
#   * arrival_time -- the time unit at which the process enters the system
#   * burst_time   -- how many time units of CPU the process needs in total
#
# The simulator refers to processes by their position in the list:
# index 0 is shown as "P1", index 1 as "P2", and so on.


@dataclass
class GanttSegment:
    """One continuous block on the Gantt chart.

    A new segment starts whenever the CPU switches to a different
    process (or becomes idle / stops being idle).

    Attributes:
        pid:   Index of the process that ran (0-based), or ``None``
               when the CPU was idle during this segment.
        start: Time unit at which the segment began (inclusive).
        end:   Time unit at which the segment ended (exclusive),
               so ``end - start`` is how long the segment lasted.
    """

    pid: int | None
    start: int
    end: int

    @property
    def duration(self) -> int:
        """How many time units this segment lasted."""
        return self.end - self.start

    @property
    def label(self) -> str:
        """Human-readable name, e.g. ``P2`` or ``IDLE``."""
        return "IDLE" if self.pid is None else f"P{self.pid + 1}"


@dataclass
class SchedulingResult:
    """Everything the simulation learned about one run.

    All per-process lists are in the same order as the input list
    (index 0 == P1, index 1 == P2, ...).

    Attributes:
        waiting:          waiting[i]    = time Pi spent ready but not running
        turnaround:       turnaround[i] = finish[i] - arrival[i]
        response:         response[i]   = (first time Pi ran) - arrival[i]
        finish:           finish[i]     = time at which Pi completed
        gantt:            merged Gantt chart segments, in time order
        total_time:       the final value of the simulation clock
                          (also called the *makespan*)
        idle_time:        time units during which no process was ready
        context_switches: how often the CPU switched directly from one
                          process to a *different* process
    """

    waiting: list[int]
    turnaround: list[int]
    response: list[int]
    finish: list[int]
    gantt: list[GanttSegment] = field(default_factory=list)
    total_time: int = 0
    idle_time: int = 0
    context_switches: int = 0

    @property
    def cpu_utilization(self) -> float:
        """Percentage of the makespan during which the CPU was busy."""
        if self.total_time == 0:
            return 0.0
        busy = self.total_time - self.idle_time
        return busy / self.total_time * 100


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def get_non_negative_int(prompt: str) -> int:
    """Keep asking until the user types an integer >= 0.

    Used for values that may legitimately be zero, such as an
    arrival time (a process may arrive at time 0).
    """
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("  Error: Please enter a valid integer.")
            continue
        if value < 0:
            print("  Error: Value cannot be negative.")
            continue
        return value


def get_positive_int(prompt: str) -> int:
    """Keep asking until the user types an integer >= 1.

    Used for values that must not be zero: the number of processes
    and burst times. A process with a burst time of 0 would need no
    CPU at all, so it could never be "finished" by the simulation
    loop -- the original version of this program looped forever on
    such input. See docs/03-code-walkthrough.md, "Bugs we fixed".
    """
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("  Error: Please enter a valid integer.")
            continue
        if value < 1:
            print("  Error: Value must be at least 1.")
            continue
        return value


# ---------------------------------------------------------------------------
# The SRTF algorithm
# ---------------------------------------------------------------------------

def _validate_processes(processes: list[tuple[int, int]]) -> None:
    """Reject inputs the simulation cannot handle.

    Raises:
        ValueError: if the list is empty, an arrival time is
            negative, or a burst time is smaller than 1.
    """
    if not processes:
        raise ValueError("At least one process is required.")
    for i, (arrival, burst) in enumerate(processes, start=1):
        if arrival < 0:
            raise ValueError(f"P{i}: arrival time cannot be negative ({arrival}).")
        if burst < 1:
            raise ValueError(
                f"P{i}: burst time must be at least 1 ({burst}). "
                "A process needing 0 CPU time can never finish in the simulation."
            )


def _pick_next(processes: list[tuple[int, int]],
               remaining: list[int],
               time: int) -> int:
    """Return the index of the process that should run at ``time``.

    The SRTF rule: among the processes that have *arrived*
    (``arrival <= time``) and still *need CPU time*
    (``remaining > 0``), pick the one with the smallest remaining time.

    Tie-breaking: the strict ``<`` comparison keeps the *first*
    process found with the minimum value, so when two processes have
    equal remaining time the one with the smaller index (P1 before
    P2) wins. This matters -- see docs/02-srtf-explained.md.

    Returns -1 when no process is ready (the CPU must idle).
    """
    idx = -1
    shortest = float("inf")

    for i in range(len(processes)):
        arrival = processes[i][0]
        if arrival <= time and 0 < remaining[i] < shortest:
            shortest = remaining[i]
            idx = i

    return idx


def srtf(processes: list[tuple[int, int]]) -> SchedulingResult:
    """Simulate SRTF scheduling, one time unit ("tick") at a time.

    Args:
        processes: A list of ``(arrival_time, burst_time)`` tuples.

    Returns:
        A :class:`SchedulingResult` with per-process waiting,
        turnaround, response and finish times, plus the Gantt chart.

    Example:
        >>> result = srtf([(0, 8), (1, 4), (2, 9), (3, 5)])
        >>> result.finish
        [17, 5, 26, 10]
        >>> result.waiting
        [9, 0, 15, 2]

    The simulation advances a clock one unit at a time. On every
    tick it re-applies the SRTF rule from scratch -- this is what
    makes SRTF *preemptive*: a newly arrived shorter process is
    picked on the very next tick, interrupting the running one.
    """
    _validate_processes(processes)
    n = len(processes)

    remaining = [burst for _, burst in processes]  # CPU time each process still needs
    response = [-1] * n   # -1 means "has not run yet" (a sentinel value)
    finish = [0] * n
    waiting = [0] * n
    turnaround = [0] * n

    # One entry per tick: the index of the process that used that
    # tick, or None for an idle tick. Merged into segments afterwards.
    timeline: list[int | None] = []

    complete = 0
    time = 0

    while complete != n:
        idx = _pick_next(processes, remaining, time)

        # --- Case 1: nobody has arrived yet -> the CPU idles. ---
        if idx == -1:
            timeline.append(None)
            time += 1
            continue

        # --- Case 2: run the chosen process for exactly 1 tick. ---

        # Response time is recorded only on the *first* tick a
        # process ever runs; the -1 sentinel tells us this is it.
        if response[idx] == -1:
            response[idx] = time - processes[idx][0]

        timeline.append(idx)
        remaining[idx] -= 1
        time += 1

        # Did that tick finish the process?
        if remaining[idx] == 0:
            complete += 1
            finish[idx] = time
            # The two key formulas (see docs/05-metrics-formulas.md):
            turnaround[idx] = finish[idx] - processes[idx][0]
            waiting[idx] = turnaround[idx] - processes[idx][1]

    gantt = _merge_timeline(timeline)

    return SchedulingResult(
        waiting=waiting,
        turnaround=turnaround,
        response=response,
        finish=finish,
        gantt=gantt,
        total_time=time,
        idle_time=sum(seg.duration for seg in gantt if seg.pid is None),
        context_switches=_count_context_switches(gantt),
    )


def _merge_timeline(timeline: list[int | None]) -> list[GanttSegment]:
    """Merge a per-tick timeline into continuous Gantt segments.

    Example: ``[0, 0, 1, None, None]`` becomes
    ``P1: 0-2, P2: 2-3, IDLE: 3-5``.
    """
    segments: list[GanttSegment] = []
    for tick, pid in enumerate(timeline):
        if segments and segments[-1].pid == pid:
            segments[-1].end = tick + 1  # extend the current block
        else:
            segments.append(GanttSegment(pid=pid, start=tick, end=tick + 1))
    return segments


def _count_context_switches(gantt: list[GanttSegment]) -> int:
    """Count direct switches from one process to a different process.

    Starting the first process, resuming after an idle period, etc.
    are not counted -- only P_i -> P_j (i != j) transitions are.
    """
    switches = 0
    previous_pid: int | None = None
    for segment in gantt:
        if segment.pid is None:
            previous_pid = None
            continue
        if previous_pid is not None and previous_pid != segment.pid:
            switches += 1
        previous_pid = segment.pid
    return switches


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def print_gantt_chart(result: SchedulingResult) -> None:
    """Print the Gantt chart: who held the CPU, and when."""
    print("\nGantt Chart:")
    blocks = " | ".join(
        f"{seg.label} ({seg.start}-{seg.end})" for seg in result.gantt
    )
    print(f"  | {blocks} |")


def print_results(processes: list[tuple[int, int]],
                  result: SchedulingResult) -> None:
    """Print the per-process table and the average metrics."""
    n = len(processes)

    print("\n===================== RESULTS =====================")
    print("Process | Arrival | Burst | Finish | Waiting | Turnaround | Response")
    print("---------------------------------------------------------------")
    for i in range(n):
        print(
            f"P{i + 1:<7} | {processes[i][0]:7} | {processes[i][1]:5} | "
            f"{result.finish[i]:6} | {result.waiting[i]:7} | "
            f"{result.turnaround[i]:10} | {result.response[i]:8}"
        )

    print(f"\nAverage Waiting Time:     {sum(result.waiting) / n:.2f}")
    print(f"Average Turnaround Time:  {sum(result.turnaround) / n:.2f}")
    print(f"Average Response Time:    {sum(result.response) / n:.2f}")
    print(f"\nTotal time (makespan):    {result.total_time}")
    print(f"CPU idle time:            {result.idle_time}")
    print(f"CPU utilization:          {result.cpu_utilization:.1f}%")
    print(f"Context switches:         {result.context_switches}")


def run_and_report(processes: list[tuple[int, int]]) -> SchedulingResult:
    """Run the simulation for ``processes`` and print everything."""
    result = srtf(processes)
    print_gantt_chart(result)
    print_results(processes, result)
    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

# The classic textbook example used by --demo (traced by hand in
# docs/04-worked-example.md so you can check the program's output).
DEMO_PROCESSES: list[tuple[int, int]] = [(0, 8), (1, 4), (2, 9), (3, 5)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SRTF (Shortest Remaining Time First) scheduling simulator."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="run the built-in textbook example instead of asking for input",
    )
    args = parser.parse_args()

    print("=== SRTF (Shortest Remaining Time First) Scheduling ===")

    if args.demo:
        print("\nDemo processes (arrival, burst):")
        for i, (arrival, burst) in enumerate(DEMO_PROCESSES, start=1):
            print(f"  P{i}: arrival={arrival}, burst={burst}")
        run_and_report(DEMO_PROCESSES)
        return

    processes: list[tuple[int, int]] = []
    n = get_positive_int("Enter the number of processes: ")

    for i in range(n):
        print(f"\nProcess P{i + 1}:")
        arrival = get_non_negative_int("  Arrival time: ")
        burst = get_positive_int("  Burst time:   ")
        processes.append((arrival, burst))

    run_and_report(processes)


if __name__ == "__main__":
    main()
