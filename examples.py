"""
Ready-made SRTF examples -- run them all with:

    python examples.py

Each example is chosen to teach one specific idea (noted above it).
Try predicting the Gantt chart *before* you run this file, then
check your prediction. That is the fastest way to learn SRTF.

Want the theory first? Start with docs/02-srtf-explained.md.
"""

from srtf import run_and_report

EXAMPLES: list[tuple[str, str, list[tuple[int, int]]]] = [
    (
        "Example 1 -- The classic textbook example",
        "P2 arrives at t=1 with less remaining time than P1, so it "
        "preempts P1. Hand-traced in docs/04-worked-example.md.",
        [(0, 8), (1, 4), (2, 9), (3, 5)],
    ),
    (
        "Example 2 -- Everybody arrives at time 0",
        "With no later arrivals there is nothing to preempt for: "
        "SRTF behaves exactly like non-preemptive SJF and simply "
        "runs the shortest job to completion, then the next one.",
        [(0, 6), (0, 2), (0, 4)],
    ),
    (
        "Example 3 -- The CPU sits idle",
        "P1 does not arrive until t=5, so the chart starts with an "
        "IDLE block. Between t=8 and t=10 the CPU idles again: "
        "being 'ready' matters as much as being 'short'.",
        [(5, 3), (10, 2)],
    ),
    (
        "Example 4 -- A dramatic preemption",
        "P1 needs 10 units, but tiny P2 (1 unit) arrives at t=2 and "
        "immediately takes the CPU. P1 resumes afterwards. Notice "
        "P1's response time is 0 even though it finishes last.",
        [(0, 10), (2, 1), (3, 2)],
    ),
    (
        "Example 5 -- A tie",
        "P1 and P2 arrive together with equal burst times. The "
        "simulator's tie-break rule (lowest process number wins) "
        "lets P1 run to completion first -- SRTF never switches "
        "between equals, because the running process's remaining "
        "time only gets smaller.",
        [(0, 3), (0, 3)],
    ),
    (
        "Example 6 -- Starvation in action",
        "Long P1 keeps being pushed aside by a stream of short "
        "jobs. Its waiting time explodes. This is SRTF's biggest "
        "weakness -- see docs/02-srtf-explained.md.",
        [(0, 12), (1, 2), (3, 2), (5, 2), (7, 2), (9, 2)],
    ),
]


def main() -> None:
    for title, lesson, processes in EXAMPLES:
        print("\n" + "=" * 72)
        print(title)
        print("=" * 72)
        print(f"Lesson: {lesson}")
        print("\nProcesses (arrival, burst):")
        for i, (arrival, burst) in enumerate(processes, start=1):
            print(f"  P{i}: arrival={arrival}, burst={burst}")
        run_and_report(processes)


if __name__ == "__main__":
    main()
