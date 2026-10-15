"""
Tests for the SRTF simulator.

Run them with the standard library only (no installs needed):

    python -m unittest discover -s tests -v

Every expected value below was computed by hand first -- the tests
double as worked examples. If you change the algorithm and a test
fails, check the hand computation in the test's comment before
assuming the test is wrong!
"""

import sys
import unittest
from pathlib import Path

# Make `import srtf` work no matter where the tests are run from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from srtf import srtf  # noqa: E402


class TestClassicExample(unittest.TestCase):
    """The textbook example, also traced in docs/04-worked-example.md.

    Processes: P1(0,8)  P2(1,4)  P3(2,9)  P4(3,5)

    By hand:
        0-1 P1 | 1-5 P2 | 5-10 P4 | 10-17 P1 | 17-26 P3
    """

    def setUp(self):
        self.result = srtf([(0, 8), (1, 4), (2, 9), (3, 5)])

    def test_finish_times(self):
        self.assertEqual(self.result.finish, [17, 5, 26, 10])

    def test_turnaround_times(self):
        # turnaround = finish - arrival
        self.assertEqual(self.result.turnaround, [17, 4, 24, 7])

    def test_waiting_times(self):
        # waiting = turnaround - burst
        self.assertEqual(self.result.waiting, [9, 0, 15, 2])

    def test_average_waiting_time(self):
        self.assertAlmostEqual(sum(self.result.waiting) / 4, 6.5)

    def test_response_times(self):
        # P3 waits the longest for its *first* tick: 17 - 2 = 15.
        self.assertEqual(self.result.response, [0, 0, 15, 2])

    def test_gantt_chart(self):
        chart = [(seg.label, seg.start, seg.end) for seg in self.result.gantt]
        self.assertEqual(
            chart,
            [("P1", 0, 1), ("P2", 1, 5), ("P4", 5, 10),
             ("P1", 10, 17), ("P3", 17, 26)],
        )

    def test_no_idle_time(self):
        self.assertEqual(self.result.idle_time, 0)
        self.assertEqual(self.result.total_time, 26)
        self.assertAlmostEqual(self.result.cpu_utilization, 100.0)


class TestSingleProcess(unittest.TestCase):
    def test_single_process_arriving_late(self):
        # CPU idles 0-3, then P1 runs uninterrupted 3-7.
        result = srtf([(3, 4)])
        self.assertEqual(result.finish, [7])
        self.assertEqual(result.turnaround, [4])
        self.assertEqual(result.waiting, [0])
        self.assertEqual(result.response, [0])
        self.assertEqual(result.idle_time, 3)
        chart = [(seg.label, seg.start, seg.end) for seg in result.gantt]
        self.assertEqual(chart, [("IDLE", 0, 3), ("P1", 3, 7)])


class TestPreemption(unittest.TestCase):
    def test_short_newcomer_preempts(self):
        # P1 runs 0-2, tiny P2 preempts 2-3, P1 resumes 3-11.
        result = srtf([(0, 10), (2, 1)])
        self.assertEqual(result.finish, [11, 3])
        self.assertEqual(result.waiting, [1, 0])   # P1 waited only while P2 ran
        self.assertEqual(result.response, [0, 0])
        self.assertEqual(result.context_switches, 2)  # P1->P2, P2->P1


class TestIdleCpu(unittest.TestCase):
    def test_gap_between_processes(self):
        # P1: 5-8, idle 8-10, P2: 10-12.
        result = srtf([(5, 3), (10, 2)])
        self.assertEqual(result.finish, [8, 12])
        self.assertEqual(result.waiting, [0, 0])
        self.assertEqual(result.idle_time, 7)  # 0-5 and 8-10
        # Idle gaps are not context switches.
        self.assertEqual(result.context_switches, 0)


class TestTies(unittest.TestCase):
    def test_equal_processes_run_in_index_order(self):
        # Tie at t=0 -> P1 wins (lowest index). After one tick P1's
        # remaining (2) beats P2's (3), so P1 is never preempted.
        result = srtf([(0, 3), (0, 3)])
        self.assertEqual(result.finish, [3, 6])
        self.assertEqual(result.waiting, [0, 3])
        self.assertEqual(result.response, [0, 3])


class TestAllArriveAtZero(unittest.TestCase):
    def test_degenerates_to_sjf(self):
        # Shortest job first, each to completion: P2, P3, P1.
        result = srtf([(0, 6), (0, 2), (0, 4)])
        self.assertEqual(result.finish, [12, 2, 6])
        self.assertEqual(result.context_switches, 2)


class TestValidation(unittest.TestCase):
    """The bugs fixed relative to the original version (see docs/03)."""

    def test_empty_list_rejected(self):
        with self.assertRaises(ValueError):
            srtf([])

    def test_negative_arrival_rejected(self):
        with self.assertRaises(ValueError):
            srtf([(-1, 5)])

    def test_zero_burst_rejected(self):
        # The original program looped forever on this input.
        with self.assertRaises(ValueError):
            srtf([(0, 0)])

    def test_negative_burst_rejected(self):
        with self.assertRaises(ValueError):
            srtf([(0, -3)])


class TestInvariants(unittest.TestCase):
    """Properties that must hold for *any* input."""

    CASES = [
        [(0, 8), (1, 4), (2, 9), (3, 5)],
        [(5, 3), (10, 2)],
        [(0, 1)],
        [(2, 5), (0, 3), (4, 1), (4, 1)],
        [(0, 12), (1, 2), (3, 2), (5, 2), (7, 2), (9, 2)],
    ]

    def test_metric_formulas_are_consistent(self):
        for processes in self.CASES:
            with self.subTest(processes=processes):
                result = srtf(processes)
                for i, (arrival, burst) in enumerate(processes):
                    self.assertEqual(result.turnaround[i],
                                     result.finish[i] - arrival)
                    self.assertEqual(result.waiting[i],
                                     result.turnaround[i] - burst)
                    self.assertGreaterEqual(result.waiting[i], 0)
                    self.assertGreaterEqual(result.response[i], 0)
                    # The wait for the *first* tick is part of the
                    # total wait, so response can never exceed waiting.
                    self.assertLessEqual(result.response[i],
                                         result.waiting[i])

    def test_gantt_covers_the_whole_makespan(self):
        for processes in self.CASES:
            with self.subTest(processes=processes):
                result = srtf(processes)
                covered = sum(seg.duration for seg in result.gantt)
                self.assertEqual(covered, result.total_time)
                self.assertEqual(result.gantt[0].start, 0)
                self.assertEqual(result.gantt[-1].end, result.total_time)
                # Busy ticks must add up to the total burst time.
                busy = sum(seg.duration for seg in result.gantt
                           if seg.pid is not None)
                self.assertEqual(busy, sum(b for _, b in processes))


if __name__ == "__main__":
    unittest.main()
