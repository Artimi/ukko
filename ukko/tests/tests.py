import unittest
import nose

import numpy as np
from ukko import RCPParser, Problem,  ActivityList, Schedule, ResourceUtilization, SSGS, SSGS_AL


TEST_FILE = '../../psplib/j30rcp/J301_1.RCP'


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = RCPParser()
        self.result = self.parser(TEST_FILE)

    def test_basic_info(self):
        self.assertEqual(self.result['num_activities'], 32)
        self.assertEqual(self.result['num_resources'], 4)
        np.testing.assert_array_equal(self.result['res_constraints'], np.array([12, 13, 4, 12], ndmin=2).T)

    def test_activities(self):
        activity = self.result['activities']
        self.assertEqual(activity['duration'][1], 8)
        np.testing.assert_array_equal(activity['res_demands'][:, 1], np.array([4, 0, 0, 0]))


class ProblemTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)

    def test_graph(self):
        self.assertEqual(len(self.problem.graph.vs), self.problem_dict['num_activities'])
        self.assertEqual(self.problem.graph.vs[1]['duration'], 8)
        self.assertListEqual(self.problem.graph.vs[1]['res_demands'], [4, 0, 0, 0])

    def test_dict_class(self):
        self.assertEqual(self.problem.num_activities, self.problem_dict['num_activities'])


class ActivityListTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)
        self.activities_order = [0, 1, 2, 3, 5, 10, 14, 6, 7, 12, 4, 8, 9, 25, 11, 18, 26,
                      17, 15, 13, 28, 19, 20, 16, 24, 27, 21, 30, 22, 23, 29, 31]
        self.al = ActivityList(self.problem, self.activities_order)

    def test_get_item(self):
        self.assertEqual(self.al[4], 5)

    def test_iterator(self):
        activities_order_real = [i for i in self.al]
        self.assertListEqual(activities_order_real, self.activities_order)

    def test_precedence_feasibility(self):
        self.assertTrue(self.al.is_precedence_feasible())
        wrong_order = self.activities_order
        wrong_order[0], wrong_order[1] = wrong_order[1], wrong_order[0]
        al_wrong = ActivityList(self.problem, wrong_order)
        self.assertFalse(al_wrong.is_precedence_feasible())


class ScheduleTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)
        self.activities_order = [0, 1, 2, 3, 5, 10, 14, 6, 7, 12, 4, 8, 9, 25, 11, 18, 26,
                                 17, 15, 13, 28, 19, 20, 16, 24, 27, 21, 30, 22, 23, 29, 31]
        self.al = ActivityList(self.problem, self.activities_order)
        self.schedule = Schedule(self.problem)

    def test_add(self):
        self.schedule.add(0, 0)
        self.assertIn(0, self.schedule.start_times[0])
        self.assertIn(0, self.schedule.finish_times[0])
        self.schedule.add(1, 0)
        self.assertIn(1, self.schedule.start_times[0])
        self.assertIn(1, self.schedule.finish_times[self.problem_dict['activities']['duration'][1]])

    def test_remove(self):
        self.assertRaises(KeyError, self.schedule.remove, 0)
        self.schedule.add(0, 0)
        self.schedule.remove(0)
        self.assertNotIn(0, self.schedule.start_times[0])
        self.assertNotIn(0, self.schedule.finish_times[0])
        self.schedule.add(0, 0)
        self.schedule.add(1, 0)
        self.schedule.remove(1)
        self.assertNotIn(1, self.schedule.start_times[0])
        self.assertNotIn(1, self.schedule.finish_times[self.problem_dict['activities']['duration'][1]])


    def test_can_place(self):
        self.assertFalse(self.schedule.can_place(1, 0))  # violated precedence 0->1
        self.schedule.add(0, 0)
        self.assertTrue(self.schedule.can_place(1, 0))
        self.schedule.add(1, 0)
        self.assertFalse(self.schedule.can_place(2, 0))  # violated resource constraints

    def test_makespan(self):
        self.assertEqual(self.schedule.makespan, 0)
        self.schedule.add(0, 0)
        self.assertEqual(self.schedule.makespan, 0)
        self.schedule.add(1, 0)
        self.assertEqual(self.schedule.makespan, 8)

    def test_eligible_activities(self):
        self.assertEqual(self.schedule.eligible_activities, {0})
        self.schedule.add(0, 0)
        self.assertEqual(self.schedule.eligible_activities, {1, 2, 3})
        self.schedule.add(1, 0)
        self.assertEqual(self.schedule.eligible_activities, {2, 3, 5, 10, 14})

    def test_earliest_start(self):
        self.schedule.add(0, 0)
        self.schedule.add(1, 0)
        self.assertEqual(self.schedule.earliest_precedence_start(5), 8)

    def test_shift(self):
        ssgs_al = SSGS_AL(self.problem, self.al)
        self.schedule = ssgs_al.get_schedule()
        initial_makespan = self.schedule.makespan
        self.schedule.shift('right')
        self.assertEqual(len(self.schedule.scheduled_activities), self.problem.num_activities)
        self.schedule.shift('right')  # nothing should change
        self.assertEqual(len(self.schedule.scheduled_activities), self.problem.num_activities)
        self.schedule.shift('left')
        self.assertEqual(len(self.schedule.scheduled_activities), self.problem.num_activities)
        self.assertGreaterEqual(initial_makespan, self.schedule.makespan)  # makespan should be same or better


class ResourceUtilizationTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)
        self.ru = ResourceUtilization(self.problem, max_makespan=16)

    def test_add(self):
        self.ru.add([4, 0, 0, 0], 0, 8)
        self.assertEqual(self.ru.get(0, 0), 4)
        self.assertEqual(self.ru.get(0, 7), 4)
        self.assertEqual(self.ru.get(0, 8), 0)
        self.assertEqual(self.ru.get(0, 9), 0)

    def test_remove(self):
        self.assertRaises(KeyError, self.ru.remove, [1, 1, 1, 1], 0, 8)
        self.ru.add([4, 0, 0, 0], 0, 8)
        self.ru.remove([4, 0, 0, 0], 0, 8)
        self.assertEqual(self.ru.get(0, 0), 0)
        self.assertEqual(self.ru.get(0, 8), 0)

    def test_extend(self):
        self.ru.add([4, 0, 0, 0], 16, 18)
        self.assertGreaterEqual(self.ru.max_makespan, 18)

    def test_free(self):
        res_constraints = np.array([12, 13, 4, 12], dtype=int)
        self.assertTrue(self.ru.is_free(res_constraints, 0, 5))
        self.ru.add(res_constraints, 0, 5)
        self.assertFalse(self.ru.is_free(np.array([1, 1, 1, 1], ndmin=2).T, 4, 6))


class SSGSTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)

    def test_basic(self):
        ssgs = SSGS(self.problem)
        schedule = ssgs.get_schedule()
        self.assertEqual(len(schedule.scheduled_activities), self.problem.num_activities)

    def test_al(self):
        activities_order = [0, 2, 1, 3, 5, 10, 14, 6, 7, 12, 4, 8, 9, 25, 11, 18, 26,
                            17, 15, 13, 28, 19, 20, 16, 24, 27, 21, 30, 22, 23, 29, 31]
        al = ActivityList(self.problem, activities_order)
        ssgs_al = SSGS_AL(self.problem, al)
        schedule = ssgs_al.get_schedule()
        self.assertEqual(len(schedule.scheduled_activities), self.problem.num_activities)
